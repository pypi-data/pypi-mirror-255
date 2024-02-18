from typing import Optional, Dict, Any
import json
from my_aws_helpers.errors import *

class API:
    def response(code: int, body: Optional[str] = None):
        return {
            "statusCode": code, 
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": body,
        }

    def parse_payload(event: Dict[str, Any]):
        payload = {}
        if event.get("queryParameters"): payload["queryParameters"] = event["queryParameters"]
        if event.get("pathParameters"): payload["pathParameters"] = event["pathParameters"]
        if event.get("body"): payload["body"] = json.loads(event["body"])
        return payload
    
    def handle_error_response(func):
        def wrapper(event, context):
            try:
                response = func(event, context)        
                return API.response(
                    code = 200, 
                    body = json.dumps(response) 
                )
            except ClientError as e:
                return API.response(
                    code = 400, 
                    body = json.dumps({"Error": f"{e}"}) 
                )
            except NotFoundError as e:
                return API.response(
                    code = 404, 
                    body = json.dumps({"Error": f"{e}"}) 
                )
            except ServerError as e:
                return API.response(
                    code = 500, 
                    body = json.dumps({"Error": f"{e}"}) 
                )
            except Exception as e:
                return API.response(
                    code = 500, 
                    body = json.dumps({"Error": f"{e}"}) 
                )
        return wrapper
