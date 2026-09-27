"""Load and actually execute each configured model; failures are recorded, never replaced."""

import json
import time
from pathlib import Path

from infra_rag.encoding import BGEEncoder, CLIPEncoder


def main():
    from sentence_transformers import CrossEncoder

    report = {}
    checks = [
        (
            "bge",
            lambda: BGEEncoder("BAAI/bge-small-zh-v1.5"),
            lambda model: model.encode(["PagedAttention 管理 KV Cache。"]),
        ),
        (
            "reranker",
            lambda: CrossEncoder("BAAI/bge-reranker-base"),
            lambda model: model.predict(
                [("如何管理 KV Cache？", "PagedAttention 采用分页管理。")]
            ).tolist(),
        ),
        ("clip", CLIPEncoder, lambda model: model.encode_query("GPU 架构图")),
    ]
    for name, load, encode in checks:
        start = time.perf_counter()
        print("Loading", name, flush=True)
        try:
            model = load()
            result = encode(model)
            report[name] = {
                "status": "passed",
                "seconds": time.perf_counter() - start,
                "output_length": len(result[0]) if isinstance(result[0], list) else len(result),
            }
            del model
        except Exception as exc:
            report[name] = {
                "status": "failed",
                "error": str(exc),
                "seconds": time.perf_counter() - start,
            }
        print(name, report[name], flush=True)
    output = Path("evals/results/model-preflight.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    if any(result["status"] == "failed" for result in report.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
