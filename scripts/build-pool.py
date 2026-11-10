#!/usr/bin/env python3
"""build-pool.py: owned, on-theme candidate pool for the We Are the Borg upgrade.
Pool = cards you own that have a TRK/TRC/EOE/EOC printing (Scryfall, W/U/B identity),
plus any owned nonbasic land in W/U/B/colorless from AllPrintings (any set)."""
import csv, glob, json, os, re, sqlite3, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(r"C:\MTG_Decks")
INV = VAULT / "inventory"
DECK = VAULT / "decks" / "we-are-the-borg"
SETS = {"trk", "trc", "eoe", "eoc"}
QUERY = "(e:trk or e:trc or e:eoe or e:eoc) id<=wub"
UA = {"User-Agent": "MTGDeckbuildingSession/1.0", "Accept": "application/json"}
ALIASES = {"Central Plexus Core": "The Immortal Sun"}


def load_inventory():
    path = Path(max(glob.glob(str(INV / "moxfield_haves_*.csv")), key=os.path.getmtime))
    owned = {}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            name = row["Name"].strip()
            try:
                n = int(row["Count"])
            except ValueError:
                continue
            if not name:
                continue
            d = owned.setdefault(name, {"n": 0, "sets": set(), "proxy": False})
            d["n"] += n
            d["sets"].add(row["Edition"].strip().lower())
            d["proxy"] |= row["Proxy"].strip().upper() == "TRUE"
    for name in list(owned):
        if " // " in name:
            owned.setdefault(name.split(" // ")[0], owned[name])
    print("Inventory:", path.name, "-", len(owned), "names")
    return owned


def deck_names():
    names = set()
    for line in (DECK / "decklist.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*\d+x?\s+(.+?)\s+\(", line)
        if m:
            n = m.group(1).split(" // ")[0].strip()
            names.add(n)
            if n in ALIASES:
                names.add(ALIASES[n])
    return names


def norm(c):
    faces = c.get("card_faces") or []
    if "oracle_text" in c:
        text = c["oracle_text"]
    else:
        text = " // ".join(f.get("oracle_text", "") for f in faces)
    cost = c.get("mana_cost") or (faces[0].get("mana_cost", "") if faces else "")
    return {"name": c["name"], "flavor": c.get("flavor_name"),
            "type": c.get("type_line", ""), "cost": cost,
            "text": text.replace("\n", " / "),
            "produced": c.get("produced_mana") or [],
            "gc": bool(c.get("game_changer"))}


def scryfall_pool():
    url = "https://api.scryfall.com/cards/search?" + urllib.parse.urlencode(
        {"q": QUERY, "unique": "cards", "order": "name"})
    out = {}
    while url:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r:
            data = json.load(r)
        for c in data["data"]:
            out[c["name"]] = norm(c)
        url = data.get("next_page")
        time.sleep(0.1)
    print("Scryfall pool:", len(out), "cards")
    return out


def old_lands():
    con = sqlite3.connect(INV / "AllPrintings.sqlite")
    rows = con.execute(
        "SELECT name, type, text, colorIdentity FROM cards "
        "WHERE type LIKE '%Land%' AND type NOT LIKE 'Basic%'").fetchall()
    out = {}
    for name, t, text, ci in rows:
        ids = {x.strip() for x in (ci or "").split(",") if x.strip()}
        if ids <= {"W", "U", "B"} and name not in out:
            out[name] = {"name": name, "flavor": None, "type": t or "", "cost": "",
                         "text": (text or "").replace("\n", " / "),
                         "produced": [], "gc": False}
    print("AllPrintings lands:", len(out))
    return out


def find_owned(owned, it):
    return owned.get(it["name"]) or owned.get(it["name"].split(" // ")[0]) \
        or (owned.get(it["flavor"]) if it["flavor"] else None)


def kind(it):
    if "Land" in it["type"]:
        return "lands"
    t = it["text"]
    if it["produced"] or re.search(r"\bAdd \{", t) or "basic land card" in t:
        return "ramp"
    return "spells"


def write(path, title, items):
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    lines = [f"# {title}", f"Generated {stamp}. {len(items)} owned cards.", ""]
    for it, o in sorted(items, key=lambda x: x[0]["name"]):
        label = it["name"] + (f" (aka {it['flavor']})" if it["flavor"] else "")
        inset = "in-set copy" if o["sets"] & SETS else "off-set copy only"
        flags = (" [GC]" if it["gc"] else "") + (" [proxy]" if o["proxy"] else "")
        lines.append(f"=== {label} ===  [{o['n']} owned, {inset}]{flags}")
        lines.append(f"{it['type']}  {it['cost']}".strip())
        lines.append(it["text"])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote", path, len(items))


def main():
    owned = load_inventory()
    skip = deck_names()
    pool = old_lands()
    pool.update(scryfall_pool())
    groups = {"lands": [], "ramp": [], "spells": []}
    for it in pool.values():
        if it["name"] in skip:
            continue
        o = find_owned(owned, it)
        if o:
            groups[kind(it)].append((it, o))
    write(DECK / "pool-lands.md", "Owned lands (any set)", groups["lands"])
    write(DECK / "pool-ramp.md", "Owned on-theme ramp", groups["ramp"])
    write(DECK / "pool-spells.md", "Owned on-theme spells", groups["spells"])


if __name__ == "__main__":
    main()