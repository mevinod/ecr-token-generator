# ECR Token Generator — Architectural Document

## 1. Overview

**ECR Token Generator** is a lightweight utility that retrieves AWS Elastic Container Registry (ECR) login tokens from the AWS API. It exposes two independent delivery mechanisms for the same core capability:

- **Web API** — a Flask HTTP service suitable for programmatic, service-to-service use
- **CLI Tool** — a standalone command-line binary for interactive or scripted use

Both interfaces accept AWS credentials (Access Key, Secret Key, optional Region), call the AWS ECR `GetAuthorizationToken` API via `boto3`, and return a base64-encoded login token.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Consumers                            │
│   ┌────────────────┐       ┌──────────────────────────┐ │
│   │  HTTP Client   │       │  Shell / Script / CI Job │ │
│   └───────┬────────┘       └────────────┬─────────────┘ │
└───────────┼────────────────────────────┼───────────────┘
            │ POST /get-token            │ CLI flags
            ▼                            ▼
┌───────────────────┐        ┌───────────────────────────┐
│  Web App (Flask)  │        │  CLI (ecr_token_cli.py)   │
│  app/app.py       │        │  cli/ecr_token_cli.py     │
│  Port 5000        │        │  (compiled binary)        │
└─────────┬─────────┘        └─────────────┬─────────────┘
          │                                │
          └──────────────┬─────────────────┘
                         ▼
              ┌─────────────────────┐
              │  AWS SDK (boto3)    │
              │  ECR Client         │
              └──────────┬──────────┘
                         ▼
              ┌─────────────────────┐
              │  AWS ECR API        │
              │  GetAuthorizationToken│
              └─────────────────────┘
```

---

## 3. Component Breakdown

### 3.1 Web Application (`app/app.py`)

| Property | Detail |
|---|---|
| **Framework** | Flask |
| **Language** | Python 3.10+ |
| **Transport** | HTTP/JSON over TCP port 5000 |
| **Endpoint** | `POST /get-token` |

**Request flow:**
1. Client sends a JSON body with `aws_access_key`, `aws_secret_key`, and optional `region`.
2. The handler validates that both required credential fields are present; returns `400` if not.
3. A `boto3` ECR client is instantiated per-request using the supplied credentials.
4. `client.get_authorization_token()` is called against AWS.
5. On success, the base64 token is returned as `{"token": "..."}` with HTTP `200`.
6. On AWS SDK errors (`BotoCoreError`, `ClientError`), a `500` with an error message is returned.

**Key design choices:**
- Credentials are supplied per-request (no server-side credential storage or caching).
- A new boto3 client is created on every request — stateless, simple, no session reuse.
- No authentication or authorization layer on the HTTP service itself.

### 3.2 CLI Tool (`cli/ecr_token_cli.py`)

| Property | Detail |
|---|---|
| **Interface** | `argparse` command-line flags |
| **Distribution** | Compiled Linux binary via PyInstaller |
| **Output** | Token printed to stdout; errors to stderr with `sys.exit(1)` |

**Flags:**

| Flag | Required | Default | Description |
|---|---|---|---|
| `--access-key` | Yes | — | AWS Access Key ID |
| `--secret-key` | Yes | — | AWS Secret Access Key |
| `--region` | No | `us-east-1` | AWS region |

**Key design choices:**
- Pure functional design — one function (`get_ecr_token`) does the work; `main()` handles I/O.
- Compiled to a self-contained binary with PyInstaller for dependency-free distribution.
- Uses the same boto3 call as the web app — identical AWS interaction logic.

---

## 4. Data Flow

```
Caller → Supplies credentials (access key, secret key, region)
       → boto3 ECR client created with credentials
       → AWS STS validates credentials
       → AWS ECR returns authorizationData[]
       → authorizationToken (base64) extracted from response[0]
       → Token returned to caller
```

The token returned is a base64-encoded string in the format `AWS:<password>`, which is the standard Docker registry password for ECR (`docker login` compatible).

---

## 5. Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 / 3.11 |
| Web framework | Flask |
| AWS SDK | boto3 / botocore |
| CLI packaging | PyInstaller |
| Containerization | Docker (python:3.11-slim base) |
| CI/CD | GitHub Actions |
| Testing | pytest |
| Dependency updates | Dependabot (weekly, pip) |

---

## 6. Packaging and Distribution

### 6.1 Web App Docker Image (`Dockerfile`)

```
python:3.11-slim
  └─ COPY app/requirements.txt → pip install (flask, boto3)
  └─ COPY app/ → /app/app/
  └─ EXPOSE 5000
  └─ CMD: python app/app.py
```

The image exposes port 5000 and runs the Flask development server directly. Intended for internal/tooling use.

### 6.2 CLI Binary Docker Image (`Dockerfile.cli`)

```
python:3.11-slim
  └─ pip install boto3 pyinstaller
  └─ COPY cli/ecr_token_cli.py
  └─ RUN pyinstaller --onefile ecr_token_cli.py
  └─ ENTRYPOINT: ./dist/ecr_token_cli
```

Used to reproducibly build the Linux binary. The output artifact is `dist/ecr_token_cli`.

---

## 7. CI/CD Pipeline (GitHub Actions)

Four workflows govern the automation lifecycle:

| Workflow | Trigger | Purpose |
|---|---|---|
| `test.yaml` | Push/PR to `master` | Runs full pytest suite |
| `webapp_test.yml` | Push/PR (any branch) | Runs web app unit tests |
| `cli_build.yml` | Push/PR (any branch) | Builds CLI binary; uploads as artifact |
| `release.yml` | Manual (`workflow_dispatch`) | Versions, builds, and publishes GitHub Release |

### Release Workflow Detail

1. Accepts optional `version` input; auto-increments the patch segment of the latest git tag if none is given.
2. Generates a changelog from commits since the last tag.
3. Builds the web app Docker image (tagged with version).
4. Builds the CLI binary via PyInstaller.
5. Creates a GitHub Release with the changelog as the release body.
6. Attaches the `ecr_token_cli` binary to the release as a downloadable asset.

Docker Hub push is present in the workflow but commented out (requires `DOCKER_USERNAME`/`DOCKER_PASSWORD` secrets).

---

## 8. Testing Strategy

| Test file | Coverage |
|---|---|
| `tests/test_app.py` | Web API: missing credentials (400), invalid credentials (400/500) |
| `tests/test_cli.py` | Placeholder (no assertions yet) |

Tests use Flask's built-in test client. AWS calls are not mocked — invalid credentials are expected to produce an error response from AWS, which is asserted as a 4xx/5xx. No integration or end-to-end tests exist.

---

## 9. Directory Structure

```
ecr-token-generator/
├── app/
│   ├── __init__.py
│   ├── app.py              # Flask web API
│   └── requirements.txt    # flask, boto3
├── cli/
│   ├── __init__.py
│   ├── ecr_token_cli.py    # CLI entrypoint
│   └── requirements.txt    # boto3
├── tests/
│   ├── test_app.py         # Web app tests
│   └── test_cli.py         # CLI tests (placeholder)
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       ├── cli_build.yml
│       ├── release.yml
│       ├── test.yaml
│       └── webapp_test.yml
├── Dockerfile              # Web app container image
├── Dockerfile.cli          # CLI build container
├── ARCHITECTURE.md         # This document
└── README.md
```

---

## 10. Security Considerations

| Concern | Current State |
|---|---|
| Credential handling | Passed as request parameters / CLI flags; never persisted |
| Transport security | HTTP only (no TLS) — suitable only for trusted internal networks |
| Web API authentication | None — any caller can use the endpoint |
| Secrets in CI | `GITHUB_TOKEN` used for releases; Docker Hub credentials optional via secrets |
| Dependency scanning | Dependabot monitors pip dependencies weekly |

> **Notable:** AWS credentials are accepted in plaintext over HTTP (web app) and as CLI arguments (visible in process list). For production use, TLS and an authentication layer should be added to the web API, and the CLI should support credential sourcing from environment variables or AWS credential files.

---

## 11. Architectural Limitations and Recommendations

| Limitation | Recommendation |
|---|---|
| Flask dev server used in production image | Replace with `gunicorn` or `uvicorn` for production |
| No TLS on the web API | Add a reverse proxy (nginx, Caddy) or terminate TLS at the load balancer |
| No API authentication | Add an API key or mTLS for the `/get-token` endpoint |
| No token caching | ECR tokens are valid for 12 hours; caching would reduce AWS API calls |
| CLI credentials visible in process list | Support `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` env vars |
| Minimal CLI test coverage | Add boto3 mocking with `unittest.mock` or `moto` |
| Single region per request | Could be extended to support multi-region batch token retrieval |
