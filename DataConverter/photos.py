"""Prepare offline photographs; never modify the source collection."""

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import re
import tempfile

SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def match_photo(stem, entries, indexes, headwords, normalize):
    """Prefer exact headwords, then indexed forms; don't guess homonym senses."""
    candidates = list(dict.fromkeys([stem.strip(), re.sub(r"[.\- ]\d+$", "", stem).strip()]))
    for caption in candidates:
        term = normalize(caption)
        homonym = re.sub(r"\d+$", lambda m: m[0].translate(SUBSCRIPTS), term)
        exact = headwords.get(term, [])
        explicit_homonym = False
        if not exact and homonym != term:
            exact = headwords.get(homonym, [])
            explicit_homonym = bool(exact)
        matches = exact or indexes.get(term, [])
        if not matches:
            continue
        main = [i for i in matches if entries[i]["source"] == "main"]
        if len(main) > 1:
            case_exact = [i for i in main if entries[i]["headword"] == caption]
            if len(case_exact) == 1:
                main = case_exact
            else:
                return [], caption, "ambiguous homonym or word form"
        # A numbered homonym photo cannot safely be assigned to an unnumbered
        # reverse index term (which might refer to a different sense).
        students = [] if explicit_homonym else [
            i for i in indexes.get(term, []) if entries[i]["source"] == "student"
        ]
        if explicit_homonym and main:
            caption = entries[main[0]]["headword"]
        return sorted(set(main + students)), caption, None
    return [], stem, "no matching headword or indexed Matigsalug form"


def _atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(content)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare_photos(data, source_repo, output, normalize, *, check=False, size=960, quality=75):
    """Return a reproducible report; add photo references to the dictionary.

    Cache hits require unchanged source bytes, encoder settings and output hash.
    New assets have content-derived names, so failures cannot damage the old
    dictionary's photos. The caller publishes JSON only after all photos succeed.
    """
    root = source_repo / "Dictionary photos"
    report_path = output.with_name(output.stem + "-photos.json")
    if not root.is_dir():
        if report_path.exists():
            raise ValueError(f"Previously used photo folder is missing: {root}")
        return None
    paths = sorted(
        (p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}),
        # Prefer the primary picture (word.jpg) before extra shots (word.1.jpg).
        key=lambda p: (len(p.relative_to(root).parts),
                       re.sub(r"[.\- ]\d+$", "", p.stem).casefold(),
                       bool(re.search(r"[.\- ]\d+$", p.stem)), p.as_posix()),
    )
    try:
        from PIL import Image, ImageOps, features, __version__ as pillow_version
    except ImportError as error:
        raise ValueError("Photos require Pillow: pip install -r DataConverter/requirements.txt") from error
    if not features.check("webp"):
        raise ValueError("This Pillow installation does not support WebP")
    settings = {"maxDimension": size, "quality": quality, "format": "webp",
                "pillowVersion": pillow_version, "webpVersion": features.version("webp")}
    cache = {}
    if report_path.exists():
        previous = json.loads(report_path.read_text(encoding="utf-8"))
        if previous.get("settings") == settings:
            cache = {item["source"]: item for item in previous.get("files", [])}
    entries = data["entries"]
    indexes = dict(data["indexes"]["matigsalug"])
    headwords = defaultdict(list)
    for i, entry in enumerate(entries):
        if entry["source"] == "main":
            headwords[normalize(entry["headword"])].append(i)
    plans, skipped = [], []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        ids, caption, reason = match_photo(path.stem, entries, indexes, headwords, normalize)
        if not ids:
            skipped.append({"source": relative, "reason": reason})
        else:
            plans.append((path, relative, ids, caption))

    def convert(plan):
        path, relative, ids, caption = plan
        raw = path.read_bytes()
        source_hash = hashlib.sha256(raw).hexdigest()
        cached = cache.get(relative)
        if cached and cached.get("sourceSha256") == source_hash:
            asset = cached.get("asset", "")
            if re.fullmatch(r"assets/photos/[0-9a-f]{64}\.webp", asset):
                target = output.parent / "photos" / Path(asset).name
                if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == cached.get("sha256"):
                    return {**cached, "entries": ids, "caption": caption}, None
        try:
            with Image.open(BytesIO(raw)) as original:
                picture = ImageOps.exif_transpose(original).convert("RGB")
                picture.thumbnail((size, size), Image.Resampling.LANCZOS)
                encoded = BytesIO()
                # Deliberately omit EXIF/location metadata from distributable copies.
                picture.save(encoded, format="WEBP", quality=quality, method=4)
                width, height = picture.size
                picture.close()
        except (OSError, ValueError) as error:
            raise ValueError(f"Cannot prepare photo {relative}: {error}") from error
        content = encoded.getvalue()
        digest = hashlib.sha256(content).hexdigest()
        filename = f"{digest}.webp"
        target = output.parent / "photos" / filename
        info = {
            "source": relative, "sourceSha256": source_hash, "sourceBytes": len(raw),
            "asset": f"assets/photos/{filename}", "sha256": digest,
            "bytes": len(content), "width": width, "height": height,
            "entries": ids, "caption": caption,
        }
        if check:
            if not target.exists() or target.read_bytes() != content:
                raise ValueError(f"Bundled photo is missing or stale: {relative}; run the converter without --check")
        else:
            _atomic_write(target, content)
        return info, content

    with ThreadPoolExecutor(max_workers=4) as pool:
        # map preserves source-path order regardless of worker completion order.
        files = [info for info, _ in pool.map(convert, plans)]
    unique = {}
    for info in files:
        unique[info["asset"]] = info["bytes"]
        for index in info["entries"]:
            photos = entries[index].setdefault("photos", [])
            if not any(p["asset"] == info["asset"] for p in photos):
                photos.append({k: info[k] for k in ("asset", "caption", "width", "height")})
    data["photos"] = {
        "images": len(unique), "entries": sum(bool(e.get("photos")) for e in entries),
        "bundledBytes": sum(unique.values()), "maxDimension": size, "quality": quality,
    }
    data["attribution"]["changes"] += " Photographs matched by headword or indexed word form, resized and converted to WebP; photo metadata removed."
    return {
        "settings": settings, "sourcePhotos": len(paths), "matchedFiles": len(files),
        "sourceBytes": sum(p.stat().st_size for p in paths),
        **data["photos"], "files": files, "skipped": skipped,
    }


def publish_photo_report(report, output, *, check=False):
    if report is None:
        return
    report_path = output.with_name(output.stem + "-photos.json")
    content = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if check:
        if not report_path.exists() or report_path.read_bytes() != content:
            raise ValueError("Photo report is stale; run the converter without --check")
    else:
        _atomic_write(report_path, content)
        # Only retire our own content-addressed files, after publishing the new data.
        active = {Path(item["asset"]).name for item in report["files"]}
        for path in (output.parent / "photos").glob("*.webp"):
            if re.fullmatch(r"[0-9a-f]{64}\.webp", path.name) and path.name not in active:
                path.unlink()
