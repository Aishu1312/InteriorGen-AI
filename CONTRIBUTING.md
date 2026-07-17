# Contributing to AI Interior Designer Pro

Thanks for your interest in improving this project! Contributions of all sizes are welcome.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your own API keys.
4. Run the app locally:
   ```bash
   streamlit run app.py
   ```

## Branching

- Create a feature branch off `main`: `git checkout -b feature/short-description`
- Keep pull requests focused on a single change.

## Code Style

- Follow **PEP 8**.
- Use type hints on function signatures.
- Keep functions small and single-purpose; place shared logic in `utils/` or `services/`.
- Run a formatter (e.g. `black .`) before committing.

## Commit Messages

Use clear, imperative commit messages, e.g. `Add Scandinavian theme preset` rather than `updated stuff`.

## Submitting a Pull Request

1. Ensure the app still runs without errors (`streamlit run app.py`).
2. Update the README if you changed setup steps, features, or environment variables.
3. Fill out the pull request template completely.
4. Link any related issues.

## Reporting Bugs / Requesting Features

Please use the issue templates under `.github/ISSUE_TEMPLATE/` so maintainers have the context needed to help quickly.

## Code of Conduct

Be respectful and constructive. This project welcomes contributors of all experience levels.
