import json
import os

import dolomite_base as dl
from dolomite_se import save_common_se_props
from singlecellexperiment import SingleCellExperiment


@dl.save_object.register
@dl.validate_saves
def save_single_cell_experiment(
    x: SingleCellExperiment,
    path: str,
    data_frame_args: dict = None,
    assay_args: dict = None,
    rdim_args: dict = None,
    alt_expts_args: dict = None,
    **kwargs,
):
    """Method for saving
    :py:class:`~singlecellexperiment.SingleCellExperiment.SingleCellExperiment`
    objects to their corresponding file representations, see
    :py:meth:`~dolomite_base.save_object.save_object` for details.

    Args:
        x:
            Object to be staged.

        path:
            Path to a directory in which to save ``x``.

        data_frame_args:
            Further arguments to pass to the ``save_object`` method for the
            row/column data.

        assay_args:
            Further arguments to pass to the ``save_object`` method for the
            assays.

        rdim_args:
            Further arguments to pass to the ``save_object`` method for the
            reduced dimensions.

        alt_expts_args:
            Further arguments to pass to the ``save_object`` method for the
            alternative experiments.

        kwargs:
            Further arguments, ignored.

    Returns:
        ``x`` is saved to path.
    """
    os.mkdir(path)

    if data_frame_args is None:
        data_frame_args = {}

    if assay_args is None:
        assay_args = {}

    if rdim_args is None:
        rdim_args = {}

    if alt_expts_args is None:
        alt_expts_args = {}

    _se_meta = f"{list(x.shape)}"

    _sce_meta = '"single_cell_experiment": { "version": "1.0" }'
    if x.get_main_experiment_name() is not None:
        _sce_meta = (
            '"single_cell_experiment": { "version": "1.0", "main_experiment_name": "'
            + str(x.get_main_experiment_name())
            + '" }'
        )

    with open(os.path.join(path, "OBJECT"), "w", encoding="utf-8") as handle:
        handle.write(
            '{ "type": "single_cell_experiment", '
            + _sce_meta
            + ", "
            + '"ranged_summarized_experiment": { "version": "1.0" },'
            + '"summarized_experiment": {"version": "1.0", "dimensions": '
            + _se_meta
            + " } }"
        )

    save_common_se_props(
        x, path, data_frame_args=data_frame_args, assay_args=assay_args
    )

    _ranges = x.get_row_ranges()
    if _ranges is not None:
        dl.save_object(_ranges, path=os.path.join(path, "row_ranges"))

    # save rdims
    _rdim_names = x.get_reduced_dim_names()
    if len(_rdim_names) > 0:
        _rdim_path = os.path.join(path, "reduced_dimensions")
        os.mkdir(_rdim_path)

        with open(os.path.join(_rdim_path, "names.json"), "w") as handle:
            json.dump(_rdim_names, handle)

        for _aidx, _aname in enumerate(_rdim_names):
            _rdim_save_path = os.path.join(_rdim_path, str(_aidx))
            try:
                dl.save_object(x.reduced_dim(_aname), path=_rdim_save_path, **rdim_args)
            except Exception as ex:
                raise RuntimeError(
                    "failed to stage reduced dimension '"
                    + _aname
                    + "' for "
                    + str(type(x))
                    + "; "
                    + str(ex)
                )

    # save alt expts.
    _alt_names = x.get_alternative_experiment_names()
    if len(_alt_names) > 0:
        _alt_path = os.path.join(path, "alternative_experiments")
        os.mkdir(_alt_path)

        with open(os.path.join(_alt_path, "names.json"), "w") as handle:
            json.dump(_alt_names, handle)

        for _aidx, _aname in enumerate(_alt_names):
            _alt_save_path = os.path.join(_alt_path, str(_aidx))
            try:
                dl.save_object(
                    x.alternative_experiment(_aname),
                    path=_alt_save_path,
                    **alt_expts_args,
                )
            except Exception as ex:
                raise RuntimeError(
                    "failed to stage alternative experiment '"
                    + _aname
                    + "' for "
                    + str(type(x))
                    + "; "
                    + str(ex)
                )
    return
