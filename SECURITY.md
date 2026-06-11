# Security Policy

This repository handles research workflow metadata and teaching artifacts. It
should not contain secrets, credentials, restricted participant-level data, or
private account information.

## Supported Branch

Security fixes should target the default branch unless a maintained release
branch is explicitly documented.

## Do Not Commit

- API keys, portal cookies, access tokens, or passwords.
- CHARLS raw files or other registered-access participant-level files.
- Direct identifiers or re-identifiable participant records.
- Screenshots that reveal private account details.
- Private reviewer comments or journal correspondence without permission.

## Reporting Issues

Open a private security advisory or contact the repository owner if a security
issue involves credentials, restricted data, or identifiable information. For
ordinary documentation or validation bugs, use a public issue.

## Expected Maintainer Response

Maintainers should remove exposed secrets or restricted data from active files,
rotate affected credentials, document the remediation, and add a validation or
policy guard when feasible.
