import os
from tempfile import mkdtemp

from biocframe import BiocFrame
from dolomite_base import read_object, save_object
from genomicranges import GenomicRanges, GenomicRangesList
from iranges import IRanges
import dolomite_ranges


def test_genomic_ranges_list():
    a = GenomicRanges(
        seqnames=["chr1", "chr2", "chr1", "chr3"],
        ranges=IRanges([1, 3, 2, 4], [10, 30, 50, 60]),
        strand=["-", "+", "*", "+"],
        mcols=BiocFrame({"score": [1, 2, 3, 4]}),
    )

    b = GenomicRanges(
        seqnames=["chr2", "chr4", "chr5"],
        ranges=IRanges([3, 6, 4], [30, 50, 60]),
        strand=["-", "+", "*"],
        mcols=BiocFrame({"score": [2, 3, 4]}),
    )

    grl = GenomicRangesList(ranges=[a, b], names=["a", "b"])

    dir = os.path.join(mkdtemp(), "granges")
    save_object(grl, dir)

    roundtrip = read_object(dir)
    assert roundtrip.get_names() == grl.get_names()
    assert len(roundtrip.get_ranges()) == len(grl.get_ranges())
    assert (roundtrip["a"].get_start() == grl["a"].get_start()).all()
    assert (roundtrip["a"].get_strand() == grl["a"].get_strand()).all()


def test_genomic_ranges_list_empty():
    grl = GenomicRangesList.empty(n=100)

    dir = os.path.join(mkdtemp(), "granges_empty")
    save_object(grl, dir)

    roundtrip = read_object(dir)
    assert roundtrip.get_names() == grl.get_names()
    assert len(roundtrip.get_ranges()) == len(grl.get_ranges())
    assert (roundtrip.get_range_lengths() == grl.get_range_lengths()).all()