import docker
from fastapi import APIRouter
import json


router = APIRouter(
    prefix="/dst/mod",
    responses={404: {"description": "Not found"}},
)


@router.get("/info/")
async def get_info_list(mod_id_list: list[str]):
    client = docker.from_env()
    json_str = client.containers.run(image='alpine', command=['cat', '/dst/mods/info.json'], auto_remove=True,
                                     remove=True, volumes={'woc-dst-mods': {'bind': '/dst/mods', 'mode': 'ro'}})
    data = json.loads(json_str)
    return {k: data[k] for k in mod_id_list if k in data}


@router.get("/info/{mod_id}")
async def get_info(mod_id: str):
    return await get_info_list([mod_id])


@router.post("/info/")
async def update_info(mod_id_list: list[str]):
    client = docker.from_env()
    client.images.pull('superjump22/woc-backend-dst')
    client.images.prune()
    container = client.containers.run(image='superjump22/woc-backend-dst', command=['tail', '-f', '/dev/null'], auto_remove=True, detach=True, remove=True, volumes={'woc-dst-mods': {'bind': '/dst/mods', 'mode': 'rw'}, 'woc-dst-ugc_mods': {'bind': '/dst/ugc_mods', 'mode': 'ro'}})
    json_str = container.exec_run('cat /dst/mods/info.json').output.decode('utf-8')
    try:
        data = json.loads(json_str)
    except:
        data = {}
    for mod_id in mod_id_list:
        container.exec_run(f'cp /dst/ugc_mods/content/322330/{mod_id}/modinfo.lua /tmp/{mod_id}.lua')
        container.exec_run(f'cp /dst/mods/workshop-{mod_id}/modinfo.lua /tmp/{mod_id}.lua')
        container.exec_run(cmd=['sh', '-c', f"echo '\\r' >> /tmp/{mod_id}.lua"])
        container.exec_run(cmd=['sh', '-c', f'''echo "local rapidjson = require('rapidjson')\\r" >> /tmp/{mod_id}.lua'''])
        container.exec_run(cmd=['sh', '-c', f'''echo "print(rapidjson.encode(configuration_options))\\r" >> /tmp/{mod_id}.lua'''])
        json_str = container.exec_run(f"lua /tmp/{mod_id}.lua").output.decode('utf-8')
        try:
            item = json.loads(json_str)
        except:
            item = {}
        data[mod_id] = item
    container.exec_run(f'''echo \'{json.dumps(data)}\' > /dst/mods/info.json''')


@router.post("/info/{mod_id}")
async def update_info(mod_id: str):
    return await update_info([mod_id])
