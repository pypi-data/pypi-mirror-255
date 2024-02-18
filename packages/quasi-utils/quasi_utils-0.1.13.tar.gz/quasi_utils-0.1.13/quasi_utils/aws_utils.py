from base64 import b64decode, b64encode

import boto3


def encrypt(text, key_id='alias/kite_api_key'):
	kms = boto3.client('kms')
	return b64encode(kms.encrypt(KeyId=key_id, Plaintext=bytes(text, encoding='utf8'))['CiphertextBlob']).decode('utf8')


def decrypt(text, key_id='alias/kite_api_key'):
	kms = boto3.client('kms')
	return kms.decrypt(KeyId=key_id, CiphertextBlob=bytes(b64decode(text)))['Plaintext'].decode('utf8')


def get_from_s3(bucket, file_path):
	s3 = boto3.client('s3')
	file_obj = s3.get_object(Bucket=bucket, Key=file_path)
	
	return file_obj['Body'].read().decode('utf-8')


def upload_to_s3(bucket, file, key):
	s3 = boto3.client('s3')
	s3.put_object(Body=file, Bucket=bucket, Key=key)


def download_s3(bucket, s3_path, save_path):
	s3 = boto3.client('s3')
	s3.download_file(bucket, s3_path, save_path)
