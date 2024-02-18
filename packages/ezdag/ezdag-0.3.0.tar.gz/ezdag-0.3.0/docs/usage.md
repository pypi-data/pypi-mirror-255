# Usage

This library provides a high-level API on top of
[htcondor.dags](https://htcondor.readthedocs.io/en/latest/apis/python-bindings/api/dags.html),
with various helper classes to define jobs (nodes), job groupings (layers), and
the parent-child relations between them, described as a DAG.

The node and layer terminology is borrowed from `htcondor.dags`.

Extra information about `htcondor.dags` can be found here:

* [API documentation](https://htcondor.readthedocs.io/en/latest/apis/python-bindings/api/dags.html)
* [DAG Tutorial](https://htcondor.readthedocs.io/en/latest/apis/python-bindings/tutorials/DAG-Creation-And-Submission.html)

The general procedure for creating a DAG is as follows:

1. Create a `DAG`.
2. For each grouping of nodes, create a `Layer`. All jobs corresponding to this
   layer share the same submit description.
3. Create a `Node`with job arguments, inputs and outputs and attach them
   to the layer, one for each distinct job.
4. Attach the `Layer` to the `DAG`.
5. Repeat with every grouping of nodes, adding parent layers first.
6. Write the `DAG` to disk.

## Setting up the DAG

```python
from ezdag import Argument, DAG, Option, Layer, Node

dag = DAG("workflow")
```

A `DAG` represents the workflow and captures all parent-child relations between
nodes. Adding layers to the DAG tracks inputs and outputs and automatically
determines the parent-child relations between them. It is important that parent
layers are added to the DAG before child layers so the linking can be done
correctly.

The `DAG` extends from
[htcondor.dags.DAG](https://htcondor.readthedocs.io/en/latest/apis/python-bindings/api/dags.html#htcondor.dags.DAG)
so all keyword arguments for initialization and methods can be used in the same
way here.

## Defining groups of nodes

### Submit descriptors

First, we define submit descriptors for the jobs in question:

```python
description = {
    "environment": {
        "OMP_NUM_THREADS": 1,
    },
    "requirements": [
        "HAS_CVMFS_oasis_opensciencegrid_org=TRUE",
    ],
    "request_cpus": 1,
    "request_memory": 2000
}
```

This capture the job's requirements in terms of environment variables, resource
allocation, etc. Note that submit description values can take standard python
types, and the formatting will be handled automatically when writing the submit
file to disk. e.g. passing in a list of `getenv` variables will format them to
be comma separated.

Also note that this captures a subset of the submit descriptors needed for the
jobs. Descriptors such as the universe, executable, arguments, and all
descriptors related to logging and file transfer are added by the layer itself.

### The layer (job groupings)

Then, we define the layer itself with the executable and the submit description:

```python
layer = Layer("process_bins", submit_description=description)
```

By default, the layer name is taken from the executable name. In addition, the
path to the executable is resolved at DAG generation through `$PATH`. Both of
these can be customized by providing a different layer name and providing a valid
path to the executable in question, respectively:

```python
layer = Layer(
    "/path/to/process_bins",
    name="my_super_cool_process",
    submit_description=description
)
```

Also by default, Condor file transfer is enabled. Any files provided in job inputs
and outputs (seen later) will be resolved and the relevant submit descriptors will
be added to the submit file. To disable this behavior, you can set `transfer_files`
to `False`.

Other relevant parameters to `Layer` include:

* `universe`: Set the execution environment for the jobs.
* `retries`: Number of retries given for jobs.
* `log_dir`: Set the directory where job logs are written to.

### The nodes (jobs)

Nodes define the individual job arguments, as well as any file inputs and outputs
for file transfer and for determining parent-child relationships between jobs.

```python
for i in range(3):
    node = Node(
        arguments = [
            Argument("job-index", i),                       # {i}
            Option("verbose"),                              # --verbose
            Option("bins", [3 * j + i for j in range(3)]),  # --bins {i} --bins {3 + i} --bins {6 + i}
            "--num-cores", 1,                                # --num-cores 1
        ],
        inputs = Option("input", "data.txt"),               # --input data.txt
        outputs = Argument("output", f"output_{i}.txt")     # output_{i}.txt
    )
    layer.append(node)
```

In order to aid in generating job arguments for jobs, we also provide a few
helper classes, the `Argument` and `Option` which provide positional arguments
and options, respectively. Some examples of the output they provide to the
job's arguments are shown in the comments on the right. Both of these are used
to parameterize job arguments so they can be changed on a per-job level for a
given layer without having to do this manually, as in `htcondor.dags`.

In addition to these, non-parameterized arguments can be provided as primitive
types which will be passed directly to `arguments` in the submit description.

Inputs and outputs are used to track which files the job requires and provides,
respectively, and are used to track job dependencies. Any path or URL supported
by Condor are accepted and will be modified accordingly so that Condor file
transfer works as expected.

Finally, nodes can take meta-parameters (`variables`) which can be referred
to within the submit description. These can be useful for example, when
parameterizing log filenames.

### Defining node parameters

As mentioned above, the `Argument` and `Option` are helpers to generate job
arguments, which provide positional arguments and options, respectively.

Both take a parameter which defines the parameter name, as well as the value
to be provided to the job itself. For arguments, only the value is used, while
for options, the name is used within the argument to define the flag name.
In both cases, the value can be any primitive type or a list of such.

Some examples:

* `#!python Argument("factor", 4.1)` &rarr; `4.1`
* `#!python Argument("files", ["file1.txt", "file2.txt"])` &rarr; `file1.txt file2.txt`
* `#!python Option("verbose")` &rarr; `--verbose`
* `#!python Option("num-jobs", 2)` &rarr; `--num-jobs 2`
* `#!python Option("input", ["file1.txt", "file2.txt"])` &rarr; `--input file1.txt --input file2.txt`

As jobs may not always have an intuitive CLI or provide and/or generate files
directly through their CLI, some extra options are provided to `Argument` and
`Option` to deal with these edge cases. For example, jobs may generate extra
files which are not specified anywhere, but may be required for child jobs. In
this case, you can define these implicit job outputs by providing
`suppress=True` which will hide the command from the job's `arguments`.

If you don't want to track any files in the inputs or outputs for inter-job
relationships, you can provide `track=False` to `Argument` or `Option`. This
can be useful when jobs need files to be transferred in, but you may not want
or need this file to be a decision when determining job relationships.

## Adding inter-layer relationships

To define inter-layer relationships between layers, simply add the layers in
the DAG with parent layers first:

```python
dag.attach(layer)
```

When the layers are added to the DAG, node inputs and outputs determine how
they are connected to each other.

## Submitting the DAG

You can submit the DAG directly:

```python
dag.submit()
```

This will build and write the DAG as well as all the submit files to disk
prior to submission. The submitted DAG will take the name given upon creation,
i.e. for `DAG("workflow")`, this will create `workflow.dag`.

If you want to instead write the DAG to disk without submitting it:

```python
dag.write()
```

Both methods take a `path` parameter which changes where the DAG is written
to disk. By default, this is written to the current working directory.
