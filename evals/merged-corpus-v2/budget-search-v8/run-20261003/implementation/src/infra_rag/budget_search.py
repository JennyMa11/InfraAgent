"""Query-only budget search for isolated experiments; never consume relevance labels."""

import itertools
import math
from dataclasses import replace

from .budget_ablation import AblationPacker
from .chunking import stable_id
from .context import pack_context


class BudgetSearch:
    """Compare greedy and bounded exchanges with an identical set objective."""

    def __init__(self, hits, query, count, *, frontier_limit=30):
        self.packer = AblationPacker(
            hits, {"evidence": []}, {}, query, count, frontier_limit=frontier_limit
        )
        (
            self.frontier,
            _,
            self.words,
            self.wanted,
            self.weights,
            self.total,
            self.texts,
            _,
        ) = self.packer.prepare(False)
        self.ids = tuple(self.frontier)
        self.positions = {cid: i for i, cid in enumerate(self.ids)}
        self.count = count
        self.similarity = {
            (a, b): len(self.words[a] & self.words[b]) / max(1, len(self.words[a] | self.words[b]))
            for a, b in itertools.combinations(self.ids, 2)
        }

    def ordered(self, ids):
        return tuple(sorted(ids, key=self.positions.__getitem__))

    def objective(self, ids):
        """Relevance, weighted query coverage and redundancy; no length reward."""
        ids = self.ordered(ids)
        coverage = set().union(*(self.words[cid] for cid in ids)) if ids else set()
        novelty = sum(self.weights[w] for w in coverage & self.wanted) / self.total
        relevance = sum(self.frontier[cid].rerank_score for cid in ids)
        redundancy = sum(
            self.similarity[a, b]
            * min(self.frontier[a].rerank_score, self.frontier[b].rerank_score)
            for a, b in itertools.combinations(ids, 2)
        )
        return relevance + 0.5 * novelty - 0.5 * redundancy

    def pack(
        self,
        *,
        policy="greedy",
        token_budget=1200,
        char_budget=4000,
        limit=8,
        rounds=2,
        proposal_cap=5000,
    ):
        if policy not in {"greedy", "exchange"}:
            raise ValueError("unknown search policy")
        if min(token_budget, char_budget, limit, proposal_cap) <= 0 or rounds < 0:
            raise ValueError("invalid search bounds")
        seen, evaluations = {}, 0

        def feasible(ids):
            ids = self.ordered(ids)
            if ids not in seen:
                text = "\n\n".join(self.texts[cid] for cid in ids)
                seen[ids] = (
                    len(ids) <= limit
                    and len(text) <= char_budget
                    and self.count(text) <= token_budget
                )
            return seen[ids]

        # Match the old protected-first fallback when the first full block cannot fit.
        if self.ids and not feasible(self.ids[:1]):
            chosen, context, trace = self.packer.pack(
                limit=8,
                length_power=0.0,
                protect=1,
                neighbors=False,
                token_budget=token_budget,
                char_budget=char_budget,
            )
            trace.update(policy=policy, fallback="protected_block_does_not_fit")
            return chosen, context, trace
        selected = self.ids[:1]
        changes = []
        while len(selected) < limit:
            options = []
            for cid in self.ids:
                if cid in selected:
                    continue
                candidate = self.ordered((*selected, cid))
                if feasible(candidate):
                    options.append((self.objective(candidate), candidate))
            if not options:
                break
            score, candidate = min(options, key=lambda v: (-v[0], v[1]))
            if score <= self.objective(selected) + 1e-12:
                break
            selected = candidate
        seed = selected
        if policy == "exchange":
            for _ in range(rounds):
                best, best_score = selected, self.objective(selected)
                removable = selected[1:]
                remaining = tuple(cid for cid in self.ids if cid not in selected)
                exhausted = False
                for remove_n, add_n in ((1, 1), (1, 2), (2, 1)):
                    for removed in itertools.combinations(removable, remove_n):
                        retained = tuple(cid for cid in selected if cid not in removed)
                        for added in itertools.combinations(remaining, add_n):
                            if evaluations >= proposal_cap:
                                exhausted = True
                                break
                            evaluations += 1
                            candidate = self.ordered((*retained, *added))
                            if not feasible(candidate):
                                continue
                            score = self.objective(candidate)
                            if score > best_score + 1e-12 or (
                                math.isclose(score, best_score, abs_tol=1e-12)
                                and score > self.objective(selected) + 1e-12
                                and candidate < best
                            ):
                                best, best_score = candidate, score
                        if exhausted:
                            break
                    if exhausted:
                        break
                if best == selected:
                    break
                changes.append(
                    {"before": list(selected), "after": list(best), "objective": best_score}
                )
                selected = best
                if exhausted:
                    break
        chosen = [replace(self.frontier[cid]) for cid in selected]
        parents = {}
        for hit in chosen:
            parents.setdefault(hit.chunk.parent_id, []).append(hit.chunk)
        context = pack_context(
            chosen, parents, self.count, token_budget, char_budget, "infra", "text"
        )
        if any(e["truncated"] for e in context["evidence"]):
            raise ValueError("full-block solution unexpectedly truncated")
        return (
            chosen,
            context,
            {
                "eligible_ids": list(self.ids),
                "policy": policy,
                "seed_ids": list(seed),
                "seed_objective": self.objective(seed),
                "objective": self.objective(selected),
                "exchanges": changes,
                "evaluated_proposals": evaluations,
                "proposal_cap_reached": evaluations >= proposal_cap,
                "feasibility_checks": len(seen),
                "objective_version": "relevance+0.5coverage-0.5pair_redundancy-v1",
                "parameters": {
                    "frontier": self.packer.frontier_limit,
                    "limit": limit,
                    "protect": 1,
                    "rounds": rounds,
                    "proposal_cap": proposal_cap,
                },
            },
        )


def full_block_oracle(ids, gold, chunks, count, *, protect_first=False, combination_cap=100000):
    """Offline gold diagnostic only; feasibility says nothing about answer correctness."""
    ids = tuple(ids)
    allowed = set(ids)
    evaluated, unknown = 0, False
    feasible_groups = []
    for group in gold["evidence_alternatives"]:
        options = [sorted(set(required) & allowed) for required in group["requirements"]]
        if not all(options):
            continue
        visited = set()
        for assignment in itertools.product(*options):
            if evaluated >= combination_cap:
                unknown = True
                break
            selected = set(assignment)
            if protect_first and ids:
                selected.add(ids[0])
            ordered = tuple(cid for cid in ids if cid in selected)
            if ordered in visited:
                continue
            visited.add(ordered)
            evaluated += 1
            text = "\n\n".join(
                f"[E{stable_id(cid)}] {chunks[cid].heading}\n{chunks[cid].content}"
                for cid in ordered
            )
            tokens = count(text)
            if len(ordered) <= 8 and len(text) <= 4000 and tokens <= 1200:
                feasible_groups.append(
                    {"ids": list(ordered), "tokens": tokens, "characters": len(text)}
                )
        if unknown:
            break
    best = min(
        feasible_groups, key=lambda x: (x["tokens"], x["characters"], x["ids"]), default=None
    )
    return {
        "feasible": True if best else (None if unknown else False),
        "best_full_block_witness": best,
        "evaluated": evaluated,
        "exhaustive": not unknown,
        "protect_first": protect_first,
        "scope": "full original blocks, ID AND/OR labels, diagnostic only",
    }
