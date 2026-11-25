# Contributing to NASA NEX-GDDP-CMIP6 Downloader

Thank you for your interest in contributing to **NASA NEX-GDDP-CMIP6 Downloader**! Contributions of all kinds are welcome, including bug reports, feature suggestions, documentation improvements, testing, and code changes.

This document explains how to report issues, propose changes, and submit pull requests.

---

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Before Making Code Changes](#before-making-code-changes)
- [Development Setup](#development-setup)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Testing Guidelines](#testing-guidelines)
- [Code and Documentation Guidelines](#code-and-documentation-guidelines)
- [Branch and Commit Conventions](#branch-and-commit-conventions)
- [Questions and Contact](#questions-and-contact)

---

## Ways to Contribute

You can help the project by:

- Reporting reproducible bugs.
- Suggesting improvements or new features.
- Improving the README, user guidance, or other documentation.
- Testing the application on different operating systems and environments.
- Reviewing code and submitting fixes or enhancements.

Please open an issue before starting substantial changes. This helps discuss the proposed approach and reduces the chance of duplicated or incompatible work.

## Reporting Bugs

Before opening a new issue, check the existing issues to see whether the problem has already been reported.

When reporting a bug, include as much of the following information as possible:

- **Operating system and version** (Windows, macOS, or Linux).
- **Application version** (for example, v1.1.0).
- **How the application is being run**: packaged executable or Python source.
- **Python version**, if running from source (`python --version`).
- **Steps to reproduce** the problem, in the order performed.
- **Expected behavior** and **actual behavior**.
- Relevant error messages, screenshots, or log excerpts.
- Whether the problem occurs consistently or intermittently.

For download-related issues, also include relevant details when available:

- Download type: global file or study-area subset.
- Selected model, scenario, ensemble, variable, and year.
- Whether the issue occurs during catalog loading, queue creation, or file transfer.
- HTTP status code or network error, if shown.

Please remove personal information, access tokens, credentials, and other sensitive data before attaching logs or screenshots. Do not include large downloaded climate-data files unless they are specifically requested.

## Suggesting Features

Feature suggestions are welcome. Before submitting one, check existing issues and discussions for similar proposals.

A useful feature request explains:

- **What** the proposed feature should do.
- **Why** it would be useful and which users or workflows it would help.
- **How** you expect it to work, including a short example where possible.
- Any relevant limitations, alternatives, or references.

For changes affecting data selection or downloading, clarify whether the proposal concerns global downloads, study-area downloads, or both.

## Before Making Code Changes

For substantial changes, open an issue first and describe the problem or proposed enhancement. Wait for feedback before investing significant time in implementation.

Please keep contributions focused. A pull request that addresses one issue or one closely related group of changes is easier to review than a large collection of unrelated modifications.

Do not commit:

- API keys, passwords, access tokens, or other secrets.
- Personal files, local configuration, cache files, logs, or crash dumps.
- Downloaded climate-data files or other generated data that do not belong in the source repository.
- Build artifacts or packaged executables unless they are explicitly requested for a release.

## Development Setup

The application is written in Python and provides a graphical interface as well as command-line operation.

1. Fork the repository on GitHub.
2. Clone your fork:

   ```bash
   git clone https://github.com/YOUR-USERNAME/NEX-GDDP-CMIP6-Downloader.git
   cd NEX-GDDP-CMIP6-Downloader
   ```

3. Install the application's Python dependency:

   ```bash
   python -m pip install requests
   ```

4. Run the application using the Python script included in the repository. For example:

   ```bash
   python "nex_gddp_cmip6_downloader_v1.1 FINAL.py"
   ```

   If the script has been renamed in the current branch, use its actual filename.

The graphical interface requires `tkinter` to be available in your Python installation. The command-line and self-test modes do not require the graphical interface.

## Submitting a Pull Request

1. Create a branch for your change:

   ```bash
   git checkout -b fix/describe-the-problem
   ```

2. Make your changes. Keep the scope focused and follow the project guidelines below.
3. Test the affected functionality and review your changes for unintended modifications.
4. Commit with a clear, descriptive message:

   ```bash
   git add .
   git commit -m "Fix: handle interrupted global downloads"
   ```

5. Push your branch to your fork:

   ```bash
   git push origin fix/describe-the-problem
   ```

6. Open a Pull Request against the project's `main` branch.

### Pull Request description

A helpful pull request should include:

- A concise summary of the change.
- The issue it addresses (for example, `Closes #123`), if applicable.
- The reason for the change.
- A description of the implementation.
- Tests performed and their results.
- Screenshots or short recordings for user-interface changes.
- Any compatibility considerations or known limitations.

If the change affects the README, command-line arguments, download behavior, output structure, or user-facing settings, update the relevant documentation as part of the same contribution.

## Testing Guidelines

Please test the functionality affected by your change before submitting a pull request. The appropriate tests depend on the scope of the contribution.

Where relevant, consider the following areas:

### Application and interface

- The application starts without errors.
- Navigation between workflow stages behaves correctly.
- Search, filtering, and multi-selection work as expected.
- Changing an upstream selection does not leave incompatible downstream selections active.

### Catalog and selection

- Catalog loading, refresh, and cache behavior work as expected.
- Model, scenario, ensemble, variable, and year selections produce the intended queue.
- Model-specific unavailable combinations are handled correctly.

### Downloads

- Global file downloads work as expected.
- Segmented transfer and resume behavior work for global downloads.
- Pause, resume, and stop controls behave correctly.
- Retry and error handling do not leave misleading queue states or invalid files.
- Study-area requests use the intended bounding box and produce the expected subset.
- Interrupted or failed study-area downloads are handled correctly. Study-area downloads use NCSS and do not provide segmented resume support.
- Output directories and downloaded filenames are correct.

### CLI and self-test

- Relevant command-line arguments are accepted and validated.
- CLI operation works without launching the graphical interface.
- The built-in self-test mode completes successfully, where applicable.

Network-dependent tests may require access to NASA's remote data services. Clearly state which tests were run and which could not be performed. Do not report a test as passing unless it was actually run.

## Code and Documentation Guidelines

Please follow these guidelines when contributing:

- Follow **PEP 8** where practical and remain consistent with the surrounding code.
- Use clear, descriptive names for variables, functions, and classes.
- Keep functions focused and avoid unnecessary complexity.
- Add comments or docstrings where they clarify non-obvious behavior.
- Handle network, file-system, and user-input errors carefully.
- Avoid blocking the graphical user interface with long-running operations; use the application's established background-work patterns.
- Preserve existing behavior unless the change intentionally modifies it.
- Avoid introducing new dependencies unless they are necessary; explain the reason in the pull request.
- Keep user-facing messages and documentation clear and consistent.
- Update screenshots when a user-interface change makes existing screenshots inaccurate.

### Download behavior considerations

The application supports two distinct download paths:

- **Global downloads:** complete files, with segmented downloading and resume support.
- **Study-area downloads:** spatial subsets requested through THREDDS NCSS. These use a single transfer per file and do not support segmented resume.

Changes to the download engine should preserve this distinction and should be tested against the relevant path.

## Branch and Commit Conventions

Use short, descriptive branch names with a prefix that identifies the type of work.

| Type | Example |
|---|---|
| Bug fix | `fix/download-retry-error` |
| New feature | `feature/study-area-validation` |
| Documentation | `docs/update-contributing-guide` |
| Refactoring | `refactor/catalog-loading` |
| Maintenance | `chore/dependency-update` |

Use clear commit messages. Suggested prefixes include:

- `Fix:` for bug fixes.
- `Add:` for new functionality.
- `Update:` for improvements or documentation updates.
- `Refactor:` for code restructuring without intended behavior changes.
- `Docs:` for documentation-only changes.
- `Test:` for test-related changes.

Examples:

```bash
git commit -m "Fix: handle invalid bounding box coordinates"
git commit -m "Add: improve catalog cache refresh"
git commit -m "Docs: update CLI usage examples"
```

These conventions are recommendations intended to keep the project history readable.

## Questions and Contact

If you have a question about contributing or need clarification, you can:

- Open a GitHub Issue and use the `question` label, if available.
- Contact the project author by email: [hadi.asghari@outlook.com](mailto:hadi.asghari@outlook.com).

Project repository:  
https://github.com/haadiasghari/NEX-GDDP-CMIP6-Downloader

---

Thank you for helping improve **NASA NEX-GDDP-CMIP6 Downloader**! Your time, feedback, and contributions are appreciated.
