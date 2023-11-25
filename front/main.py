import uuid

import aiofiles
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from driver import get_async_session, Files
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
import paho.mqtt.publish as publish

app = FastAPI()


@app.post("/api/load_video")
async def post_endpoint(video: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)):
    if not video:
        return {"Result": "File dont exists"}

    uid_file = f'{uuid.uuid4()}_{video.filename}'
    path_to_file = '/home/ftpuser2/' + uid_file
    async with aiofiles.open(path_to_file, 'wb') as out_file:
        while content := await video.read(1024):
            await out_file.write(content)

    stmt = Files(file_path=path_to_file,)
    session.add(stmt)
    await session.flush()
    id_file = stmt.id
    await session.commit()

    message = str({"id": id_file, "file_path": uid_file})

    publish.single(topic='/detect/input', payload=el, hostname='127.0.0.1')

    return {"id": id_file}


@app.post("/api/get_video_status")
async def get_video_status(video_id: int, session: AsyncSession = Depends(get_async_session)):
    file_record = await session.execute(select(Files).filter(Files.id == video_id))
    file = file_record.scalar_one_or_none()
    if file:
        status = file.status  # Example status
        return {"status": status}
    else:
        raise HTTPException(status_code=404, detail="File not found")
    

@app.post("/api/video_params")
async def video_params(video_id: int, session: AsyncSession = Depends(get_async_session)):
    file_record = await session.execute(select(Files).filter(Files.id == video_id))
    file = file_record.scalar_one_or_none()
    if file:
        # Here you'd implement your logic to retrieve video params
        return {
            "class_pred": file.class_pred,  # Example data
            "special_code": file.special_code,
            "probability": file.probability
        }
    else:
        raise HTTPException(status_code=404, detail="File not found")


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
