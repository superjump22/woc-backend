from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from contextlib import asynccontextmanager
from fastapi import FastAPI

from datetime import datetime


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

job_defaults = {
    'coalesce': True
}

scheduler = BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults)


def tick():
    with open("text.txt", "a") as file:
        file.write("\n")
        file.write('Tick! The time is: %s' % datetime.now())


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(tick, 'interval', seconds=5)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}
