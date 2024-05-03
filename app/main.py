from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from contextlib import asynccontextmanager
from datetime import datetime
import docker
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any


class ScheduleJob(BaseModel):
    id: str
    container_name: str
    trigger: str
    trigger_args: Any


def update_docker_image(container_name: str):
    print('')
    print(datetime.now())
    print(f"updating docker image for container {container_name}", flush=True)
    client = docker.from_env()
    client.containers.run(image="containrrr/watchtower", command=["--run-once", container_name], auto_remove=True, detach=True, remove=True, volumes=['/var/run/docker.sock:/var/run/docker.sock'])
    client.images.prune()


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:////data/woc.sqlite')
}

job_defaults = {
    'coalesce': True,
    'replace_existing': True
}

scheduler = BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)


@app.get("/scheduler/jobs/")
async def get_schedule_jobs():
    print('')
    print(datetime.now())
    print('Jobs:')
    jobs = []
    for job in scheduler.get_jobs():
        print(u'    id: %s, %s' % (job.id, job))
        jobs.append(u'id: %s, %s' % (job.id, job))
    return jobs


@app.post("/scheduler/jobs/")
async def add_schedule_job(job: ScheduleJob):
    if scheduler.get_job(job.id) != None:
        scheduler.remove_job(job.id)
    scheduler.add_job(id=job.id, func=update_docker_image, args=[job.container_name], trigger=job.trigger, **job.trigger_args)
    return await get_schedule_jobs()


@app.get("/scheduler/jobs/{job_id}")
async def get_schedule_job(job_id: str):
    print('')
    print(datetime.now())
    job = scheduler.get_job(job_id)
    if job == None:
        print('None', flush=True)
        return 'None'
    print(u'%s' % job, flush=True)
    return u'%s' % job


@app.delete("/scheduler/jobs/{job_id}")
async def del_schedule_job(job_id: str):
    print('')
    print(datetime.now())
    try:
        scheduler.remove_job(job_id)
        print('True', flush=True)
        return 'True'
    except:
        print('False', flush=True)
        return 'False'
