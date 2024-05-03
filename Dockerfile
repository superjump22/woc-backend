FROM python:slim-bookworm

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

VOLUME ["/data"]

EXPOSE 10880/tcp

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10880"]
