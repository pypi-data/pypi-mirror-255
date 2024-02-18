import os
from tempfile import mkdtemp

from biocframe import BiocFrame
import dolomite_se
import numpy
from summarizedexperiment import RangedSummarizedExperiment
from genomicranges import GenomicRanges, GenomicRangesList
from iranges import IRanges
from dolomite_base import read_object, save_object


def test_stage_rse_granges():
    x = numpy.random.rand(3, 200)
    rr = GenomicRanges(
        seqnames=["chr2", "chr4", "chr5"],
        ranges=IRanges([3, 6, 4], [30, 50, 60]),
        strand=["-", "+", "*"],
        mcols=BiocFrame({"score": [2, 3, 4]}),
    )
    se = RangedSummarizedExperiment({"counts": x}, row_ranges=rr)

    dir = os.path.join(mkdtemp(), "rse_simple")
    save_object(se, dir)

    roundtrip = read_object(dir)
    assert isinstance(roundtrip, RangedSummarizedExperiment)
    ass = roundtrip.assay("counts")
    assert ass.shape == (3, 200)

def test_stage_rse_grangeslist():
    # Works with multiple assays.
    x = numpy.random.rand(2, 200)
    x2 = (numpy.random.rand(2, 200) * 10).astype(numpy.int32)
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

    se = RangedSummarizedExperiment({"logcounts": x, "counts": x2}, row_ranges=grl)

    dir = os.path.join(mkdtemp(), "rse_simple2")
    save_object(se, dir)

    roundtrip = read_object(dir)
    assert roundtrip.assay_names == ["logcounts", "counts"]
