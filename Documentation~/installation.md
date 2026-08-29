# Installation and Compatibility

Editor Dark Mode is a Windows-only native Unity Editor extension. Choose the
installation method that matches how you want to receive and verify updates.

## Requirements

- Windows 10 version 1903 or newer, or Windows 11.
- An x64 Unity Editor.
- Unity 2021.3.37f1 or newer.
- An Editor restart after installation, update, or removal.

The package can resolve on macOS and Linux, but Unity's plugin importer excludes
the native DLL on those platforms. It provides no dark-mode functionality
there and does not support Windows player builds.

## Installation Methods

| Method | Network required | UPM package signature | Version pinning |
| --- | :---: | :---: | :---: |
| Unity bootstrap `.unitypackage` | Yes during the confirmed install step | Installs the signed OpenUPM package | Exact `1.1.1` |
| OpenUPM | Yes | Yes | Registry dependency |
| GitHub Release `.tgz` | Only to download | Yes | Exact archive |
| Git URL | Yes | No | Exact tag when `#v1.1.1` is present |
| Local folder | No after checkout | No | Local checkout |

## Unity Bootstrap Installer

1. Download
   [`EditorDarkModeInstaller-1.1.1.unitypackage`](https://github.com/martincalander/UnityEditorDarkModeUPM/releases/download/v1.1.1/EditorDarkModeInstaller-1.1.1.unitypackage)
   and `SHA256SUMS` from the
   [`v1.1.1` release](https://github.com/martincalander/UnityEditorDarkModeUPM/releases/tag/v1.1.1).
2. Verify the downloaded checksum as described in
   [Verify Release Checksums](#verify-release-checksums).
3. In Unity, choose **Assets > Import Package > Custom Package** and import all
   bootstrap files.
4. Review the exact installation plan shown by the bootstrap.
5. Choose **Install 1.1.1**. This is the step that contacts OpenUPM and changes
   the project's package manifest.
6. Wait for the bootstrap to verify the exact package version and registry
   source, and to remove its own unchanged files.
7. Close and reopen the Editor so the preloaded native DLL can attach.

The `.unitypackage` is checksummed but is not itself a signed UPM archive. Its
purpose is to configure the exact OpenUPM scope and install the signed UPM
package. It does not bundle a second copy of `UnityEditorDarkMode.dll`.
The bootstrap refuses to modify a project when imported on macOS, Linux, a
non-x64 Editor, or an unsupported Unity version.

## OpenUPM (Recommended)

### OpenUPM CLI

From the Unity project root, run:

```bash
openupm add com.martincalander.editordarkmode
```

Restart the Editor after Package Manager finishes.

### Manual Scoped Registry

Merge the following registry into `Packages/manifest.json`. Preserve other
registries, scopes, and dependencies already in the project.

```json
{
  "scopedRegistries": [
    {
      "name": "OpenUPM",
      "url": "https://package.openupm.com",
      "scopes": [
        "com.martincalander.editordarkmode"
      ]
    }
  ],
  "dependencies": {
    "com.martincalander.editordarkmode": "1.1.1"
  }
}
```

Alternatively, after adding the scoped registry, open
**Window > Package Management > Package Manager**, choose
**+ > Install package by name**, and enter:

```text
com.martincalander.editordarkmode
```

Use `1.1.1` as the version when Unity offers a version field.

## Signed GitHub Release Tarball

1. Download
   [`com.martincalander.editordarkmode-1.1.1.tgz`](https://github.com/martincalander/UnityEditorDarkModeUPM/releases/download/v1.1.1/com.martincalander.editordarkmode-1.1.1.tgz)
   and `SHA256SUMS` from the `v1.1.1` release.
2. Verify its checksum.
3. In Package Manager, choose **+ > Install package from tarball** and select
   the `.tgz` file.
4. Restart the Editor.

The tarball contains Unity's UPM signing attestation. Compatible Unity versions
can validate that signature. Older supported Editors can install the same
archive but might not display package-signature information in their UI.

## Pinned Git URL

In Package Manager, choose **+ > Install package from git URL** and enter:

```text
https://github.com/martincalander/UnityEditorDarkModeUPM.git#v1.1.1
```

The tag is important. Without `#v1.1.1`, the dependency follows the mutable
`main` branch. Git dependencies install repository source and do not contain
the UPM signing attestation from the release tarball.

## Local Folder for Development

Clone the repository outside the Unity project, check out the intended tag or
branch, then choose **+ > Install package from disk** in Package Manager and
select its `package.json`.

You can also add an absolute file dependency manually:

```json
{
  "dependencies": {
    "com.martincalander.editordarkmode": "file:/absolute/path/to/UnityEditorDarkModeUPM"
  }
}
```

Local folder installs are mutable development inputs. They are not signed
release artifacts.

## Verify Release Checksums

Download both release artifacts and `SHA256SUMS` into the same directory. On
macOS or Linux, run:

```bash
shasum -a 256 -c SHA256SUMS
```

On Windows PowerShell, compare each value in `SHA256SUMS` with:

```powershell
Get-FileHash -Algorithm SHA256 .\EditorDarkModeInstaller-1.1.1.unitypackage
Get-FileHash -Algorithm SHA256 .\com.martincalander.editordarkmode-1.1.1.tgz
```

The bundled native DLL has this independently pinned upstream hash:

```text
745ddf984b84b98fd1915e64b94ef480367867de4b6363e0b4abb238b523f6b7
```

UPM signing authenticates the package archive and detects archive tampering.
Checksums authenticate downloads only after you obtain the expected checksum
from the GitHub Release. Neither mechanism makes the unsigned native DLL an
Authenticode-signed Windows binary.

## Upgrade

- OpenUPM installations can be updated through Package Manager or by rerunning
  `openupm add com.martincalander.editordarkmode` after a newer release.
- Tarball, Git URL, and local-folder installations must be updated through the
  same method used to install them.
- Restart the Editor after every update.

Never edit files in Unity's package cache. Updates replace cached package
contents, including `UnityEditorDarkMode.dll.ini`.

## Remove

Remove `com.martincalander.editordarkmode` from Package Manager or from the
project manifest, then close and reopen the Editor. Windows can keep the DLL
locked until the Unity process that loaded it exits.

If the bootstrap stopped before completing, remove only its
`Assets/EditorDarkModeInstaller` folder after reviewing any recovery message it
left. Do not delete unrelated `Assets` or `Packages` content.

## Troubleshooting

### The Editor Did Not Change

Confirm all of the following:

- the operating system is a supported Windows release;
- the Unity Editor process is x64;
- the installed package version is visible in Package Manager;
- the Editor was fully closed and reopened after installation.

The package intentionally has no visual effect on macOS or Linux.

### The Native Plugin Could Not Load

Inspect the Unity Editor log for the exact native loader error. The DLL depends
on standard Windows system libraries and the Microsoft Visual C++ 14 runtime.
Install current Windows updates and the supported Microsoft Visual C++ x64
redistributable before retrying. Do not download replacement runtime DLLs from
untrusted websites.

### OpenUPM Cannot Find the Package

Confirm that the registry URL is exactly `https://package.openupm.com` and that
the scoped registry includes `com.martincalander.editordarkmode`. Remove stale
references to the historical `com.0x7c13.darkmode` package ID.

### Removal Left the Editor Dark

Confirm the package is absent from `Packages/manifest.json`, then fully exit all
Unity Editor processes for that project and reopen it. The native DLL cannot be
unloaded safely from a running Editor process.

## Trust and Attribution

The complete provenance, signature boundaries, copyright, and third-party
license notices are in [NOTICE.md](../NOTICE.md),
[LICENSE.md](../LICENSE.md), and
[THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md).
