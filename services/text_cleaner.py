import html
import re


MAX_TEXT_LENGTH = 12000
INNER_WHITESPACE_RE = re.compile(r"[ \t]+")
MULTIPLE_EMPTY_LINES_RE = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    if not text:
        return ""

    normalized = html.unescape(text)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

    cleaned_lines = []
    previous_line = None

    for raw_line in normalized.split("\n"):
        line = INNER_WHITESPACE_RE.sub(" ", raw_line).strip()
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue
        if line == previous_line:
            continue
        cleaned_lines.append(line)
        previous_line = line

    prepared = "\n".join(cleaned_lines).strip()
    prepared = MULTIPLE_EMPTY_LINES_RE.sub("\n\n", prepared)

    if len(prepared) > MAX_TEXT_LENGTH:
        prepared = prepared[:MAX_TEXT_LENGTH].rstrip() + "\n\n[Текст сокращен для анализа]"

    return prepared
