import filecmp
from unittest import mock

import pytest

from .. import Argument, DAG, Option, Layer, Node


@mock.patch("shutil.which", side_effect=lambda x: f"/path/to/{x}")
def test_dag_generation(mock_which, shared_datadir, tmp_path):
    # create DAG
    dag_name = "my_dag"
    dag = DAG(dag_name)

    # define job requirements
    requirements = {
        "environment": {
            "OMP_NUM_THREADS": 1,
        },
        "getenv": [
            "HOME",
            "USER",
        ],
        "request_cpus": 1,
        "request_memory": 2000,
        "requirements": [
            "HAS_CVMFS_oasis_opensciencegrid_org=TRUE",
        ],
    }

    # create processing layer, add nodes
    process_layer = Layer("process_bins", submit_description=requirements)
    output_files = []
    for i in range(3):
        output_file = f"output_{i}.txt"
        bin_idx = [3 * j + i for j in range(3)]
        node = Node(
            arguments=[
                Argument("job-index", i),
                Option("verbose"),
                Option("bins", bin_idx),
            ],
            inputs=Option("input", "data.txt"),
            outputs=Argument("output", output_file),
        )

        process_layer.append(node)
        output_files.append(output_file)

        # check command
        cmd = process_layer.command(node)
        bin_cmd = Option("bins", bin_idx).vars()
        expected = (
            f"process_bins {i} --verbose {bin_cmd} --input data.txt {output_file}"
        )
        assert cmd == expected

    # add layer to DAG
    dag.attach(process_layer)

    # create combine layer, add node
    with pytest.warns(DeprecationWarning):
        combine_layer = Layer("combine_bins", requirements=requirements)
    combine_layer += Node(
        arguments=Option("verbose"),
        inputs=Argument("input", output_files),
        outputs=Argument("output", "combined.txt"),
    )

    # add layer to DAG
    dag.attach(combine_layer)

    # write DAG to disk
    dag.write(tmp_path, write_script=True)

    # compare contents of generated files
    dag_filename = f"{dag_name}.dag"
    script_filename = f"{dag_name}.sh"
    assert filecmp.cmp(
        tmp_path / dag_filename, shared_datadir / dag_filename
    ), f"contents for {dag_filename} does not match expected output"
    for job in ("process_bins", "combine_bins"):
        sub_filename = f"{job}.sub"
        sub_path = tmp_path / sub_filename
        assert filecmp.cmp(
            sub_path, shared_datadir / sub_filename
        ), f"contents for {sub_filename} does not match expected output"
    assert filecmp.cmp(
        tmp_path / script_filename, shared_datadir / script_filename
    ), f"contents for {script_filename} does not match expected output"


@mock.patch("shutil.which", side_effect=lambda x: f"/path/to/{x}")
@pytest.mark.parametrize(
    "name,base_path,transfer_files",
    [
        ["rel", "relative/path/to", True],
        ["rel", "relative/path/to", False],
        ["abs", "/absolute/path/to", True],
        ["abs", "/absolute/path/to", False],
        ["url", "osdf:///path/to", True],
    ],
)
def test_dag_file_paths(
    mock_which, name, base_path, transfer_files, shared_datadir, tmp_path
):
    transfer_path = "transfer" if transfer_files else "no_transfer"
    expected_datadir = shared_datadir / name / transfer_path

    # create DAG
    dag_name = "count_dag"
    dag = DAG(dag_name)

    # define job requirements
    options = {
        "request_cpus": 1,
        "request_memory": 2000,
    }

    # create partitioning layer
    partition_layer = Layer(
        "partition_by_key", submit_description=options, transfer_files=transfer_files
    )
    output_files = []
    for i in range(3):
        input_files = [f"/abs/dir/data_{3 * i + j}.txt" for j in range(3)]
        output_file = f"{base_path}/output_{i}.txt"
        partition_layer += Node(
            arguments=["-j", 4],
            inputs=Argument("data", input_files),
            outputs=Argument("partitioned", output_file),
        )
        output_files.append(output_file)
    dag.attach(partition_layer)

    # create aggregation layer
    agg_layer = Layer(
        "aggregate_by_key", submit_description=options, transfer_files=transfer_files
    )
    for output_file in output_files:
        agg_layer += Node(
            arguments=Option("aggregate", "max"),
            inputs=Argument("data", output_file),
            outputs=Argument("aggregated-data", output_file, suppress=True),
        )
    dag.attach(agg_layer)

    # create count layer
    count_layer = Layer(
        "count_keys", submit_description=options, transfer_files=transfer_files
    )
    count_layer += Node(
        arguments=Option("verbose"),
        inputs=Argument("input", output_files),
        outputs=Argument("output", "combined.txt"),
    )
    dag.attach(count_layer)

    # write DAG to disk
    dag.write(tmp_path, write_script=True)

    # compare contents of generated files
    dag_filename = f"{dag_name}.dag"
    script_filename = f"{dag_name}.sh"
    assert filecmp.cmp(
        tmp_path / dag_filename, expected_datadir / dag_filename
    ), f"contents for {dag_filename} does not match expected output"
    for job in ("partition_by_key", "aggregate_by_key", "count_keys"):
        sub_filename = f"{job}.sub"
        sub_path = tmp_path / sub_filename
        assert filecmp.cmp(
            sub_path, expected_datadir / sub_filename
        ), f"contents for {sub_filename} does not match expected output"
    assert filecmp.cmp(
        tmp_path / script_filename, expected_datadir / script_filename
    ), f"contents for {script_filename} does not match expected output"
