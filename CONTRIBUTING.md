# Contributing to BridgeGuard

Thank you for your interest in contributing! This project is a defensive security research tool for cross-chain bridges. We welcome:

- New historical bridge incident data (in `backend/app/sample_data/attacks.json`)
- Additional reason codes or invariants
- UI improvements
- Bug fixes
- Documentation enhancements

## How to Contribute

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Make your changes, ensuring all tests pass (`python -m pytest tests/`).
4. Submit a pull request with a clear description of the changes.

## Data Contribution Guidelines

When adding a new incident to `attacks.json`, include a `source` field with a publicly accessible URL. Do not include exploit code or step-by-step attack instructions.

## Code of Conduct

Be respectful and constructive. This is a defensive-security project - any offensive exploit submissions will be rejected.
