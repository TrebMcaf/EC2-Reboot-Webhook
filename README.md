# EC2 Auto Restart Webhook

A Python Flask application that receives webhook messages and automatically restarts an EC2 instance when the correct password/keyword and instance ID are provided.

## Features

- 🔐 Password-protected webhook endpoint
- ☁️ Dynamic EC2 instance restart functionality (specify instance ID per request)
- 🌍 Support for multiple AWS regions
- 📝 Comprehensive logging
- 🏥 Health check endpoint
- ⚙️ Environment-based configuration

## Prerequisites

- Python 3.7+
- AWS Account with EC2 access
- AWS credentials configured (IAM role or access keys)

## Installation

1. Clone this repository or navigate to the project directory

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file:
```bash
cp .env.example .env
```

4. Edit `.env` and configure your settings:
   - `WEBHOOK_PASSWORD`: The secret password/keyword to trigger the restart
   - `AWS_REGION`: Default AWS region (can be overridden in webhook request)
   - AWS credentials (if not using IAM role)

**Note:** The EC2 instance ID is now provided in each webhook request payload, allowing you to reboot different instances dynamically.

## AWS Credentials Setup

### Option 1: IAM Role (Recommended for EC2/ECS deployment)
If running on an EC2 instance or ECS, attach an IAM role with the following permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:RebootInstances",
                "ec2:DescribeInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

### Option 2: Access Keys (For local development)
Set these in your `.env` file:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## Usage

### Running the Application

#### Development Mode:
```bash
python app.py
```

#### Production Mode (using Gunicorn):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Sending Webhook Requests

The webhook endpoint accepts POST requests at `/webhook`.

**Required fields:**
- `password`: Your webhook password
- `instance_id`: The EC2 instance ID to reboot (e.g., i-0123456789abcdef0)

**Optional fields:**
- `region`: AWS region (defaults to `AWS_REGION` from .env if not provided)

#### Example using curl:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"password": "your_secret_password_here", "instance_id": "i-0123456789abcdef0"}'
```

#### Example with custom region:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"password": "your_secret_password_here", "instance_id": "i-0123456789abcdef0", "region": "us-west-2"}'
```

#### Example using Python:
```python
import requests

response = requests.post(
    'http://localhost:5000/webhook',
    json={
        'password': 'your_secret_password_here',
        'instance_id': 'i-0123456789abcdef0'
    }
)
print(response.json())
```

#### Example using PowerShell:
```powershell
$body = @{
    password = "your_secret_password_here"
    instance_id = "i-0123456789abcdef0"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/webhook" -Method Post -Body $body -ContentType "application/json"
```

### Supported Password Field Names

The application looks for the password in the following JSON fields:
- `password`
- `secret`
- `keyword`
- `token`
- `key`

### Endpoints

- `POST /webhook` - Main webhook endpoint to trigger EC2 restart
- `GET /health` - Health check endpoint

### Response Examples

#### Success Response:
```json
{
    "status": "success",
    "message": "Successfully initiated reboot for instance i-0123456789abcdef0",
    "instance_id": "i-0123456789abcdef0"
}
```

#### Invalid Password:
```json
{
    "status": "error",
    "message": "Invalid password"
}
```

#### Missing Instance ID:
```json
{
    "status": "error",
    "message": "instance_id is required in the request body"
}
```

#### AWS Error:
```json
{
    "status": "error",
    "message": "AWS Error: The instance ID 'i-xxx' does not exist"
}
```

## Security Considerations

1. **Use HTTPS**: Always use HTTPS in production to encrypt webhook traffic
2. **Strong Password**: Use a strong, unique password for the webhook
3. **IP Whitelisting**: Consider adding IP whitelisting for added security
4. **IAM Permissions**: Follow the principle of least privilege for AWS permissions
5. **Environment Variables**: Never commit `.env` file to version control

## Deployment

### Docker Deployment (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t ec2-restart-webhook .
docker run -p 5000:5000 --env-file .env ec2-restart-webhook
```

### Systemd Service (Linux)
Create `/etc/systemd/system/ec2-restart-webhook.service`:
```ini
[Unit]
Description=EC2 Auto Restart Webhook
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/AutoRestoreWebhook
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Testing

A test script is included to verify the webhook functionality:

```bash
# Basic test with default values
python test_webhook.py

# Test with custom password and instance ID
python test_webhook.py "your_password" "i-0123456789abcdef0"

# Test with custom password, instance ID, and URL
python test_webhook.py "your_password" "i-0123456789abcdef0" "http://your-server:5000/webhook"
```

The test script will:
1. Check the health endpoint
2. Send a webhook request with the specified password and instance ID
3. Display the response

## Logging

The application logs all important events including:
- Incoming webhook requests
- Password verification attempts
- EC2 restart operations
- Errors and exceptions

Logs are printed to stdout/stderr and can be redirected to a file if needed.

## Troubleshooting

### "instance_id is required in the request body" error
Make sure you're including the `instance_id` field in your webhook request JSON payload.

### AWS Authentication Errors
Verify your AWS credentials are correctly configured and have the necessary permissions.

### Instance Not Rebooting
Check the application logs for error messages. Ensure:
- The instance ID in your request is correct and exists
- The instance is in the correct region (either specified in the request or matching your `AWS_REGION` env variable)
- Your AWS credentials have permission to reboot the specified instance

## License

MIT License - Feel free to use and modify as needed.

