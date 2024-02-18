from io import BytesIO

from fastapi import APIRouter, File, HTTPException, Response, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, select

from edea_ms.db import async_session, models

router = APIRouter()

# TODO: list testrun files


@router.post(
    "/file/{testrun_id}", tags=["testruns"], description="Upload a single file"
)
async def upload_file(
    testrun_id: int,
    file: UploadFile = File(description="File to upload"),
) -> dict[str, int] | None:
    async with async_session() as session:
        if file.size is None:
            raise HTTPException(500, detail="unknown file size")
        content = file.file.read(file.size)
        testrun_file = models.TestrunFile(
            testrun_id=testrun_id,
            filename=file.filename,
            content_type=file.content_type,
            size=file.size,
            content=content,
        )

        session.add(testrun_file)
        await session.commit()
        return {testrun_file.filename: testrun_file.id}


@router.get("/file/{file_id}", tags=["testruns"], description="Get a single file")
async def get_file(file_id: int) -> StreamingResponse:
    async with async_session() as session:
        res = (
            await session.scalars(
                select(models.TestrunFile).where(models.TestrunFile.id == file_id)
            )
        ).one()

        if res.content is None:
            raise HTTPException(status_code=500, detail="no content")

        filename = res.filename
        content_type = res.content_type

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": content_type,
        }
        return StreamingResponse(content=BytesIO(res.content), headers=headers)


@router.delete("/file/{file_id}", tags=["testruns"], description="Get a single file")
async def delete_file(file_id: int) -> Response:
    async with async_session() as session:
        await session.execute(
            delete(models.TestrunFile).where(models.TestrunFile.id == file_id)
        )

    return Response(status_code=200)
