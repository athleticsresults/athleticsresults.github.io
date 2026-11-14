import re
from html.parser import HTMLParser
from pathlib import Path

root = Path("/Users/jackbrackenbury/athleticsresults.github.io/international/was/world-athletics-indoor-championships")

STATUS_OTHER = re.compile(r"\b(DNS|DNF|NM|NH)\b")
STATUS_DQ = re.compile(r"\bDQ\b")


class TableFinder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.stack = []
        self.cur = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.cur = {"rows": [], "caption": ""}
            self.stack.append("table")
        elif tag == "tr" and self.cur is not None:
            self.row = {"cells": []}
            self.stack.append("tr")
        elif tag in ("td", "th") and self.row is not None:
            self.cell = {"text": ""}
            self.stack.append("cell")
        elif tag == "caption" and self.cur is not None:
            self.stack.append("caption")
            self.cell = {"text": ""}

    def handle_endtag(self, tag):
        if tag == "table" and self.stack and self.stack[-1] == "table":
            self.tables.append(self.cur)
            self.cur = None
            self.stack.pop()
        elif tag == "tr" and self.stack and self.stack[-1] == "tr":
            self.cur["rows"].append(self.row)
            self.row = None
            self.stack.pop()
        elif tag in ("td", "th") and self.stack and self.stack[-1] == "cell":
            self.row["cells"].append(self.cell)
            self.cell = None
            self.stack.pop()
        elif tag == "caption" and self.stack and self.stack[-1] == "caption":
            self.cur["caption"] = self.cell["text"] if self.cell else ""
            self.cell = None
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1] in ("cell", "caption") and self.cell is not None:
            self.cell["text"] += data


issues = []
for p in sorted(root.rglob("*.html")):
    text = p.read_text(encoding="utf-8", errors="replace")
    parser = TableFinder()
    parser.feed(text)
    for ti, table in enumerate(parser.tables):
        statuses = []
        for ri, row in enumerate(table["rows"]):
            if not row or not row.get("cells"):
                continue
            joined = " | ".join(c["text"] for c in row["cells"] if c)
            has_dq = bool(STATUS_DQ.search(joined))
            has_other = bool(STATUS_OTHER.search(joined))
            if has_dq and not has_other:
                statuses.append(("DQ", ri, joined[:100]))
            elif has_other and not has_dq:
                statuses.append(("OTHER", ri, joined[:100]))
            elif has_dq and has_other:
                statuses.append(("BOTH", ri, joined[:100]))
        kinds = [s[0] for s in statuses]
        if "DQ" in kinds and "OTHER" in kinds:
            last_dq = max(i for i, k in enumerate(kinds) if k == "DQ")
            first_other = kinds.index("OTHER")
            if first_other < last_dq:
                issues.append((str(p.relative_to(root)), ti, statuses, table.get("caption", "")))

print("tables with OTHER before DQ:", len(issues))
for p, ti, statuses, cap in issues:
    print("\n", p, "table", ti, "cap=", repr(cap))
    for s in statuses:
        print("   ", s)
