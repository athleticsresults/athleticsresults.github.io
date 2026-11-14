import re
from pathlib import Path

root = Path(
    "/Users/jackbrackenbury/athleticsresults.github.io/international/was/world-athletics-indoor-championships"
)

TABLE_RE = re.compile(r"(<table\b[^>]*>)(.*?)(</table>)", re.DOTALL | re.IGNORECASE)
ROW_RE = re.compile(r"<tr\b[^>]*>.*?</tr>", re.DOTALL | re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
DQ_RE = re.compile(r"\bDQ\b")
OTHER_RE = re.compile(r"\b(DNS|DNF|NM|NH)\b")


def classify_row(html: str) -> str:
    text = TAG_RE.sub(" ", html)
    has_dq = bool(DQ_RE.search(text))
    has_other = bool(OTHER_RE.search(text))
    if has_dq and not has_other:
        return "DQ"
    if has_other and not has_dq:
        return "OTHER"
    return "KEEP"


def reorder_table_inner(inner: str) -> tuple[str, bool]:
    rows = list(ROW_RE.finditer(inner))
    if not rows:
        return inner, False
    kinds = [classify_row(m.group(0)) for m in rows]
    special = [i for i, k in enumerate(kinds) if k in ("DQ", "OTHER")]
    if not special:
        return inner, False
    if not any(kinds[i] == "DQ" for i in special) or not any(kinds[i] == "OTHER" for i in special):
        return inner, False
    start, end = min(special), max(special) + 1
    if any(kinds[i] == "KEEP" for i in range(start, end)):
        return inner, False
    first_other = next(i for i in range(start, end) if kinds[i] == "OTHER")
    last_dq = max(i for i in range(start, end) if kinds[i] == "DQ")
    if first_other > last_dq:
        return inner, False
    block = [m.group(0) for m in rows[start:end]]
    block_kinds = kinds[start:end]
    dq_rows = [r for r, k in zip(block, block_kinds) if k == "DQ"]
    other_rows = [r for r, k in zip(block, block_kinds) if k == "OTHER"]
    new_block = dq_rows + other_rows
    pieces = []
    last = 0
    for i, m in enumerate(rows):
        pieces.append(inner[last : m.start()])
        if start <= i < end:
            pieces.append(new_block[i - start])
        else:
            pieces.append(m.group(0))
        last = m.end()
    pieces.append(inner[last:])
    return "".join(pieces), True


changed_files = []
for p in sorted(root.rglob("*.html")):
    text = p.read_text(encoding="utf-8")
    n = [0]

    def repl(m):
        inner, changed = reorder_table_inner(m.group(2))
        if changed:
            n[0] += 1
        return m.group(1) + inner + m.group(3)

    new = TABLE_RE.sub(repl, text)
    if n[0]:
        p.write_text(new, encoding="utf-8")
        changed_files.append((str(p.relative_to(root)), n[0]))

print("files", len(changed_files))
for f, n in changed_files:
    print(n, f)
