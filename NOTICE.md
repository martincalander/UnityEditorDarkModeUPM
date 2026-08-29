# Notices

Editor Dark Mode is an unofficial UPM wrapper maintained by Martin Calander.
The native extension is the work of Jiaqi Liu (@0x7c13), not Martin Calander.

## Bundled Native DLL

`Editor/UnityEditorDarkMode.dll` is redistributed byte-for-byte from Jiaqi
Liu's public
[UnityEditor-DarkMode v1.1 release](https://github.com/0x7c13/UnityEditor-DarkMode/releases/tag/v1.1).

```text
File: UnityEditorDarkMode.dll
Size: 79360 bytes
SHA-256: 745ddf984b84b98fd1915e64b94ef480367867de4b6363e0b4abb238b523f6b7
```

The upstream source is available in the
[UnityEditor-DarkMode repository](https://github.com/0x7c13/UnityEditor-DarkMode)
under Jiaqi Liu's MIT license. That license is reproduced in
[LICENSE.md](LICENSE.md). The license notices for incorporated
ReaperThemeHackDll and inipp code are reproduced in
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

The DLL is a preloaded, unsigned Windows x64 native plugin. Unity's UPM package
signature covers the published `.tgz` payload. It does not Authenticode-sign
the DLL and does not certify the package as Unity QA "Verified". Release
checksums cover the downloadable `.tgz` and bootstrap `.unitypackage` files.

## Unity Trademark Notice

Editor Dark Mode is not sponsored by or affiliated with Unity Technologies or
its affiliates. Unity and the Unity logo are trademarks or registered
trademarks of Unity Technologies or its affiliates in the United States and
elsewhere.
