"""Source-grounded AI dev expansion; never ingest questions into the corpus."""

import argparse
from pathlib import Path

from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.retrieval_diagnostic import validate_cases

SEEDS = [
    (
        "66df372b0d2a0810b05a280f7a8138b0",
        "TensorRT-LLM的KV cache除了避免重复计算，还支持哪些复用和注意力优化？",
    ),
    (
        "64413f9f9d63e8238314fb9a9d7ff3f4",
        "TensorRT-LLM的单个KV block可容纳token数何时设置，有什么数值约束，匹配前缀如何复用？",
    ),
    (
        "0f81427424416d6159ec56e62d1bd549",
        "长时间暂停的多轮会话为何可能重新执行prefill，CPU或外部缓存层能保留什么？",
    ),
    ("c3569e278cfccd8942b0aa096f16ba64", "Megatron-FSDP在哪个NVIDIA容器中随Megatron-Core预装？"),
    (
        "7af0482bce1bc0ba8dca30b7d2d2ac17",
        "Megatron-FSDP列出的PyTorch基础组件及NVIDIA相关生态有哪些？",
    ),
    (
        "1ffd99287eaf82af510153a4208103a2",
        "vLLM的preemption和recomputation虽然增强鲁棒性，会对哪项延迟造成不利影响？",
    ),
    (
        "a19b4f38e9164638adfa8880767b94df",
        "Ray Serve的fractional GPU适合怎样的模型、并发和多模型部署需求？",
    ),
    (
        "064ae74b327fd489d33cdcd3da68d4a4",
        "Ray Serve的L4示例用几张GPU承载几个小模型副本，每张GPU几个副本？",
    ),
    (
        "0d2a55a5e082668863a558ba2194b248",
        "PyTorch DCP的checkpoint文件数量与rank有什么关系，加载时由谁先分配存储？",
    ),
    (
        "f151dfd9d70dd31dceaf2a73a7e2e441",
        "这份TensorRT-LLM资料有哪些attention backend，使用哪个参数选择Flashinfer？",
    ),
    (
        "13e2e6a2060290f045ca80b1eb0a3544",
        "CUDA怎样用stream对象组织kernel和host-device拷贝，示例的hostPtr属于什么内存？",
    ),
    (
        "e24f1f313cfe80230409f92738bc906e",
        "CUDA示例如何创建两个stream并用cudaMallocHost分配hostPtr？",
    ),
    (
        "1b72346bc7f750c9e2d038aec291f86d",
        "SGLang Router列出的三种启动部署模式是什么，哪种面向单节点或多节点？",
    ),
    (
        "9be343bb711c9d61f5a9c23d206d0f6f",
        "SGLang Router的co-launch怎样启动router与worker，它替代哪个Runtime参数？",
    ),
    (
        "4db9cda349f44b016e4ed3963cfe7ede",
        "PyTorch流水线并行除了切模型权重还要切什么，micro-batch调度需要考虑什么依赖？",
    ),
    (
        "979a2ca9289b74fc8f19345a8413c651",
        "PyTorch流水线文档所述场景中，每设备计算为何难以隐藏FSDP等传统并行的通信？",
    ),
    ("b6233554b58661c2c75f5be830a6f85f", "位置编码推导用什么形状和约束的排列矩阵表示输入行重排？"),
    (
        "9b572fef1b98b82d7ae589cc4e98fc8e",
        "这份vLLM多模态PR如何把mm_hashes构成唯一key，是否提到后续优化空间？",
    ),
    ("f353c82d910c3564cb6e414838e68ee6", "Triton进程内C API通过哪两个接口发起取消和查询取消状态？"),
    (
        "0667e7f4c91a7beedb8752e65c66aeb6",
        "Triton的gRPC endpoint检测到客户端取消后会尝试做什么，资料是否承诺一定终止？",
    ),
    (
        "e90bacc647eb351f028aadaa7eafa248",
        "CUDA还有哪些所有线程可访问的只读内存空间，texture提供哪些额外能力？",
    ),
    (
        "5e32b7f4a5c521261afa8f07308a89ff",
        "CUDA哪些内存空间会在同一应用的多次kernel launch之间持续存在？",
    ),
    (
        "8de1247d7bd786c8821366ade1999418",
        "这份vLLM快速入门的GPU示例要求先核对哪些环境条件，作者是否声称当前机器已跑GPU推理？",
    ),
    (
        "92f820725a43a8a7f1b52aedf1cd7d07",
        "模型仓库的generation_config.json怎样影响vLLM默认采样，哪个启动参数可排除这种隐式默认？",
    ),
    (
        "c58224003a49392a25a91950f18054a1",
        "SGLang监控里queue-req经常为0说明什么，资料建议的范围及过大风险是什么？",
    ),
    (
        "2d8feba7e12356708c4fd925ccea957f",
        "SGLang的token usage指标表示什么，这份资料用什么阈值描述良好利用率？",
    ),
    (
        "71c5584bb0875a4d822b8443f43ea5f5",
        "Megatron checkpoint merge的元数据布局是不是安全边界，为什么源checkpoint必须可信？",
    ),
    (
        "522b88d9836f4218713cee67e9a25a51",
        "Megatron checkpoint merge是否需要模型并行状态初始化或构造模型，它基于哪些API？",
    ),
    (
        "e1ebd2e7d44bc5c5c768e09334d230f7",
        "混合精度Adam训练显存的四个组成是什么，资料中7B模型静态显存怎样估到112GB？",
    ),
    (
        "01ac4f16200ec6b7cc68e56d8545ccd6",
        "Triton关闭auto-complete-config后是否还会为缺失instance_group填默认值？",
    ),
]


def prepare(out):
    source = ROOT / "data/evidence-delivery-v1/run-20261028-v2"
    for name, sha in load(source / "artifacts-manifest.json").items():
        if digest(source / name) != sha:
            raise ValueError("Frozen source changed")
    docs = [load(p) for p in sorted((source / "documents").glob("*.json"))]
    original = load(ROOT / "data/native-pagination-v1/run-20261029/questions.json")
    rows = {
        r["document_id"]: r
        for r in load(ROOT / "data/structural-chunk-pilot-v1/run-20261028-v2/selection.json")
    }
    catalog = {
        u["unit_id"]: (d, u) for d in docs for parent in d["parents"] for u in parent["units"]
    }
    expanded = []
    for i, (uid, query) in enumerate(SEEDS, 31):
        d, u = catalog[uid]
        row = rows[d["document_id"]]
        req = {
            "document_id": d["document_id"],
            "unit_id": uid,
            "char_range": [0, len(u["content"])],
            "quote": u["content"],
            "input_sha256": row["input_sha256"],
            "source_url": row["source_url"],
            "input_lines": u["input_lines"],
            "source_lines": u["source_lines"],
            "coordinate_type": row["coordinate_type"],
        }
        expanded.append(
            {
                "id": f"expand-{i:03}",
                "query": query,
                "group_id": d["document_id"],
                "repository": row["repository"],
                "answerable": True,
                "source_language": row["language"],
                "kind": "source_grounded_development",
                "evidence_alternatives": [{"requirements": [req]}],
                "required_points": [{"rubric": u["content"]}],
                "annotation": "AI-authored source-grounded expansion; not independent human gold",
                "review_status": "pending_independent_review",
            }
        )
    cases = original + expanded
    validate_cases(cases, docs)
    if len(cases) != 60 or len({c["query"] for c in cases}) != 60:
        raise ValueError("Need 60 distinct queries")
    save(out / "dev.json", cases)
    save(out / "source-selection.json", list(rows.values()))
    save(
        out / "dataset-manifest.json",
        {
            "questions": 60,
            "original": 30,
            "new_ai_authored": 30,
            "source_groups": len(rows),
            "scope": "development only; same sources, no independent confirmation claim",
            "dev_sha256": digest(out / "dev.json"),
            "generator_sha256": digest(Path(__file__)),
            "case_hashes": {c["id"]: canonical_hash(c) for c in cases},
        },
    )
    save(
        out / "question-review-template.json",
        [
            {
                "id": c["id"],
                "case_sha256": canonical_hash(c),
                "status": "pending",
                "reviewer": None,
                "answerability": None,
                "all_requirements_necessary": None,
            }
            for c in cases
        ],
    )
    return {"questions": 60, "new_ai_questions": 30, "sources": 24}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = prepare(args.output.resolve())
    record_operation(
        "扩展同24来源至60开发题",
        "先冻结原文证据再检索，不读holdout",
        str(result),
        "新增30题为AI标注待审，不是独立确认集",
    )
    print(result)
