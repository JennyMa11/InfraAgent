"""Paired cluster statistics for fixed development experiments."""

import itertools
import math
import random
from collections import defaultdict


def paired_statistics(before, after, *, samples=10000, seed=42):
    if samples < 40:
        raise ValueError("at least 40 bootstrap samples required")
    indexed = {row["id"]: row for row in after if row["answerable"]}
    old = {row["id"]: row for row in before if row["answerable"]}
    if old.keys() != indexed.keys() or not old:
        raise ValueError("paired answerable IDs must match")
    groups = defaultdict(lambda: [0, 0])
    lost, recovered = [], []
    for cid, row in old.items():
        new = indexed[cid]
        if row["group_id"] != new["group_id"]:
            raise ValueError("paired cluster IDs must match")
        left, right = row["delivered"]["complete"], new["delivered"]["complete"]
        groups[row["group_id"]][0] += right - left
        groups[row["group_id"]][1] += 1
        if left and not right:
            lost.append(cid)
        if right and not left:
            recovered.append(cid)
    grouped = list(groups.values())
    delta = sum(d for d, _ in grouped)
    rng, draws = random.Random(seed), []
    for _ in range(samples):
        draw = rng.choices(grouped, k=len(grouped))
        draws.append(sum(d for d, _ in draw) / sum(n for _, n in draw))
    draws.sort()
    # Zero-delta clusters contribute identical copies of every permutation.
    nonzero = [d for d, _ in grouped if d]
    if len(nonzero) <= 20:
        extreme = sum(
            abs(sum(sign * d for sign, d in zip(signs, nonzero, strict=True))) >= abs(delta)
            for signs in itertools.product((-1, 1), repeat=len(nonzero))
        )
        permutation_p = extreme / 2 ** len(nonzero)
        permutation_method = "exact_cluster_sign"
    else:
        permutation_rng = random.Random(seed)
        extreme = sum(
            abs(sum(permutation_rng.choice((-1, 1)) * d for d in nonzero)) >= abs(delta)
            for _ in range(100000)
        )
        permutation_p = (extreme + 1) / 100001
        permutation_method = "monte_carlo_cluster_sign_100000"
    discordant = len(lost) + len(recovered)
    mcnemar = (
        min(
            1.0,
            2
            * sum(math.comb(discordant, i) for i in range(min(len(lost), len(recovered)) + 1))
            / 2**discordant,
        )
        if discordant
        else 1.0
    )
    return {
        "n": len(old),
        "clusters": len(grouped),
        "delta_count": delta,
        "delta_rate": delta / len(old),
        "delta_rate_ci95": [draws[int(samples * 0.025)], draws[int(samples * 0.975)]],
        "cluster_permutation_p": permutation_p,
        "permutation_method": permutation_method,
        "nonzero_clusters": len(nonzero),
        "mcnemar_p_supplemental": mcnemar,
        "lost_ids": sorted(lost),
        "recovered_ids": sorted(recovered),
        "samples": samples,
        "seed": seed,
    }


def holm(p_values):
    adjusted, highest = {}, 0.0
    for i, (key, value) in enumerate(sorted(p_values.items(), key=lambda item: item[1])):
        highest = max(highest, min(1.0, value * (len(p_values) - i)))
        adjusted[key] = highest
    return adjusted
