# Install Matigsalug Dictionary on Windows

This preview is for Windows 10 or 11 on a 64-bit Intel or AMD computer (x64).
The ZIP includes the dictionary, photos, Flutter libraries and Microsoft Visual
C++ runtime DLLs. You do not need Docker, Flutter or Visual Studio to use it.

1. Download `matigsalug-dictionary-0.5.0-windows-x64.zip` from the release page:
   https://github.com/MALACAI-org/Matigsalug-dictionary-app/releases/tag/v0.5.0
2. Right-click the ZIP and choose **Extract All**. Choose a folder you want to
   keep, such as `Documents\Matigsalug Dictionary`.
3. Open the extracted folder and double-click `matigsalug_dictionary.exe`.

Extract the whole ZIP before opening the app. Keep the executable, all DLL files
and the `data` folder together; moving only the executable will stop it working.
The dictionary and photos work offline.

For a desktop shortcut, right-click the executable, select **Show more options**
if necessary, then **Send to > Desktop (create shortcut)**. Leave the original
application folder in place.

This preview is not digitally signed, so Windows may display an
unknown-publisher or reputation warning. Windows interaction still needs testing
on users' computers; successful automated builds do not verify every feature.

If Windows reports a missing `VCRUNTIME140` or `MSVCP140` DLL, first check that
you extracted all files. If necessary, install Microsoft's latest **x64 Visual
C++ Redistributable** and try again:
https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist

To update, close the app, extract the new complete ZIP into a new folder, and
point your shortcut at the new executable. To uninstall, close the app and
delete its folder and shortcut. No separate installer is used for this preview.

Theme and linguistic-detail choices currently last for the app session.
