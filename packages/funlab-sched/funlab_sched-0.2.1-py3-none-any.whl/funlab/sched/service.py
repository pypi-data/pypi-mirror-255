
import logging
import threading
import time
from dataclasses import fields
from datetime import datetime, timedelta

from apscheduler.events import (EVENT_ALL, EVENT_JOB_ADDED, EVENT_JOB_MODIFIED,
                                EVENT_JOB_REMOVED, EVENT_SCHEDULER_PAUSED,
                                EVENT_SCHEDULER_RESUMED,
                                EVENT_SCHEDULER_SHUTDOWN, JobEvent,
                                JobExecutionEvent, JobSubmissionEvent,
                                SchedulerEvent)
from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template, request
from flask_login import login_required

from funlab.flaskr.plugin import ServicePlugin
from funlab.flaskr.menu import MenuItem
from funlab.sched.task import SchedTask
from funlab.utils import plugin, log

mylogger = log.get_logger(__name__, level=logging.INFO)

class SchedService(ServicePlugin):
    def __init__(self, app, trace_job_status=True):
        super().__init__(app)
        self._task_lock = threading.Lock()
        self._scheduler = BackgroundScheduler()
        self.sched_tasks: dict[str, SchedTask] = {}
        self._load_config()
        self._load_tasks()
        self.start_service()
        self.register_routes()
        if trace_job_status:
            self._scheduler.add_listener(self._listener_all_event, EVENT_ALL)
        mi = MenuItem(title='Sched Tasks',
                icon='<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-calendar-stats" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">\
                        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>\
                        <path d="M11.795 21h-6.795a2 2 0 0 1 -2 -2v-12a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v4"></path>\
                        <path d="M18 14v4h4"></path>\
                        <path d="M18 18m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0"></path>\
                        <path d="M15 3v4"></path>\
                        <path d="M7 3v4"></path>\
                        <path d="M3 11h16"></path>\
                        </svg>',
                href=f'/{self.name}/tasks', admin_only=True)
        self.app.add_adminmenu(mi)

    def _load_config(self):
        self._scheduler.configure(**self.plugin_config.as_dict())

    def _load_tasks(self):
        """
        Load the job from the plugin class.
        """
        tasks = plugin.load_plugins(group="funlab_sched_task")
        for task in tasks.values():
            task: SchedTask = task(self)
            if (next_plan:=task.plan_schedule()):
                task.task_def.update(next_plan)
            job: Job = self._scheduler.get_job(task.id)
            if not job:
                job = self._scheduler.add_job(**task.task_def)
                self._align_task_job(None, task, job)
            else:
                if task.task_def.get("replace_existing", False):
                    job.modify(**task.task_def)
                    pass
            mylogger.info(f"Sched loaded task {task.id}")

    def _align_task_job(self, old_task, new_task, new_job):
        if old_task:
            self.sched_tasks.pop(old_task.id, None)
        if new_task and new_job:
            new_task.id = new_job.id
            setattr(new_task, "job", new_job)
            self.sched_tasks[new_task.id] = new_task

    def _listener_all_event(self, event):
        """
        keep tracing of job execution
        """
        # with self._task_lock:
        time.sleep(1)
        if isinstance(event, JobSubmissionEvent):
            event: JobSubmissionEvent = event
            self.sched_tasks[
                event.job_id
            ].last_status = (
                f'summited:{event.scheduled_run_times[0].strftime("%y-%m-%d %H:%M:%S")}'
            )
        elif isinstance(event, JobExecutionEvent):
            event: JobExecutionEvent = event
            if event.exception:
                self.sched_tasks[
                    event.job_id
                ].last_status = f'failed:{event.scheduled_run_time.strftime("%y-%m-%d %H:%M:%S")},{event.exception}'
            else:
                self.sched_tasks[event.job_id].last_status = (
                    f'executed:{event.scheduled_run_time.strftime("%y-%m-%d %H:%M:%S")}'
                    + (f"ret={event.retval}" if event.retval is not None else "")
                )  # {'status': 'executed', 'time': event.scheduled_run_time, 'retval': event.retval}
        elif isinstance(event, JobEvent):
            event: JobEvent = event
            # if event.code == EVENT_JOB_ADDED:
            #     self.sched_tasks[event.job_id].last_status = 'added'
            # elif event.code == EVENT_JOB_REMOVED:
            #     self.sched_tasks[event.job_id].last_status = 'removed'

        elif isinstance(event, SchedulerEvent):
            if event.code == EVENT_SCHEDULER_PAUSED:
                status = "Paused"
            elif event.code == EVENT_SCHEDULER_RESUMED:
                status = "Waiting"
            elif event.code == EVENT_SCHEDULER_SHUTDOWN:
                status = "Shutdown"
            else:
                status = ""
            if status:
                for task in self.sched_tasks.values():
                    task.last_status = status

    def register_routes(self):
        @self.blueprint.route("/tasks", methods=["GET", "POST"])
        @login_required
        def tasks():
            def run_task(task):
                task_kwargs = {}
                for field in fields(task):
                    if arg_value := request.form.get(field.name, None):
                        task_kwargs.update({field.name: arg_value})
                job = self._scheduler.get_job(task_id)
                if job:
                    job.modify(
                        next_run_time=datetime.now() + timedelta(seconds=1),
                        kwargs=task_kwargs,
                    )
                else:
                    task.task_def.update({"kwargs": task_kwargs})
                    task.task_def.update(
                        {"next_run_time": datetime.now() + timedelta(seconds=1)}
                    )
                    job = self._scheduler.add_job(**task.task_def)
                    self._align_task_job(task, task, job)

            if task_id:=request.form.get('id'):
                run_task(self.sched_tasks[task_id])
            forms = {}
            for task in self.sched_tasks.values():
                form = request.form if (request.form and task.id in request.form) else None
                if formcls := task.generate_params_formclass():
                    forms[task.id] = formcls(formdata=form)  # task.form_class(formdata=form)
            return render_template(
                "tasks.html", tasks=self.sched_tasks.values(), forms=forms
            )

    @property
    def running(self):
        """Get true whether the scheduler is running."""
        return self._scheduler.running

    @property
    def state(self):
        """Get the state of the scheduler."""
        return self._scheduler.state

    @property
    def scheduler(self):
        return self._scheduler

    @property
    def task(self):
        """Get the base scheduler decorator"""
        return self._scheduler.scheduled_job

    def start_service(self, paused=False):
        """Start the configured executors and job stores and begin processing scheduled jobs.
        Args:
            paused (bool, optional): if True, don't start job processing until resume is called. Defaults to False.
        """
        self._scheduler.start(paused=paused)

    def stop_service(self, wait=True):
        """Shuts down the scheduler, along with its executors and job stores. Does not interrupt any currently running jobs.
        Args:
            wait (bool, optional): True to wait until all currently executing jobs have finished. Defaults to True.
        """
        self._scheduler.shutdown(wait)

    def restart_service(self, wait=True):
        self.stop_service(wait=wait)
        self.start_service()

    def reload_service(self, wait=True):
        self.stop_service(wait=wait)
        self._load_config()
        self._load_tasks()
        self.start_service()

    def pause(self):
        """
        Pause job processing in the scheduler.
        This will prevent the scheduler from waking up to do job processing until :meth:`resume`
        is called. It will not however stop any already running job processing.
        """
        self._scheduler.pause()

    def resume(self):
        """
        Resume job processing in the scheduler.
        """
        self._scheduler.resume()
