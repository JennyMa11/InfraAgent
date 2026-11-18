"""Frozen D/E continuation retaining the baseline when all C challengers lose evidence."""

import argparse
import shutil
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path

from operation_log import ROOT, record_operation
from run_grid_v2 import BASE, Grid, cached, load, prepare, save

import infra_rag.grid_delivery as delivery
from infra_rag.benchmarking import canonical_hash, digest, write_new
from infra_rag.grid_packet_cache import PacketReranker
from infra_rag.grid_v2 import Arm, delivery_gate, refinements
from infra_rag.paired_statistics import holm, paired_statistics


def parse_arm(value):
    parts = value.split("-")
    if len(parts) != 9:
        raise ValueError("Unknown config identity")
    i, s, k, r, on, n, f, p, neighbor = parts
    return Arm(i, s, int(k), int(r), on == "True", int(n), f, p, neighbor == "True")


def parent_rows(parent, stage):
    result = []
    for path in sorted((parent / "rows" / stage).rglob("*.json")):
        if not path.name.endswith(".sha256.json"):
            value = cached(path)
            if value["status"] == "completed":
                result.append((path, value))
    return result


def freeze_followup(parent, out):
    if not (parent / "run-artifacts-manifest.json").exists():
        raise ValueError("Parent must be terminal with a sealed manifest")
    manifest = load(parent / "run-artifacts-manifest.json")
    for name, sha in manifest.items():
        if digest(parent / name) != sha:
            raise ValueError("Parent artifact changed: " + name)
    for stage in ("baseline", "A", "B", "C"):
        schedule = load(parent / "schedules" / (stage + ".json"))
        if len(parent_rows(parent, stage)) != len(schedule):
            raise ValueError("Parent stage incomplete: " + stage)
    prepare(out)
    p = load(parent / "protocol.json")
    child = load(out / "protocol.json")
    if p["sources"] != child["sources"] or p["models"] != child["models"]:
        raise ValueError("Parent sources/models differ")
    for name, sha in p["implementation"].items():
        if digest(ROOT / name) != sha:
            raise ValueError("Parent retrieval/scorer implementation changed: " + name)
    origins = {}
    for meta in (parent / "indexes").glob("*/manifest.json"):
        value = load(meta)
        snapshot = meta.parent / "index.json"
        if digest(snapshot) != value["index_sha256"]:
            raise ValueError("Parent index changed")
        target = out / "indexes" / meta.parent.name
        shutil.copytree(meta.parent, target)
        origins[str(target.relative_to(out))] = value["index_sha256"]
    script = Path(__file__).resolve()
    shutil.copyfile(script, out / "implementation/scripts/continue_grid_v2.py")
    write_new(
        out / "followup-protocol.json",
        {
            "scope": "D/E correction; rescore raw A-C observations; not independent",
            "parent": str(parent.resolve()),
            "parent_manifest_sha256": digest(parent / "run-artifacts-manifest.json"),
            "script_sha256": digest(script),
            "indexes": origins,
            "D_reference": "Retain BASE even when all C challengers fail the zero-loss gate",
            "D_variants": [asdict(a) for a in refinements(BASE)],
            "no_op": "Skip depth60 only if every reference pool has<=60; record equivalence",
            "selection": "Zero losses, each corpus noninferior, net>=2 for a new champion; "
            "otherwise keep BASE. Tie fewer pairs, fewer deviations, stable identity.",
            "E": "Six labels. RRF ablation aliases a measured best single route; "
            "same-size window contrast; complete policy has no neighbor expansion, mark N/A.",
            "reuse": "Exact input packets, same model/batch32; no grades or decisions copied",
            "latency": "3 uncached warm repetitions and3 ANN repetitions; packet cache disabled, "
            "local pair accounting overhead included equally for all arms",
            "statistics": "Per-stage Holm, paired cluster bootstrap10000 seed42, dev exploratory",
            "generation_calls": 0,
            "test_holdout_read": False,
            "default_adoption": False,
        },
    )


def memoize_alignment():
    original_map = delivery.mapped_chunk
    original_gold = delivery.freeze_gold
    ranges = {}
    golds = {}

    def mapped(chunk, doc):
        key = (
            chunk.source,
            chunk.content,
            chunk.start_line,
            chunk.end_line,
            tuple(chunk.metadata.get("text_char_range", [])),
            doc["sha256"],
        )
        if key not in ranges:
            metadata = original_map(chunk, doc).metadata
            ranges[key] = {
                k: metadata[k]
                for k in ("source_normalized_ranges", "source_sha256", "range_version")
            }
        return replace(chunk, metadata={**chunk.metadata, **ranges[key]})

    def gold(question, docs):
        key = canonical_hash(
            [
                question["id"],
                question["evidence_alternatives"],
                sorted(
                    (s, docs[s]["sha256"])
                    for group in question["evidence_alternatives"]
                    for s in (span["absolute_source"] for span in group["spans"])
                ),
            ]
        )
        if key not in golds:
            golds[key] = original_gold(question, docs)
        return golds[key]

    delivery.mapped_chunk = mapped
    delivery.freeze_gold = gold


def import_packets(g, parent, packet):
    p = load(parent / "protocol.json")
    spec = load(parent / "grid-spec.json")
    identity = canonical_hash([p, spec])
    imported = set()
    for stage in ("baseline", "C", "E"):
        for path, r in parent_rows(parent, stage):
            arm = parse_arm(r["config"])
            if not arm.rerank:
                continue
            cs = {c.id: c for c in g.index(arm.index)[0]}
            prefix = r["candidate_ids"][: arm.depth]
            pairs = [(r["query"], cs[cid].content) for cid in prefix]
            signature = canonical_hash(
                [identity, r["query"], [(cid, cs[cid].content) for cid in prefix], arm.depth, 32]
            )
            source = parent / "cache/scores" / (signature + ".json")
            scores = cached(source)
            if scores is None:
                raise ValueError("Completed parent prediction missing")
            key = packet.seed(
                pairs,
                scores["scores"],
                {
                    "path": str(source),
                    "sha256": digest(source),
                    "parent_trace": str(path),
                    "parent_trace_sha256": digest(path),
                },
            )
            imported.add(key)
    save(g.out / "packet-import.json", {"unique_packets": len(imported), "new_predictions": 0})


def rescore_parent(g, parent):
    groups = defaultdict(list)
    for stage in ("baseline", "A", "B", "C"):
        for path, row in parent_rows(parent, stage):
            arm = parse_arm(row["config"])
            cs = {c.id: c for c in g.index(arm.index)[0]}
            case = g.cases[row["dataset"] + ":" + row["id"]]
            question = {
                **case,
                "evidence_alternatives": case["resolved_gold"]["evidence_alternatives"]
                if case["answerable"]
                else [],
            }
            new = {k: row[k] for k in ("id", "dataset", "group_id", "answerable", "config")}
            for k in (5, 10):
                value = delivery.score_delivery(row[f"pack{k}"]["evidence"], question, cs, g.docs)
                if value != row[f"delivery{k}"]:
                    raise ValueError("Raw-delivery rescore differs")
                new[f"delivery{k}"] = value
            candidate = delivery.score_delivery(
                [
                    {"chunk_id": cid, "source": cs[cid].source, "content": cs[cid].content}
                    for cid in row["candidate_ids"]
                ],
                question,
                cs,
                g.docs,
            )
            if candidate != row["candidate"]:
                raise ValueError("Raw-candidate rescore differs")
            new.update(candidate=candidate, parent_trace_sha256=digest(path))
            groups[stage + ":" + row["config"]].append(new)
    save(g.out / "parent-rescored.json", groups)
    return groups


def run_followup(out):
    protocol = load(out / "followup-protocol.json")
    parent = Path(protocol["parent"])
    if digest(Path(__file__)) != protocol["script_sha256"]:
        raise ValueError("Continuation implementation changed")
    if digest(parent / "run-artifacts-manifest.json") != protocol["parent_manifest_sha256"]:
        raise ValueError("Parent manifest changed")
    for folder, sha in protocol["indexes"].items():
        if digest(out / folder / "index.json") != sha:
            raise ValueError("Copied index changed")
    g = Grid(out)
    memoize_alignment()
    packet = PacketReranker(g.service.reranker, out / "packets", g.p["models"]["reranker"])
    import_packets(g, parent, packet)
    g.service.reranker = packet
    rescored = rescore_parent(g, parent)
    baseline = g.stage("baseline", [BASE])[BASE.identity()]
    prior = rescored["baseline:" + BASE.identity()]
    if not delivery_gate(baseline, prior)["eligible"] or delivery_gate(baseline, prior)["net"] != 0:
        raise ValueError("Replayed BASE does not match rescored parent evidence")
    c_gates = {k: delivery_gate(v, baseline) for k, v in rescored.items() if k.startswith("C:")}
    save(out / "C-recheck.json", c_gates)
    if any(v["eligible"] for v in c_gates.values()):
        raise ValueError(
            "Continuation expected no eligible C challenger; retain existing C champion too"
        )
    max_pool = max(len(r["candidate_ids"]) for _, r in parent_rows(parent, "baseline"))
    variants = [a for a in refinements(BASE) if not (a.depth == 60 and max_pool <= 60)]
    save(
        out / "D-equivalences.json",
        {
            "reference_max_pool": max_pool,
            "depth60": "equivalent to BASE depth90 for all110 questions"
            if max_pool <= 60
            else "measured",
        },
    )
    data = g.stage("D", variants)
    all_data = {BASE.identity(): baseline, **data}
    arms = {a.identity(): a for a in [BASE, *variants]}
    gates = {k: delivery_gate(rs, baseline) for k, rs in all_data.items()}
    qualified = [arms[k] for k, v in gates.items() if v["eligible"] and v["net"] >= 2]

    def order(a):
        return (
            -gates[a.identity()]["net"],
            sum(r["pairs"] for r in all_data[a.identity()]),
            sum(asdict(a)[k] != asdict(BASE)[k] for k in asdict(BASE)),
            a.identity(),
        )

    winner = min(qualified, key=order) if qualified else BASE
    save(
        out / "quality-selection.json",
        {
            "winner": asdict(winner),
            "gates": gates,
            "new_quality_champion": bool(qualified),
            "adopt": False,
        },
    )
    named = {
        "minus_bm25": replace(winner, strategy="dense"),
        "minus_dense": replace(winner, strategy="bm25"),
        "minus_reranker": replace(winner, rerank=False),
        "minus_semantic": replace(winner, index="I3"),
    }
    if winner.policy == "prefix" and winner.neighbors:
        named["minus_neighbors"] = replace(winner, neighbors=False)
    e = g.stage("E", list({a.identity(): a for a in named.values()}.values()))

    def quality(a):
        return (
            -sum(r["delivery5"]["complete"] for r in e[a.identity()] if r["answerable"]),
            sum(r["pairs"] for r in e[a.identity()]),
            a.identity(),
        )

    named["minus_rrf"] = min((named["minus_bm25"], named["minus_dense"]), key=quality)
    save(
        out / "ablation.json",
        {
            "reference": winner.identity(),
            "labels": {k: a.identity() for k, a in named.items()},
            "not_applicable": []
            if "minus_neighbors" in named
            else ["minus_neighbors: no expansion in complete policy"],
            "minus_rrf": "Aliases best single route; not an independent experiment",
            "deltas": {
                label: delivery_gate(e[a.identity()], all_data[winner.identity()])
                for label, a in named.items()
            },
        },
    )
    stats = {}
    ps = {}
    for ident, rs in data.items():
        for ds in ("official", "repository"):
            before = [{**r, "delivered": r["delivery5"]} for r in baseline if r["dataset"] == ds]
            after = [{**r, "delivered": r["delivery5"]} for r in rs if r["dataset"] == ds]
            stats[ident + ":" + ds] = paired_statistics(before, after)
            ps[ident + ":" + ds] = stats[ident + ":" + ds]["cluster_permutation_p"]
    save(
        out / "statistics.json",
        {"contrasts": stats, "holm": holm(ps), "scope": "D family; dev exploratory"},
    )
    save(
        out / "A-E-quality-complete.json",
        {
            "parent_A_C": str(parent),
            "D_E": str(out),
            "adopt": False,
            "new_quality_champion": bool(qualified),
            "generation_calls": 0,
        },
    )
    # The same wrapper now accounts every fresh prediction without using packet results.
    packet.enabled = False
    finalists = list({a.identity(): a for a in [BASE, winner]}.values())
    repeated, timing = g.timed("repeat", finalists)
    ann, ann_timing = g.timed("ann", finalists, ann=True)
    temporal = {}
    for stage, results, times in (("repeat", repeated, timing), ("ann", ann, ann_timing)):
        temporal[stage] = {
            "quality": [
                delivery_gate(
                    [r for r in results[winner.identity()] if r["rep"] == rep],
                    [r for r in results[BASE.identity()] if r["rep"] == rep],
                )
                for rep in range(3)
            ],
            "p95_pass": all(
                times[winner.identity()][ds]["p95_ms"] <= 1.5 * times[BASE.identity()][ds]["p95_ms"]
                for ds in ("official", "repository")
            ),
            "timing": times,
        }
    save(out / "confirmation-gates.json", temporal)
    save(
        out / "decision.json",
        {
            "adopt": False,
            "reason": "Independent human review pending; dev grid only",
            "new_quality_champion": bool(qualified),
            "quality_winner": asdict(winner),
            "A_E_complete": True,
            "generation_calls": 0,
            "test_holdout_read": False,
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["freeze", "run"])
    parser.add_argument("--parent", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.phase == "freeze":
            freeze_followup(args.parent, args.out)
        else:
            run_followup(args.out)
    finally:
        if args.out.exists():
            path = args.out / (args.phase + "-followup-manifest.json")
            if not path.exists():
                write_new(
                    path,
                    {
                        str(f.relative_to(args.out)): digest(f)
                        for f in args.out.rglob("*")
                        if f.is_file()
                    },
                )
    record_operation(
        "Grid v2 D/E修订" + args.phase, "保留基线、修正遗漏D分支并执行公平消融", str(args.out)
    )


if __name__ == "__main__":
    main()
