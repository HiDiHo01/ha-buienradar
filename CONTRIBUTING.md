# Contributing to ha-buienradar

Thank you for your interest in contributing to `ha-buienradar`! Contributions from the community help keep this Home Assistant integration accurate, feature-rich, and reliable for thousands of users.

---

## 📋 How Can You Contribute?

- **Reporting Bugs**: Open an issue detailing the problem, your Home Assistant version, and steps to reproduce.
- **Suggesting Enhancements**: Feature requests and ideas are welcome via GitHub Issues.
- **Improving Documentation**: Fix typos, add examples, or clarify setup steps in `README.md` or other docs.
- **Submitting Code Changes**: Add new features, optimize API polling, or fix bugs via Pull Requests.
- **Adding Translations**: Help translate integration strings in `custom_components/buienradar/translations/`.

---

## 🛠 Local Development Setup

1. **Fork and Clone the Repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ha-buienradar.git
   cd ha-buienradar
   ```

2. **Set Up a Home Assistant Core Test Environment**:
   - Link or copy `custom_components/buienradar` into your local Home Assistant testing `config/custom_components/` folder.

3. **Validate Code Syntax**:
   ```bash
   python3 -m py_compile custom_components/buienradar/*.py
   ```

---

## 📐 Coding Standards & Guidelines

- **Style**: Follow PEP 8 guidelines for Python code.
- **Async Code**: Ensure non-blocking async practices are adhered to (`async_setup_entry`, `async_update`, etc.).
- **Type Hints**: Include type hints for function signatures.
- **Translations**: If adding new user-facing strings, add them to `custom_components/buienradar/strings.json` and `en.json`.

---

## 📥 Submitting a Pull Request

1. Create a descriptive branch for your feature or bugfix:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Commit your changes with a clear commit message.
3. Push to your branch and open a Pull Request against `main`.
4. Fill out the PR template with description and verification details.
