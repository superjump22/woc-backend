# woc-backend

```sh
# run
docker run --rm -d --name woc-backend \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v woc-backend:/data \
    -p 10880:10880 \
    -e TZ=Asia/Shanghai \
    superjump22/woc-backend
```

```sh
# get jobs
curl http://127.0.0.1:10880/scheduler/jobs/
```

```sh
# add a new job
curl -X POST -H "Content-Type: application/json" -d '{"id": "v2raya", "container_name": "v2raya", "trigger": "cron", "trigger_args": {"month":"5", "day":"1st fri", "hour":"19", "minute": "00"}}' http://127.0.0.1:10880/scheduler/jobs/
```
