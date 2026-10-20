# Matigsalug Dictionary

An offline Flutter dictionary for Android, with Linux (Ubuntu) and Windows
desktop targets. Android is the first release priority.

Version **0.5.0 (build 6)** is the first Flutter prerelease and has been submitted
to Google Play's internal testing track. Submission does not indicate approval
or public availability. Downloads and release details are available under
[GitHub Releases](https://github.com/MALACAI-org/Matigsalug-dictionary-app/releases)
and in [CHANGELOG.md](CHANGELOG.md).

The app includes Matigsalug and English prefix search, exact-match ranking,
main/student dictionary filters, alphabetical browsing, selectable desktop entry text,
optional linguistic detail, light/dark themes, and an adaptive desktop reading
pane. Ctrl+F focuses search on desktop. Text follows the system font-size setting.
Main entries use green, student entries yellow/amber, and English words purple,
with separate palettes for light and dark mode. The entry-page linguistic switch
changes between the normal reading view and the detailed field-by-field layout,
including word forms, affixes, case frames, semantic categories and word history.
It shows how many extra fields are available. The choice is shared with the main
menu.

On a phone, swipe left/right or use the previous/next buttons to move through
the current filtered results, including results beyond the first 100 displayed
in the index. Returning to the index keeps the query and filters.
The dictionary and its photos are bundled for offline use. Tap a photo to enlarge
it and pinch to zoom; use the photo arrows to see additional images.

### Reading entries

Normal mode groups definitions by sense and part of speech, combines a main
dictionary `gli` introduction with its `gl` meaning (for example, “for someone
**to build a house**”), and keeps examples beside their translations. The main
meaning is larger and bold. The original converter assembled these glosses in
`legacy/MakeIndexesForDictionaries.py`; the Kotlin styles in
`legacy/android/app/src/main/kotlin/info/mlca/ms_dict/DisplayEntryActivity.kt`
emphasized them and hid inflection fields in simple mode. The Flutter reading
view follows that approach while keeping all published fields in detailed mode.
In the main dictionary `sn` means scientific name; in the student dictionary it
is a sense number.

Photos named for an inflected form are placed with the section containing that
form. Root-named photos normally accompany the first/root definition. For
`baley₁`, the two `baley1` photos accompany the noun and `egbebaley` accompanies
the building verb. Wide layouts put photos to the right; narrow layouts put
them after the corresponding definition and before examples. Photos whose
section cannot be identified uniquely remain under “Other photos for this
entry” for review.

Dotted-underlined words in definitions and cross-references are internal links.
They use exact, whole-word matches in the appropriate language; common English
function words and links back to the current entry are omitted. A single match
opens directly; multiple matches offer a choice with dictionary labels and
meaning summaries. Links support touch, mouse and keyboard focus. Back returns
to the previous entry without changing the original search or filters. This is
word lookup, not automatic identification of the intended sense in a sentence.

## Development

Install the stable Flutter SDK and run `flutter doctor`. The project requires
Flutter 3.47.7 / Dart 3.13.5 or newer. CI pins Flutter 3.47.7; retain the committed
dependency lockfile when reproducing a build. Android SDK 36 and command-line tools are
required for Android. Linux builds also need Clang, CMake, Ninja, pkg-config and
GTK 3 development libraries. Windows builds need Windows and Visual Studio's
Desktop development with C++ workload.

From this repository:

```bash
flutter pub get
flutter devices
flutter run -d <android-device-id>
flutter run -d linux
# On Windows:
flutter run -d windows
```

## Refreshing the dictionary

Keep the source repository beside this one:

```text
MALACAI-org/
  Matigsalug-dictionary/
    Main dictionary/MBT_Root.dic
    Student dictionary/Dictionary.txt
    Dictionary photos/
  Matigsalug-dictionary-app/
```

Use Python 3.10+ with Pillow for resizing photos. No BibleOrgSys installation is
needed. Paths are resolved relative to the script, not the current directory.
For an isolated Python environment on Ubuntu:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r DataConverter/requirements.txt
source .venv/bin/activate
```

```bash
python3 DataConverter/MakeIndexesForDictionaries.py
python3 DataConverter/MakeIndexesForDictionaries.py --check
# Explicitly fetch upstream changes before rebuilding (clean checkout required):
python3 DataConverter/MakeIndexesForDictionaries.py --fetch
# Or use a different checkout:
python3 DataConverter/MakeIndexesForDictionaries.py --source-repo /path/to/Matigsalug-dictionary
```

The converter writes `assets/dictionary.json` atomically after reading both
sources and preparing the photos. Commit it, `assets/photos/` and
`assets/dictionary-photos.json` with data changes so app builds do not depend on a
network connection to the source repository. `--fetch` runs `git pull --ff-only`
in the source checkout and refuses to proceed if it has uncommitted changes.
The default command only reads the checkout; it never edits the original files.

The main dictionary has Matigsalug headwords and English `ie` reverse-index
fields. The student dictionary has English headwords and Matigsalug `re` fields.
Online-only student fields (suffix `1`) are included. Homonyms remain separate;
repeated fields, examples and their order are retained. Tilde working records
and main-dictionary `z.` records are excluded. Unfinished records containing only
vowel/pronunciation placeholders are also excluded. Editorial notes, editing status
and old morphology-tool metadata are not published. Explicit field maps in the
converter document the publication choices, and each source's omitted-field
counts are included in the output for review.

Toolbox emphasis controls are simplified to plain text; homonym subscripts and
accented display text are retained. Search is case- and accent-insensitive, with
the same character-folding map generated for Python and Dart. Main word forms
and variants are searchable. The student's reverse index also retains the
legacy prefix-stripping aliases. This is dictionary prefix lookup, not fuzzy
matching or full-text searching of all examples.

The data schema is versioned. It contains source SHA-256 checksums, attribution,
ordered entry fields and sorted search indexes referring to entry positions.
The app validates the schema and references, parses data off the UI thread, and
uses binary search to find matching index ranges. A future data format change
must update both the converter and the reader together.

### Photos

The converter looks in `Dictionary photos/`, including its `New/` subfolder.
It matches filenames to Matigsalug headwords or indexed word forms, prioritising
exact headwords. Explicit numbered homonyms such as `baley1` match `baley₁`;
extra-shot suffixes such as `.1` or `-1` are recognised separately. Ambiguous
homonyms and unmatched filenames are listed for review in
`assets/dictionary-photos.json`, rather than assigned to a guessed meaning.
Unambiguous reverse-index matches can also illustrate student entries.

Copies are oriented correctly, resized to a maximum edge of 960 pixels without
upscaling, and saved as WebP at quality 75. EXIF metadata is omitted. Originals
are unchanged. Identical encoded images share one asset, and unchanged images
are cached; changing a source photo or encoder settings regenerates its copy.
Only obsolete generated photo assets are removed after a successful refresh.
`--check` verifies photo files as well as the dictionary without writing.

Override size/quality with `--photo-size 800 --photo-quality 70` if a smaller
download is preferred. The current prepared set contains 1,295 distinct images
across 1,276 entries, occupying about 104 MB. The original collection has 1,602
photos totalling about 2.57 GB; videos are not included. There are 288 filenames
needing matching review. Matching follows the source names, so the associations
should also be reviewed by a dictionary editor before publishing.

## Checks and builds

```bash
python3 -m unittest discover -s DataConverter -p 'test_*.py' -v
python3 DataConverter/MakeIndexesForDictionaries.py --check
dart format --output=none --set-exit-if-changed lib test tool
flutter analyze
flutter test
flutter build apk --debug
flutter build linux --release
# On Windows:
flutter build windows --release
```

GitHub Actions runs Python/Dart/widget checks and builds Android debug, Linux
and Windows. Builds use the committed offline data; checking it against the
source checkout is a separate local step when refreshing content.

To render phone and desktop previews using the bundled dictionary, run
`flutter test tool/capture_preview.dart`. Images are saved in `build/previews/`.

## Ubuntu installation

For a release download, extract `matigsalug-dictionary-0.5.0-linux-x64.tar.gz`
and run `matigsalug_dictionary` inside the extracted folder. Keep its `data/`
and `lib/` folders alongside the executable. The archive includes its own
installation notes. This x64 build was produced on Ubuntu 26.04; compatibility
with older Ubuntu releases has not been verified. GTK 3 runtime libraries are
required.

Run these commands from the repository's top-level directory. They use the
x64 Linux release bundle. If it has not been built yet, first run:

```bash
flutter build linux --release
```

To try the existing build immediately:

```bash
./build/linux/x64/release/bundle/matigsalug_dictionary
```

To install a copy for your account and add it to Ubuntu's applications menu,
paste the following into a terminal opened in the repository directory:

```bash
dict_app_dir="$HOME/.local/share/matigsalug-dictionary"
dict_project="$PWD"

mkdir -p "$dict_app_dir" "$HOME/.local/share/applications"
cp -a "$dict_project/build/linux/x64/release/bundle/." "$dict_app_dir/"
cp "$dict_project/android/app/src/main/res/drawable/ic_launcher.png" "$dict_app_dir/icon.png"

cat > "$HOME/.local/share/applications/org.malacai.matigsalug_dictionary.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Matigsalug Dictionary
Comment=Offline Matigsalug and English dictionary
Exec="$dict_app_dir/matigsalug_dictionary"
Icon=$dict_app_dir/icon.png
Terminal=false
Categories=Education;
EOF
```

Press **Super** (the Windows key), search for **Matigsalug Dictionary**, and
open it. This installation needs no administrator password. The dictionary and
photos are included and work offline. Keep the executable, `data/` and `lib/`
together if moving the app; copying only the executable is insufficient.

To update an installed copy, close the app, build the new Linux release, and
rerun the installation block above from the repository directory. Rebuilding
alone does not update the installed copy.

## Android release work

The archived signed APK confirms the application ID `info.MLCA.MSDict`
(version 0.22, code 1); the old Gradle source had reached version 0.24, code 3.
The stale manifest's `info.SUMALCA.MSDict` was not the packaged application ID.
Confirm the signing arrangements and highest uploaded version code in Play
Console before making a release. Debug builds use a `.dev` suffix to install
separately. Android retains the original dictionary launcher icon.

Release configuration belongs in the ignored `android/key.properties`; see
`android/key.properties.example`. Release builds require an explicit published
application ID and a real upload/signing key. Never commit passwords or keys.
The original MLCA signing certificate has SHA-256 fingerprint
`73767c2788ae2d300cb6427809645efeb15fb0436b91ecf6204739dd230905f2`.
The local key supplied for this migration matches that certificate; the keystore
remains outside this repository. Local signing configuration is not committed.
The current development version is `0.5.0+6` (shown as `0.5` in About).
The internal build number increases with each test release so this APK can
update earlier 0.5 and 1.0.0 test builds. Before publishing, it must exceed every
version already uploaded to the old listing.

After configuring signing:

```bash
flutter build apk --release
flutter build appbundle --release
```

The APK is under `build/app/outputs/flutter-apk/`; the Play app bundle is under
`build/app/outputs/bundle/release/`. Building does not upload to Google Play.

The initial migration was checked on Android 16: the signed Flutter APK installed
over the archived 0.22 APK, launched, and searched the bundled dictionary in
airplane mode. Linux release builds and phone/desktop widget checks pass.
GitHub Actions also verifies the Windows build; Windows runtime behaviour has
not yet been tested.

Version 0.5 also passed an emulator upgrade from the 1.0.0 test build, offline
photo display/enlargement, swiping between entries, the shared linguistic switch,
dark-mode About counts and the MALACAI browser link. The signed universal APK
is about 158.8 MB (previously 53.2 MB); the app bundle is about 158.0 MB. The photo converter
and app passed 15 Python checks. Entry-layout checks cover sense-specific photos,
joined meanings, exact links, ambiguous choices, return navigation and text scaling.
Build 6 passed all 34 Flutter checks and an Android emulator upgrade from build 5;
linked-word choices and Back navigation were also verified in airplane mode.

Before promoting a build to public production, test on Android hardware and
test updating an installation of
the published app, confirm settings migration needs, review entry rendering
with speakers, and complete the Play listing, privacy/data-safety and content
rating declarations. Theme and linguistic-detail choices currently last for
the app session. Audio, persistent preferences and polished desktop installers
are subsequent work. The project does not yet include production signing keys.
Signing passwords, keystores, `android/key.properties`, and local Play App
Signing enrollment files are excluded from Git and release downloads. In
particular, keep `play-signing/`, `pepk.jar`, and `encryption_public_key.pem`
local; they are not application assets.
Windows currently retains the Flutter scaffold icon; replace it before publishing
a Windows package.

The previous Kotlin project and converter are preserved in `legacy/` for
comparison. They are not used by Flutter.

## MS dictionary
The Matigsalug dictionary was initially developed by members of [SIL Philippines](https://philippines.sil.org), including Dick & Betty Elkins, Peter Wang, Robert Hunt, Jeffrey McGriff, and Naomi Keith. It started as a shoebox full of index cards, then became computerized onto floppy disks and entered into the Shoebox software which went on to evolve into [Toolbox](https://software.sil.org/toolbox).

In later years, Robert and Naomi supervised further development of the lexicon under the auspices of MLCA, Inc, which evolved into SUMALCA Inc. and now [MALACAI](https://MALACAI.org): Matigsalug Language Christian Association, Inc.

## Licences

The repository's application licence is in `LICENSE` (MPL 2.0). The archived
converter retains its original GPL notice. Dictionary content is separately
licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/),
as declared by the source repository. The converted data and the app's About
dialog retain attribution, the source link, the content licence and a description
of conversion changes.

Noto Sans is bundled for consistent phonetic symbols and homonym subscripts;
its SIL Open Font License notice is in `assets/fonts/OFL.txt`. Flutter's platform
runner templates retain their BSD licence in `third_party/FLUTTER_LICENSE`.
