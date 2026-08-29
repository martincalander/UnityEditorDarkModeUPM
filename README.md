# UnityEditorDarkModeUPM

This package loads the original native Windows DLL in the Unity Editor to darken the title bar, menu bar, and context menus. It works only on Windows 10 1903+ and Windows 11; restart Unity after installing it.

![Unity Editor Dark Mode](Documentation~/screenshot.jpg)

## Install with UPM

In Unity, open **Window > Package Manager**, choose **+ > Install package from Git URL**, and enter:

```text
https://github.com/martincalander/UnityEditorDarkModeUPM.git
```

Alternatively, install the creator's original [Unity Asset Store package](https://assetstore.unity.com/packages/tools/gui/darkmode-for-unity-editor-on-windows-281842).

The original [UnityEditor-DarkMode](https://github.com/0x7c13/UnityEditor-DarkMode) project and implementation are by [Jiaqi Liu (@0x7c13)](https://github.com/0x7c13). This repository's only change is packaging his work for UPM.
