<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/dolomite-sce.svg?branch=main)](https://cirrus-ci.com/github/<USER>/dolomite-sce)
[![ReadTheDocs](https://readthedocs.org/projects/dolomite-sce/badge/?version=latest)](https://dolomite-sce.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/dolomite-sce/main.svg)](https://coveralls.io/r/<USER>/dolomite-sce)
[![PyPI-Server](https://img.shields.io/pypi/v/dolomite-sce.svg)](https://pypi.org/project/dolomite-sce/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/dolomite-sce.svg)](https://anaconda.org/conda-forge/dolomite-sce)
[![Monthly Downloads](https://pepy.tech/badge/dolomite-sce/month)](https://pepy.tech/project/dolomite-sce)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/dolomite-sce)
-->

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![PyPI-Server](https://img.shields.io/pypi/v/dolomite-sce.svg)](https://pypi.org/project/dolomite-sce/)
![Unit tests](https://github.com/ArtifactDB/dolomite-sce/actions/workflows/pypi-test.yml/badge.svg)

# Save and write `SingleCellExperiments` in Python

## Introduction

The **dolomite-sce** package is the Python counterpart to the [**alabaster.sce**](https://github.com/ArtifactDB/alabaster.sce) R package,
providing methods for saving/reading `SingleCellExperiment` objects within the [**dolomite** framework](https://github.com/ArtifactDB/dolomite-base).

## Quick start

Let's mock up a `SingleCellExperiment` that contains reduced dimensions and alternative experiments,

```python
from singlecellexperiment import SingleCellExperiment
import biocframe
import numpy

sce = SingleCellExperiment(
     assays={"counts": numpy.random.rand(1000, 200)},
     row_data=biocframe.BiocFrame(
          {"foo": numpy.random.rand(1000), "bar": numpy.random.rand(1000)}
     ),
     column_data=biocframe.BiocFrame(
          {"whee": numpy.random.rand(200), "stuff": numpy.random.rand(200)}
     ),
     reduced_dims={"tsnooch": numpy.random.rand(200, 4)},
     alternative_experiments={
          "very_useful_modality": SummarizedExperiment(
               {"counts": numpy.random.rand(100, 200)}
          )
     },
)
```

Now we can save it:

```python
from dolomite_base import save_object
import dolomite_sce
import os
from tempfile import mkdtemp

path = os.path.join(mkdtemp(), "test")
save_object(se, path)
```

And load it again, e,g., in a new session:

```python
from dolomite_base import read_object

roundtrip = read_object(path)
## Class SingleCellExperiment with 1000 features and 200 cells
##   assays: ['counts']
##   row_data: ['foo']
##   column_data: ['whee']
```