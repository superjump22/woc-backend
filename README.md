# woc-backend

docker run --rm -d --name woc-backend -v /var/run/docker.sock:/var/run/docker.sock -v woc-backend:/data -p 10880:10880 -e TZ=Asia/Shanghai superjump22/woc-backend
curl http://127.0.0.1:10880/scheduler/jobs/
curl -X POST -H "Content-Type: application/json" -d '{"id": "jovial_chandrasekhar", "container_name": "jovial_chandrasekhar", "trigger": "cron", "trigger_args": {"month":"5", "day":"1st fri", "hour":"17", "minute": "55"}}' http://127.0.0.1:10880/scheduler/jobs/
