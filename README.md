# ECR Token Generator

This project contains both a **Web App** and a **CLI Binary** for generating AWS ECR login tokens.

## Web App
- Flask-based API in `app/app.py`
- Dockerfile for container deployment
- Unit tests in `tests/test_app.py`

## CLI Binary
- Python CLI in `cli/ecr_token_cli.py`
- Optional PyInstaller Linux binary
- Unit tests in `tests/test_cli.py` (optional)

## Folder Structure

```
ecr-token-generator/
├── app/
│   ├── app.py
│   └── requirements.txt
├── cli/
│   ├── ecr_token_cli.py
│   └── requirements.txt
├── tests/
│   ├── test_app.py
│   └── test_cli.py
├── Dockerfile
├── Dockerfile.cli
├── README.md
└── .github/
    ├── workflows/
    │   ├── webapp_test.yml
    │   └── cli_build.yml
    └── dependabot.yml
```
