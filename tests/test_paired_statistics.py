import pytest

from infra_rag.paired_statistics import holm, paired_statistics


def rows(values):
    return [
        {"id": str(i), "group_id": group, "answerable": True, "delivered": {"complete": value}}
        for i, (group, value) in enumerate(values)
    ]


def test_cluster_sign_test_uses_groups_and_ignores_zero_delta_duplicates():
    before = rows([("a", False), ("a", False), ("b", False), ("c", True)])
    after = rows([("a", True), ("a", True), ("b", True), ("c", True)])
    result = paired_statistics(before, after, samples=100)
    assert result["delta_count"] == 3
    assert result["cluster_permutation_p"] == 0.5
    assert result["nonzero_clusters"] == 2
    assert result["recovered_ids"] == ["0", "1", "2"]
    reverse = paired_statistics(after, before, samples=100)
    assert reverse["delta_rate_ci95"] == [-x for x in reversed(result["delta_rate_ci95"])]
    assert reverse["cluster_permutation_p"] == result["cluster_permutation_p"]


def test_many_unchanged_clusters_still_use_exact_test():
    before = rows([(str(i), False) for i in range(37)])
    after = rows([(str(i), i < 2) for i in range(37)])
    result = paired_statistics(before, after, samples=100)
    assert result["permutation_method"] == "exact_cluster_sign"
    assert result["cluster_permutation_p"] == 0.5


def test_mismatched_pairs_are_rejected():
    before, after = rows([("a", False)]), rows([("b", True)])
    with pytest.raises(ValueError, match="cluster"):
        paired_statistics(before, after)
    with pytest.raises(ValueError, match="IDs"):
        paired_statistics(before, [])


def test_holm_is_monotone_and_capped():
    assert holm({"a": 0.01, "b": 0.03, "c": 0.9}) == {"a": 0.03, "b": 0.06, "c": 0.9}
