"""Edges -> CLIP/geometric region aggregation -> bounded, content-aware crops."""

import hashlib
import math
from pathlib import Path

from .encoding import dot
from .models import Chunk


def union(a, b):
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def rough_regions(image, settings):
    import cv2
    import numpy as np

    gray = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 60, 160)
    mask = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((5, 5), dtype=np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    width, height = image.size
    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        fraction = w * h / (width * height)
        if settings.image_min_area <= fraction <= 0.95 and min(w, h) >= 12:
            boxes.append(
                [max(0, x - 4), max(0, y - 4), min(width, x + w + 4), min(height, y + h + 4)]
            )
    boxes.sort(key=lambda box: (box[2] - box[0]) * (box[3] - box[1]), reverse=True)
    return sorted(boxes[: settings.image_max_regions], key=lambda box: (box[1], box[0])), edges


def aggregate_regions(boxes, vectors, image_size, threshold):
    groups = []
    diagonal = math.hypot(*image_size)
    for box, vector in zip(boxes, vectors, strict=True):
        selected = None
        for index, (previous, features) in enumerate(groups):
            dx = max(0, previous[0] - box[2], box[0] - previous[2])
            dy = max(0, previous[1] - box[3], box[1] - previous[3])
            # Similar appearance alone must not merge far-apart diagram panels.
            if math.hypot(dx, dy) <= diagonal * 0.035 and dot(features, vector) >= threshold:
                selected = index
                break
        if selected is None:
            groups.append((box, vector))
        else:
            previous, features = groups[selected]
            merged = [a + b for a, b in zip(features, vector, strict=True)]
            norm = math.sqrt(dot(merged, merged)) or 1
            groups[selected] = (union(previous, box), [value / norm for value in merged])
    return [box for box, _ in groups]


def refine_regions(boxes, edges, max_side):
    regions = []
    for x0, y0, x1, y1 in boxes:
        columns, rows = math.ceil((x1 - x0) / max_side), math.ceil((y1 - y0) / max_side)
        for row in range(rows):
            for column in range(columns):
                left, top = x0 + column * max_side, y0 + row * max_side
                right, bottom = min(x1, left + max_side), min(y1, top + max_side)
                if edges[top:bottom, left:right].any():
                    regions.append([left, top, right, bottom])
    return regions


def image_chunks(
    path,
    source,
    domain,
    settings,
    encoder,
    *,
    caption=None,
    page=None,
    page_bbox=None,
    caption_locator=None,
    caption_source=None,
):
    import cv2
    import numpy as np
    from PIL import Image, ImageOps

    from .chunking import stable_id

    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
    digest = hashlib.sha256(image.tobytes()).hexdigest()
    parent_id = stable_id(source, page, page_bbox, image.size, digest, "figure")
    width, height = image.size
    root_box = [0, 0, width, height]
    boxes, edges = rough_regions(image, settings)
    assets = settings.data_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    def save_crop(box, tag):
        file = assets / (stable_id(parent_id, box, tag) + ".png")
        image.crop(tuple(box)).save(file)
        return str(file.resolve())

    rough_paths = [save_crop(box, "rough") for box in boxes]
    vectors = encoder.encode_images(rough_paths) if rough_paths else []
    merged = aggregate_regions(boxes, vectors, image.size, settings.image_merge_threshold)
    # With no isolated contour, refine the full figure rather than silently skipping refinement.
    fine = refine_regions(merged or [root_box], edges, settings.image_max_side)
    fine = sorted(fine, key=lambda box: (box[1], box[0]))[: settings.image_max_regions]
    if len(fine) == 1 and fine[0] == root_box:
        fine = []
    caption = caption or Path(source).stem
    caption_source = caption_source or "label"
    chunks = []
    for index, box in enumerate([root_box] + fine):
        x0, y0, x1, y1 = box
        array = np.asarray(image.crop(tuple(box)))
        gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
        features = {
            "edge_density": float((edges[y0:y1, x0:x1] > 0).mean()),
            "contrast": float(gray.std()),
            "area_fraction": (x1 - x0) * (y1 - y0) / (width * height),
        }
        if page_bbox is not None:
            px0, py0, px1, py1 = page_bbox
            bbox = [
                px0 + x0 / width * (px1 - px0),
                py0 + y0 / height * (py1 - py0),
                px0 + x1 / width * (px1 - px0),
                py0 + y1 / height * (py1 - py0),
            ]
            coordinate_space = "pdf_points"
        else:
            bbox, coordinate_space = box, "image_pixels"
        content = caption if index == 0 else f"{caption}\n区域 {index}: {box}"
        chunks.append(
            Chunk(
                id=stable_id(parent_id, box),
                parent_id=parent_id,
                source=source,
                content=content,
                domain=domain,
                modality="image",
                locator=f"{source}#page={page}" if page else source,
                page=page,
                image_path=save_crop(box, "final"),
                bbox=list(bbox),
                parent_bbox=list(page_bbox or root_box),
                coordinate_space=coordinate_space,
                chunk_type="figure" if index == 0 else "image_region",
                caption_source=caption_source,
                caption_locator=caption_locator,
                visual_features=features,
            )
        )
    return chunks
