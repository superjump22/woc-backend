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
    client = docker.from_env()
    try:
        oldId = client.images.get('containrrr/watchtower').id
    except:
        oldId = None
    newId = client.images.pull('containrrr/watchtower').id
    watchtowerPulled = oldId != newId
    if watchtowerPulled:
        client.images.prune()
        print('')
        print(datetime.now())
        print('containrrr/watchtower updated', flush=True)
    try:
        oldId = client.images.get('superjump22/woc-backend').id
    except:
        oldId = None
    newId = client.images.pull('superjump22/woc-backend').id
    wocPulled = oldId != newId
    if wocPulled:
        client.containers.run(image='containrrr/watchtower', command=['--run-once', '--cleanup', '--remove-volumes', '--no-pull', '--stop-timeout', '30s', 'woc-backend'],
                              auto_remove=True, detach=True, remove=True, volumes=['/var/run/docker.sock:/var/run/docker.sock'])
        print('')
        print(datetime.now())
        print('superjump22/woc-backend updated', flush=True)


def update_image(container_name: str):
    if container_name == '' or container_name == 'woc-backend':
        return
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        tags = container.image.tags
        pulled = False
        for tag in tags:
            if tag.startswith('superjump22/woc-backend'):
                continue
            if not tag.startswith('superjump22/'):
                continue
            if client.images.pull(tag).id == container.image.id:
                continue
            else:
                pulled = True
        if pulled:
            client.containers.run(image='containrrr/watchtower', command=['--run-once', '--cleanup', '--remove-volumes', '--no-pull', '--stop-timeout', '30s', container_name],
                                  auto_remove=True, detach=True, remove=True, volumes=['/var/run/docker.sock:/var/run/docker.sock'])
            print('')
            print(datetime.now())
            print(f'{container_name} updated', flush=True)
    except:
        return


def update_all():
    try:
        client = docker.from_env()
        containers = client.containers.list()
        pulled = False
        for container in containers:
            tags = container.image.tags
            for tag in tags:
                if tag.startswith('superjump22/woc-backend'):
                    continue
                if not tag.startswith('superjump22/'):
                    continue
                if client.images.pull(tag).id == container.image.id:
                    continue
                else:
                    pulled = True
        if pulled:
            client.containers.run(image='containrrr/watchtower', command=['--run-once', '--cleanup', '--remove-volumes', '--no-pull', '--stop-timeout', '30s', '--disable-containers', 'woc-backend'],
                                  auto_remove=True, detach=True, remove=True, volumes=['/var/run/docker.sock:/var/run/docker.sock'])
            print('')
            print(datetime.now())
            print(f'all running containers updated', flush=True)
    except:
        return


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
    client = docker.from_env()
    client.images.prune()
    update_self()
    scheduler.start()
    if scheduler.get_job('woc-backend') == None:
        scheduler.add_job(id='woc-backend', func=update_self,
                          trigger='interval', minutes=30)
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)


@app.get('/scheduler/jobs/')
async def get_schedule_jobs():
    print('')
    print(datetime.now())
    print('Jobs:')
    jobs = []
    for job in scheduler.get_jobs():
        print(u'    id: %s, %s' % (job.id, job))
        jobs.append({'id': job.id, 'content': u'%s' % job})
    return jobs


@app.post('/scheduler/jobs/')
async def add_schedule_job(job: ScheduleJob):
    if scheduler.get_job(job.id) != None:
        scheduler.remove_job(job.id)
    if job.container_name == None:
        scheduler.add_job(id=job.id, func=update_all,
                          trigger=job.trigger, **job.trigger_args)
    else:
        scheduler.add_job(id=job.id, func=update_image, args=[job.container_name],
                          trigger=job.trigger, **job.trigger_args)
    return await get_schedule_jobs()


@app.get('/scheduler/jobs/{job_id}')
async def get_schedule_job(job_id: str):
    print('')
    print(datetime.now())
    job = scheduler.get_job(job_id)
    if job == None:
        print('None', flush=True)
        return 'None'
    print(u'%s' % job, flush=True)
    return {'id': job.id, 'content': u'%s' % job}


@app.delete('/scheduler/jobs/{job_id}')
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
