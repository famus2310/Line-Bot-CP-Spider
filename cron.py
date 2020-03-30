from apscheduler.schedulers.blocking import BlockingScheduler
import os
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=30)
def timed_job():
    print('This job is run every 30 minutes.')
    os.system("python scraper.py")

sched.start()
