
import os
import json
import http.client

# Lambda 환경 변수에서 슬랙 Webhook URL을 가져옵니다.
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']

def lambda_handler(event, context):
    """
    SNS 이벤트를 받아 파싱한 후, 슬랙으로 알림을 보냅니다.
    """
    print("Received event from SNS:", json.dumps(event))
    
    conn = None
    try:
        # SNS 이벤트에서 실제 메시지를 추출합니다.
        sns_message_str = event['Records'][0]['Sns']['Message']
        sns_message = json.loads(sns_message_str)
        
        subject = event['Records'][0]['Sns'].get('Subject', 'EC2 Health Alert')
        
        # 슬랙 메시지 형식을 보기 좋게 꾸밉니다. (Attachment 형식)
        slack_message = {
            "attachments": [
                {
                    "color": "#danger", # 빨간색으로 표시
                    "pretext": f":alert: *{subject}*",
                    "fields": [
                        {"title": "Service", "value": sns_message.get("service", "N/A"), "short": True},
                        {"title": "Status", "value": sns_message.get("status", "N/A"), "short": True},
                        {"title": "Endpoint", "value": sns_message.get("url", "N/A"), "short": False},
                        {"title": "Reason", "value": sns_message.get("reason", "N/A"), "short": False},
                        {"title": "Timestamp (UTC)", "value": sns_message.get("timestamp", "N/A"), "short": False}
                    ],
                    "footer": "Automated Health Check Alert"
                }
            ]
        }
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing SNS message: {e}")
        # 메시지 파싱 실패 시, 원본 이벤트를 그대로 슬랙으로 보냅니다.
        slack_message = {
            "text": ":warning: *An un-parsable alert was received from SNS.*\n>>>" + json.dumps(event)
        }

    # 슬랙으로 메시지를 보냅니다.
    try:
        # Webhook URL에서 호스트와 경로를 분리합니다.
        webhook_url_parts = SLACK_WEBHOOK_URL.replace('https://', '').split('/', 1)
        host = webhook_url_parts[0]
        path = '/' + webhook_url_parts[1]

        conn = http.client.HTTPSConnection(host)
        
        conn.request(
            "POST",
            path,
            body=json.dumps(slack_message),
            headers={"Content-Type": "application/json"}
        )
        
        response = conn.getresponse()
        response_body = response.read().decode()
        
        if response.status == 200:
            print("Successfully sent message to Slack.")
        else:
            # 슬랙 전송 실패 시 로그를 남깁니다.
            print(f"Failed to send message to Slack. Status: {response.status}, Body: {response_body}")

    except Exception as e:
        print(f"Error sending message to Slack: {e}")
        return {'statusCode': 500, 'body': json.dumps(f"Error: {e}")}
    
    finally:
        if conn:
            conn.close()

    return {'statusCode': 200, 'body': json.dumps("Message sent to Slack successfully.")}
