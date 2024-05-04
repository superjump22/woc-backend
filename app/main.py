# coding=utf-8
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
    container_name: str | None
    trigger: str
    trigger_args: Any


def update_self():
    print('')
    print(datetime.now())
    print("updating containrrr/watchtower & superjump22/woc-backend", flush=True)
    client = docker.from_env()
    client.images.pull("containrrr/watchtower")
    client.images.pull("superjump22/woc-backend")
    client.images.prune()
    client.containers.run(image="containrrr/watchtower", command=["--run-once", 'woc-backend'],
                          auto_remove=True, detach=True, remove=True, volumes=['/var/run/docker.sock:/var/run/docker.sock'])


def update_docker_image(container_name: str):
    print('')
    print(datetime.now())
    print(f"updating docker image for container {container_name}", flush=True)
    client = docker.from_env()
    client.containers.run(image="containrrr/watchtower", command=["--run-once", container_name],
                          auto_remove=True, detach=True, remove=True, volumes=['/var/run/docker.sock:/var/run/docker.sock'])
    client.images.prune()


def update_docker_images():
    print('')
    print(datetime.now())
    print(f"updating docker images for all containers", flush=True)
    client = docker.from_env()
    client.containers.run(image="containrrr/watchtower", command="--run-once",
                          auto_remove=True, detach=True, remove=True, volumes=['/var/run/docker.sock:/var/run/docker.sock'])
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
    update_self()
    scheduler.start()
    if scheduler.get_job('woc-backend') == None:
        scheduler.add_job(id='woc-backend', func=update_self,
                          trigger='interval', minutes=30)
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
        jobs.append({"id": job.id, "content": u'%s' % job})
    return jobs


@app.post("/scheduler/jobs/")
async def add_schedule_job(job: ScheduleJob):
    if scheduler.get_job(job.id) != None:
        scheduler.remove_job(job.id)
    if job.container_name == None:
        scheduler.add_job(id=job.id, func=update_docker_images,
                          trigger=job.trigger, **job.trigger_args)
    else:
        scheduler.add_job(id=job.id, func=update_docker_image, args=[job.container_name],
                          trigger=job.trigger, **job.trigger_args)
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
    return {"id": job.id, "content": u'%s' % job}


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
