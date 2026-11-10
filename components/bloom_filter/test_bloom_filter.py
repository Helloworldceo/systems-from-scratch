import pytest

from bloom_filter import BloomFilter


def test_add_and_contains():
    bf = BloomFilter(size=128, num_hashes=3)
    bf.add("apple")
    bf.add("banana")
    assert "apple" in bf
    assert "banana" in bf
    assert "cherry" not in bf


def test_no_false_negatives():
    bf = BloomFilter(size=256, num_hashes=4)
    items = [f"item-{i}" for i in range(50)]
    for item in items:
        bf.add(item)
    for item in items:
        assert item in bf


def test_false_positives_possible_with_small_filter():
    # Tiny filter + many inserts forces collisions.
    bf = BloomFilter(size=16, num_hashes=2)
    for i in range(30):
        bf.add(f"x{i}")
    # Something never inserted should occasionally appear present.
    # With these parameters the FP rate is high enough that at least one of
    # a few probes is a false positive.
    probes = [f"never-{i}" for i in range(20)]
    assert any(p in bf for p in probes)


def test_invalid_arguments():
    with pytest.raises(ValueError):
        BloomFilter(0, 3)
    with pytest.raises(ValueError):
        BloomFilter(10, 0)
    with pytest.raises(ValueError):
        BloomFilter.from_capacity(0, 0.01)
    with pytest.raises(ValueError):
        BloomFilter.from_capacity(10, 0.0)


def test_from_capacity_and_estimate():
    bf = BloomFilter.from_capacity(capacity=100, error_rate=0.01)
    assert bf.size > 0
    assert bf.num_hashes >= 1
    for i in range(100):
        bf.add(i)
    rate = bf.estimated_false_positive_rate()
    assert 0 < rate < 0.1  # roughly the design target


def test_duplicate_adds_and_stats():
    bf = BloomFilter(size=64, num_hashes=2)
    bf.add("same")
    bf.add("same")
    assert len(bf) == 2
    assert bf.added == 2
    assert bf.bit_count() > 0
    assert "same" in bf
