from django_cron import CronJobBase, Schedule
from stela_control.tasks import schedule_blogpost


class SchedulePost(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'stela_control.tasks.schedule_blogpost'

    def do(self):
        schedule_blogpost()