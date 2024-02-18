import json
import boto3
import os

CERT_NAME = 'cert.pem'
MONGO_SECRET_NAME = 'mongodb/cert'

class secretsManager:
    def __init__(self, logger
                 ):
        self.logger = logger
        current_region = os.environ['AWS_REGION']
        session = boto3.session.Session()
        self.secrets_client = session.client(
            service_name = 'secretsmanager',
            region_name = current_region
        )

    def write_mongo_cert_to_tmp_file(self, cert_str):
        try:            
            cert_full_path = os.path.join('/tmp', CERT_NAME)
            with open(cert_full_path, 'w') as f:
                f.write(cert_str)
        except Exception as e:
            self.logger.error(f"Error writing certificate to temp: {e}")
            raise

    def fetch_and_write_mongo_cert(self):
        try:
            response = self.secrets_client.get_secret_value(SecretId=MONGO_SECRET_NAME)
            cert_str = response['SecretString'] 
            self.write_mongo_cert_to_tmp_file(cert_str)
        except Exception as e:
            #self.logger.error(f"Error occurred while fetching the secret - {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('Error fetching the mongodb secret')
            }

