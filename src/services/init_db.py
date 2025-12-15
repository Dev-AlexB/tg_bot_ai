import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from db.database import async_session, engine
from models.models import Base, Video, VideoSnapshot


JSON_FILE = "videos.json"


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


def normalize_dt(data: dict):
    datetime_fields = {
        "video_created_at",
        "created_at",
        "updated_at",
    }
    for key in datetime_fields:
        if key in data:
            data[key] = datetime.fromisoformat(data[key])


async def load_from_json(session: AsyncSession, json_file: str):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    for video_data in data["videos"]:
        snapshots_data = video_data.pop("snapshots")
        normalize_dt(video_data)
        video = Video(**video_data)
        for snap in snapshots_data:
            normalize_dt(snap)
            video.snapshots.append(VideoSnapshot(**snap))
        session.add(video)
    await session.commit()


async def init_db():
    await create_tables()
    async with async_session() as session:
        await load_from_json(session, JSON_FILE)
