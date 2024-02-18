import os
from tempfile import mkdtemp

import biocframe
import dolomite_sce
import numpy
from dolomite_base import read_object, save_object
from singlecellexperiment import SingleCellExperiment
from summarizedexperiment import SummarizedExperiment


def test_stage_sce_basic():
    x = numpy.random.rand(1000, 200)
    se = SingleCellExperiment({"counts": x})

    dir = os.path.join(mkdtemp(), "sce_simple")
    save_object(se, dir)

    roundtrip = read_object(dir)
    assert isinstance(roundtrip, SingleCellExperiment)
    ass = roundtrip.assay("counts")
    assert ass.shape == (1000, 200)

    # Works with multiple assays.
    x2 = (numpy.random.rand(1000, 200) * 10).astype(numpy.int32)
    se = SingleCellExperiment(
        {"logcounts": x, "counts": x2}, main_experiment_name="aaron's secret modality"
    )

    dir = os.path.join(mkdtemp(), "sce_simple2")
    save_object(se, dir)

    roundtrip = read_object(dir)
    assert roundtrip.assay_names == ["logcounts", "counts"]
    assert se.main_experiment_name == roundtrip.main_experiment_name


def test_stage_sce_with_dimdata_with_names():
    x = numpy.random.rand(1000, 200)
    se = SingleCellExperiment(
        assays={"counts": x},
        row_data=biocframe.BiocFrame(row_names=["gene" + str(i) for i in range(1000)]),
        column_data=biocframe.BiocFrame(
            row_names=["cell" + str(i) for i in range(200)]
        ),
    )

    dir = os.path.join(mkdtemp(), "sce_dimdata2")
    save_object(se, dir)

    roundtrip = read_object(dir)
    assert isinstance(roundtrip, SingleCellExperiment)
    assert se.row_data.row_names == roundtrip.row_data.row_names
    assert se.column_data.row_names == roundtrip.column_data.row_names


def test_stage_sce_with_rdims():
    x = numpy.random.rand(1000, 200)
    se = SingleCellExperiment(
        assays={"counts": x},
        row_data=biocframe.BiocFrame(
            {"foo": numpy.random.rand(1000), "bar": numpy.random.rand(1000)}
        ),
        column_data=biocframe.BiocFrame(
            {"whee": numpy.random.rand(200), "stuff": numpy.random.rand(200)}
        ),
        reduced_dims={"tsnooch": numpy.random.rand(200, 4)},
    )

    dir = os.path.join(mkdtemp(), "sce_dimdata")
    save_object(se, dir)

    roundtrip = read_object(dir)
    assert isinstance(roundtrip, SingleCellExperiment)
    assert numpy.allclose(se.row_data["foo"], roundtrip.row_data["foo"])
    assert numpy.allclose(se.column_data["stuff"], roundtrip.column_data["stuff"])
    assert se.get_reduced_dim_names() == roundtrip.get_reduced_dim_names()
    assert numpy.allclose(
        se.reduced_dim("tsnooch"), numpy.array(roundtrip.reduced_dim("tsnooch"))
    )


def test_stage_sce_with_rdims_and_alts():
    x = numpy.random.rand(1000, 200)
    se = SingleCellExperiment(
        assays={"counts": x},
        row_data=biocframe.BiocFrame(
            {"foo": numpy.random.rand(1000), "bar": numpy.random.rand(1000)}
        ),
        column_data=biocframe.BiocFrame(
            {"whee": numpy.random.rand(200), "stuff": numpy.random.rand(200)}
        ),
        reduced_dims={"tsnooch": numpy.random.rand(200, 4)},
        alternative_experiments={
            "useless_modality": SummarizedExperiment(
                {"counts": numpy.random.rand(100, 200)}
            )
        },
    )

    dir = os.path.join(mkdtemp(), "sce_dimdata")
    save_object(se, dir)

    roundtrip = read_object(dir)
    assert isinstance(roundtrip, SingleCellExperiment)
    assert numpy.allclose(se.row_data["foo"], roundtrip.row_data["foo"])
    assert numpy.allclose(se.column_data["stuff"], roundtrip.column_data["stuff"])
    assert se.get_reduced_dim_names() == roundtrip.get_reduced_dim_names()
    assert numpy.allclose(
        se.reduced_dim("tsnooch"), numpy.array(roundtrip.reduced_dim("tsnooch"))
    )
    assert (
        se.get_alternative_experiment_names()
        == roundtrip.get_alternative_experiment_names()
    )
    assert numpy.allclose(
        se.alternative_experiment("useless_modality").assay("counts"),
        numpy.array(
            roundtrip.alternative_experiment("useless_modality").assay("counts")
        ),
    )


def test_stage_sce_with_other_meta():
    x = numpy.random.rand(1000, 200)
    se = SingleCellExperiment(assays={"counts": x}, metadata={"YAY": 2, "FOO": "a"})

    dir = os.path.join(mkdtemp(), "sce_other_meta")
    save_object(se, dir)

    roundtrip = read_object(dir)
    assert roundtrip.metadata == se.metadata


def test_empty_sce():
    se = SingleCellExperiment(assays={}, metadata={"YAY": 2, "FOO": "a"})

    dir = os.path.join(mkdtemp(), "sce_other_meta2")
    save_object(se, dir)

    roundtrip = read_object(dir)
    assert roundtrip.metadata == se.metadata
    assert len(se.get_assay_names()) == len(roundtrip.get_assay_names())


def test_empty_dimnames():
    se = SingleCellExperiment(
        assays={},
        row_data=biocframe.BiocFrame(row_names=["gene" + str(i) for i in range(1000)]),
        column_data=biocframe.BiocFrame(
            row_names=["cell" + str(i) for i in range(200)]
        ),
    )

    dir = os.path.join(mkdtemp(), "sce_dimdata3")
    save_object(se, dir)

    roundtrip = read_object(dir)
    assert isinstance(roundtrip, SingleCellExperiment)
    assert se.row_data.row_names == roundtrip.row_data.row_names
    assert se.column_data.row_names == roundtrip.column_data.row_names
    assert len(se.get_assay_names()) == len(roundtrip.get_assay_names())
