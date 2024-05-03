from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any


class ScheduleJob(BaseModel):
    id: str
    container_name: str
    trigger: str
    trigger_args: Any


def update_docker_image(container_name: str):
    print(f"Updating docker image for container {container_name}")


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


@app.get("/")
async def home():
    return {"message": "Hello Woc!"}


@app.get("/schedule/jobs/")
async def get_schedule_jobs():
    scheduler.print_jobs()
    return {"jobs": len(scheduler.get_jobs())}


@app.post("/schedule/jobs/")
async def create_schedule_job(job: ScheduleJob):
    scheduler.add_job(id=job.id, func=update_docker_image, args=[job.container_name], trigger=job.trigger, **job.trigger_args)
    return {"jobs": len(scheduler.get_jobs())}
