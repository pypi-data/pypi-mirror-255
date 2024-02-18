import os

import dolomite_base as dl
from dolomite_base.read_object import read_object_registry
from summarizedexperiment import RangedSummarizedExperiment

from .utils import read_common_se_props

read_object_registry[
    "ranged_summarized_experiment"
] = "dolomite_se.read_ranged_summarized_experiment"


def read_ranged_summarized_experiment(
    path: str, metadata: dict, **kwargs
) -> RangedSummarizedExperiment:
    """Load a
    :py:class:`~summarizedexperiment.RangedSummarizedExperiment.RangedSummarizedExperiment`
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
        :py:class:`~summarizedexperiment.RangedSummarizedExperiment.RangedSummarizedExperiment`
        with file-backed arrays in the assays.
    """

    _row_data, _column_data, _assays = read_common_se_props(path)

    rse = RangedSummarizedExperiment(
        assays=_assays,
        row_data=_row_data,
        column_data=_column_data,
    )

    _meta_path = os.path.join(path, "other_data")
    if os.path.exists(_meta_path):
        _meta = dl.read_object(_meta_path)
        rse = rse.set_metadata(_meta.as_dict())

    _ranges_path = os.path.join(path, "row_ranges")
    if os.path.exists(_ranges_path):
        _ranges = dl.read_object(_ranges_path)
        rse = rse.set_row_ranges(_ranges)

    return rse
