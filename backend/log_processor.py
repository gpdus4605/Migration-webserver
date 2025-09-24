# backend/log_processor.py

import json
import os
from datetime import datetime

# --- 설정 --- #
LOG_DIR = os.path.join(os.path.dirname(__file__), 'log', 'nginx')
# TODO: Slack/Notion Webhook URL을 환경 변수 등에서 가져오도록 설정해야 합니다.
NOTIFICATION_WEBHOOK_URL = ""

def send_notification(log_data):
    """주어진 로그 데이터를 기반으로 알림을 전송합니다."""
    # TODO: 실제 Slack/Notion API 호출 로직을 구현해야 합니다.
    print(f"[알림 발생] 5xx 에러가 감지되었습니다: {log_data}")
    # 예시: requests.post(NOTIFICATION_WEBHOOK_URL, json={"text": f"5xx Error: {log_data}"})

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

            except json.JSONDecodeError:
                print(f"JSON 파싱 오류: {line.strip()}")
            except Exception as e:
                print(f"알 수 없는 오류 발생: {e}")

    print(f"로그 처리 완료: {log_file_path}")

if __name__ == "__main__":
    # 스크립트 실행 시 오늘 날짜의 로그를 처리합니다.
    # Cronjob으로 실행될 것을 가정합니다.
    today_str = datetime.now().strftime('%Y-%m-%d')
    process_logs_for_date(today_str)
