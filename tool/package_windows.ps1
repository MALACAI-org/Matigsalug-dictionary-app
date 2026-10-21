# Run after flutter build windows --release, from any working directory.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$project = Split-Path $PSScriptRoot -Parent
$bundle = Join-Path $project 'build/windows/x64/runner/Release'
$versionLine = Get-Content (Join-Path $project 'pubspec.yaml') |
    Where-Object { $_ -match '^version: ' } | Select-Object -First 1
if ($versionLine -notmatch '^version: ([0-9]+\.[0-9]+\.[0-9]+)\+([0-9]+)$') {
    throw 'Expected a release version and build number in pubspec.yaml.'
}
$version = $Matches[1]
$buildNumber = $Matches[2]
foreach ($required in @('matigsalug_dictionary.exe', 'flutter_windows.dll', 'data/app.so',
        'data/icudtl.dat', 'data/flutter_assets/assets/dictionary.json')) {
    if (-not (Test-Path (Join-Path $bundle $required))) {
        throw "Missing release file: $required. Build Windows in release mode first."
    }
}

# Flutter's documented app-local deployment includes these Microsoft CRT DLLs.
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$visualStudio = & $vswhere -latest -products '*' `
    -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if ($LASTEXITCODE -ne 0 -or -not $visualStudio) {
    throw 'Visual Studio C++ tools were not found.'
}
$runtime = Get-ChildItem (Join-Path $visualStudio 'VC/Redist/MSVC/*/x64/Microsoft.VC*.CRT') -Directory |
    Sort-Object { [version]$_.Parent.Parent.Name } -Descending | Select-Object -First 1
if (-not $runtime) {
    throw 'Microsoft x64 Visual C++ redistributable directory was not found.'
}
foreach ($dll in @('msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll')) {
    Copy-Item (Join-Path $runtime.FullName $dll) (Join-Path $bundle $dll)
}

Copy-Item (Join-Path $project 'docs/windows-installation.md') (Join-Path $bundle 'INSTALL-WINDOWS.txt')
Copy-Item (Join-Path $project 'LICENSE') (Join-Path $bundle 'LICENSE')
Copy-Item (Join-Path $project 'third_party/FLUTTER_LICENSE') (Join-Path $bundle 'FLUTTER_LICENSE')
$revision = git -C $project rev-parse HEAD
if ($LASTEXITCODE -ne 0) {
    throw 'Could not identify the source revision.'
}
@(
    "Matigsalug Dictionary $version (build $buildNumber)",
    "Source revision: $revision",
    'Source: https://github.com/MALACAI-org/Matigsalug-dictionary-app',
    'Dictionary: https://github.com/MALACAI-org/Matigsalug-dictionary',
    'Dictionary content: CC BY-SA 4.0; see About for attribution and conversion details.',
    'https://creativecommons.org/licenses/by-sa/4.0/',
    'Noto Sans: data/flutter_assets/assets/fonts/OFL.txt',
    'Microsoft Visual C++ runtime DLLs are included for app-local deployment.',
    'https://docs.flutter.dev/platform-integration/windows/building#building-your-own-zip-file-for-windows'
) | Set-Content (Join-Path $bundle 'BUILD-INFO.txt') -Encoding utf8

$output = Join-Path $project 'build/releases'
New-Item -ItemType Directory -Path $output -Force | Out-Null
$archive = Join-Path $output "matigsalug-dictionary-$version-windows-x64.zip"
Compress-Archive -Path (Join-Path $bundle '*') -DestinationPath $archive -Force
$checksum = (Get-FileHash $archive -Algorithm SHA256).Hash.ToLowerInvariant()
"$checksum  $(Split-Path $archive -Leaf)" | Set-Content "$archive.sha256" -Encoding ascii
Write-Output "Packaged $archive"
