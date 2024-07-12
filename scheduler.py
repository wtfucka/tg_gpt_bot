import time
import schedule

from proxyai_balance import check_balance


def run_scheduler():
    schedule.every(3).hours.do(check_balance)
    while True:
        schedule.run_pending()
        time.sleep(60)
