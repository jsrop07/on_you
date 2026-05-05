import os
import uuid
import shutil
from pathlib import Path

from .deps import get_current_user_id
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, Request

"""
upload_router.py
─────────────────────────────────────────────────────────────
엔드포인트 목록:
    POST   /upload    이미지 파일을 로컬에 업로드하고 URL 반환
─────────────────────────────────────────────────────────────
"""

router = APIRouter(prefix="/upload", tags=["Upload"])

# ─────────────────────────────────────────────
# 로컬 저장소 설정
# ─────────────────────────────────────────────

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}     # 지원 이미지 확장자
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# 분석 유형 → 로컬 폴더 매핑
FOLDER_MAP = {
    "simple"    : "skin-analysis",
    "detailed"  : "skin-analysis",
    "ingredient": "ingredient-analysis",
    "personal"  : "personal-analysis",
    "profile"   : "profile",
}

# ─────────────────────────────────────────────
# 이미지 업로드
# ─────────────────────────────────────────────

@router.post("")
def upload_image(
    request       : Request,
    file          : UploadFile = File(...),
    analysis_type : str        = Query(default="quick"),
    user_id       : int        = Depends(get_current_user_id),
):
    """
    이미지 파일을 로컬 uploads 폴더에 업로드하고 접근 가능한 URL 반환.

    로컬 경로: uploads/{user_id}/skin-analysis/{uuid}.ext
               uploads/{user_id}/ingredient-analysis/{uuid}.ext

    프론트 요청 예시:
        POST /upload?analysis_type=quick
        Content-Type: multipart/form-data
        Body: file=<이미지 파일>

    응답:
        { "url": "http://localhost:8001/uploads/{user_id}/skin-analysis/..." }
    """

    # 파일 타입 검증
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    # 파일 크기 검증
    contents = file.file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하여야 합니다.")

    file.file.seek(0)  # 포인터 리셋

    # 폴더 및 파일명 생성
    folder = FOLDER_MAP.get(analysis_type, "skin-analysis")
    ext    = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "jpg"
    filename = "profile" if analysis_type == "profile" else str(uuid.uuid4())
    
    # 저장할 경로: uploads/{user_id}/{folder}/{filename}.{ext}
    save_dir = UPLOAD_DIR / str(user_id) / folder
    save_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = save_dir / f"{filename}.{ext}"
    
    # 로컬 디스크에 저장
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 로컬 업로드 실패: {e}")

    # 반환할 URL 생성
    base_url = str(request.base_url).rstrip("/")
    local_url = f"{base_url}/uploads/{user_id}/{folder}/{filename}.{ext}"
    
    return {"url": local_url}
