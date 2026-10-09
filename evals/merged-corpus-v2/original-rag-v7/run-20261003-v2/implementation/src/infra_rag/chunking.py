"""Blank-line blocks -> heading/semantic aggregation -> sentence refinement."""

import hashlib
import re
from pathlib import Path

from .encoding import dot
from .models import Chunk
from .text_chunking import centroid, heading_line, semantic_refine, window_pieces

TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".rst"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def stable_id(*values):
    return hashlib.sha256("\0".join(map(str, values)).encode()).hexdigest()[:24]


def chunk_text(text, source, domain, encoder, settings, *, page=None):
    lines = text.splitlines()
    blocks, current, heading, start = [], [], "", 1
    heading_stack = []
    markdown = Path(source).suffix.lower() in {".md", ".markdown"}
    if settings.chunk_strategy == "window":
        pieces = window_pieces(text, settings.chunk_size, encoder)
        return [
            Chunk(
                id=stable_id(source, page, "window", i, piece),
                parent_id=stable_id(source, page, "window", i),
                source=source,
                content=piece,
                domain=domain,
                page=page,
                chunk_type="window",
                locator=f"{source}#page={page}" if page else f"{source}#L1-L{len(lines)}",
            )
            for i, piece in enumerate(pieces)
        ]

    def flush(end):
        nonlocal current
        if current:
            content = "\n".join(current)
            only_structure = all(
                not line.strip()
                or re.fullmatch(r"(?:[-*_]\s*){3,}", line.strip())
                or re.match(r"^#{1,6}\s+", line.strip())
                for line in current
            )
            if not (settings.heading_context and only_structure):
                blocks.append((content, heading, start, end))
            current = []

    in_fence = False
    for number, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
        isolated = (number == 1 or not lines[number - 2].strip()) and (
            number < len(lines) and not lines[number].strip()
        )
        title = heading_line(line.strip(), allow_plain=isolated) if not in_fence else None
        if settings.heading_context and markdown and not in_fence:
            explicit = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line.strip())
            title = explicit[2] if explicit else None
        if title:
            flush(number - 1)
            if settings.heading_context:
                level = len(explicit[1]) if markdown else 1
                heading_stack = [(n, t) for n, t in heading_stack if n < level]
                heading_stack.append((level, title))
                heading = " > ".join(t for _, t in heading_stack)
            else:
                heading = title
            start = number
            current = [line]
        elif not line.strip() and not in_fence:
            flush(number - 1)
        else:
            if not current:
                start = number
            current.append(line)
    flush(len(lines))
    if not blocks:
        return []
    vectors = encoder.encode([block[0] for block in blocks])
    parents = []
    for block, vector in zip(blocks, vectors, strict=True):
        content, title, first, last = block
        if (
            parents
            and parents[-1][1] == title
            and (
                dot(parents[-1][4], vector) >= settings.semantic_threshold
                or heading_line(parents[-1][0].strip(), allow_plain=True) is not None
            )
            and (
                heading_line(parents[-1][0].strip(), allow_plain=True) is not None
                or len(parents[-1][0]) + len(content) < settings.chunk_size * 3
            )
        ):
            previous = parents.pop()
            parents.append(
                (
                    previous[0] + "\n\n" + content,
                    title,
                    previous[2],
                    last,
                    centroid(previous[4], vector, previous[5]),
                    previous[5] + 1,
                )
            )
        else:
            parents.append((content, title, first, last, vector, 1))
    chunks = []
    for content, title, first, last, _, _count in parents:
        parent_id = stable_id(source, page, first, content)
        for index, piece in enumerate(
            semantic_refine(content, settings.chunk_size, encoder, settings.refinement_threshold)
        ):
            locator = f"{source}#page={page}" if page else f"{source}#L{first}-L{last}"
            chunks.append(
                Chunk(
                    id=stable_id(parent_id, index, piece),
                    parent_id=parent_id,
                    source=source,
                    content=piece,
                    domain=domain,
                    heading=title,
                    locator=locator,
                    page=page,
                    start_line=first,
                    end_line=last,
                )
            )
    return chunks


def parse_file(path: Path, domain, encoder, settings, visual_encoder=None):
    source = str(path.resolve())
    suffix = path.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        return chunk_text(path.read_text(encoding="utf-8"), source, domain, encoder, settings)
    if suffix == ".pdf":
        import pymupdf

        chunks = []
        with pymupdf.open(path) as document:
            for page_number, page in enumerate(document, 1):
                text = page.get_text(sort=True)
                if not text.strip() and (not settings.multimodal or not page.get_image_info()):
                    raise ValueError(f"{path}: page {page_number} has no text; OCR is required")
                chunks.extend(
                    chunk_text(
                        text,
                        source,
                        domain,
                        encoder,
                        settings,
                        page=page_number,
                    )
                )
                if settings.multimodal:
                    for image_index, info in enumerate(page.get_image_info(xrefs=True)):
                        if not info.get("xref"):
                            continue
                        image = document.extract_image(info["xref"])
                        asset = (
                            settings.data_dir
                            / "assets"
                            / (
                                stable_id(source, page_number, image_index, image["image"])
                                + "."
                                + image["ext"]
                            )
                        )
                        asset.parent.mkdir(parents=True, exist_ok=True)
                        asset.write_bytes(image["image"])
                        from .image_chunking import image_chunks

                        caption, caption_box = find_caption(page, info["bbox"])
                        label = f"{path.stem} 第 {page_number} 页图 {image_index + 1}"
                        chunks.extend(
                            image_chunks(
                                asset,
                                source,
                                domain,
                                settings,
                                visual_encoder,
                                caption=caption or label,
                                page=page_number,
                                page_bbox=list(info["bbox"]),
                                caption_source="pdf_caption" if caption else "label",
                                caption_locator=(
                                    f"{source}#page={page_number}&bbox="
                                    + ",".join(map(str, caption_box))
                                )
                                if caption_box
                                else None,
                            )
                        )
        return chunks
    if suffix in IMAGE_SUFFIXES:
        if not settings.multimodal:
            raise ValueError("image ingestion requires --multimodal")
        # A sidecar caption is evidence; filename alone is only a locator label.
        sidecar = path.with_suffix(path.suffix + ".txt")
        caption = sidecar.read_text(encoding="utf-8") if sidecar.exists() else path.stem
        from .image_chunking import image_chunks

        return image_chunks(
            path,
            source,
            domain,
            settings,
            visual_encoder,
            caption=caption,
            caption_source="sidecar" if sidecar.exists() else "label",
            caption_locator=str(sidecar.resolve()) if sidecar.exists() else None,
        )
    raise ValueError(f"unsupported file type: {suffix}")


def find_caption(page, image_bbox):
    """Associate caption-looking text spatially, excluding distant/body-text blocks."""
    x0, y0, x1, y1 = image_bbox
    candidates = []
    for block in page.get_text("blocks", sort=True):
        bx0, by0, bx1, by1, text = block[:5]
        if len(block) > 6 and block[6] != 0:
            continue
        if not re.match(r"^\s*(?:图\s*\d+|Figure\s*\d+|Fig\.?\s*\d+)", text, re.I):
            continue
        horizontal_overlap = max(0, min(x1, bx1) - max(x0, bx0))
        gap = max(0, by0 - y1, y0 - by1)
        if horizontal_overlap > 0 and gap <= 80:
            candidates.append((gap, text.strip(), [bx0, by0, bx1, by1]))
    if not candidates:
        return None, None
    _, text, box = min(candidates, key=lambda item: item[0])
    return text, box
