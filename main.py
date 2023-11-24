import uuid

import aiofiles
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession

from driver import get_async_session, Files
from fastapi import FastAPI, UploadFile, File, Depends

app = FastAPI()


@app.post("/")
async def post_endpoint(video: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)):
    if not video:
        return {"Result": "File dont exists"}

    path_to_file = f'files/{uuid.uuid4()}_{video.filename}'
    async with aiofiles.open(path_to_file, 'wb') as out_file:
        while content := await video.read(1024):
            await out_file.write(content)

    stmt = Files(file_path=path_to_file,)
    session.add(stmt)
    await session.flush()
    id_file = stmt.id
    await session.commit()

    return {"id": id_file}


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
