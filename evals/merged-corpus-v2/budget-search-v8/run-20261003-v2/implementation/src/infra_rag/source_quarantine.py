"""Corpus-only scope-risk rules for an experimental quarantine, not factual truth labels."""

import re


def source_risks(chunks):
    records = []
    for c in chunks:
        if c.metadata.get("collection") != "community":
            continue
        text = c.content
        rules = []
        if re.search(r"模型(?:的)?总参数量[^\n]*=([^\n]*)专家[^\n]*之和", text) and not re.search(
            r"近似|约等于|approximately|approx\.", text, re.I
        ):
            rules.append("expert_only_model_total_scope")
        coalescing = bool(re.search(r"合并访问|coalesc|\bfloat\b", text, re.I))
        old_arch = bool(
            re.search(r"(?:计算能力|compute capability|CC)\s*[=:]?\s*[125]\.", text, re.I)
        )
        if coalescing and not old_arch:
            if re.search(r"随机访问[^\n]*(?:完全无法合并|完全不能合并)", text):
                rules.append("absolute_random_access_noncoalescing")
            if re.search(r"一次\s*128\s*B\s*事务", text, re.I):
                rules.append("unqualified_single_128b_transaction")
            if re.search(r"(?:地址连续|连续[^\n]*地址)[^\n]*一次事务[^\n]*(?:所有线程|整个)", text):
                rules.append("unqualified_contiguous_single_transaction")
        if rules:
            records.append(
                {
                    "chunk_id": c.id,
                    "source": c.source,
                    "locator": c.locator,
                    "start_line": c.start_line,
                    "end_line": c.end_line,
                    "source_sha256": c.metadata.get("sha256"),
                    "quote": text,
                    "rules": rules,
                    "status": "AI_scope_risk_pending_human",
                }
            )
    return records
