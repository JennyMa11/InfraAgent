"""Title-aware aggregation, semantic sentence refinement, and token-bounded windows."""

import math
import re

import jieba.posseg as posseg

from .encoding import dot


def heading_line(line, *, allow_plain=False):
    if "\n" in line or not line:
        return None
    if re.match(r"^#{1,6}\s+\S", line):
        return re.sub(r"^#+\s+", "", line)
    if len(line) < 80 and re.match(
        r"^(?:第[一二三四五六七八九十\d]+[章节]|\d+(?:\.\d+)*[.、\s])", line
    ):
        return line
    # Plain TXT heading candidates must be isolated short noun phrases.
    if not allow_plain or len(line) > 32 or re.search(r"[。！？!?；;，,：:]", line):
        return None
    if not re.search(r"[\u3400-\u9fff]", line):
        return (
            line
            if re.fullmatch(r"[A-Z][A-Za-z0-9+/-]*(?: [A-Z][A-Za-z0-9+/-]*){0,4}", line)
            else None
        )
    words = [word for word in posseg.cut(line) if word.word.strip()]
    noun_count = sum(word.flag.startswith(("n", "eng")) for word in words)
    if (
        words
        and noun_count / len(words) >= 0.75
        and not any(word.flag.startswith("v") for word in words)
    ):
        return line
    return None


def fits(text, size, encoder):
    return len(text) <= size and (
        not hasattr(encoder, "token_length") or encoder.token_length(text) <= encoder.token_limit
    )


def _fitting_length(text, size, encoder):
    """Largest prefix satisfying both the character and token limits."""
    if not text:
        return 0
    low, high = 1, min(size, len(text))
    while low < high:
        middle = (low + high + 1) // 2
        if fits(text[:middle], size, encoder):
            low = middle
        else:
            high = middle - 1
    return low


def bounded_units(text, size, encoder):
    """Keep punctuation; split oversize single sentences without model truncation."""
    units = []
    for part in re.split(r"(```[^\n]*\n.*?```)", text, flags=re.DOTALL):
        if not part:
            continue
        sentences = (
            [part]
            if part.startswith("```")
            else re.findall(r".+?(?:[。！？!?；;]|\.(?=\s|$)|\n|$)", part, flags=re.DOTALL)
        )
        for sentence in sentences:
            remainder = sentence.strip()
            while remainder:
                if fits(remainder, size, encoder):
                    units.append(remainder)
                    break
                length = _fitting_length(remainder, size, encoder)
                units.append(remainder[:length])
                remainder = remainder[length:].lstrip()
    return units


def semantic_refine(text, size, encoder, threshold):
    if fits(text, size, encoder):
        return [text]
    units = bounded_units(text, size, encoder)
    vectors = encoder.encode(units)
    result, current, previous = [], "", None
    for sentence, vector in zip(units, vectors, strict=True):
        combined = current + ("\n" if current else "") + sentence
        topic_change = (
            previous is not None
            and len(current) >= size * 0.25
            and dot(previous, vector) < threshold
        )
        if current and (topic_change or not fits(combined, size, encoder)):
            result.append(current)
            current = ""
        current += ("\n" if current else "") + sentence
        previous = vector
    if current:
        result.append(current)
    return result


def centroid(left, right, count):
    total = [a * count + b for a, b in zip(left, right, strict=True)]
    norm = math.sqrt(dot(total, total)) or 1
    return [value / norm for value in total]


def window_ranges(text, size, encoder, overlap=0):
    """Character intervals with optional overlap, bounded by one fixed tokenizer."""
    if size < 1 or not 0 <= overlap < size:
        raise ValueError("window requires positive size and 0 <= overlap < size")
    ranges, start = [], 0
    while start < len(text):
        end = start + _fitting_length(text[start:], size, encoder)
        if not fits(text[start:end], size, encoder):
            raise ValueError("one character exceeds the tokenizer limit")
        ranges.append((start, end))
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return ranges
