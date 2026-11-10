#!/usr/bin/env python3
import json, os, re, sys, time, html, urllib.parse, urllib.request
from collections import defaultdict

_html_escape = html.escape
html.escape = lambda s, quote=False: _html_escape(s, quote=quote)

ROOT = "/Users/jackbrackenbury/athleticsresults.github.io/international/was/world-athletics-cross-country-championships"
CACHE = "/tmp/wxcwiki"
os.makedirs(CACHE, exist_ok=True)
UA = {"User-Agent": "AthleticsResultsBot/1.0 (personal static archive)"}

NATION = {
    "AFG": "Afghanistan", "ALG": "Algeria", "AND": "Andorra", "ANG": "Angola",
    "ANT": "Antigua & Barbuda", "ARG": "Argentina", "ARM": "Armenia", "ARU": "Aruba",
    "ASA": "American Samoa", "AUS": "Australia", "AUT": "Austria", "AZE": "Azerbaijan",
    "BAH": "Bahamas", "BAN": "Bangladesh", "BAR": "Barbados", "BDI": "Burundi",
    "BEL": "Belgium", "BEN": "Benin", "BER": "Bermuda", "BHU": "Bhutan",
    "BIH": "Bosnia & Herzegovina", "BIZ": "Belize", "BLR": "Belarus", "BOL": "Bolivia",
    "BOT": "Botswana", "BRA": "Brazil", "BRN": "Bahrain", "BRU": "Brunei",
    "BUL": "Bulgaria", "BUR": "Burkina Faso", "CAF": "Central African Republic",
    "CAM": "Cambodia", "CAN": "Canada", "CAY": "Cayman Islands", "CGO": "Congo",
    "CHA": "Chad", "CHI": "Chile", "CHN": "China", "CIV": "Côte d'Ivoire",
    "CMR": "Cameroon", "COD": "DR Congo", "COK": "Cook Islands", "COL": "Colombia",
    "COM": "Comoros", "CPV": "Cape Verde", "CRC": "Costa Rica", "CRO": "Croatia",
    "CUB": "Cuba", "CYP": "Cyprus", "CZE": "Czech Republic", "TCH": "Czechoslovakia",
    "DEN": "Denmark", "DJI": "Djibouti", "DMA": "Dominica", "DOM": "Dominican Republic",
    "ECU": "Ecuador", "EGY": "Egypt", "ERI": "Eritrea", "ESA": "El Salvador",
    "ESP": "Spain", "EST": "Estonia", "ETH": "Ethiopia", "FIJ": "Fiji",
    "FIN": "Finland", "FRA": "France", "FSM": "Micronesia", "GAB": "Gabon",
    "GAM": "Gambia", "GBR": "Great Britain & NI", "GEO": "Georgia", "GEQ": "Equatorial Guinea",
    "GER": "Germany", "FRG": "West Germany", "GDR": "East Germany", "GHA": "Ghana",
    "GRE": "Greece", "GRN": "Grenada", "GUA": "Guatemala", "GUI": "Guinea",
    "GUM": "Guam", "GUY": "Guyana", "HAI": "Haiti", "HKG": "Hong Kong",
    "HON": "Honduras", "HUN": "Hungary", "INA": "Indonesia", "IND": "India",
    "IRI": "Iran", "IRL": "Ireland", "IRQ": "Iraq", "ISL": "Iceland",
    "ISR": "Israel", "ISV": "US Virgin Islands", "ITA": "Italy", "IVB": "British Virgin Islands",
    "JAM": "Jamaica", "JOR": "Jordan", "JPN": "Japan", "KAZ": "Kazakhstan",
    "KEN": "Kenya", "KGZ": "Kyrgyzstan", "KIR": "Kiribati", "KOR": "South Korea",
    "KOS": "Kosovo", "KSA": "Saudi Arabia", "KUW": "Kuwait", "LAO": "Laos",
    "LAT": "Latvia", "LBA": "Libya", "LBR": "Liberia", "LCA": "Saint Lucia",
    "LES": "Lesotho", "LIB": "Lebanon", "LIE": "Liechtenstein", "LTU": "Lithuania",
    "LUX": "Luxembourg", "MAD": "Madagascar", "MAR": "Morocco", "MAS": "Malaysia",
    "MAW": "Malawi", "MDA": "Moldova", "MDV": "Maldives", "MEX": "Mexico",
    "MGL": "Mongolia", "MHL": "Marshall Islands", "MKD": "North Macedonia",
    "MLI": "Mali", "MLT": "Malta", "MNE": "Montenegro", "MON": "Monaco",
    "MOZ": "Mozambique", "MRI": "Mauritius", "MTN": "Mauritania", "MYA": "Myanmar",
    "NAM": "Namibia", "NCA": "Nicaragua", "NED": "Netherlands", "NEP": "Nepal",
    "NGR": "Nigeria", "NIG": "Niger", "NOR": "Norway", "NRU": "Nauru",
    "NZL": "New Zealand", "OMA": "Oman", "PAK": "Pakistan", "PAN": "Panama",
    "PAR": "Paraguay", "PER": "Peru", "PHI": "Philippines", "PLE": "Palestine",
    "PLW": "Palau", "PNG": "Papua New Guinea", "POL": "Poland", "POR": "Portugal",
    "PRK": "DPR of Korea", "PUR": "Puerto Rico", "QAT": "Qatar", "ROU": "Romania",
    "RSA": "South Africa", "RUS": "Russian Federation", "RWA": "Rwanda", "SAM": "Samoa",
    "SCO": "Scotland", "SEN": "Senegal", "SEY": "Seychelles", "SGP": "Singapore",
    "SKN": "Saint Kitts & Nevis", "SLE": "Sierra Leone", "SLO": "Slovenia",
    "SMR": "San Marino", "SOL": "Solomon Islands", "SOM": "Somalia", "SRB": "Serbia",
    "SRI": "Sri Lanka", "SSD": "South Sudan", "STP": "São Tomé & Príncipe",
    "SUD": "Sudan", "SUI": "Switzerland", "SUR": "Suriname", "SVK": "Slovakia",
    "SWE": "Sweden", "SWZ": "Eswatini", "SYR": "Syria", "TAN": "Tanzania",
    "TGA": "Tonga", "THA": "Thailand", "TJK": "Tajikistan", "TKM": "Turkmenistan",
    "TLS": "Timor-Leste", "TOG": "Togo", "TPE": "Chinese Taipei", "TTO": "Trinidad & Tobago",
    "TUN": "Tunisia", "TUR": "Turkey", "TUV": "Tuvalu", "UAE": "United Arab Emirates",
    "UGA": "Uganda", "UKR": "Ukraine", "URS": "Soviet Union", "URU": "Uruguay",
    "USA": "United States", "UZB": "Uzbekistan", "VAN": "Vanuatu", "VEN": "Venezuela",
    "VIE": "Vietnam", "VIN": "St Vincent", "WAL": "Wales", "YAR": "North Yemen",
    "YEM": "Yemen", "YUG": "Yugoslavia", "ZAM": "Zambia", "ZIM": "Zimbabwe",
    "EUN": "Unified Team", "SCG": "Serbia & Montenegro", "ENG": "England",
    "NIR": "Northern Ireland", "IOA": "Independent Athletes", "ART": "Refugee Athletes",
}

FLAG_ALIAS = {
    "United Kingdom": "GBR", "Great Britain": "GBR", "Great Britain and Northern Ireland": "GBR",
    "Soviet Union": "URS", "United States": "USA", "United States of America": "USA",
    "West Germany": "FRG", "East Germany": "GDR", "Germany": "GER",
    "Chinese Taipei": "TPE", "Taiwan": "TPE", "Ivory Coast": "CIV",
    "South Africa": "RSA", "North Yemen": "YAR", "Yemen Arab Republic": "YAR",
    "Czech Republic": "CZE", "Czechia": "CZE", "Netherlands": "NED",
    "Switzerland": "SUI", "Romania": "ROU", "Croatia": "CRO",
}

EDITIONS = [
    (1989, "1989-stavanger", "stavanger-1989", "Stavanger", "NOR"),
    (1990, "1990-aix-les-baines", "aix-les-baines-1990", "Aix-les-Bains", "FRA"),
    (1991, "1991-antwerp", "antwerp-1991", "Antwerp", "BEL"),
    (1992, "1992-boston", "boston-1992", "Boston", "USA"),
    (1993, "1993-amorebieta", "amorebieta-1993", "Amorebieta", "ESP"),
    (1994, "1994-budapest", "budapest-1994", "Budapest", "HUN"),
    (1995, "1995-durham", "durham-1995", "Durham", "GBR"),
    (1996, "1996-cape-town", "cape-town-1996", "Cape Town", "RSA"),
    (1997, "1997-turin", "turin-1997", "Turin", "ITA"),
    (1998, "1998-marrakech", "marrakech-1998", "Marrakech", "MAR"),
    (1999, "1999-belfast", "belfast-1999", "Belfast", "GBR"),
    (2000, "2000-vilamoura", "vilamoura-2000", "Vilamoura", "POR"),
    (2001, "2001-ostend", "ostend-2001", "Ostend", "BEL"),
    (2002, "2002-dublin", "dublin-2002", "Dublin", "IRL"),
    (2003, "2003-lausanne", "lausanne-2003", "Lausanne", "SUI"),
    (2004, "2004-brussels", "brussels-2004", "Brussels", "BEL"),
    (2005, "2005-saint-galmier", "saint-galmier-2005", "Saint-Galmier", "FRA"),
    (2006, "2006-fukuoka", "fukuoka-2006", "Fukuoka", "JPN"),
    (2007, "2007-mombasa", "mombasa-2007", "Mombasa", "KEN"),
    (2008, "2008-edinburgh", "edinburgh-2008", "Edinburgh", "GBR"),
    (2009, "2009-amman", "amman-2009", "Amman", "JOR"),
    (2010, "2010-bydgoszcz", "bydgoszcz-2010", "Bydgoszcz", "POL"),
    (2011, "2011-punta-umbria", "punta-umbria-2011", "Punta Umbría", "ESP"),
    (2013, "2013-bydgoszcz", "bydgoszcz-2013", "Bydgoszcz", "POL"),
    (2015, "2015-qingzhen", "qingzhen-2015", "Qingzhen", "CHN"),
    (2017, "2017-kampala", "kampala-2017", "Kampala", "UGA"),
    (2019, "2019-aarhus", "aarhus-2019", "Aarhus", "DEN"),
    (2023, "2023-bathurst", "bathurst-2023", "Bathurst", "AUS"),
    (2024, "2024-belgrade", "belgrade-2024", "Belgrade", "SRB"),
    (2026, "2026-tallahassee", "tallahassee-2026", "Tallahassee", "USA"),
]


def edition_num(year):
    if year <= 2011:
        return year - 1972
    if year <= 2019:
        return 39 + (year - 2011) // 2
    return {2023: 44, 2024: 45, 2026: 46}[year]


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def races_for(year):
    races = [
        ("Senior men's race", "senior-men.html", "Senior Men's Race", "men",
         "6 to run, 4 to score" if year >= 2009 or 2002 <= year <= 2006 else "9 to run, 6 to score"),
        ("Junior men's race", "junior-men.html", "U20 Men's Race" if year >= 2017 else "Junior Men's Race", "men", "6 to run, 4 to score"),
        ("Senior women's race", "senior-women.html", "Senior Women's Race", "women", "6 to run, 4 to score"),
        ("Junior women's race", "junior-women.html", "U20 Women's Race" if year >= 2017 else "Junior Women's Race", "women", "6 to run, 4 to score"),
    ]
    if 1998 <= year <= 2006:
        races.insert(1, ("Men's short race", "senior-men-short.html", "Senior Men's Short Race", "men", "6 to run, 4 to score"))
        races.insert(4, ("Women's short race", "senior-women-short.html", "Senior Women's Short Race", "women", "6 to run, 4 to score"))
    if year >= 2017:
        races.append(("Mixed relay", "mixed-relay.html", "Mixed Relay", "mixed", None))
    return races


def wiki_get(title):
    key = re.sub(r"[^A-Za-z0-9]+", "_", title)
    path = os.path.join(CACHE, key + ".wiki")
    if os.path.exists(path) and os.path.getsize(path) > 200:
        return open(path, encoding="utf-8").read()
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "prop": "revisions", "rvprop": "content",
        "rvslots": "main", "titles": title, "format": "json", "redirects": 1,
    })
    for attempt in range(8):
        try:
            req = urllib.request.Request(url, headers=UA)
            data = json.loads(urllib.request.urlopen(req, timeout=60).read())
            pages = data["query"]["pages"]
            page = list(pages.values())[0]
            if "missing" in page:
                open(path, "w").write("")
                return ""
            text = page["revisions"][0]["slots"]["main"]["*"]
            open(path, "w", encoding="utf-8").write(text)
            time.sleep(1.1)
            return text
        except Exception as e:
            print("retry", title, e)
            time.sleep(4 * (attempt + 1))
    raise RuntimeError("failed " + title)


def wiki_name(s):
    s = s.strip()
    s = re.sub(r"\{\{sortname\|([^|}]+)\|([^|}]+)[^}]*\}\}", lambda m: m.group(1) + " " + m.group(2), s, flags=re.I)
    s = re.sub(r"\{\{ill\|([^}|]+)", lambda m: m.group(1), s, flags=re.I)
    s = re.sub(r"\{\{flagathlete\|\[\[([^\]|]+)(?:\|[^\]]+)?\]\]\|([^}]+)\}\}", lambda m: m.group(1), s, flags=re.I)
    def repl(m):
        inner = m.group(1)
        return inner.split("|")[-1] if "|" in inner else inner
    s = re.sub(r"\[\[([^\]]+)\]\]", repl, s)
    s = re.sub(r"\{\{[^}]+\}\}", "", s)
    s = s.replace("'''", "").replace("''", "")
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").strip()
    s = s.strip("() ").strip()
    return re.sub(r"\s+", " ", s)


def wiki_code(s):
    m = re.search(r"\{\{flagcountry\|([A-Z]{3})", s, re.I)
    if m:
        return m.group(1).upper()
    m = re.search(r"\{\{flagathlete\|[^|]+\|([A-Z]{3})", s, re.I)
    if m:
        return m.group(1).upper()
    m = re.search(r"\{\{flagathlete\|[^|]+\|([^}]+)\}\}", s, re.I)
    if m:
        raw = m.group(1).strip()
        if re.fullmatch(r"[A-Z]{3}", raw):
            return raw
        return FLAG_ALIAS.get(raw, FLAG_ALIAS.get(raw.title(), ""))
    m = re.search(r"\{\{flagg\|[^|]+\|([A-Z]{3})", s, re.I)
    if m:
        return m.group(1).upper()
    m = re.search(r"\{\{flag(?:icon|IOC)?\|([^}|]+)", s, re.I)
    if m:
        raw = m.group(1).strip()
        if re.fullmatch(r"[A-Z]{3}", raw):
            return raw
        return FLAG_ALIAS.get(raw, FLAG_ALIAS.get(raw.title(), raw[:3].upper()))
    m = re.search(r"\{\{([A-Z]{3})\}\}", s)
    if m:
        return m.group(1)
    return ""


def infobox(text):
    m = re.search(r"\{\{Infobox XC Championships(.*?)(?:\n\}\}|\n\|\}|\n\{\{)", text, re.S | re.I)
    box = m.group(1) if m else text[:2500]
    def field(name):
        mm = re.search(r"\|\s*" + name + r"\s*=\s*(.*)", box, re.I)
        return mm.group(1).strip() if mm else ""
    return {
        "date": field("Date"),
        "host": field("Host city"),
        "location": field("Location") or field("Venue"),
        "nations": field("Nations participating"),
        "athletes": field("Athletes participating"),
        "distances": field("Distances"),
        "edition": field("Edition"),
    }


def format_date(raw, year):
    raw = re.sub(r"\[\[([^\]]+)\]\]", lambda m: m.group(1).split("|")[-1], raw)
    raw = re.sub(r"\{\{[^}]+\}\}", "", raw).strip()
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    # 21–22 March 1998 or March 19 or 19 March
    m = re.search(r"(\d{1,2})\s*[–-]\s*(\d{1,2})\s+([A-Za-z]+)", raw)
    if m:
        mon = m.group(3)[:3].title()
        return f"{int(m.group(1)):d}–{int(m.group(2)):d} {mon} {year}"
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2})\s*[–-]\s*(\d{1,2})", raw)
    if m:
        mon = m.group(1)[:3].title()
        return f"{int(m.group(2)):d}–{int(m.group(3)):d} {mon} {year}"
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2})", raw)
    if m:
        return f"{int(m.group(2)):d} {m.group(1)[:3].title()} {year}"
    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)", raw)
    if m:
        return f"{int(m.group(1)):d} {m.group(2)[:3].title()} {year}"
    return raw or str(year)


def format_dist(raw):
    raw = re.sub(r"\[\[([^\]]+)\]\]", lambda m: m.group(1).split("|")[-1], raw)
    m = re.search(r"([\d.,]+)\s*(km|m)\b", raw, re.I)
    if not m:
        return raw.strip()
    num, unit = m.group(1).replace(",", ""), m.group(2).lower()
    val = float(num)
    if unit == "km":
        metres = int(round(val * 1000))
    else:
        metres = int(round(val))
    if metres < 10000:
        return f"{metres}m"
    return f"{metres:,}m"


def split_tables(section):
    tables = []
    i = 0
    while True:
        start = section.find("{|", i)
        if start < 0:
            break
        depth = 0
        j = start
        while j < len(section):
            if section.startswith("{|", j):
                depth += 1
                j += 2
                continue
            if section.startswith("|}", j):
                depth -= 1
                j += 2
                if depth == 0:
                    tables.append(section[start:j])
                    break
                continue
            j += 1
        i = j if j > start else start + 2
    return tables


def _row_cells(part):
    if "||" in part:
        return [c.strip() for c in re.split(r"\|\|", part) if c.strip()]
    cells = []
    for line in part.split("\n"):
        line = line.strip()
        if not line.startswith("|") or line.startswith("|-") or line.startswith("|}"):
            continue
        cells.append(line.lstrip("|").strip())
    return cells


def _flatten_wiki(text):
    text = re.sub(r"\{\{[Ii]ll\|([^}|]+)[^}]*\}\}", r"[[\1]]", text)
    return text


def parse_individuals(text):
    text = _flatten_wiki(text)
    idx = re.search(r"(====\s*Individual|\|\+Individual(?: race)?)", text, re.I)
    if not idx:
        idx = re.search(r"Individual", text)
    if idx:
        brace = text.rfind("{|", 0, idx.start() + 1)
        blob = text[brace if brace >= 0 else idx.start():]
    else:
        blob = text
    tables = split_tables(blob)
    if not tables:
        return []
    table = tables[0]
    if "US$" in table[:400] and tables[1:]:
        table = tables[1]
    rows = []
    parts = re.split(r"\n\|-(?!\n\|align=left style=\"border:0\")", table)
    for part in parts[1:]:
        if part.strip().startswith("{|") or "width=100%" in part[:40]:
            continue
        if part.lstrip().startswith("!"):
            continue
        cells = _row_cells(part)
        if len(cells) < 3:
            continue
        rank_cell = cells[0]
        time_cell = cells[-1]
        ath_cell = cells[1]
        cty_cell = ""
        for c in cells[1:-1]:
            if wiki_code(c):
                cty_cell = c
                break
        if not cty_cell and len(cells) >= 4:
            cty_cell = cells[-2]
            ath_cell = cells[1]
        rank_cell = re.sub(r"\{\{gold0?1\}\}", "1", rank_cell, flags=re.I)
        rank_cell = re.sub(r"\{\{silver0?2\}\}", "2", rank_cell, flags=re.I)
        rank_cell = re.sub(r"\{\{bronze0?3\}\}", "3", rank_cell, flags=re.I)
        rank_txt = re.sub(r"<[^>]+>", "", rank_cell)
        rank_txt = re.sub(r"align=center\|", "", rank_txt)
        rank_txt = wiki_name(rank_txt).replace("—", "-").replace("–", "-")
        if rank_txt in {"", "-", "–", "—"}:
            rank = "-"
        else:
            m = re.search(r"\d+", rank_txt)
            rank = m.group(0) if m else "-"
        athlete = wiki_name(re.sub(r"align=left\s*\|", "", ath_cell))
        code = wiki_code(cty_cell) or wiki_code(part)
        mark = wiki_name(time_cell.split("\n")[0])
        mark = mark.replace("{{n/a}}", "").strip()
        if not athlete or athlete.lower() in {"athlete", "rank", "country", "time", "team", "points", "place"}:
            continue
        if "width=" in ath_cell or "width=" in time_cell:
            continue
        if "pts" in athlete.lower() or "vertical-align" in athlete:
            continue
        if not code and mark.upper() not in {"DNF", "DNS", "DQ"}:
            continue
        if code in {"IAAF"}:
            continue
        rows.append({"rank": rank, "athlete": athlete, "noc": code, "mark": mark})
    return rows


def parse_teams(text):
    text = _flatten_wiki(text)
    idx = re.search(r"====\s*Teams?", text, re.I)
    if not idx:
        return []
    blob = text[idx.start():]
    tables = split_tables(blob)
    if not tables:
        return []
    table = tables[0]
    teams = []
    chunks = re.split(r"\n\|-(?!\n\|align=left style=\"border:0\")", "\n" + table)
    for chunk in chunks:
        code = wiki_code(chunk)
        if not code:
            continue
        rank_m = re.search(
            r"(\{\{gold0?1\}\}|\{\{silver0?2\}\}|\{\{bronze0?3\}\}|\b\d+\b)",
            chunk,
            re.I,
        )
        if not rank_m:
            continue
        rs = rank_m.group(1)
        if "gold" in rs.lower():
            rank = "1"
        elif "silver" in rs.lower():
            rank = "2"
        elif "bronze" in rs.lower():
            rank = "3"
        else:
            rank = re.search(r"\d+", rs).group(0)
        pts_m = re.findall(r"\|\|\s*([\d]+)\s*(?:\n|$)", chunk)
        if not pts_m:
            pts_m = re.findall(r"\|(\d+)\s*(?:\n|$)", chunk)
        points = pts_m[-1] if pts_m else ""
        members = []
        for mm in re.finditer(
            r"\|align=left style=\"border:0\"\|\s*(.*?)\s*\|\|\s*align=right style=\"border:0\"\|\s*(.*)",
            chunk,
        ):
            raw_name, raw_pl = mm.group(1).strip(), mm.group(2).strip()
            nonscore = raw_name.startswith("(") or raw_pl.startswith("(")
            name = wiki_name(raw_name)
            pl = wiki_name(raw_pl).strip("()")
            members.append({"name": name, "place": pl, "nonscore": nonscore})
        if code and code not in {"IAAF"}:
            teams.append({"rank": rank, "noc": code, "points": points, "members": members})
    return teams


def fill_team_members(teams, inds, nscore=4, nrun=6):
    by = defaultdict(list)
    for r in inds:
        if r["rank"].isdigit() and r["noc"]:
            by[r["noc"]].append(r)
    for t in teams:
        if t["members"]:
            continue
        mems = sorted(by.get(t["noc"], []), key=lambda x: int(x["rank"]))[:nrun]
        t["members"] = [
            {"name": m["athlete"], "place": m["rank"], "nonscore": i >= nscore}
            for i, m in enumerate(mems)
        ]
    if teams:
        return teams
    scored = []
    for noc, mems in by.items():
        mems = sorted(mems, key=lambda x: int(x["rank"]))
        if len(mems) < nscore:
            continue
        pts = sum(int(m["rank"]) for m in mems[:nscore])
        members = [
            {"name": m["athlete"], "place": m["rank"], "nonscore": i >= nscore}
            for i, m in enumerate(mems[:nrun])
        ]
        scored.append({"rank": "", "noc": noc, "points": f"{pts}pts", "members": members, "pts": pts})
    scored.sort(key=lambda t: t["pts"])
    for i, t in enumerate(scored, 1):
        t["rank"] = str(i)
    return scored


def parse_mixed(text):
    """Relay: one table of teams with time."""
    text = _flatten_wiki(text)
    tables = split_tables(text)
    rows = []
    if not tables:
        return rows
    table = tables[0]
    parts = re.split(r"\n\|-", table)
    for part in parts[1:]:
        if (
            "flag" not in part.lower()
            and "flagcountry" not in part.lower()
            and not re.search(r"\{\{[A-Z]{3}\}\}", part)
        ):
            continue
        cells = [c.strip() for c in re.split(r"\|\|", part)] if "||" in part else _row_cells(part)
        if len(cells) < 2:
            continue
        rank_cell = cells[0]
        rank_cell = re.sub(r"\{\{gold0?1\}\}", "1", rank_cell, flags=re.I)
        rank_cell = re.sub(r"\{\{silver0?2\}\}", "2", rank_cell, flags=re.I)
        rank_cell = re.sub(r"\{\{bronze0?3\}\}", "3", rank_cell, flags=re.I)
        rm = re.search(r"\d+", rank_cell)
        rank = str(int(rm.group(0))) if rm else "-"
        code = wiki_code(part)
        if not code:
            mcode = re.search(r"\{\{([A-Z]{3})\}\}", part)
            if mcode:
                code = mcode.group(1)
        # last numeric-looking / time cell
        mark = ""
        for c in reversed(cells):
            t = wiki_name(c)
            if re.search(r"\d+:\d+", t) or t in {"DNF", "DQ", "DNS"}:
                mark = t
                break
        names = []
        for mm in re.finditer(r"\[\[([^\]]+)\]\]", part):
            nm = wiki_name("[[" + mm.group(1) + "]]")
            if nm and "Championships" not in nm and not nm.startswith("Category:"):
                names.append(nm)
        rows.append({"rank": rank, "noc": code, "mark": mark, "names": names})
    return rows


def medal_cls(rank):
    return { "1": "gold", "2": "silver", "3": "bronze" }.get(rank, "")


def medal_rank_cell(rank):
    return {
        "1": "&#129351;",
        "2": "&#129352;",
        "3": "&#129353;",
    }.get(rank, html.escape(rank))


def mark_html(mark, nonscore=False):
    m = mark.strip()
    special = m.upper() in {"DNF", "DNS", "DQ", "NM", "DNC"}
    inner = f"<b>{html.escape(m)}</b>" if special else html.escape(m)
    if nonscore:
        inner = f"({inner})"
    return inner


def html_page(title, nav, body):
    return f"""<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <title>{html.escape(title, quote=False)}</title>
    <meta name="description" content="" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" href="/../style.css" />
</head>

<body>
    <div class="nav">
        {nav}
    </div>

{body}

    <footer>
        <p>Copyright &copy; Athletics Results 2025 - 2026.</p>
    </footer>
</body>

</html>
"""


def ind_table(rows):
    out = []
    out.append("            <table>")
    out.append("                <tr>")
    out.append("                    <th>Rank</th>")
    out.append("                    <th>Athlete</th>")
    out.append("                    <th>Nation</th>")
    out.append("                    <th>Mark</th>")
    out.append("                </tr>")
    for r in rows:
        cls = medal_cls(r["rank"])
        tr = f'                <tr class="{cls}">' if cls else "                <tr>"
        out.append(tr)
        out.append(f"                    <td>{medal_rank_cell(r['rank'])}</td>")
        out.append(f"                    <td>{html.escape(r['athlete'])}</td>")
        out.append(f"                    <td><b>{html.escape(r['noc'])}</b></td>")
        out.append(f"                    <td>{mark_html(r['mark'])}</td>")
        out.append("                </tr>")
    out.append("            </table>")
    return "\n".join(out)


def team_table(teams):
    out = []
    out.append("            <table>")
    out.append("                <tr>")
    out.append("                    <th>Rank</th>")
    out.append("                    <th colspan=\"2\">Nation</th>")
    out.append("                    <th>Mark</th>")
    out.append("                </tr>")
    for t in teams:
        cls = medal_cls(t["rank"])
        n = 1 + len(t["members"])
        trc = f' class="{cls}"' if cls else ""
        name = NATION.get(t["noc"], t["noc"])
        out.append(f"                <tr{trc}>")
        out.append(f'                    <td rowspan="{n}">{medal_rank_cell(t["rank"])}</td>')
        out.append(f"                    <td><b>{html.escape(name)}</b></td>")
        out.append(f"                    <td><b>{html.escape(t['noc'])}</b></td>")
        pts = t["points"]
        pts_s = f"{pts}pts" if pts and not pts.lower().endswith("pts") else pts
        out.append(f'                    <td rowspan="{n}">{html.escape(pts_s)}</td>')
        out.append("                </tr>")
        for mem in t["members"]:
            out.append(f"                <tr{trc}>")
            out.append(f"                    <td>{html.escape(mem['name'])}</td>")
            pl = mem["place"]
            special = pl.upper() in {"DNF", "DNS", "DQ"}
            if mem["nonscore"]:
                cell = f"(<b>{html.escape(pl)}</b>)" if special else f"({html.escape(pl)})"
            else:
                cell = f"<b>{html.escape(pl)}</b>" if special else html.escape(pl)
            out.append(f"                    <td>{cell}</td>")
            out.append("                </tr>")
    out.append("            </table>")
    return "\n".join(out)


def mixed_table(rows):
    out = []
    out.append("            <table>")
    out.append("                <tr>")
    out.append("                    <th>Rank</th>")
    out.append("                    <th colspan=\"2\">Nation</th>")
    out.append("                    <th>Mark</th>")
    out.append("                </tr>")
    for r in rows:
        cls = medal_cls(r["rank"])
        names = [n for n in r["names"] if n and n != NATION.get(r["noc"], "")]
        n = 1 + len(names)
        trc = f' class="{cls}"' if cls else ""
        name = NATION.get(r["noc"], r["noc"])
        out.append(f"                <tr{trc}>")
        out.append(f'                    <td rowspan="{n}">{medal_rank_cell(r["rank"])}</td>')
        out.append(f"                    <td><b>{html.escape(name)}</b></td>")
        out.append(f"                    <td><b>{html.escape(r['noc'])}</b></td>")
        out.append(f'                    <td rowspan="{n}">{mark_html(r["mark"])}</td>')
        out.append("                </tr>")
        for nm in names:
            out.append(f"                <tr{trc}>")
            out.append(f'                    <td colspan="2">{html.escape(nm)}</td>')
            out.append("                </tr>")
    out.append("            </table>")
    return "\n".join(out)


def medal_table(tallies):
    items = []
    for noc, (g, s, b) in tallies.items():
        if g or s or b:
            items.append((g, s, b, g + s + b, NATION.get(noc, noc), noc))
    items.sort(key=lambda x: (-x[0], -x[1], -x[2], x[4]))
    ranked = []
    i = 0
    while i < len(items):
        j = i
        while j < len(items) and items[j][:3] == items[i][:3]:
            j += 1
        rank = str(i + 1)
        if j - i > 1:
            rank = "=" + rank
        for k in range(i, j):
            ranked.append((rank,) + items[k])
        i = j
    out = []
    out.append("            <table>")
    out.append("                <tr>")
    out.append("                    <th>Rank</th>")
    out.append("                    <th colspan=\"2\">Nation</th>")
    out.append('                    <th class="gold">&#129351;</th>')
    out.append('                    <th class="silver">&#129352;</th>')
    out.append('                    <th class="bronze">&#129353;</th>')
    out.append("                    <th>Total</th>")
    out.append("                </tr>")
    for rank, g, s, b, tot, name, noc in ranked:
        out.append("                <tr>")
        out.append(f"                    <td>{html.escape(rank)}</td>")
        out.append(f"                    <td>{html.escape(name)}</td>")
        out.append(f"                    <td><b>{html.escape(noc)}</b></td>")
        out.append(f"                    <td>{g}</td>")
        out.append(f"                    <td>{s}</td>")
        out.append(f"                    <td>{b}</td>")
        out.append(f"                    <td>{tot}</td>")
        out.append("                </tr>")
    out.append("            </table>")
    return "\n".join(out)


def add_medals(tallies, rows_or_teams, is_team=False):
    seq = rows_or_teams
    for item in seq:
        r = item["rank"]
        if r not in {"1", "2", "3"}:
            continue
        noc = item["noc"]
        if not noc:
            continue
        g, s, b = tallies[noc]
        if r == "1":
            g += 1
        elif r == "2":
            s += 1
        else:
            b += 1
        tallies[noc] = [g, s, b]


def venue_name(raw):
    raw = re.sub(r"\[\[([^\]]+)\]\]", lambda m: m.group(1).split("|")[-1], raw)
    raw = re.sub(r"\{\{[^}]+\}\}", "", raw)
    return re.sub(r"\s+", " ", raw).strip(" ,")


def main():
    wanted = {int(x) for x in sys.argv[1:]} if len(sys.argv) > 1 else None
    summary = []
    for year, folder, slug, city, noc in EDITIONS:
        if wanted and year not in wanted:
            continue
        print("===", year, flush=True)
        if year >= 2023:
            ch_title = f"{year} World Athletics Cross Country Championships"
            brand = "World Athletics"
        else:
            ch_title = f"{year} IAAF World Cross Country Championships"
            brand = "IAAF"
        ch = wiki_get(ch_title)
        info = infobox(ch)
        date = format_date(info["date"], year)
        venue = venue_name(info["location"]) or city
        athletes = re.search(r"\d+", info["athletes"] or "")
        nations = re.search(r"\d+", info["nations"] or "")
        # sometimes participation on championship page
        if not athletes:
            m = re.search(r"(\d+)\s+athletes from\s+(\d+)", ch, re.I)
            if m:
                athletes, nations = m.group(1), m.group(2)
            else:
                athletes, nations = "?", "?"
        else:
            athletes = athletes.group(0)
            nations = nations.group(0) if nations else "?"

        edn = edition_num(year)
        full = f"{ordinal(edn)} {brand} Cross Country Championships {city} {year}" if year >= 2023 else f"{ordinal(edn)} IAAF World Cross Country Championships {city} {year}"
        os.makedirs(os.path.join(ROOT, folder), exist_ok=True)

        race_meta = []
        tallies = defaultdict(lambda: [0, 0, 0])

        for wiki_race, fname, label, gender, team_note in races_for(year):
            titles = [f"{ch_title} – {wiki_race}"]
            if wiki_race.startswith("Junior"):
                u20 = f"{ch_title} – {wiki_race.replace('Junior', 'U20')}"
                titles = [u20, titles[0]] if year >= 2023 else [titles[0], u20]
            if wiki_race == "Mixed relay":
                titles.append(f"{ch_title} – Mixed relay race")
                titles.append(ch_title)
            wt = ""
            used = titles[0]
            for title in titles:
                wt = wiki_get(title)
                if wt:
                    used = title
                    break
            if not wt:
                print(" missing", titles[0])
                continue
            if year >= 2023:
                sec = None
                if "Junior men's" in wiki_race:
                    sec = re.search(r"===U20 men===", wt, re.I)
                elif "Junior women's" in wiki_race:
                    sec = re.search(r"===U20 women===", wt, re.I)
                elif "Senior men's" in wiki_race:
                    sec = re.search(r"===Senior men===", wt, re.I)
                elif "Senior women's" in wiki_race:
                    sec = re.search(r"===Senior women===", wt, re.I)
                elif "Mixed" in wiki_race:
                    sec = re.search(r"===Senior 4x2km Mixed Relay===|===Mixed relay===", wt, re.I)
                if sec:
                    wt = wt[sec.start():]
            rinfo = infobox(wt)
            dist = format_dist(rinfo["distances"] or wiki_race)
            # better: first km/m in distances field or heading
            hm = re.search(r"\(([^)]+)\)", re.search(r"==[^=].*race.*==", wt, re.I).group(0) if re.search(r"==[^=].*race.*==", wt, re.I) else "")
            if rinfo["distances"]:
                dist = format_dist(rinfo["distances"].split("–")[0].split("-")[0])
            else:
                m2 = re.search(r"\(([\d.,]+\s*(?:km|m))\)", wt, re.I)
                if m2:
                    dist = format_dist(m2.group(1))
                elif "relay" in wiki_race.lower():
                    dist = "4x2km" if "2" in wt[:2000] else "Mixed Relay"

            nav = (
                '<a href="/index.html">Home</a> |\n        '
                '<a href="../world-athletics-cross-country-championships.html">World Athletics Cross Country Championships</a> |\n        '
                f'<a href="./{slug}.html">{city} {year}</a>'
            )
            page_title = f"{full} - {label} ({dist})"
            if "relay" in wiki_race.lower():
                mixed_rows = parse_mixed(wt)
                add_medals(tallies, mixed_rows)
                body = f"""    <h1>{html.escape(full)} - {html.escape(label)} <small>({html.escape(dist)})</small></h1>

    <div style="overflow-x: auto;">
        <div class="results">
{mixed_table(mixed_rows)}
        </div>
    </div>"""
                n_ind, n_team = len(mixed_rows), 0
            else:
                inds = parse_individuals(wt)
                teams = fill_team_members(parse_teams(wt), inds)
                add_medals(tallies, inds)
                add_medals(tallies, teams)
                team_h = f'Team <small>({team_note})</small>' if team_note else "Team"
                body = f"""    <h1>{html.escape(full)} - {html.escape(label)} <small>({html.escape(dist)})</small></h1>

    <div class="bookmarks">
        <p><a href="#individual">Individual</a></p>
        <p><a href="#team">Team</a></p>
    </div>

    <h2 id="individual">Individual</h2>
    <div style="overflow-x: auto;">
        <div class="results">
{ind_table(inds)}
        </div>
    </div>

    <h2 id="team">{team_h}</h2>
    <div style="overflow-x: auto;">
        <div class="results">
{team_table(teams)}
        </div>
    </div>"""
                n_ind, n_team = len(inds), len(teams)
            path = os.path.join(ROOT, folder, fname)
            open(path, "w", encoding="utf-8").write(html_page(page_title, nav, body))
            race_meta.append((fname, label, dist, gender))
            print(f"  {label}: {n_ind} ind, {n_team} teams, dist={dist}")
            summary.append((year, label, n_ind, n_team))

        # homepage
        men = [r for r in race_meta if r[3] == "men"]
        women = [r for r in race_meta if r[3] == "women"]
        mixed = [r for r in race_meta if r[3] == "mixed"]

        def disc_block(heading, items):
            if not items:
                return ""
            rows = "\n".join(
                f"""                <tr>
                    <td><a href="./{fn}">{html.escape(lab)}</a> <small>({html.escape(d)})</small></td>
                </tr>"""
                for fn, lab, d, _ in items
            )
            return f"""    <div style="overflow-x: auto;">
        <h3>{heading}</h3>
        <div class="general">
            <table>
{rows}
            </table>
        </div>
    </div>
"""

        nav = (
            '<a href="/index.html">Home</a> |\n        '
            '<a href="../world-athletics-cross-country-championships.html">World Athletics Cross Country Championships</a>'
        )
        body = f"""    <h1>{html.escape(full)}</h1>

    <div class="bookmarks">
        <p><a href="#information">Information</a></p>
        <p><a href="#disciplines">Disciplines</a></p>
        <p><a href="#medal-table">Medal Table</a></p>
    </div>

    <h2 id="information">Information</h2>
    <p>&#128197;: {html.escape(date)}</p>
    <p>&#127967;: {html.escape(venue)}</p>
    <p>&#128205;: {html.escape(city)}, <b>{html.escape(noc)}</b></p>
    <p>&#127939;: {html.escape(str(athletes))}</p>
    <p>&#127757;: {html.escape(str(nations))}</p>

    <h2 id="disciplines">Disciplines</h2>
{disc_block("Men", men)}{disc_block("Women", women)}{disc_block("Mixed", mixed)}
    <h2 id="medal-table">Medal Table</h2>
    <div style="overflow-x: auto;">
        <div class="results">
{medal_table(tallies)}
        </div>
    </div>"""
        open(os.path.join(ROOT, folder, slug + ".html"), "w", encoding="utf-8").write(
            html_page(full, nav, body)
        )
        print("  homepage", athletes, "athletes", nations, "nations")

    print("DONE", len(summary), "races")


if __name__ == "__main__":
    main()
