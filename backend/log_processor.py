# backend/log_processor.py

import json
import os
import requests
from datetime import datetime

# --- 설정 --- #
LOG_DIR = os.path.join(os.path.dirname(__file__), 'log', 'nginx')
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_notification(log_data):
    """주어진 로그 데이터를 기반으로 Slack 알림을 전송합니다."""
    if not SLACK_WEBHOOK_URL:
        print("[에러] SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.")
        return

    # Slack 메시지 서식을 보기 좋게 구성합니다. (Block Kit)
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
                    {"type": "mrkdwn", "text": f"*Timestamp:*\n`{log_data.get('timestamp')}`"},
                    {"type": "mrkdwn", "text": f"*Status Code:*\n`{log_data.get('status')}`"},
                    {"type": "mrkdwn", "text": f"*Client IP:*\n`{log_data.get('client_ip')}`"},
                    {"type": "mrkdwn", "text": f"*Request:*\n`{log_data.get('request_method')} {log_data.get('request_uri')}`"}
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
        response.raise_for_status()  # 2xx 응답이 아닐 경우 예외 발생
        print(f"[알림 성공] 5xx 에러 로그를 Slack으로 전송했습니다.")
    except requests.exceptions.RequestException as e:
        print(f"[알림 실패] Slack으로 알림을 보내는 중 오류가 발생했습니다: {e}")


def process_logs_for_date(date_str):
    """특정 날짜의 로그 파일을 처리합니다."""
    log_file_name = f"access-{date_str}.log"
    log_file_path = os.path.join(LOG_DIR, log_file_name)

    if not os.path.exists(log_file_path):
        print(f"로그 파일이 존재하지 않습니다: {log_file_path}")
        return

    print(f"로그 처리 시작: {log_file_path}")
    
    # TODO: 이미 처리한 로그를 다시 처리하지 않도록 파일의 마지막 위치를 기록하고, 그 이후부터 읽도록 구현해야 합니다.
    with open(log_file_path, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line.strip())
                
                # 5xx 에러 감지
                if 'status' in log_entry and 500 <= int(log_entry['status']) < 600:
                    send_notification(log_entry)

            except (json.JSONDecodeError, ValueError):
                # JSON 파싱 오류 또는 int 변환 오류를 함께 처리
                print(f"로그 라인 처리 오류: {line.strip()}")
            except Exception as e:
                print(f"알 수 없는 오류 발생: {e}")

    print(f"로그 처리 완료: {log_file_path}")

if __name__ == "__main__":
    # --- DEBUG: 모든 환경 변수 출력 ---
    import os
    print("--- All Environment Variables ---")
    for key, value in os.environ.items():
        print(f'{key}={value}')
    print("---------------------------------")
    # ------------------------------------

    # 스크립트 실행 시 오늘 날짜의 로그를 처리합니다.
    # Cronjob으로 실행될 것을 가정합니다.
    if not SLACK_WEBHOOK_URL:
        print("[시작 실패] SLACK_WEBHOOK_URL 환경 변수가 필요합니다.")
    else:
        today_str = datetime.now().strftime('%Y-%m-%d')
        process_logs_for_date(today_str)