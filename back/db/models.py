import json

from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field

"""
models.py
─────────────────────────────────────────────────────────────
목적  : 각 테이블의 데이터 구조를 Python dataclass로 정의
역할  :
    - DB에서 조회한 raw dict 데이터를 타입이 있는 객체로 변환
    - services 에서 데이터를 다룰 때 타입 안전성 확보
    - DB 저장용이 아닌 '데이터 표현' 용도 (ORM 아님)

포함 테이블:
    Keyword / User / AuthProvider / ChatRoom
    ChatMessage / SkinAnalysisResult / Wishlist
    Image / EntityImage / AnalysisRecommendationTag / Qna / UserTestResult
─────────────────────────────────────────────────────────────
"""

# ─────────────────────────────────────────────
# 1. Keyword
# 테이블: keywords
# ─────────────────────────────────────────────
@dataclass
class Keyword:
    keyword_id  : int
    type        : str                   # 키워드 그룹 (예: skin_type, gender)
    keyword     : str                   # 코드 내부 값 (예: dry, oily)
    label       : Optional[str] = None  # 화면 표시 이름 (예: 건성, 지성)
    description : Optional[str] = None  # 설명

    @staticmethod
    def from_dict(row: dict) -> "Keyword":
        """ DB 조회 결과 dict → Keyword 객체 변환 """
        return Keyword(
            keyword_id  = row["keyword_id"],
            type        = row["type"],
            keyword     = row["keyword"],
            label       = row.get("label"),
            description = row.get("description"),
        )

# ─────────────────────────────────────────────
# 2. User
# 테이블: users
# ─────────────────────────────────────────────
@dataclass
class User:
    user_id           : int
    is_admin          : bool
    email             : str
    nickname          : str
    terms_agreed      : bool
    privacy_agreed    : bool
    created_at        : datetime
    updated_at        : datetime
    age               : Optional[int]      = None
    gender            : Optional[str]      = None  # male / female
    skin_type         : Optional[int]      = None  # FK → keywords.keyword_id
    skin_concern      : Optional[str]      = None  # 피부 고민
    deleted_at        : Optional[datetime] = None  # soft delete 시각
    profile_image_url : Optional[str]      = None  # entity_images 조인 결과

    @staticmethod
    def from_dict(row: dict) -> "User":
        """ DB 조회 결과 dict → User 객체 변환 """
        return User(
            user_id        = row["user_id"],
            is_admin       = bool(row.get("is_admin", False)),
            email          = row["email"],
            nickname       = row["nickname"],
            terms_agreed   = bool(row.get("terms_agreed", False)),
            privacy_agreed = bool(row.get("privacy_agreed", False)),
            created_at     = row["created_at"],
            updated_at     = row["updated_at"],
            age            = row.get("age"),
            gender         = row.get("gender"),
            skin_type      = row.get("skin_type"),
            skin_concern   = row.get("skin_concern"),
            deleted_at     = row.get("deleted_at"),
        )

# ─────────────────────────────────────────────
# 3. AuthProvider
# 테이블: auth_providers
# ─────────────────────────────────────────────
@dataclass
class AuthProvider:
    auth_id       : int
    user_id       : int
    provider_type : str                     # local / google / kakao
    provider_id   : str                     # 각 provider의 고유 사용자 ID
    created_at    : datetime
    password_hash : Optional[str] = None    # local 로그인 전용 (소셜이면 None)

    @staticmethod
    def from_dict(row: dict) -> "AuthProvider":
        """ DB 조회 결과 dict → AuthProvider 객체 변환 """
        return AuthProvider(
            auth_id       = row["auth_id"],
            user_id       = row["user_id"],
            provider_type = row["provider_type"],
            provider_id   = row["provider_id"],
            created_at    = row["created_at"],
            password_hash = row.get("password_hash"),
        )

# ─────────────────────────────────────────────
# 4. Image
# 테이블: images
# ─────────────────────────────────────────────
@dataclass
class Image:
    image_id   : int
    image_url  : str
    created_at : Optional[datetime] = None

    @staticmethod
    def from_dict(row: dict) -> "Image":
        return Image(
            image_id   = row["image_id"],
            image_url  = row["image_url"],
            created_at = row.get("created_at"),
        )

# ─────────────────────────────────────────────
# 5. EntityImage
# 테이블: entity_images
# ─────────────────────────────────────────────
@dataclass
class EntityImage:
    entity_image_id : int
    image_id        : int
    entity_type     : str  # message / analysis
    entity_id       : int

    @staticmethod
    def from_dict(row: dict) -> "EntityImage":
        return EntityImage(
            entity_image_id = row["entity_image_id"],
            image_id        = row["image_id"],
            entity_type     = row["entity_type"],
            entity_id       = row["entity_id"],
        )

# ─────────────────────────────────────────────
# 6. ChatRoom
# 테이블: chat_rooms
# ─────────────────────────────────────────────
@dataclass
class ChatRoom:
    chat_room_id : int
    user_id      : int
    title        : Optional[str]      = None  # 첫 질문 요약 제목
    created_at   : Optional[datetime] = None
    deleted_at   : Optional[datetime] = None  # soft delete 시각

    @staticmethod
    def from_dict(row: dict) -> "ChatRoom":
        """ DB 조회 결과 dict → ChatRoom 객체 변환 """
        return ChatRoom(
            chat_room_id = row["chat_room_id"],
            user_id      = row["user_id"],
            title        = row.get("title"),
            created_at   = row.get("created_at"),
            deleted_at   = row.get("deleted_at"),
        )

# ─────────────────────────────────────────────
# 7. ChatMessage
# 테이블: chat_messages
# ─────────────────────────────────────────────
@dataclass
class ChatMessage:
    message_id   : int
    chat_room_id : int
    role         : str                          # user / assistant / system
    model_type   : str                          # simple / detailed
    content      : Optional[str]      = None    # 텍스트 내용
    created_at   : Optional[datetime] = None
    image_urls   : list               = field(default_factory=list)  # entity_images 조인 결과

    @staticmethod
    def from_dict(row: dict) -> "ChatMessage":
        """ DB 조회 결과 dict → ChatMessage 객체 변환 """
        return ChatMessage(
            message_id   = row["message_id"],
            chat_room_id = row["chat_room_id"],
            role         = row["role"],
            model_type   = row["model_type"],
            content      = row.get("content"),
            created_at   = row.get("created_at"),
        )

# ─────────────────────────────────────────────
# 8. SkinAnalysisResult
# 테이블: skin_analysis_results
# ─────────────────────────────────────────────
@dataclass
class SkinAnalysisResult:
    analysis_id   : int
    user_id       : int
    model_type    : str     # simple / detailed
    analysis_data : dict    # 피부 분석 구조화 데이터 (JSON)
    created_at    : datetime
    skin_score    : Optional[int]      = None  # 피부 종합 점수
    deleted_at    : Optional[datetime] = None  # soft delete 시각
    image_urls    : list               = field(default_factory=list)  # entity_images 조인 결과
    factorial     : list               = field(default_factory=list)  # analysis_recommendation_tags 조인 결과

    @staticmethod
    def from_dict(row: dict) -> "SkinAnalysisResult":
        """ DB 조회 결과 dict → SkinAnalysisResult 객체 변환 """
        raw_data = row["analysis_data"]

        return SkinAnalysisResult(
            analysis_id   = row["analysis_id"],
            user_id       = row["user_id"],
            model_type    = row["model_type"],
            analysis_data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data,
            created_at    = row["created_at"],
            skin_score    = row.get("skin_score"),
            deleted_at    = row.get("deleted_at"),
        )

# ─────────────────────────────────────────────
# 9. AnalysisRecommendationTag
# 테이블: analysis_recommendation_tags
# ─────────────────────────────────────────────
@dataclass
class AnalysisRecommendationTag:
    analysis_id : int
    keyword_id  : int

    @staticmethod
    def from_dict(row: dict) -> "AnalysisRecommendationTag":
        return AnalysisRecommendationTag(
            analysis_id = row["analysis_id"],
            keyword_id  = row["keyword_id"],
        )

# ─────────────────────────────────────────────
# 10. Wishlist
# 테이블: wishlist
# ─────────────────────────────────────────────
@dataclass
class Wishlist:
    wish_id      : int
    user_id      : int
    product_name : str                    # 제품명 (화면 표시용)
    added_at     : datetime
    message_id   : Optional[int]  = None  # 추천한 assistant 메시지 ID
    product_url  : Optional[str]  = None  # 제품 URL

    @staticmethod
    def from_dict(row: dict) -> "Wishlist":
        """ DB 조회 결과 dict → Wishlist 객체 변환 """
        return Wishlist(
            wish_id      = row["wish_id"],
            user_id      = row["user_id"],
            product_name = row["product_name"],
            added_at     = row["added_at"],
            message_id   = row.get("message_id"),
            product_url  = row.get("product_url"),
        )

# ─────────────────────────────────────────────
# 11. Qna
# 테이블: qna
# ─────────────────────────────────────────────
@dataclass
class Qna:
    qna_id         : int
    user_id        : int
    question_title : Optional[str]
    question       : str
    created_at     : datetime
    updated_at     : datetime
    manager_id     : Optional[int] = None
    category       : Optional[str] = None
    answer         : Optional[str] = None
    nickname       : Optional[str] = None

    @staticmethod
    def from_dict(row: dict) -> "Qna":
        return Qna(
            qna_id         = row["qna_id"],
            user_id        = row["user_id"],
            question_title = row.get("question_title"),
            question       = row["question"],
            created_at     = row["created_at"],
            updated_at     = row["updated_at"],
            manager_id     = row.get("manager_id"),
            category       = row.get("category"),
            answer         = row.get("answer"),
            nickname       = row.get("nickname"),
        )

# ─────────────────────────────────────────────
# 12. UserTestResult
# 테이블: user_test_results
# ─────────────────────────────────────────────
@dataclass
class UserTestResult:
    result_id   : int
    user_id     : int
    test_type   : str                   # 테스트 종류 (ex: skin_mbti)
    created_at  : datetime
    updated_at  : datetime
    result_code : Optional[str] = None  # 결과 코드 (ex: SBC)
    result_json : Optional[dict] = None # 테스트 상세 결과 JSON

    @staticmethod
    def from_dict(row: dict) -> "UserTestResult":
        raw = row.get("result_json")
        return UserTestResult(
            result_id   = row["result_id"],
            user_id     = row["user_id"],
            test_type   = row["test_type"],
            created_at  = row["created_at"],
            updated_at  = row["updated_at"],
            result_code = row.get("result_code"),
            result_json = json.loads(raw) if isinstance(raw, str) else raw,
        )