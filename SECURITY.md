# Security Policy

## Supported Versions

Security fixes are provided for the latest release only.

## Reporting a Vulnerability

Please open a private security advisory on GitHub or contact the maintainer
directly. Include:

- Affected version
- Reproduction steps
- Impact assessment
- Suggested fix (optional)

## Security Practices in This Repository

- Dependency vulnerability scan with `pip-audit`
- Static analysis with `bandit`
- Automated dependency updates via Dependabot
- No hardcoded credentials in source code
- Local network only (Modbus TCP), no cloud dependency

