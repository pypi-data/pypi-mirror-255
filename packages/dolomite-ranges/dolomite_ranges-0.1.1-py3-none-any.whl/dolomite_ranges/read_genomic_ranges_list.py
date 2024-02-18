import os
from typing import Optional

import dolomite_base as dl
import h5py
from dolomite_base.read_object import read_object_registry
from genomicranges import GenomicRangesList

from .read_genomic_ranges import read_genomic_ranges

read_object_registry["genomic_ranges_list"] = "dolomite_ranges.read_genomic_ranges_list"


def read_genomic_ranges_list(
    path: str, metadata: Optional[dict], **kwargs
) -> GenomicRangesList:
    """Load genomic ranges into a
    :py:class:`~genomicranges.GenomicRanges.GenomicRangesList` object.

    This method
    should generally not be called directly but instead be invoked by
    :py:meth:`~dolomite_base.read_object.read_object`.

    Args:
        path:
            Path to the directory containing the object.

        metadata:
            Metadata for the object.

        kwargs:
            Further arguments, ignored.

    Returns:
        A :py:class:`~genomicranges.GenomicRangesList.GenomicRangesList` object.
    """

    with h5py.File(os.path.join(path, "partitions.h5"), "r") as handle:
        ghandle = handle["genomic_ranges_list"]

        lengths = dl.load_vector_from_hdf5(
            ghandle["lengths"], expected_type=int, report_1darray=True
        )

        names = None
        if "names" in ghandle:
            names = dl.load_vector_from_hdf5(
                ghandle["names"], expected_type=str, report_1darray=True
            )

    _all_granges = read_genomic_ranges(
        path=os.path.join(path, "concatenated"), metadata=None
    )

    counter = 0
    _split_granges = []
    if lengths.sum() == 0:
        _split_granges = _all_granges
    else:
        for ilen in lengths:
            _frag = _all_granges[counter : (counter + ilen)]
            _split_granges.append(_frag)
            counter += ilen

    grl = GenomicRangesList(names=names, range_lengths=lengths, ranges=_split_granges)

    _elem_annotation_path = os.path.join(path, "element_annotations")
    if os.path.exists(_elem_annotation_path):
        _mcols = dl.read_object(_elem_annotation_path)
        grl = grl.set_mcols(_mcols)

    _meta_path = os.path.join(path, "other_annotations")
    if os.path.exists(_meta_path):
        _meta = dl.read_object(_meta_path)
        grl = grl.set_metadata(_meta.as_dict())

    return grl
