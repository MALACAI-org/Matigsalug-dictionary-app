# Archived Android implementation

`android/` contains the previous Kotlin/Android project. Its conflicting app
identifiers and incomplete build migration are preserved for reference; it is
not part of the Flutter build. `MakeIndexesForDictionaries.py` is the original
converter, including its original copyright and licence notice.

The active app is in the repository root. The active converter is
`DataConverter/MakeIndexesForDictionaries.py`; its photo support uses Pillow.

The archived signed APK and the owner confirm `info.MLCA.MSDict` as the original
package name. Its certificate matches the supplied MLCA key. The old manifest's
`info.SUMALCA.MSDict` was not the packaged application ID. Check the highest
uploaded version code and signing arrangements in Play Console before publishing.
