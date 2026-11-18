"""Fresh Exact/ANN confirmation over a strict identical-ID dense backend view."""

import argparse
import shutil
from pathlib import Path

from operation_log import ROOT, record_operation
from run_grid_v2 import BASE, Grid, load, prepare, save

from infra_rag.benchmarking import canonical_hash, digest, write_new
from infra_rag.exact_search import ExactCollection
from infra_rag.grid_identity_view import canonical_points
from infra_rag.grid_packet_cache import PacketReranker
from infra_rag.grid_v2 import delivery_gate


def freeze_confirmation(parent, out):
    if not (parent / "A-E-quality-complete.json").exists():
        raise ValueError("D/E not complete")
    if not (parent / "run-followup-manifest.json").exists():
        raise ValueError("Quality parent not terminal")
    for name, sha in load(parent / "run-followup-manifest.json").items():
        if digest(parent / name) != sha:
            raise ValueError("Parent artifact changed")
    if load(parent / "quality-selection.json")["new_quality_champion"]:
        raise ValueError("This confirmation expects retained BASE; include new winner if selected")
    prepare(out)
    old = load(parent / "protocol.json")
    new = load(out / "protocol.json")
    if old["sources"] != new["sources"] or old["models"] != new["models"]:
        raise ValueError("Inputs differ")
    changed = []
    for name, sha in old["implementation"].items():
        if digest(ROOT / name) != sha:
            changed.append(name)
    if set(changed) - {"src/infra_rag/grid_packet_cache.py"}:
        raise ValueError("Unexpected retrieval/scoring change: " + str(changed))
    for meta in (parent / "indexes").glob("*/manifest.json"):
        if load(meta)["name"] == "I0":
            target = out / "indexes" / meta.parent.name
            target.mkdir(parents=True)
            for name in ("index.json", "manifest.json"):
                shutil.copyfile(meta.parent / name, target / name)
    shutil.copyfile(Path(__file__), out / "implementation/scripts/confirm_grid_v2.py")
    write_new(
        out / "confirmation-protocol.json",
        {
            "parent": str(parent.resolve()),
            "parent_manifest_sha256": digest(parent / "run-followup-manifest.json"),
            "script_sha256": digest(Path(__file__)),
            "config": {"reference": "BASE", "new_champion": False},
            "dense_view": "one point per ID ONLY if all chunk fields and vectors are exactly equal",
            "conflicting_ID": "hard failure; never rename or drop different evidence",
            "corpus": "Raw frozen rows/BM25 unchanged; strict dense logical ID view",
            "preflight": "All110 RawExact == CanonicalExact == archived Top30 IDs",
            "timing": "Fresh3x110 Exact/ANN; no model result cache; accounting included",
            "generation_calls": 0,
            "test_holdout_read": False,
            "default_adoption": False,
        },
    )


def run_confirmation(out):
    cp = load(out / "confirmation-protocol.json")
    parent = Path(cp["parent"])
    if digest(Path(__file__)) != cp["script_sha256"]:
        raise ValueError("Runner changed")
    if digest(parent / "run-followup-manifest.json") != cp["parent_manifest_sha256"]:
        raise ValueError("Parent changed")
    g = Grid(out)
    chunks, vectors, folder, cfg = g.index("I0")
    unique, values, duplicates = canonical_points(chunks, vectors)
    save(
        out / "dense-identity-view.json",
        {
            "raw_rows": len(chunks),
            "logical_points": len(unique),
            "duplicates": duplicates,
            "canonical_chunks_sha256": canonical_hash([vars(c) for c in unique]),
            "canonical_vectors_sha256": canonical_hash(values),
            "raw_index_sha256": digest(folder / "index.json"),
            "raw_index_modified": False,
            "BM25_rows_modified": False,
        },
    )
    raw = ExactCollection(chunks, vectors)
    canonical = ExactCollection(unique, values)
    checked = []
    for key, query in g.queries.items():
        v = g.encoder.encode([query], query=True)
        a = raw.query(v, 30)["ids"][0]
        b = canonical.query(v, 30)["ids"][0]
        r = load(parent / "rows/baseline" / BASE.identity() / (key + ".json"))
        old = [x["chunk_id"] for x in r["diagnostics"]["channels"]["dense"]["ranking"]]
        if a != b or a != old:
            raise ValueError("Exact ID-view equivalence failed: " + key)
        checked.append(key)
    save(
        out / "exact-view-equivalence.json",
        {
            "verified_queries": len(checked),
            "IDs": checked,
            "raw_exact_equals_canonical_exact": True,
            "canonical_exact_equals_archived_raw": True,
        },
    )
    g.activate(BASE)
    g.exact_collections["I0"] = canonical
    g.service.text_collection = canonical
    packets = PacketReranker(g.service.reranker, out / "packets", g.p["models"]["reranker"])
    packets.enabled = False
    g.service.reranker = packets
    repeated, timing = g.timed("repeat", [BASE])
    # Use the production collection builder and its validation on strict unique logical points.
    g.service.index_fingerprint = cfg.fingerprint()
    collections = g.service._collections(unique, values)
    if collections[0].count() != len(unique):
        raise ValueError("ANN count differs")
    g.ann_collections["I0"] = collections
    ann, ann_timing = g.timed("ann", [BASE], ann=True)
    # Quality must match the frozen source trial for every repetition, not just on average.
    before = [
        load(f)
        for f in (parent / "rows/baseline" / BASE.identity()).glob("*.json")
        if not f.name.endswith(".sha256.json")
    ]
    gates = {}
    for stage, data, measure in [("repeat", repeated, timing), ("ann", ann, ann_timing)]:
        gates[stage] = {
            "quality": [
                delivery_gate([r for r in data[BASE.identity()] if r["rep"] == rep], before)
                for rep in range(3)
            ],
            "timing": measure,
        }
    save(out / "confirmation-gates.json", gates)
    save(
        out / "decision.json",
        {
            "adopt": False,
            "A_E_complete": True,
            "quality_winner": vars(BASE),
            "new_quality_champion": False,
            "reason": "No new quality champion; independent review pending",
            "quality_parent": str(parent),
            "generation_calls": 0,
            "test_holdout_read": False,
        },
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("phase", choices=["freeze", "run"])
    p.add_argument("--parent", type=Path)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    try:
        if a.phase == "freeze":
            freeze_confirmation(a.parent, a.out)
        else:
            run_confirmation(a.out)
    finally:
        if a.out.exists():
            path = a.out / (a.phase + "-confirmation-manifest.json")
            if not path.exists():
                write_new(
                    path,
                    {str(f.relative_to(a.out)): digest(f) for f in a.out.rglob("*") if f.is_file()},
                )
    record_operation(
        "Grid严格身份视图确认 " + a.phase, "同逻辑ID点集配对Exact/ANN，不丢弃冲突数据", str(a.out)
    )


if __name__ == "__main__":
    main()
