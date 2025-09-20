# AWS ECR Login Token Generator API

This is a simple Flask-based API that accepts AWS credentials (Access Key, Secret Key, and optional Region) and returns an **ECR login token**.

If no region is provided, it defaults to `us-east-1`.

---

## Project Structure

```
.
├── app.py          # Flask application code
├── requirements.txt # Python dependencies
├── Dockerfile      # Dockerfile to containerize the app
└── README.md       # Documentation
```

---

## Prerequisites

- Python 3.8+
- AWS IAM user credentials with permissions to access **ECR**
- Docker (if running in a container)

---

## Installation (Local)

1. Clone the repository or copy the files.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python app.py
   ```

By default, it runs on port **5000**.

---

## Running with Docker

1. Build the image:

   ```bash
   docker build -t ecr-token-app .
   ```

2. Run the container:

   ```bash
   docker run -p 5000:5000 ecr-token-app
   ```

---

## API Usage

### Endpoint

`POST /get-token`

### Request Body

```json
{
  "aws_access_key": "YOUR_AWS_ACCESS_KEY",
  "aws_secret_key": "YOUR_AWS_SECRET_KEY",
  "region": "us-west-2" 
}
```

- `region` is **optional**. Defaults to `us-east-1`.

### Example Request (cURL)

```bash
curl -X POST http://localhost:5000/get-token \
  -H "Content-Type: application/json" \
  -d '{
    "aws_access_key": "AKIAxxxxxxxxxxxx",
    "aws_secret_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "region": "us-west-2"
  }'
```

### Example Response (Success)

```json
{
  "token": "ecr-login-token-string=="
}
```

### Example Response (Error)

```json
{
  "error": "Unable to get ECR token: An error occurred (UnrecognizedClientException) ..."
}
```

---

## Environment Variables (Optional)

Instead of passing keys in the request body, you can set AWS credentials as environment variables inside the container or host:

```bash
export AWS_ACCESS_KEY_ID=AKIAxxxxxxxxxxxx
export AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export AWS_DEFAULT_REGION=us-east-1
```

Then send a request without providing keys in the body (future enhancement idea).

---

## Security Note

- Do **NOT** expose this app publicly with real AWS credentials in requests.
- For production, use AWS IAM roles, Secrets Manager, or a secure vault.

---

## License

MIT

