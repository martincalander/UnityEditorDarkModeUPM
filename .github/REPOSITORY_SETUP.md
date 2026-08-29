# Repository Publication Checklist

These GitHub settings are not stored in the repository. Complete them before
publishing Editor Dark Mode.

## Repository and Actions

- [ ] Confirm `main` is the default branch and the MIT license is detected.
- [ ] Enable GitHub Issues so the `package.json` support URL is available.
- [ ] Use the description `Jiaqi Liu's Windows-only Unity Editor dark mode mod,
  packaged for UPM.`
- [ ] Add the topics `unity`, `unity-editor`, `upm`, `windows`, `dark-mode`,
  `editor-extension`, and `package-manager`.
- [ ] Keep the default Actions token permission read-only.
- [ ] Require full commit SHA pinning and allow only the actions referenced by
  the committed workflows.
- [ ] Enable secret scanning, push protection, Dependabot alerts and security
  updates, private vulnerability reporting, and CodeQL for C# and Actions.

## Main and Release Protection

- [ ] Protect `main` against deletion and force pushes.
- [ ] Require the `Required sanity gate` check after the first **Sanity Checks**
  run establishes that status context.
- [ ] Require pull requests, resolved conversations, and stale-review dismissal
  when collaborators will merge changes.
- [ ] Protect `v*` tags against creation, update, and deletion except by the
  release maintainer.
- [ ] Enable immutable releases before pushing the first release tag.

## Signing Environment

Create a GitHub environment named `release` and restrict it to tags matching
`v*`. Add only these values to that environment:

- secret `UPM_SERVICE_ACCOUNT_KEY_ID`;
- secret `UPM_SERVICE_ACCOUNT_KEY_SECRET`;
- variable `UPM_ORG_ID`.

Use a dedicated Unity service account with only the organization-level
**Package Manager Package Signer** role. Do not store a Unity Editor license,
personal account password, or email address in this repository. Environment
secrets are encrypted by GitHub and are exposed only to the signing job after
the environment policy is satisfied.

## OpenUPM Bootstrap

Do not create the repository variable `OPENUPM_ENABLED` before initial OpenUPM
registration. The first release must be published to GitHub, then registered at
<https://openupm.com/packages/add/> with:

```yaml
name: com.martincalander.editordarkmode
aliases:
  - com.0x7c13.darkmode
displayName: Editor Dark Mode
description: >-
  Jiaqi Liu's Windows-only dark mode mod for the Unity Editor, packaged for UPM.
repoUrl: https://github.com/martincalander/UnityEditorDarkModeUPM
trackingMode: githubRelease
parentRepoUrl: null
licenseSpdxId: MIT
licenseName: MIT License
image: https://raw.githubusercontent.com/martincalander/UnityEditorDarkModeUPM/main/Documentation~/Images/EditorDarkModeCover.png
topics:
  - editor-enhancement
  - gui
  - utilities
hunter: martincalander
gitTagPrefix: ''
gitTagIgnore: ''
minVersion: '1.1.1'
readme: main:README.md
githubReleaseAssetName: 'com.martincalander.editordarkmode-'
```

Let the OpenUPM form generate `createdAt`. After the metadata pull request is
merged and version `1.1.1` is published, create the repository Actions variable
`OPENUPM_ENABLED=true` for later releases.

## First Release

1. Follow [RELEASING.md](RELEASING.md).
2. Confirm the signed `.tgz`, bootstrap `.unitypackage`, and `SHA256SUMS` are
   present on the GitHub Release.
3. Confirm the `.tgz` contains `package/.attestation.p7m`.
4. Submit and merge the OpenUPM metadata pull request.
5. Test the published OpenUPM package in a clean supported Windows Unity
   project and restart the Editor.
