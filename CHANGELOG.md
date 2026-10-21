# Changelog

## 0.5.0 (build 6) — 2026-10-21

First Flutter prerelease of Matigsalug Dictionary, prioritising Android with
Ubuntu and Windows desktop targets. Submitted to Google Play's internal testing
track; review and rollout status remain in Play Console. Version 0.5 is retained
while testing and improving the app.

### Dictionary and reading

- Bundle 10,225 entries: 7,197 main dictionary entries and 3,028 student entries.
- Search Matigsalug and English offline, rank exact matches first, and filter
  by dictionary. Main entries are green, student entries amber, and English
  words purple, with colours adjusted for dark mode.
- Combine meaning introductions and glosses into readable definitions with
  emphasis on the main meaning; keep the original field layout in linguistic
  detail mode, accessible from entry pages and the main menu.
- Include 1,295 resized photos across 1,276 entries, with enlargement and zoom.
  Place photos beside their relevant definitions on wide screens and beneath
  the definitions on phones, including separate noun and verb photos for baley₁.
- Link exact words in definitions to dictionary entries, offering a choice
  when multiple entries match. Back returns to the previous entry.
- Restore left/right entry swipes, support previous/next navigation through
  filtered results, and preserve search and filters when returning to the index.
- Show formatted entry totals, counts for each dictionary, attribution and a
  MALACAI website link in About.

### Platforms and data preparation

- Preserve the published Android package `info.MLCA.MSDict` and original signing
  identity. Target Android 16 (API 36), with Android 7.0 (API 24) as the minimum.
- Add an adaptive Ubuntu desktop reading pane and document installation.
  Include a Windows target, build workflow and portable Windows ZIP with
  installation instructions and app-local Microsoft runtime libraries.
- Replace the Python converter with a reproducible import from the parallel
  dictionary repository, including optional fetching, reverse indexes, data
  checks and cached WebP photo resizing. Original source data and photos remain
  unchanged; distributed images omit EXIF metadata.
- Preserve the previous Android project and converter under `legacy/`.

### Release files

- `matigsalug-dictionary-0.5.0-build6.apk`: signed Android installation package.
- `matigsalug-dictionary-0.5.0-build6.aab`: signed Google Play upload bundle.
- `matigsalug-dictionary-0.5.0-linux-x64.tar.gz`: complete Linux application
  bundle, built on Ubuntu 26.04; GTK 3 libraries are required. Older Ubuntu
  releases have not been verified.
- `matigsalug-dictionary-0.5.0-windows-x64.zip`: complete Windows x64 preview;
  extract all files and run `matigsalug_dictionary.exe`.
- `SHA256SUMS`: checksums for the four downloads.

### Validation and remaining work

- Python converter/photo tests, bundled-data verification, Dart formatting,
  Flutter analysis and phone/desktop widget tests pass.
- GitHub Actions passes its checks and builds Android, Linux and Windows.
  A successful Windows build does not yet establish Windows runtime behaviour.
- Android emulator checks covered upgrading from the original APK and earlier
  Flutter builds, offline search and photos, entry navigation, linked words,
  dark mode and About information.
- Theme and linguistic-detail choices currently last for the app session.
  Persistent preferences, audio and polished desktop installers remain future
  work.
- Review photo associations with dictionary editors. The import report lists
  288 unmatched or ambiguous source filenames; those photos are not assigned
  to entries automatically. Linked words use exact lookup rather than inferred
  meanings.
- Windows support is preliminary and retains the Flutter scaffold icon.
- Signing keys, passwords and local Play enrollment files are excluded from
  the repository and downloadable release assets.
