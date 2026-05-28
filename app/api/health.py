from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["health"])

frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/", include_in_schema=False)
def serve_ui() -> FileResponse:
    index_file = frontend_dir / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="UI not found")
    return FileResponse(index_file)
