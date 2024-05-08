from datetime import datetime
import docker
from fastapi import APIRouter
import json
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite import insert


Base = declarative_base()


class ModInfo(Base):
    __tablename__ = 'mod_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mod_id = Column(String[32], index=True, unique=True)
    info = Column(Text)
    create_at = Column(DateTime)
    update_at = Column(DateTime)

    def __repr__(self):
        return f"<ModInfo(mod_id={self.mod_id}, info={self.info})>"


engine = create_engine(
    'sqlite:////data/dst.sqlite?check_same_thread=False', echo=True)
Base.metadata.create_all(engine, checkfirst=True)
Session = sessionmaker(bind=engine)
router = APIRouter(
    prefix="/dst/mod",
    responses={404: {"description": "Not found"}},
)


@router.get("/info/")
async def get_info_list(mod_id_list: list[str]):
    session = Session()
    mod_info_list = session.query(ModInfo).filter(
        ModInfo.mod_id.in_(mod_id_list)).all()
    res = {}
    for mod_info in mod_info_list:
        res[mod_info.mod_id] = json.loads(mod_info.info)
    return res


@router.get("/info/{mod_id}")
async def get_info(mod_id: str):
    res = await get_info_list([mod_id])
    return res.get(mod_id, [])


@router.post("/info/")
async def update_info_list(mod_id_list: list[str]):
    print(mod_id_list)
    client = docker.from_env()
    client.images.pull('superjump22/woc-backend-dst')
    client.images.prune()
    container = client.containers.run(image='superjump22/woc-backend-dst', command=['tail', '-f', '/dev/null'], auto_remove=True, detach=True, remove=True, volumes={
                                      'woc-dst-mods': {'bind': '/dst/mods', 'mode': 'ro'}, 'woc-dst-ugc_mods': {'bind': '/dst/ugc_mods', 'mode': 'ro'}})
    data = []
    try:
        for mod_id in mod_id_list:
            container.exec_run(
                f'cp /dst/ugc_mods/content/322330/{mod_id}/modinfo.lua /tmp/{mod_id}.lua')
            container.exec_run(
                f'cp /dst/mods/workshop-{mod_id}/modinfo.lua /tmp/{mod_id}.lua')
            container.exec_run(
                cmd=['sh', '-c', f"echo '\\r' >> /tmp/{mod_id}.lua"])
            container.exec_run(
                cmd=['sh', '-c', f'''echo "local rapidjson = require('rapidjson')\\r" >> /tmp/{mod_id}.lua'''])
            container.exec_run(
                cmd=['sh', '-c', f'''echo "print(rapidjson.encode(configuration_options))\\r" >> /tmp/{mod_id}.lua'''])
            json_str = container.exec_run(
                f"lua /tmp/{mod_id}.lua").output.decode('utf-8')
            try:
                item = json.loads(json_str)
            except:
                item = []
            data.append({"mod_id": mod_id, "info": json.dumps(item),
                       "create_at": datetime.now(), "update_at": datetime.now()})
    finally:
        container.stop()
    print(data)
    table = ModInfo.__table__
    stmt = insert(table).values(data)
    session = Session()
    session.execute(stmt.on_conflict_do_update(
        index_elements=['mod_id'],
        set_=dict(info=stmt.excluded.info, update_at=stmt.excluded.update_at)
    ))
    session.commit()


@router.post("/info/{mod_id}")
async def update_info(mod_id: str):
    return await update_info_list([mod_id])
