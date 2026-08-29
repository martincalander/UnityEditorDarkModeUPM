#!/usr/bin/env python3
"""Validate the Editor Dark Mode UPM repository and release metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[2]
ERRORS: list[str] = []

PACKAGE_NAME = "com.martincalander.editordarkmode"
DISPLAY_NAME = "Editor Dark Mode"
REPOSITORY_URL = "https://github.com/martincalander/UnityEditorDarkModeUPM"
DLL_SHA256 = "745ddf984b84b98fd1915e64b94ef480367867de4b6363e0b4abb238b523f6b7"
CONFIG_SHA256 = "e2cbd6588ce3dd297931019b5fddbf3f1d9a7cdddbe03fcf145df1c9f8880625"
PLUGIN_META_SHA256 = "a712d0c3d59508a9c9a00205973e2231f685a4efc7e8f89dcca14788eef4c492"

SEMVER_PATTERN = re.compile(
    r"^(?P<major>0|[1-9][0-9]*)\."
    r"(?P<minor>0|[1-9][0-9]*)\."
    r"(?P<patch>0|[1-9][0-9]*)"
    r"(?:-(?P<prerelease>"
    r"(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*"
    r"))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


def parse_semver(version: str) -> re.Match[str] | None:
    return SEMVER_PATTERN.fullmatch(version)


def semver_self_check_errors() -> list[str]:
    valid = (
        "0.0.0",
        "1.2.3",
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-0.3.7",
        "1.0.0-x.7.z.92",
        "1.0.0-x-y-z.--",
        "1.0.0+build.01",
        "1.0.0-beta+exp.sha.5114f85",
    )
    invalid = (
        "1",
        "1.2",
        "1.2.3.4",
        "01.2.3",
        "1.02.3",
        "1.2.03",
        "1.0.0-",
        "1.0.0-01",
        "1.0.0-alpha..1",
        "1.0.0+",
        "1.0.0+build..1",
        "1.0.0-alpha_beta",
        "v1.0.0",
        "1.0.0\n",
        "１.0.0",
    )
    errors = [
        f"accepted invalid version {value!r}"
        for value in invalid
        if parse_semver(value)
    ]
    errors.extend(
        f"rejected valid version {value!r}"
        for value in valid
        if not parse_semver(value)
    )
    return errors


def fail(message: str) -> None:
    ERRORS.append(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(128 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Invalid JSON: {path.relative_to(ROOT)}: {exc}")
        return {}


def check_package_json() -> None:
    package = read_json(ROOT / "package.json")
    required = {
        "name",
        "version",
        "displayName",
        "description",
        "unity",
        "unityRelease",
        "license",
        "author",
        "repository",
        "bugs",
    }
    missing = sorted(required - package.keys())
    if missing:
        fail(f"package.json missing fields: {', '.join(missing)}")

    if package.get("name") != PACKAGE_NAME:
        fail(f"package.json name must be {PACKAGE_NAME}")
    if package.get("displayName") != DISPLAY_NAME:
        fail(f"package.json displayName must be {DISPLAY_NAME}")

    version = str(package.get("version", ""))
    if not parse_semver(version):
        fail("package.json version is not valid SemVer 2.0.0")
    else:
        changelog_path = ROOT / "CHANGELOG.md"
        changelog = changelog_path.read_text(encoding="utf-8") if changelog_path.is_file() else ""
        release_heading = re.compile(
            rf"(?m)^## \[{re.escape(version)}\] - [0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$"
        )
        if len(release_heading.findall(changelog)) != 1:
            fail("CHANGELOG.md must contain one dated section for package.json version")
        if f"[{version}]:" not in changelog:
            fail("CHANGELOG.md must define a link for package.json version")

    if package.get("unity") != "2021.3" or package.get("unityRelease") != "37f1":
        fail("package.json must declare the exact Unity 2021.3.37f1 minimum")
    if package.get("license") != "MIT":
        fail("package.json license must be MIT")
    if (package.get("author") or {}).get("name") != "Martin Calander":
        fail("package.json author.name must identify the UPM wrapper maintainer")

    repository = package.get("repository") or {}
    if repository.get("type") != "git" or repository.get("url") != REPOSITORY_URL + ".git":
        fail("package.json repository must identify the canonical Git repository")
    if (package.get("bugs") or {}).get("url") != REPOSITORY_URL + "/issues":
        fail("package.json bugs URL must identify the canonical issue tracker")
    if package.get("dependencies") not in (None, {}):
        fail("package.json contains unexpected dependencies")
    if "Windows" not in str(package.get("description", "")):
        fail("package.json description must state the Windows-only platform contract")


def check_required_files() -> None:
    required = [
        "README.md",
        "LICENSE.md",
        "NOTICE.md",
        "AUTHORS.md",
        "CHANGELOG.md",
        "THIRD-PARTY-NOTICES.md",
        "Documentation~/installation.md",
        "Documentation~/screenshot.jpg",
        "Documentation~/Images/EditorDarkModeCover.png",
        "Documentation~/Images/EditorDarkModeIcon.png",
        "Editor/UnityEditorDarkMode.dll",
        "Editor/UnityEditorDarkMode.dll.meta",
        "Editor/UnityEditorDarkMode.dll.ini",
        "Editor/UnityEditorDarkMode.dll.ini.meta",
        ".github/RELEASING.md",
        ".github/REPOSITORY_SETUP.md",
        ".github/workflows/ci.yml",
        ".github/workflows/release.yml",
        ".github/scripts/build_installer.py",
        ".github/scripts/verify_installer.py",
        ".github/scripts/tests/test_installer_archive.py",
        ".npmignore",
        "Installer~/SHA256SUMS",
        "Installer~/Assets/EditorDarkModeInstaller.meta",
        "Installer~/Assets/EditorDarkModeInstaller/README.txt",
        "Installer~/Assets/EditorDarkModeInstaller/README.txt.meta",
        "Installer~/Assets/EditorDarkModeInstaller/InstallerMarker.txt",
        "Installer~/Assets/EditorDarkModeInstaller/InstallerMarker.txt.meta",
        "Installer~/Assets/EditorDarkModeInstaller/Editor.meta",
        "Installer~/Assets/EditorDarkModeInstaller/Editor/MartinCalander.EditorDarkMode.Installer.asmdef",
        "Installer~/Assets/EditorDarkModeInstaller/Editor/MartinCalander.EditorDarkMode.Installer.asmdef.meta",
        "Installer~/Assets/EditorDarkModeInstaller/Editor/StrictJson.cs",
        "Installer~/Assets/EditorDarkModeInstaller/Editor/StrictJson.cs.meta",
        "Installer~/Assets/EditorDarkModeInstaller/Editor/EditorDarkModeInstallerManifest.cs",
        "Installer~/Assets/EditorDarkModeInstaller/Editor/EditorDarkModeInstallerManifest.cs.meta",
        "Installer~/Assets/EditorDarkModeInstaller/Editor/EditorDarkModeInstaller.cs",
        "Installer~/Assets/EditorDarkModeInstaller/Editor/EditorDarkModeInstaller.cs.meta",
    ]
    for relative in required:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"Required file missing or empty: {relative}")

    license_path = ROOT / "LICENSE.md"
    if license_path.is_file():
        license_text = license_path.read_text(encoding="utf-8")
        if "MIT License" not in license_text or "Jiaqi" not in license_text:
            fail("LICENSE.md must preserve Jiaqi Liu's MIT license attribution")

    notices_path = ROOT / "THIRD-PARTY-NOTICES.md"
    if notices_path.is_file():
        notices = notices_path.read_text(encoding="utf-8")
        for name in ("ReaperThemeHackDll", "inipp"):
            if name not in notices:
                fail(f"THIRD-PARTY-NOTICES.md must attribute {name}")

    for meta in sorted((ROOT / ".github").rglob("*.meta")):
        fail(f"GitHub-only file must not have Unity metadata: {meta.relative_to(ROOT)}")

    npmignore_path = ROOT / ".npmignore"
    if npmignore_path.is_file():
        lines = {
            line.strip()
            for line in npmignore_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        for attribution in ("AUTHORS.md", "LICENSE.md", "NOTICE.md", "THIRD-PARTY-NOTICES.md"):
            if attribution in lines or f"/{attribution}" in lines:
                fail(f".npmignore must not exclude required attribution file: {attribution}")
        if "/Installer~/" not in lines:
            fail(".npmignore must exclude the release-only /Installer~/ source")


def ignored_by_unity(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    generated = {"artifacts", "dist", "Library", "Logs", "Temp"}
    return any(
        part.startswith(".") or part.endswith("~") or part in generated
        for part in relative.parts
    )


def check_unity_meta_files() -> dict[str, Path]:
    guids: dict[str, Path] = {}
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or ignored_by_unity(path) or path.name.endswith(".meta"):
            continue
        meta = Path(f"{path}.meta")
        if not meta.is_file():
            fail(f"Unity asset is missing .meta file: {path.relative_to(ROOT)}")

    for meta in ROOT.rglob("*.meta"):
        if ".git" in meta.parts or ignored_by_unity(meta):
            continue
        match = re.search(
            r"^guid:\s*([0-9a-f]{32})$",
            meta.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        if not match:
            fail(f"Invalid or missing GUID: {meta.relative_to(ROOT)}")
            continue
        guid = match.group(1)
        if guid in guids:
            fail(
                f"Duplicate Unity GUID {guid}: "
                f"{guids[guid].relative_to(ROOT)} and {meta.relative_to(ROOT)}"
            )
        guids[guid] = meta
    return guids


def check_cover() -> None:
    cover = ROOT / "Documentation~" / "Images" / "EditorDarkModeCover.png"
    if not cover.is_file():
        return
    data = cover.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("EditorDarkModeCover.png is not a valid PNG")
        return
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (600, 300):
        fail("EditorDarkModeCover.png must be exactly 600 by 300 pixels")


def check_native_plugin() -> None:
    dll_path = ROOT / "Editor" / "UnityEditorDarkMode.dll"
    config_path = ROOT / "Editor" / "UnityEditorDarkMode.dll.ini"
    meta_path = Path(f"{dll_path}.meta")
    if not dll_path.is_file() or not config_path.is_file() or not meta_path.is_file():
        return
    if any(path.is_symlink() for path in (dll_path, config_path, meta_path)):
        fail("Native plugin payload and metadata must be regular non-linked files")
        return

    dll = dll_path.read_bytes()
    if sha256(dll_path) != DLL_SHA256:
        fail("UnityEditorDarkMode.dll does not match the audited upstream v1.1 artifact")
    if sha256(config_path) != CONFIG_SHA256:
        fail("UnityEditorDarkMode.dll.ini does not match the audited configuration")
    if sha256(meta_path) != PLUGIN_META_SHA256:
        fail("UnityEditorDarkMode.dll.meta changed from the audited Windows-only importer")

    try:
        pe_offset = struct.unpack_from("<I", dll, 0x3C)[0]
        signature = dll[pe_offset:pe_offset + 4]
        machine = struct.unpack_from("<H", dll, pe_offset + 4)[0]
        characteristics = struct.unpack_from("<H", dll, pe_offset + 22)[0]
    except (struct.error, IndexError):
        fail("UnityEditorDarkMode.dll has a malformed PE header")
    else:
        if dll[:2] != b"MZ" or signature != b"PE\0\0":
            fail("UnityEditorDarkMode.dll is not a valid PE image")
        if machine != 0x8664:
            fail("UnityEditorDarkMode.dll must remain Windows x64")
        if characteristics & 0x2000 == 0:
            fail("UnityEditorDarkMode.dll PE header is not marked as a DLL")

    meta = meta_path.read_text(encoding="utf-8")
    required_patterns = {
        "preloaded": r"(?m)^  isPreloaded: 1$",
        "Editor/Windows": (
            r"(?ms)^  - first:\n      Editor: Editor\n"
            r"    second:\n      enabled: 1\n      settings:\n"
            r"        CPU: AnyCPU\n        DefaultValueInitialized: true\n"
            r"        OS: Windows$"
        ),
        "Any disabled": r"(?ms)^  - first:\n      Any: \n    second:\n      enabled: 0$",
    }
    for label, pattern in required_patterns.items():
        if not re.search(pattern, meta):
            fail(f"Native plugin importer must preserve {label}")
    for platform in ("Linux64", "OSXUniversal", "Win", "Win64"):
        if not re.search(
            rf"(?ms)^  - first:\n      Standalone: {re.escape(platform)}\n"
            r"    second:\n      enabled: 0$",
            meta,
        ):
            fail(f"Native plugin must remain disabled for {platform} players")
    if "AssetOrigin:" in meta:
        fail("UPM plugin metadata must not retain Asset Store ownership metadata")


def check_editor_only_layout() -> None:
    for source in ROOT.rglob("*.cs"):
        if ignored_by_unity(source):
            continue
        if source.relative_to(ROOT).parts[0] != "Editor":
            fail(f"C# source exists outside Editor/: {source.relative_to(ROOT)}")
    for native in ROOT.rglob("*.dll"):
        if ignored_by_unity(native):
            continue
        if native.relative_to(ROOT).parts[0] != "Editor":
            fail(f"Native plugin exists outside Editor/: {native.relative_to(ROOT)}")


def check_installer_source(package_guids: dict[str, Path]) -> None:
    installer_root = ROOT / "Installer~" / "Assets" / "EditorDarkModeInstaller"
    expected_assets = {
        "": "dd0960f86ca457173ee4011a51307f83",
        "README.txt": "471600e6df4440eeb81ccaf844f855b9",
        "InstallerMarker.txt": "d1d1a3e20b825424f4db265775f5ca23",
        "Editor": "ef7546e03c8f009c0343c9a61addd4f2",
        "Editor/MartinCalander.EditorDarkMode.Installer.asmdef":
            "7bf42f341828dfab31930ca42949eafd",
        "Editor/StrictJson.cs": "0c79f66382a9215946dc0edaf7a5b02d",
        "Editor/EditorDarkModeInstallerManifest.cs":
            "2a72f3d1ee300260e41d087b51691f02",
        "Editor/EditorDarkModeInstaller.cs":
            "ac9a0f02d877841894723b355b528c2f",
    }
    actual_assets = {""}
    if installer_root.is_dir():
        actual_assets.update(
            path.relative_to(installer_root).as_posix()
            for path in installer_root.rglob("*")
            if not path.name.endswith(".meta")
        )
    if actual_assets != set(expected_assets):
        fail(
            "Installer asset allowlist mismatch: "
            f"missing={sorted(set(expected_assets) - actual_assets)} "
            f"extra={sorted(actual_assets - set(expected_assets))}"
        )

    seen: set[str] = set()
    for relative, expected_guid in expected_assets.items():
        asset = installer_root if not relative else installer_root / relative
        meta = Path(f"{asset}.meta")
        if not asset.exists() or asset.is_symlink() or not meta.is_file() or meta.is_symlink():
            fail(f"Installer asset/meta pair is missing or linked: {relative or '<root>'}")
            continue
        matches = re.findall(
            r"(?m)^guid:\s*([0-9a-f]{32})$",
            meta.read_text(encoding="utf-8"),
        )
        if matches != [expected_guid]:
            fail(f"Installer GUID changed for {relative or '<root>'}")
        if expected_guid in seen:
            fail(f"Duplicate installer GUID: {expected_guid}")
        if expected_guid in package_guids:
            fail(
                "Installer GUID collides with packaged Unity asset "
                f"{package_guids[expected_guid].relative_to(ROOT)}: {expected_guid}"
            )
        seen.add(expected_guid)

    asmdef_path = installer_root / "Editor" / "MartinCalander.EditorDarkMode.Installer.asmdef"
    asmdef = read_json(asmdef_path)
    if asmdef.get("name") != "MartinCalander.EditorDarkMode.Installer":
        fail("Installer assembly identity changed")
    if asmdef.get("includePlatforms") != ["Editor"]:
        fail("Installer assembly must remain Editor-only")
    if asmdef.get("references") or asmdef.get("precompiledReferences"):
        fail("Installer assembly must remain self-contained before package installation")

    sources = sorted(
        path.relative_to(installer_root).as_posix()
        for path in installer_root.rglob("*.cs")
    )
    expected_sources = sorted(path for path in expected_assets if path.endswith(".cs"))
    if sources != expected_sources or any(not path.startswith("Editor/") for path in sources):
        fail("Installer C# sources must match the exact Editor-only allowlist")

    token_count = 0
    for path in installer_root.rglob("*"):
        if path.is_file() and not path.name.endswith(".meta"):
            token_count += path.read_bytes().count(b"__PACKAGE_VERSION__")
    if token_count != 2:
        fail("Installer source must contain exactly two package-version tokens")

    bootstrap_path = installer_root / "Editor" / "EditorDarkModeInstaller.cs"
    if bootstrap_path.is_file():
        bootstrap = bootstrap_path.read_text(encoding="utf-8")
        for obsolete in (
            "GitSubmoduleManager",
            "MainAssemblyName",
            "SupportedCurrentVersion",
        ):
            if obsolete in bootstrap:
                fail(f"Installer source retains obsolete bootstrap symbol: {obsolete}")
        required_safety_seams = (
            "private static bool TryVerifyNativePlugin(",
            "private static bool TryCheckAssetStoreCopy(",
            "private static bool TryCheckDuplicateNativePayload(",
            "InstallerManifest.TryRejectDependency(",
            "Application.platform != RuntimePlatform.WindowsEditor",
            "Environment.Is64BitProcess",
        )
        for seam in required_safety_seams:
            if bootstrap.count(seam) != 1:
                fail(f"Installer source must contain one required safety seam: {seam}")
        if bootstrap.count("AssetDatabase.GUIDToAssetPath(") != 2 or \
                bootstrap.count("AssetStorePluginGuid") != 3:
            fail("Installer source must check the audited native GUID before and after install")

    package = read_json(ROOT / "package.json")
    version = package.get("version")
    checksums_path = ROOT / "Installer~" / "SHA256SUMS"
    if not checksums_path.is_file() or checksums_path.is_symlink():
        fail("Installer~/SHA256SUMS must be a regular committed file")
        return
    try:
        checksums = checksums_path.read_text(encoding="ascii", errors="strict")
    except (OSError, UnicodeError) as exc:
        fail(f"Installer~/SHA256SUMS is not strict ASCII: {exc}")
        return
    pattern = re.compile(
        r"^(?P<sha256>[0-9a-f]{64})  "
        r"EditorDarkModeInstaller-(?P<version>[^/\r\n]+)\.unitypackage\n$"
    )
    match = pattern.fullmatch(checksums)
    if match is None:
        fail("Installer~/SHA256SUMS must contain exactly one strict checksum line")
    elif match.group("version") != version:
        fail("Installer checksum filename must match package.json version")


MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_SOURCE = re.compile(r"\b(?:src|href)=[\"']([^\"']+)[\"']")


def check_markdown_links() -> None:
    for document in ROOT.rglob("*.md"):
        if ".git" in document.parts:
            continue
        text = document.read_text(encoding="utf-8")
        targets = MARKDOWN_LINK.findall(text) + HTML_SOURCE.findall(text)
        for raw_target in targets:
            target = raw_target.strip().split()[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            resolved = (document.parent / target).resolve()
            if not resolved.is_relative_to(ROOT.resolve()):
                fail(
                    f"Markdown link escapes repository: "
                    f"{document.relative_to(ROOT)} -> {raw_target}"
                )
            elif not resolved.exists():
                fail(f"Broken local link: {document.relative_to(ROOT)} -> {raw_target}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-release-tag",
        metavar="TAG",
        help="validate one v-prefixed SemVer 2.0.0 release tag and print prerelease state",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    self_check_errors = semver_self_check_errors()
    if self_check_errors:
        for error in self_check_errors:
            print(f"ERROR: Internal SemVer self-check {error}.", file=sys.stderr)
        return 1

    if args.check_release_tag is not None:
        tag = args.check_release_tag
        match = parse_semver(tag[1:]) if tag.startswith("v") else None
        if not match:
            print(f"ERROR: Invalid SemVer 2.0.0 release tag: {tag!r}", file=sys.stderr)
            return 1
        print("true" if match.group("prerelease") is not None else "false")
        return 0

    check_package_json()
    check_required_files()
    package_guids = check_unity_meta_files()
    check_cover()
    check_native_plugin()
    check_editor_only_layout()
    check_installer_source(package_guids)
    check_markdown_links()

    if ERRORS:
        for error in ERRORS:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Repository validation failed with {len(ERRORS)} error(s).", file=sys.stderr)
        return 1

    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
