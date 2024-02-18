# Copyright (C) 2020 Patrick Godwin
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at
# <https://mozilla.org/MPL/2.0/>.
#
# SPDX-License-Identifier: MPL-2.0

from collections import defaultdict
import os
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple
import warnings

# disable warnings when condor config source is not found
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    import htcondor
    from htcondor import dags

from .layers import HexFormatter, Layer


class DAG(dags.DAG):
    """Defines a DAGMan workflow including the execution graph and configuration.

    Parameters
    ----------
    name : str
        The name of the DAG workflow, used for files written to disk and for
        DAG submission when calling write() and submit(). Defaults to "workflow".
    formatter : htcondor.dags.NodeNameFormatter
        Defines how the node names are defined and formatted. Defaults to a
        hex-based formatter with 5 digits.
    *args
        Any positional arguments that htcondor.dags.DAG accepts
    **kwargs
        Any keyword arguments that htcondor.dags.DAG accepts

    """

    def __init__(
        self,
        name: str = "workflow",
        formatter: Optional[dags.NodeNameFormatter] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        self._node_layers: Dict[str, dags.NodeLayer] = {}
        self._ordered_layers: List[dags.NodeLayer] = []
        self._layers: Dict[str, Layer] = {}
        self._provides: Dict[str, Tuple[str, int]] = {}
        if formatter:
            self.formatter = formatter
        else:
            self.formatter = HexFormatter()
        self._dag_path: Optional[str] = None

    def attach(self, layer: Layer) -> None:
        """Attach a layer of related job nodes to this DAG.

        Parameters
        ----------
        layer
            The layer to attach.

        """
        key = layer.name
        if key in self._layers:
            raise KeyError(f"{key} layer already added to DAG")
        self._layers[layer.name] = layer

        # determine parent-child relationships and connect accordingly
        all_edges = defaultdict(set)
        if layer.has_dependencies:
            # determine edges
            for child_idx, node in enumerate(layer.nodes):
                for input_ in node.requires:
                    if input_ in self._provides:
                        parent_name, parent_idx = self._provides[input_]
                        all_edges[parent_name].add((parent_idx, child_idx))

            if not all_edges:
                node_layer = self.layer(**layer.config(self.formatter))
                self._node_layers[key] = node_layer
                self._ordered_layers.append(node_layer)

            # determine edge type and connect
            for num, (parent, edges) in enumerate(all_edges.items()):
                edge = self._get_edge_type(parent, layer.name, edges)
                if num == 0:
                    node_layer = self._node_layers[parent].child_layer(
                        **layer.config(self.formatter), edge=edge
                    )
                    self._node_layers[key] = node_layer
                    self._ordered_layers.append(node_layer)
                else:
                    self._node_layers[key].add_parents(
                        self._node_layers[parent], edge=edge
                    )

        else:
            node_layer = self.layer(**layer.config(self.formatter))
            self._node_layers[key] = node_layer
            self._ordered_layers.append(node_layer)

        # register any data products the layer provides
        for idx, node in enumerate(layer.nodes):
            for output in node.provides:
                self._provides[output] = (key, idx)

    def create_log_dir(self, log_dir: Path = Path("logs")) -> None:
        """Create the log directory where job logs are stored.

        Parameters
        ----------
        log_dir : Path
            The directory to create logs in. Defaults to ./logs.

        """
        warnings.warn(
            "create_log_dir has been deprecated in favor of automatically "
            "creating log directories upon DAG generation. this method "
            "will be removed in a future release",
            DeprecationWarning,
        )
        os.makedirs(log_dir, exist_ok=True)

    def write(self, path: Path = Path.cwd(), write_script: bool = False) -> None:
        """Write out the given DAG to the given directory.

        This includes the DAG description file itself, as well as any
        associated submit descriptions and log directories.

        Also optionally writes out the list of commands for each node, which
        represents commands that would be run on the execute point, after
        taking into account file location changes where the job would be run if
        file transfer is enabled.

        Parameters
        ----------
        path : Path
            The directory to write the DAG files to. Defaults to the current working
            directory.
        write_script : bool
            Also write out the list of commands for each node to disk. Defaults
            to false.

        """
        dag_file = f"{self.name}.dag"
        self._write_dag(dag_file, path=path)
        self._dag_path = str(path / dag_file)
        if write_script:
            self._write_script(f"{self.name}.sh", path=path)

    def submit(
        self, path: Path = Path.cwd(), write_script: bool = False, **kwargs
    ) -> None:
        """Submit the DAG via HTCondor.

        If the DAG has not already been written to disk, do so as well.
        This is equivalent to calling write() prior to submission, making
        use of the `path` and `write_script` arguments for doing so. See
        DAG.write for more information.

        Parameters
        ----------
        path : Path
            The directory to write the DAG files to. Defaults to the current working
            directory.
        write_script : bool
            Also write out the list of commands for each node to disk. Defaults
            to false.
        **kwargs
            Any keyword arguments that `condor_submit_dag` accepts. See
            [htcondor.Submit.from_dag](https://htcondor.readthedocs.io/en/latest/apis/python-bindings/api/htcondor.html#htcondor.Submit.from_dag)
            for more information.

        """
        # write DAG to disk if not already done
        if not self._dag_path:
            self.write(path, write_script)
            self._dag_path = str(path / f"{self.name}.dag")

        # submit the DAG
        submit_kwargs = {"UseDagDir": True, **kwargs}
        dag_submit = htcondor.Submit.from_dag(self._dag_path, submit_kwargs)
        htcondor.Schedd().submit(dag_submit)

    def write_dag(self, filename: str, path: Path = Path.cwd(), **kwargs) -> None:
        """Write out the given DAG to the given directory.

        This includes the DAG description file itself, as well as any
        associated submit descriptions and log directories.

        Parameters
        ----------
        filename : str
            The name of the DAG description file itself, e.g. my_dag.dag.
        path : Path
            The directory to write the DAG files to. Defaults to the current working
            directory.
        **kwargs
            Any other keyword arguments that htcondor.dags.write_dag accepts

        """
        warnings.warn(
            "write_dag has been deprecated in favor of write. "
            "this method will be removed in a future release",
            DeprecationWarning,
        )
        self._write_dag(filename, path, **kwargs)

    def write_script(
        self,
        filename: str,
        path: Path = Path.cwd(),
    ) -> None:
        """Write out the list of commands for each node to the given directory.

        This represents commands that would be run on the execute point, after
        taking into account file location changes where the job would be run if
        file transfer is enabled.

        Parameters
        ----------
        filename : str
            The name of the script file itself, e.g. my_dag.sh.
        path : Path
            The directory to write the script file to. Defaults to the current working
            directory.

        """
        warnings.warn(
            "write_dag has been deprecated in favor of write. "
            "this method will be removed in a future release",
            DeprecationWarning,
        )
        self._write_script(filename, path)

    def _write_dag(self, filename: str, path: Path = Path.cwd(), **kwargs) -> None:
        """Write out the given DAG to the given directory.

        This includes the DAG description file itself, as well as any
        associated submit descriptions and log directories.

        Parameters
        ----------
        filename : str
            The name of the DAG description file itself, e.g. my_dag.dag.
        path : Path
            The directory to write the DAG files to. Defaults to the current working
            directory.
        **kwargs
            Any other keyword arguments that htcondor.dags.write_dag accepts

        """
        # create log directories
        for name, layer in self._layers.items():
            if os.path.isabs(layer.log_dir):
                log_path = Path(layer.log_dir)
            else:
                submit = self._node_layers[name].submit_description
                initialdir = Path(submit.get("initialdir", str(path)))
                log_path = initialdir / layer.log_dir
            os.makedirs(log_path, exist_ok=True)

        # create DAG and submit files
        dags.write_dag(
            self,
            path,
            dag_file_name=filename,
            node_name_formatter=self.formatter,
            **kwargs,
        )

    def _write_script(
        self,
        filename: str,
        path: Path = Path.cwd(),
    ) -> None:
        """Write out the list of commands for each node to the given directory.

        This represents commands that would be run on the execute point, after
        taking into account file location changes where the job would be run if
        file transfer is enabled.

        Parameters
        ----------
        filename : str
            The name of the script file itself, e.g. my_dag.sh.
        path : Path
            The directory to write the script file to. Defaults to the current working
            directory.

        """
        with open(path / filename, "w") as f:
            # traverse DAG in breadth-first order
            for layer in self._ordered_layers:
                # grab relevant submit args, format $(arg) to {arg}
                executable = layer.submit_description["executable"]
                args = layer.submit_description["arguments"]
                args = re.sub(r"\$\(((\w+?))\)", r"{\1}", args)

                # evaluate vars for each node in layer, write to disk
                for idx, node_vars in enumerate(layer.vars):
                    node_name = self.formatter.generate(layer.name, idx)
                    print(f"# Job {node_name}", file=f)
                    print(executable + " " + args.format(**node_vars) + "\n", file=f)

    def _get_edge_type(self, parent_name, child_name, edges) -> dags.BaseEdge:
        parent = self._layers[parent_name]
        child = self._layers[child_name]
        edges = sorted(list(edges))

        # check special cases, defaulting to explicit edge connections via indices
        if len(edges) == (len(parent.nodes) + len(child.nodes)):
            return dags.ManyToMany()

        elif len(parent.nodes) == len(child.nodes) and all(
            [parent_idx == child_idx for parent_idx, child_idx in edges]
        ):
            return dags.OneToOne()

        else:
            return EdgeConnector(edges)


class EdgeConnector(dags.BaseEdge):
    """This edge connects individual nodes in layers given an explicit mapping."""

    def __init__(self, indices) -> None:
        self.indices = indices

    def get_edges(self, parent, child, join_factory):
        for parent_idx, child_idx in self.indices:
            yield (parent_idx,), (child_idx,)


def write_dag(
    dag: dags.DAG,
    dag_dir: Path = Path.cwd(),
    formatter: Optional[dags.NodeNameFormatter] = None,
    **kwargs,
) -> Path:
    """Write out the given DAG to the given directory.

    This includes the DAG description file itself, as well as any associated
    submit descriptions.

    Parameters
    ----------
    dag : DAG
        The DAG to write.
    dag_dir : Path
        The directory to write the DAG files to. Defaults to the current working
        directory.
    formatter : htcondor.dags.NodeNameFormatter
        Defines how the node names are defined and formatted. Defaults to a
        hex-based formatter with 5 digits.
    **kwargs
        Any other keyword arguments that htcondor.dags.write_dag accepts

    """
    warnings.warn(
        "write_dag has been deprecated in favor of DAG.write. "
        "this method will be removed in a future release",
        DeprecationWarning,
    )
    if not formatter:
        formatter = HexFormatter()
    return dags.write_dag(dag, dag_dir, node_name_formatter=formatter, **kwargs)
