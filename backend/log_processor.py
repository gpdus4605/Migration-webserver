# backend/log_processor.py

import json
import os
import requests
from datetime import datetime

# --- 설정 --- #
LOG_DIR = os.path.join(os.path.dirname(__file__), 'log', 'nginx')
STATE_FILE_PATH = os.path.join(LOG_DIR, 'last_processed_position.txt')
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_notification(log_data):
    """주어진 로그 데이터를 기반으로 Slack 알림을 전송합니다."""
    if not SLACK_WEBHOOK_URL:
        print("[에러] SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.")
        return

    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":alert: 5xx 서버 에러 발생!"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Timestamp:*
`{log_data.get('timestamp')}`"},
                    {"type": "mrkdwn", "text": f"*Status Code:*
`{log_data.get('status')}`"},
                    {"type": "mrkdwn", "text": f"*Client IP:*
`{log_data.get('client_ip')}`"},
                    {"type": "mrkdwn", "text": f"*Request:*
`{log_data.get('request_method')} {log_data.get('request_uri')}`"}
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"User Agent: `{log_data.get('user_agent')}`"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        response.raise_for_status()
        print(f"[알림 성공] 5xx 에러 로그를 Slack으로 전송했습니다.")
    except requests.exceptions.RequestException as e:
        print(f"[알림 실패] Slack으로 알림을 보내는 중 오류가 발생했습니다: {e}")

def get_last_position():
    """상태 파일에서 마지막으로 처리한 파일 위치를 읽어옵니다."""
    if not os.path.exists(STATE_FILE_PATH):
        return 0
    with open(STATE_FILE_PATH, 'r') as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def save_last_position(position):
    """상태 파일에 마지막으로 처리한 파일 위치를 저장합니다."""
    with open(STATE_FILE_PATH, 'w') as f:
        f.write(str(position))

def process_logs_for_date(date_str):
    """특정 날짜의 로그 파일을 처리합니다."""
    log_file_name = f"access-{date_str}.log"
    log_file_path = os.path.join(LOG_DIR, log_file_name)

    if not os.path.exists(log_file_path):
        print(f"로그 파일이 존재하지 않습니다: {log_file_path}")
        return

    print(f"로그 처리 시작: {log_file_path}")
    
    last_position = get_last_position()
    current_size = os.path.getsize(log_file_path)

    # 로그 파일이 초기화되었는지 확인 (파일 크기가 줄어든 경우)
    if last_position > current_size:
        print("로그 파일이 초기화되었습니다. 처음부터 다시 처리합니다.")
        last_position = 0

    with open(log_file_path, 'r') as f:
        f.seek(last_position)
        new_logs = f.readlines()
        
        for line in new_logs:
            try:
                log_entry = json.loads(line.strip())
                
                if 'status' in log_entry and 500 <= int(log_entry['status']) < 600:
                    send_notification(log_entry)

            except (json.JSONDecodeError, ValueError):
                print(f"로그 라인 처리 오류: {line.strip()}")
            except Exception as e:
                print(f"알 수 없는 오류 발생: {e}")

    save_last_position(current_size)
    print(f"로그 처리 완료: {log_file_path}")

if __name__ == "__main__":
    import os
    print("--- All Environment Variables ---")
    for key, value in os.environ.items():
        print(f'{key}={value}')
    print("---------------------------------")

    if not SLACK_WEBHOOK_URL:
        print("[시작 실패] SLACK_WEBHOOK_URL 환경 변수가 필요합니다.")
    else:
        today_str = datetime.now().strftime('%Y-%m-%d')
        process_logs_for_date(today_str)
