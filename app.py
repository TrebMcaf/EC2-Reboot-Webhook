import os
import logging
from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

WEBHOOK_PASSWORD = os.getenv('WEBHOOK_PASSWORD', 'default_secret_password')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

def restart_ec2_instance(instance_id, region):
    """
    Restart an EC2 instance by instance ID.
    
    Args:
        instance_id (str): The EC2 instance ID to restart
        region (str): AWS region where the instance is located
        
    Returns:
        dict: Response from AWS with status information
    """
    try:
        ec2_client = boto3.client('ec2', region_name=region)
        logger.info(f"Attempting to reboot EC2 instance: {instance_id} in region: {region}")
        response = ec2_client.reboot_instances(InstanceIds=[instance_id])
        logger.info(f"Successfully initiated reboot for instance: {instance_id}")
        return {
            'success': True,
            'message': f'Successfully initiated reboot for instance {instance_id}',
            'response': response
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error: {error_code} - {error_message}")
        return {
            'success': False,
            'message': f'AWS Error: {error_message}',
            'error_code': error_code
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """
    Handle incoming webhook requests.
    Checks for the password keyword and triggers EC2 restart if found.
    """
    try:
        data = request.get_json(force=True)      
        logger.info(f"Received webhook request from IP: {request.remote_addr}")
        password = None
        possible_password_fields = ['password', 'secret', 'keyword', 'token', 'key']
        for field in possible_password_fields:
            if field in data:
                password = data.get(field)
                break
        if password is None and isinstance(data, str):
            password = data
        logger.info(f"Password field found: {password is not None}")
        if password != WEBHOOK_PASSWORD:
            logger.warning(f"Invalid password attempt from IP: {request.remote_addr}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid password'
            }), 401
        logger.info("Password verified successfully")

        instance_id = data.get('instance_id')
        if not instance_id:
            logger.error("instance_id not provided in request")
            return jsonify({
                'status': 'error',
                'message': 'instance_id is required in the request body'
            }), 400
        region = data.get('region', AWS_REGION)
        
        result = restart_ec2_instance(instance_id, region)
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': result['message'],
                'instance_id': instance_id
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            }), 500
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error processing webhook: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'EC2 Auto Restart Webhook'
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    logger.info(f"Starting webhook server on port {port}")
    logger.info(f"Default AWS Region: {AWS_REGION}")
    logger.info("Instance ID will be provided in webhook payload")
    app.run(host='0.0.0.0', port=port, debug=debug)

