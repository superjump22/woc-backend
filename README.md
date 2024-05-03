# woc-backend

docker run -d --name test -v woc_backend_data:/data -p 10880:10880 -e TZ=Asia/Shanghai superjump22/woc-backend
curl http://127.0.0.1:10880/scheduler/jobs/
curl -X POST -H "Content-Type: application/json" -d '{"id": "id", "container_name": "container_name", "trigger": "cron", "trigger_args": {"month":"5", "day":"1st fri", "hour":"18"}}' http://127.0.0.1:10880/scheduler/jobs/
