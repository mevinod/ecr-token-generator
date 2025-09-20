# ECR Token Generator

Generate AWS ECR login tokens via **CLI** or **Web API**.

---

## Table of Contents

- [Features](#features)  
- [Requirements](#requirements)  
- [Installation](#installation)  
- [Usage](#usage)  
  - [CLI](#cli)  
  - [Web App](#web-app)  
- [Docker](#docker)  
- [Examples](#examples)  
- [Testing](#testing)  

---

## Features

- Accepts AWS Access Key, Secret Key, and Region (default: `us-east-1`)  
- Generates ECR login token using AWS API  
- Web API for programmatic usage  
- CLI binary for Linux  
- Release-ready via GitHub Actions with automatic versioning  

---

## Requirements

- Python 3.10+ (for web app or CLI build)  
- Linux (for CLI binary)  
- Docker (optional, for web app image)  

---

## Installation

### CLI

Download the binary from [GitHub releases](https://github.com/<your-repo>/releases) or build locally:

```bash
pip install -r requirements.txt  # ensure boto3 is installed
pip install pyinstaller

# Clean old builds
rm -rf build/ dist/ ecr_token_cli.spec

# Build CLI binary
pyinstaller --onefile cli/ecr_token_cli.py --distpath dist --hidden-import=boto3
chmod +x dist/ecr_token_cli
```

> **Note:** `boto3` must be installed in your environment for the CLI binary to work.

The binary will be in `dist/ecr_token_cli`.

---

### Web App

```bash
pip install -r requirements.txt
python app/app.py
```

---

## Usage

### CLI

```bash
./dist/ecr_token_cli --access-key <AWS_ACCESS_KEY> \
                     --secret-key <AWS_SECRET_KEY> \
                     [--region <AWS_REGION>]
```

- `--access-key` (required) — Your AWS Access Key  
- `--secret-key` (required) — Your AWS Secret Key  
- `--region` (optional) — AWS region, default is `us-east-1`

#### Example

```bash
./dist/ecr_token_cli \
    --access-key AKIAEXAMPLE \
    --secret-key wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Response:**

```
<base64_ecr_login_token>
```

If credentials are missing:

```
Error: AWS access key or secret key is missing
```

---

### Web App

Start the server:

```bash
python app/app.py
```

The server listens on **port 5000** by default.

#### API Endpoint

```
POST /get-token
Content-Type: application/json
```

**Request Body:**

```json
{
    "aws_access_key": "<AWS_ACCESS_KEY>",
    "aws_secret_key": "<AWS_SECRET_KEY>",
    "region": "us-east-1"  // optional
}
```

**Example using `curl`:**

```bash
curl -X POST http://localhost:5000/get-token \
     -H "Content-Type: application/json" \
     -d '{
           "aws_access_key": "AKIAEXAMPLE",
           "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
         }'
```

**Response:**

```json
{
  "token": "<base64_ecr_login_token>"
}
```

If credentials are missing or invalid:

```json
{
  "error": "AWS access key or secret key is missing"
}
```

---

## Docker

Build Docker image:

```bash
docker build -t myorg/ecr-web-app .
```

Run Docker container:

```bash
docker run -p 5000:5000 myorg/ecr-web-app
```

---

## Examples

### CLI

```bash
./dist/ecr_token_cli \
    --access-key AKIAEXAMPLE \
    --secret-key wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
    --region us-west-2
```

### Web App

```bash
curl -X POST http://localhost:5000/get-token \
     -H "Content-Type: application/json" \
     -d '{
           "aws_access_key": "AKIAEXAMPLE",
           "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
           "region": "us-west-2"
         }'
```

---

## Testing

Run unit tests using `pytest`:

```bash
pytest tests/
```

Make sure Python dependencies are installed:

```bash
pip install -r requirements.txt
```

---

## Notes

- CLI binary requires `boto3` to be packaged or installed in your environment when building with PyInstaller.  
- Default AWS region is `us-east-1` if not specified.  
- GitHub Actions workflow can automatically build and attach CLI binaries to releases.

