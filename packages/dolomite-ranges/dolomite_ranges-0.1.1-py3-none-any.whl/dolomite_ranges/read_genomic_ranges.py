import os
from typing import Optional

import dolomite_base as dl
import h5py
from dolomite_base.read_object import read_object_registry
from genomicranges import GenomicRanges
from iranges import IRanges

from .read_sequence_information import read_sequence_information

read_object_registry["genomic_ranges"] = "dolomite_ranges.read_genomic_ranges"


def read_genomic_ranges(path: str, metadata: Optional[dict], **kwargs) -> GenomicRanges:
    """Load genomic ranges into a
    :py:class:`~genomicranges.GenomicRanges.GenomicRanges` object.

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
        A :py:class:`~genomicranges.GenomicRanges.GenomicRanges` object.
    """
    _seqinfo_path = os.path.join(path, "sequence_information")
    seqinfo = read_sequence_information(path=_seqinfo_path, metadata=None)

    with h5py.File(os.path.join(path, "ranges.h5"), "r") as handle:
        ghandle = handle["genomic_ranges"]

        seqnames = dl.load_vector_from_hdf5(
            ghandle["sequence"], expected_type=int, report_1darray=True
        )

        starts = dl.load_vector_from_hdf5(
            ghandle["start"], expected_type=int, report_1darray=True
        )

        widths = dl.load_vector_from_hdf5(
            ghandle["width"], expected_type=int, report_1darray=True
        )

        strand = dl.load_vector_from_hdf5(
            ghandle["strand"], expected_type=int, report_1darray=True
        )

    gr = GenomicRanges(
        seqnames=seqnames,
        ranges=IRanges(starts, widths),
        strand=strand,
        seqinfo=seqinfo,
    )

    _range_annotation_path = os.path.join(path, "range_annotations")
    if os.path.exists(_range_annotation_path):
        _mcols = dl.read_object(_range_annotation_path)
        gr = gr.set_mcols(_mcols)

    _meta_path = os.path.join(path, "other_annotations")
    if os.path.exists(_meta_path):
        _meta = dl.read_object(_meta_path)
        gr = gr.set_metadata(_meta.as_dict())

    return gr
