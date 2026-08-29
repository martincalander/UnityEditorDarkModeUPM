# Releasing Editor Dark Mode

Releases follow Semantic Versioning and are produced from annotated `v*` tags
by the [Publish Release workflow](workflows/release.yml).

## Release Authority and Signing

Only an authorized maintainer may create release tags. Configure the protected
`release` environment before publishing:

- environment secret `UPM_SERVICE_ACCOUNT_KEY_ID`;
- environment secret `UPM_SERVICE_ACCOUNT_KEY_SECRET`;
- environment variable `UPM_ORG_ID`.

The credentials must belong to a dedicated Unity service account with only the
organization-level **Package Manager Package Signer** role. No Unity Editor
license, email, or personal password is required by this workflow.

The Unity UPM CLI adds `package/.attestation.p7m` to the release `.tgz`. This
signs the UPM archive payload. It does not Authenticode-sign the bundled native
DLL, sign the bootstrap `.unitypackage`, or confer Unity QA "Verified" status.

## Prepare

1. Update `package.json` and add a dated section to `CHANGELOG.md`.
2. Confirm the package name and version match the intended tag exactly.
3. Confirm the DLL, configuration, importer metadata, attribution, and hashes
   still match the audited upstream release.
4. Run:

   ```bash
   python3 .github/scripts/validate_repository.py
   python3 -m unittest discover -s .github/scripts/tests -p 'test_*.py' -v
   npx --yes markdownlint-cli2@0.23.0 "**/*.md" "#Library" "#Temp"
   npm pack --ignore-scripts --dry-run
   ```

5. Build the deterministic bootstrap:

   ```bash
   version="$(jq -er '.version' package.json)"
   mkdir -p artifacts
   python3 .github/scripts/build_installer.py \
     --version "$version" \
     --output "artifacts/EditorDarkModeInstaller-$version.unitypackage"
   ```

6. Import that exact `.unitypackage` into a disposable Unity project. Confirm
   it compiles on macOS or Linux and fails closed without changing the manifest.
   On a supported Windows x64 Editor, confirm the plan, installation, native
   file verification, restart guidance, cleanup, and recovery path.
7. Put the builder's exact digest and filename in `Installer~/SHA256SUMS`, then
   run `verify_installer.py` against the tested archive.
8. Record every platform and Unity version not exercised. Hosted CI checks the
   deterministic builder and package portability but does not launch Unity or
   run EditMode tests.

## Publish

Enable immutable releases before creating the first tag. From a clean `main`
checkout, create and push an annotated tag matching `package.json`:

```bash
git tag -a v1.1.1 -m "Editor Dark Mode 1.1.1"
git push origin v1.1.1
```

The workflow validates the exact tag and commit, builds a source archive,
signs that validated payload, verifies that signing changed only the
attestation, independently builds the tested bootstrap, and creates a GitHub
Release containing:

- `com.martincalander.editordarkmode-1.1.1.tgz`;
- `EditorDarkModeInstaller-1.1.1.unitypackage`;
- `SHA256SUMS`.

For the first release, leave `OPENUPM_ENABLED` unset. Submit the package at
<https://openupm.com/packages/add/> using `trackingMode: githubRelease` and
`githubReleaseAssetName: 'com.martincalander.editordarkmode-'`. After the
metadata pull request is merged and the initial version appears on OpenUPM,
create the repository variable `OPENUPM_ENABLED=true`.

## Verify

- Confirm the release points to the intended commit and is immutable.
- Verify both downloaded assets against `SHA256SUMS`.
- Inspect the `.tgz` for the nonempty `package/.attestation.p7m`.
- Confirm development-only `.github` and `Installer~` content is absent from
  the `.tgz`.
- Install the signed tarball in a clean Unity project and restart the Editor.
- Import the bootstrap in another clean project and confirm it installs the
  exact OpenUPM registry version.
- Confirm Git URL installation with
  `https://github.com/martincalander/UnityEditorDarkModeUPM.git#v1.1.1`.

Do not rewrite or reuse a published version or tag. Correct a defective release
with a new patch version.
