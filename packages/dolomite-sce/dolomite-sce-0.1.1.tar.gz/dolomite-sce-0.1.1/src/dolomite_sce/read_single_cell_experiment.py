import json
import os

import dolomite_base as dl
from dolomite_base.read_object import read_object_registry
from dolomite_se import read_common_se_props
from singlecellexperiment import SingleCellExperiment

read_object_registry[
    "single_cell_experiment"
] = "dolomite_sce.read_single_cell_experiment"


def read_single_cell_experiment(
    path: str, metadata: dict, **kwargs
) -> SingleCellExperiment:
    """Load a
    :py:class:`~singlecellexperiment.SingleCellExperiment.SingleCellExperiment`
    from its on-disk representation.

    This method should generally not be called directly but instead be invoked by
    :py:meth:`~dolomite_base.read_object.read_object`.

    Args:
        path:
            Path to the directory containing the object.

        metadata:
            Metadata for the object.

        kwargs:
            Further arguments, ignored.

    Returns:
        A
        :py:class:`~singlecellexperiment.SingleCellExperiment.SingleCellExperiment`
        with file-backed arrays in the assays.
    """

    _row_data, _column_data, _assays = read_common_se_props(path)

    _main_expt_name = None
    if "main_experiment_name" in metadata["single_cell_experiment"]:
        _main_expt_name = metadata["single_cell_experiment"]["main_experiment_name"]

    sce = SingleCellExperiment(
        assays=_assays,
        row_data=_row_data,
        column_data=_column_data,
        main_experiment_name=_main_expt_name,
    )

    _meta_path = os.path.join(path, "other_data")
    if os.path.exists(_meta_path):
        _meta = dl.read_object(_meta_path)
        sce = sce.set_metadata(_meta.as_dict())

    _ranges_path = os.path.join(path, "row_ranges")
    if os.path.exists(_ranges_path):
        _ranges = dl.read_object(_ranges_path)
        sce = sce.set_row_ranges(_ranges)

    _rdim_path = os.path.join(path, "reduced_dimensions")
    if os.path.exists(_rdim_path):
        _rdims = {}

        with open(os.path.join(_rdim_path, "names.json"), "r") as handle:
            _rdim_names = json.load(handle)

        for _aidx, _aname in enumerate(_rdim_names):
            _rdim_read_path = os.path.join(_rdim_path, str(_aidx))

            try:
                _rdims[_aname] = dl.read_object(_rdim_read_path)
            except Exception as ex:
                raise RuntimeError(
                    f"failed to load reduced dimension '{_aname}' from '{path}'; "
                    + str(ex)
                )

        sce = sce.set_reduced_dims(_rdims)

    _alt_path = os.path.join(path, "alternative_experiments")
    if os.path.exists(_alt_path):
        _alts = {}

        with open(os.path.join(_alt_path, "names.json"), "r") as handle:
            _alt_names = json.load(handle)

        for _aidx, _aname in enumerate(_alt_names):
            _alt_read_path = os.path.join(_alt_path, str(_aidx))

            try:
                _alts[_aname] = dl.read_object(_alt_read_path)
            except Exception as ex:
                raise RuntimeError(
                    f"failed to load alternative experiment '{_aname}' from '{path}'; "
                    + str(ex)
                )

        sce = sce.set_alternative_experiments(_alts)

    return sce
