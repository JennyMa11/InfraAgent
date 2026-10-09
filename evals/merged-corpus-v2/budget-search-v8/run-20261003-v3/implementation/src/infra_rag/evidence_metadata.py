"""Render existing provenance fields without inferring missing facts or trust levels."""

import json


def metadata_text(metadata):
    fields = {
        key: metadata[key]
        for key in ("collection", "source_type", "product", "release", "applicability", "scope")
        if metadata.get(key) not in (None, "", [], {})
    }
    return (
        "元数据：" + json.dumps(fields, ensure_ascii=False, sort_keys=True) + "\n" if fields else ""
    )
