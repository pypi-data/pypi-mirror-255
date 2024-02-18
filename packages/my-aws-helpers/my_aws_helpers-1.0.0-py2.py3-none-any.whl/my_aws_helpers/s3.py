import boto3
import io
import json 
from typing import Tuple

class S3:
    client: boto3.client

    def __init__(self) -> None:
        self.client = boto3.client('s3')

    def _streaming_body_to_dict(self, payload):
        file_like_obj = io.BytesIO(payload.read())
        response = json.loads(file_like_obj.getvalue())
        return response
    
    def put_json_object(self, bucket_name: str, file_name: str, object: dict):
        return self.client.put_object(
            Body = json.dumps(object),
            Bucket = bucket_name,
            Key = file_name
        )
    
    def get_object(self, bucket_name: str, file_name: str):
        response = self.client.get_object(
            Bucket = bucket_name,
            Key = file_name            
        )
        return self._streaming_body_to_dict(response["Body"])
    
    def get_presigned_url(self, bucket_name: str, file_name: str, expires_in: int = 3600):
        return self.client.generate_presigned_url(
            'get_object',
            Params = {
                "Bucket": bucket_name,
                "Key": file_name,
            },
            ExpiresIn = expires_in
        )
    
    def get_s3_location_from_bucket_file(bucket_name: str, file_name: str) -> str:
        return f"{bucket_name}/{file_name}"
    
    def get_bucket_file_from_s3_location(s3_location: str) -> Tuple[str, str]:
        bucket, file_name = s3_location.split('/')[0], "/".join(s3_location.split('/')[1:])
        return bucket, file_name
    