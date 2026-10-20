#!/usr/bin/env python3
"""Build the offline Flutter dictionary from the neighbouring Toolbox repository.

Text conversion uses Python's standard library; photo preparation uses Pillow.
Run with --help for paths and source updates.
The two sources have opposite directions: main = Matigsalug headwords;
student = English headwords. Repeated fields and record order are significant.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unicodedata

from photos import prepare_photos, publish_photo_report

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ("main", "Main dictionary/MBT_Root.dic", "og", "Matigsalug"),
    ("student", "Student dictionary/Dictionary.txt", "lx", "English"),
)
# Explicit publication fields: editing notes, contributors, status and legacy
# morphology-tool metadata stay in the source repository, not the public app.
MAIN_LABELS = {
    "ph": "Pronunciation", "pn": "Pronunciation", "va": "Variant",
    "vd1": "Older-speaker variant", "vd2": "Regional variant", "ve": "Variant note",
    "ps": "Part of speech", "ms": "Main sense", "sn": "Scientific name",
    "gli": "Meaning context", "gl": "English meaning", "df": "Matigsalug definition",
    "oc": "Case frame", "oa": "Affixes", "oi": "Word form", "oz": "Word form note",
    "ex": "Matigsalug example", "tr": "English translation", "t2": "Tagalog translation",
    "t3": "Cebuano translation", "t4": "Translation", "eg": "Grammar note",
    "ec": "Cultural note", "re": "Encyclopedic note", "rf": "Reference",
    "ra": "Antonym", "rs": "Synonym", "ro": "Related meaning", "rm": "Related words",
    "co": "Comment", "sp": "Proto-Manobo form", "sc": "Semantic category",
    "ddp": "Semantic domain", "de": "English origin", "ds": "Spanish origin",
    "dc": "Cebuano origin", "mo": "Morphology", "aw": "Associated words",
}
STUDENT_LABELS = {
    "ph": "Pronunciation", "va": "Variant", "mn": "See main entry",
    "ps": "Part of speech", "sn": "Sense", "de": "Matigsalug meaning",
    "df": "Matigsalug definition", "rf": "Reference", "dv": "English explanation",
    "ng": "Grammar note", "xv": "English example", "xe": "Matigsalug translation",
    "pl": "Plural", "se": "Subentry", "cf": "Compare", "ue": "Usage",
    "pdl": "Paradigm", "pdv": "Paradigm form", "sd": "Semantic domain",
}
PREFIXES = ("pegka", "pegke", "peg-", "peg", "egka", "egke", "eg-", "eg")
PLACEHOLDERS = {"à è ì ù", "æ ə"}
SUBSCRIPT = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def plain_text(value: str) -> str:
    """Remove Toolbox display controls, preserving the words and Unicode text."""
    for old, new in (("|{emdash}", "—"), ("|{endash}", "–"), ("|{~}", " ")):
        value = value.replace(old, new)
    value = re.sub(r"\|d(.*?)\|u", lambda m: m[1].translate(SUBSCRIPT), value)
    while True:
        unwrapped = re.sub(r"\|(?:fb|u)\{([^{}]*)\}", r"\1", value)
        if unwrapped == value:
            break
        value = unwrapped
    value = re.sub(r"\bfb:", "", value)
    value = re.sub(r"\|[virub]", "", value)
    value = re.sub(r"\|(?=$|\s)", "", value)
    value = re.sub(r"(?<!\w)\+(?=\w)", "", value)
    return " ".join(unicodedata.normalize("NFC", value).split())


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFD", plain_text(value).lower().replace("æ", "ae"))
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return " ".join(value.replace("’", "'").split())


def parse_records(text: str, key: str) -> list[list[tuple[str, str]]]:
    """Read SFM, including BOMs, CRLF, empty fields and wrapped field values."""
    records: list[list[tuple[str, str]]] = []
    record: list[tuple[str, str]] = []
    for line_number, line in enumerate(text.lstrip("\ufeff").splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith("\\"):
            match = re.match(r"\\([^\s\\]+)(?:\s+(.*))?$", line)
            if not match:
                raise ValueError(f"Malformed field at line {line_number}: {line!r}")
            marker, value = match[1], (match[2] or "").strip()
            if marker == key:
                if record:
                    records.append(record)
                record = []
            if record or marker == key:
                record.append((marker, value))
        elif record:
            marker, value = record[-1]
            record[-1] = (marker, value + " " + line.strip())
        elif not line.startswith("\\_"):
            raise ValueError(f"Text before first record at line {line_number}")
    if record:
        records.append(record)
    return records


def field_marker(marker: str, source: str) -> str:
    # The suffix 1 means online-only in the student dictionary, not sense one.
    return marker[:-1] if source == "student" and marker.endswith("1") else marker


def terms(value: str) -> set[str]:
    return {v for part in re.split(r"[;,/]", value) if (v := normalize(part))}


def build_dictionary(source_repo: Path) -> dict:
    entries = []
    alphabet = set(chr(c) for c in range(0xC0, 0x250))
    indexes: dict[str, dict[str, set[int]]] = {
        "matigsalug": defaultdict(set), "english": defaultdict(set)
    }
    source_info = []
    for source, relative_path, key, language in SOURCES:
        path = source_repo / relative_path
        raw = path.read_bytes()
        alphabet.update(raw.decode("utf-8-sig"))
        records = parse_records(raw.decode("utf-8-sig"), key)
        labels = MAIN_LABELS if source == "main" else STUDENT_LABELS
        homonyms: Counter = Counter()
        ignored: Counter = Counter()
        skipped = published = 0
        for record in records:
            headword = record[0][1].strip()
            if not headword:
                raise ValueError(f"Empty headword in {relative_path}")
            if headword.startswith("~") or (source == "main" and headword.startswith("z.")):
                skipped += 1
                continue
            fields = [(field_marker(m, source), t) for m, t in record
                      if t.strip() not in PLACEHOLDERS]
            display = next((plain_text(t) for m, t in fields if m == "lx" and t), headword)
            hm = next((t for m, t in fields if m == "hm"), "")
            if hm:
                display += hm.translate(SUBSCRIPT)
            homonyms[headword] += 1
            entry_id = f"{source}:{headword}:{homonyms[headword]}"
            detail = []
            main_sense = 0
            for marker, text in fields:
                if marker == 'ms' and source == 'main':
                    main_sense += 1
                    text = text or str(main_sense)
                if marker in {'dc', 'ds'} and source == 'main':
                    text = text or 'Borrowed word'
                if marker in labels and text.strip():
                    detail.append({"marker": marker, "label": labels[marker], "text": plain_text(text)})
                elif marker not in {key, "lx", "hm"}:
                    ignored[marker] += 1
            if not detail:
                skipped += 1
                continue
            meaning_marker = "gl" if source == "main" else "de"
            meanings = list(dict.fromkeys(f["text"] for f in detail if f["marker"] == meaning_marker))
            entry = {
                "id": entry_id, "source": source, "headword": plain_text(display),
                "language": language, "summary": "; ".join(meanings[:3]), "fields": detail,
            }
            index = len(entries)
            entries.append(entry)
            published += 1
            main_language = "matigsalug" if source == "main" else "english"
            indexes[main_language][normalize(headword)].add(index)
            indexes[main_language][normalize(display)].add(index)
            for marker, value in fields:
                if source == "main":
                    language_key = "english" if marker == "ie" else "matigsalug"
                    include = marker in {"ie", "oi", "va", "vd1", "vd2"}
                else:
                    language_key = "matigsalug" if marker == "re" else "english"
                    include = marker in {"re", "se", "va"}
                if not include:
                    continue
                for term in terms(value):
                    indexes[language_key][term].add(index)
                    if language_key == "matigsalug" and marker == "re":
                        for prefix in PREFIXES:
                            if term.startswith(prefix) and len(term) > len(prefix) + 2:
                                indexes[language_key][term[len(prefix):]].add(index)
        source_info.append({
            "id": source, "path": relative_path,
            "sha256": hashlib.sha256(raw).hexdigest(), "records": len(records),
            "entries": published, "excludedRecords": skipped,
            "omittedFields": dict(sorted(ignored.items())),
        })
    if not entries or any(s["entries"] == 0 for s in source_info):
        raise ValueError("Both dictionaries must contain public entries")
    return {
        "schemaVersion": 1,
        "attribution": {
            "title": "Matigsalug main and student dictionaries",
            "contributors": "Dick & Betty Elkins, Peter Wang, Robert Hunt, Jeffrey McGriff, Naomi Keith, and Matigsalug contributors; SIL Philippines; MLCA / SUMALCA / MALACAI",
            "sourceUrl": "https://github.com/MALACAI-org/Matigsalug-dictionary",
            "license": "CC BY-SA 4.0", "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
            "changes": "Converted from Toolbox records; display markup simplified; search indexes generated.",
        },
        "sources": source_info, "entries": entries,
        # Ship the same Unicode folding rules used by the index builder, so
        # Dart needs no platform-specific Unicode library for accent-free lookup.
        "searchReplacements": {c: normalize(c) for c in sorted(alphabet)
                               if not c.isspace() and c != normalize(c)},
        "indexes": {lang: [[term, sorted(ids)] for term, ids in sorted(index.items())]
                    for lang, index in indexes.items()},
    }


def update_source(source_repo: Path) -> None:
    """An explicit opt-in update; never discard local dictionary edits."""
    result = subprocess.run(["git", "-C", str(source_repo), "status", "--porcelain"],
                            check=True, capture_output=True, text=True)
    if result.stdout.strip():
        raise ValueError("Source repository has local changes; commit/stash them before --fetch")
    subprocess.run(["git", "-C", str(source_repo), "pull", "--ff-only"], check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", type=Path, default=ROOT.parent / "Matigsalug-dictionary")
    parser.add_argument("--output", type=Path, default=ROOT / "assets/dictionary.json")
    parser.add_argument("--fetch", action="store_true", help="First update a clean source checkout with git pull --ff-only")
    parser.add_argument("--check", action="store_true", help="Verify the bundled data matches these sources without writing")
    parser.add_argument("--photo-size", type=int, default=960, help="Maximum photo edge in pixels (default: 960)")
    parser.add_argument("--photo-quality", type=int, default=75, help="WebP photo quality, 1–100 (default: 75)")
    args = parser.parse_args(argv)
    try:
        if args.photo_size < 64 or args.photo_size > 4096 or not 1 <= args.photo_quality <= 100:
            raise ValueError("Photo size must be 64–4096 and quality must be 1–100")
        if args.fetch:
            update_source(args.source_repo)
        data = build_dictionary(args.source_repo)
        report = prepare_photos(data, args.source_repo, args.output, normalize,
                                check=args.check, size=args.photo_size, quality=args.photo_quality)
        encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
        if args.check:
            if not args.output.exists() or args.output.read_text(encoding="utf-8") != encoded:
                parser.exit(1, "Bundled dictionary is out of date; run the converter without --check.\n")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            # Replace only after both sources have parsed and all indexes exist.
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=args.output.parent, delete=False) as handle:
                temp_path = Path(handle.name)
                try:
                    handle.write(encoded)
                except BaseException:
                    temp_path.unlink(missing_ok=True)
                    raise
            try:
                os.replace(temp_path, args.output)
            finally:
                temp_path.unlink(missing_ok=True)
        for source in data["sources"]:
            print(f"{source['id']}: {source['entries']:,} entries; {source['excludedRecords']} working/empty records excluded")
        publish_photo_report(report, args.output, check=args.check)
        if report:
            print(f"Photos: {report['images']:,} images across {report['entries']:,} entries; "
                  f"{report['bundledBytes'] / 1_000_000:.1f} MB bundled; {len(report['skipped']):,} files need matching review")
        print(f"{'Verified' if args.check else 'Wrote'} {args.output} ({len(encoded.encode('utf-8')):,} bytes)")
        return 0
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Dictionary conversion failed: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
