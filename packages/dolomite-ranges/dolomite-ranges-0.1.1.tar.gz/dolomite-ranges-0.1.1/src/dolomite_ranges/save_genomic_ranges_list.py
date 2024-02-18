import os
from typing import Optional

import dolomite_base as dl
import h5py
from biocutils import combine_sequences
from genomicranges import GenomicRangesList


@dl.save_object.register
@dl.validate_saves
def save_genomic_ranges_list(
    x: GenomicRangesList, path: str, data_frame_args: Optional[dict] = None, **kwargs
):
    """Method for saving :py:class:`~genomicranges.GenomicRanges.GenomicRangesList`
    objects to their corresponding file representations, see
    :py:meth:`~dolomite_base.save_object.save_object` for details.

    Args:
        x:
            Object to be staged.

        path:
            Path to a directory in which to save ``x``.

        data_frame_args:
            Further arguments to pass to the ``save_object`` method for
            ``mcols``.

        kwargs:
            Further arguments to be passed to individual methods.

    Returns:
        `x` is saved to `path`.
    """
    os.mkdir(path)

    if data_frame_args is None:
        data_frame_args = {}

    with open(os.path.join(path, "OBJECT"), "w", encoding="utf-8") as handle:
        handle.write(
            '{ "type": "genomic_ranges_list", "genomic_ranges_list": { "version": "1.0" } }'
        )

    with h5py.File(os.path.join(path, "partitions.h5"), "w") as handle:
        ghandle = handle.create_group("genomic_ranges_list")

        dl.write_integer_vector_to_hdf5(
            ghandle, name="lengths", h5type="u4", x=x.get_range_lengths()
        )

        if x.get_names() is not None:
            dl.write_string_vector_to_hdf5(ghandle, name="names", x=x.get_names())

    _all_ranges = x.get_ranges()
    if isinstance(_all_ranges, list) and len(_all_ranges) > 1:
        _all_ranges = combine_sequences(*x.get_ranges())

    dl.save_object(_all_ranges, path=os.path.join(path, "concatenated"))

    _elem_annotation = x.get_mcols()
    if _elem_annotation is not None and _elem_annotation.shape[1] > 0:
        dl.save_object(
            _elem_annotation,
            path=os.path.join(path, "element_annotations"),
            **data_frame_args
        )

    _meta = x.get_metadata()
    if _meta is not None and len(_meta) > 0:
        dl.save_object(_meta, path=os.path.join(path, "other_annotations"))

    return
