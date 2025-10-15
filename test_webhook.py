"""
Simple test script to send webhook requests to the EC2 restart service.
"""
import requests
import json
import sys

def test_webhook(url="http://localhost:5000/webhook", password="your_secret_password_here"):
    """
    Send a test webhook request.
    
    Args:
        url (str): The webhook endpoint URL
        password (str): The password to send
    """
    print(f"Sending webhook request to: {url}")
    print(f"Password: {password}")
    print("-" * 50)
    
    try:
        payload = {
            "password": password
        }
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the server.")
        print("Make sure the webhook service is running.")
        return False
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out.")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def test_health_check(url="http://localhost:5000/health"):
    """
    Test the health check endpoint.
    
    Args:
        url (str): The health check endpoint URL
    """
    print(f"\nTesting health check endpoint: {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    webhook_url = "http://localhost:5000/webhook"
    health_url = "http://localhost:5000/health"
    password = "thisisthewebhookforbws10909"
    if len(sys.argv) > 1:
        password = sys.argv[1]
    if len(sys.argv) > 2:
        webhook_url = sys.argv[2]
        health_url = webhook_url.replace("/webhook", "/health")
    
    print("=" * 50)
    print("EC2 Restart Webhook - Test Script")
    print("=" * 50)
    health_ok = test_health_check(health_url)
    
    if health_ok:
        print("\n✓ Health check passed!")
        webhook_ok = test_webhook(webhook_url, password)
        
        if webhook_ok:
            print("\n✓ Webhook test passed!")
        else:
            print("\n✗ Webhook test failed!")
    else:
        print("\n✗ Health check failed! Server may not be running.")
        print("\nTo start the server, run:")
        print("  python app.py")
    
    print("\n" + "=" * 50)

