
import os
import json
import http.client
import boto3
from datetime import datetime

# Lambda 환경 변수에서 설정값을 가져옵니다.
TARGET_URL = os.environ['TARGET_URL']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

# URL에서 호스트와 경로를 분리합니다.
try:
    url_parts = TARGET_URL.replace('http://', '').replace('https://', '').split('/', 1)
    HOST = url_parts[0]
    PATH = '/' + (url_parts[1] if len(url_parts) > 1 else '')
except IndexError:
    print(f"Invalid TARGET_URL format: {TARGET_URL}")
    raise

sns_client = boto3.client('sns')

def lambda_handler(event, context):
    """
    지정된 URL의 상태를 확인하고, 비정상일 경우 SNS로 메시지를 발행합니다.
    """
    print(f"Performing health check for {TARGET_URL}...")
    
    conn = None
    try:
        # 기본 라이브러리인 http.client를 사용하여 외부 라이브러리 의존성 없음
        if TARGET_URL.startswith('https://'):
            conn = http.client.HTTPSConnection(HOST, timeout=10)
        else:
            conn = http.client.HTTPConnection(HOST, timeout=10)
            
        conn.request("GET", PATH)
        response = conn.getresponse()
        
        status_code = response.status
        print(f"Received status code: {status_code}")
        
        if 200 <= status_code < 300:
            print("Health check successful.")
            return {
                'statusCode': 200,
                'body': json.dumps('Health check successful!')
            }
        else:
            # 2xx 응답이 아니면 실패로 간주
            raise Exception(f"Health check failed with status code: {status_code}")

    except Exception as e:
        error_message = f"Health check failed for {TARGET_URL}. Reason: {str(e)}"
        print(error_message)
        
        # SNS로 보낼 메시지 형식 정의
        sns_message = {
            "service": "EC2 Web Service",
            "url": TARGET_URL,
            "status": "DOWN",
            "reason": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # SNS 토픽으로 알람 메시지 발행
        try:
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"Service Down Alert: {TARGET_URL}",
                Message=json.dumps({'default': json.dumps(sns_message)}),
                MessageStructure='json'
            )
            print(f"Successfully published failure alert to SNS topic: {SNS_TOPIC_ARN}")
        except Exception as sns_error:
            print(f"Failed to publish to SNS. Error: {str(sns_error)}")
            # SNS 발행 실패 시에도 에러 응답 반환
            return {
                'statusCode': 500,
                'body': json.dumps(f'Health check failed, and SNS notification also failed: {str(sns_error)}')
            }
            
        return {
            'statusCode': 500,
            'body': json.dumps(error_message)
        }
        
    finally:
        if conn:
            conn.close()
