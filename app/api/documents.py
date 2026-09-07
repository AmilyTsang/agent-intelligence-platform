from __future__ import annotations


from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.concurrency import (
    run_in_threadpool,
)


from app.api.schemas import (
    DocumentDeleteResponse,
    DocumentResponse,
)

from app.documents.service import (
    DocumentNotFoundError,
    DocumentValidationError,
    delete_document_from_library,
    get_documents,
    process_document_upload,
)


router = APIRouter(
    prefix="/api/documents",

    tags=[
        "documents",
    ],
)


MAX_UPLOAD_BYTES = (
    50
    * 1024
    * 1024
)


# ============================================================
# GET /api/documents
# ============================================================


@router.get(
    "",
    response_model=list[
        DocumentResponse
    ],
)
async def list_documents_endpoint():
    return await run_in_threadpool(
        get_documents
    )


# ============================================================
# POST /api/documents
# ============================================================


@router.post(
    "",
    response_model=(
        DocumentResponse
    ),
)
async def upload_document_endpoint(
    file: UploadFile = File(...),
):
    filename = (
        file.filename
        or ""
    )

    try:
        file_bytes = (
            await file.read(
                MAX_UPLOAD_BYTES
                + 1
            )
        )

        if (
            len(file_bytes)
            >
            MAX_UPLOAD_BYTES
        ):
            raise HTTPException(
                status_code=413,

                detail=(
                    "PDF 文件不能超过 50 MB。"
                ),
            )

        result = (
            await run_in_threadpool(
                process_document_upload,

                filename=filename,

                file_bytes=file_bytes,
            )
        )

        return result

    except HTTPException:
        raise

    except DocumentValidationError as exc:
        raise HTTPException(
            status_code=400,

            detail=str(
                exc
            ),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,

            detail=(
                "文档处理失败："
                + str(exc)
            ),
        ) from exc

    finally:
        await file.close()


# ============================================================
# DELETE /api/documents/{document_id}
# ============================================================


@router.delete(
    "/{document_id}",

    response_model=(
        DocumentDeleteResponse
    ),
)
async def delete_document_endpoint(
    document_id: str,
):
    try:
        print(
            "[Documents] Delete request:",
            document_id,
        )

        result = (
            await run_in_threadpool(
                delete_document_from_library,
                document_id,
            )
        )

        print(
            "[Documents] Delete completed:",
            result,
        )

        return result

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=404,

            detail=str(
                exc
            ),
        ) from exc

    except Exception as exc:
        print(
            "[Documents] Delete failed:",
            exc,
        )

        raise HTTPException(
            status_code=500,

            detail=(
                "删除文档失败："
                + str(exc)
            ),
        ) from exc