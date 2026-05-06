-- ============================================================
-- 001_init_tables.sql
-- 실행 순서: FK 의존관계에 따라 순서대로 실행
-- keywords → users → auth_providers → images → chat_rooms
--          → chat_messages → entity_images → skin_analysis_results
--          → analysis_recommendation_tags → wishlist → qna
-- ============================================================


-- ------------------------------------------------------------
-- 1. keywords
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS keywords (
    keyword_id  INT          AUTO_INCREMENT PRIMARY KEY COMMENT '고유 ID',
    type        VARCHAR(50)  NOT NULL                  COMMENT '키워드 그룹 (예: skin_type, gender)',
    label       VARCHAR(100) NULL                      COMMENT '화면에 표시되는 이름 (예: 건성)',
    keyword     VARCHAR(100) NOT NULL                  COMMENT '코드 내부에서 사용하는 값 (예: dry)',
    description TEXT         NULL                      COMMENT '설명',
    UNIQUE KEY unique_type_keyword (type, keyword)
) COMMENT='키워드 사전 테이블';


-- ------------------------------------------------------------
-- 2. users
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id        INT          AUTO_INCREMENT PRIMARY KEY                            COMMENT '사용자 고유 ID',
    is_admin       BOOLEAN      NOT NULL DEFAULT FALSE                                COMMENT '관리자 여부',
    email          VARCHAR(255) NOT NULL UNIQUE                                       COMMENT '로그인용 이메일',
    nickname       VARCHAR(50)  NOT NULL UNIQUE                                       COMMENT '서비스 내 표시 닉네임 (중복 불가)',
    age            INT          NULL                                                  COMMENT '사용자 나이',
    gender         VARCHAR(20)  NULL                                                  COMMENT '사용자 성별 (male, female)',
    skin_type      INT          NULL                                                  COMMENT '피부 타입 FK → keywords.keyword_id',
    skin_concern   VARCHAR(255) NULL                                                  COMMENT '피부 고민',
    terms_agreed   BOOLEAN      NOT NULL DEFAULT FALSE                                COMMENT '서비스 이용약관 동의 여부 (필수)',
    privacy_agreed BOOLEAN      NOT NULL DEFAULT FALSE                                COMMENT '개인정보 처리방침 동의 여부 (필수)',
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP                    COMMENT '계정 생성 시각',
    updated_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '계정 수정 시각',
    deleted_at     DATETIME     NULL                                                  COMMENT '계정 탈퇴 시각 (soft delete)',
    FOREIGN KEY (skin_type) REFERENCES keywords(keyword_id)
) COMMENT='서비스 사용자 기본 정보 테이블';


-- ------------------------------------------------------------
-- 3. auth_providers
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS auth_providers (
    auth_id       INT          AUTO_INCREMENT PRIMARY KEY COMMENT '인증 제공자 고유 ID',
    user_id       INT          NOT NULL                  COMMENT 'users.user_id 참조',
    provider_type VARCHAR(50)  NOT NULL                  COMMENT '인증 제공자 유형 (local / google / kakao)',
    provider_id   VARCHAR(255) NOT NULL                  COMMENT '각 provider에서의 고유 사용자 ID',
    password_hash VARCHAR(255) NULL                      COMMENT 'local 로그인용 비밀번호 해시',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '인증 수단 연결 시각',
    UNIQUE KEY uq_provider (provider_type, provider_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) COMMENT='사용자의 로그인 수단을 관리하는 인증 테이블';


-- ------------------------------------------------------------
-- 4. images
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS images (
    image_id   INT          AUTO_INCREMENT PRIMARY KEY COMMENT '이미지 고유 ID',
    image_url  VARCHAR(500) NOT NULL                  COMMENT '이미지 URL (S3)',
    created_at DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '업로드 시각'
) COMMENT='이미지 저장 테이블';


-- ------------------------------------------------------------
-- 5. chat_rooms
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_rooms (
    chat_room_id INT          AUTO_INCREMENT PRIMARY KEY          COMMENT '채팅방 ID',
    user_id      INT          NOT NULL                            COMMENT 'users.user_id 참조',
    title        VARCHAR(255) NULL                                COMMENT '채팅방 제목 (첫 질문 요약)',
    created_at   DATETIME     NULL DEFAULT CURRENT_TIMESTAMP      COMMENT '채팅방 생성 시각',
    deleted_at   DATETIME     NULL                                COMMENT '채팅방 삭제 시각 (soft delete)',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) COMMENT='사용자별 채팅 세션 관리 테이블';


-- ------------------------------------------------------------
-- 6. chat_messages
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id   INT         AUTO_INCREMENT PRIMARY KEY      COMMENT '메시지 ID',
    chat_room_id INT         NOT NULL                        COMMENT 'chat_rooms.chat_room_id 참조',
    role         VARCHAR(20) NOT NULL                        COMMENT '메시지 주체 (user / assistant / system)',
    content      TEXT        NULL                            COMMENT '텍스트 내용',
    model_type   VARCHAR(20) NOT NULL                        COMMENT '사용된 분석 모델 유형 (simple / detailed)',
    created_at   DATETIME    NULL DEFAULT CURRENT_TIMESTAMP  COMMENT '메시지 생성 시각',
    FOREIGN KEY (chat_room_id) REFERENCES chat_rooms(chat_room_id) ON DELETE CASCADE
) COMMENT='LLM 챗봇 대화 메시지 저장 테이블';


-- ------------------------------------------------------------
-- 7. entity_images
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS entity_images (
    entity_image_id INT         AUTO_INCREMENT PRIMARY KEY COMMENT '엔티티 이미지 매핑 ID',
    image_id        INT         NOT NULL                  COMMENT 'images.image_id 참조',
    entity_type     VARCHAR(50) NOT NULL                  COMMENT '연결 대상 유형 (예: message, analysis)',
    entity_id       INT         NOT NULL                  COMMENT '연결 대상 ID',
    FOREIGN KEY (image_id) REFERENCES images(image_id) ON DELETE CASCADE
) COMMENT='이미지와 엔티티 간 매핑 테이블';


-- ------------------------------------------------------------
-- 8. skin_analysis_results
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS skin_analysis_results (
    analysis_id   INT          AUTO_INCREMENT PRIMARY KEY          COMMENT '피부 분석 결과 ID',
    user_id       INT          NOT NULL                            COMMENT 'users.user_id 참조',
    model_type    VARCHAR(20)  NOT NULL                            COMMENT '사용된 분석 모델 유형 (simple / detailed)',
    analysis_data JSON         NOT NULL                            COMMENT '피부 분석 구조화 데이터',
    skin_score    INT          NULL                                COMMENT '피부 종합 점수',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP  COMMENT '분석 생성 시각',
    deleted_at    DATETIME     NULL                                COMMENT '분석 삭제 시각 (soft delete)',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) COMMENT='AI 피부 분석 결과 저장 테이블';


-- ------------------------------------------------------------
-- 9. analysis_recommendation_tags
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analysis_recommendation_tags (
    analysis_id INT NOT NULL COMMENT 'skin_analysis_results.analysis_id 참조',
    keyword_id  INT NOT NULL COMMENT 'keywords.keyword_id 참조',
    PRIMARY KEY (analysis_id, keyword_id),
    FOREIGN KEY (analysis_id) REFERENCES skin_analysis_results(analysis_id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id)  REFERENCES keywords(keyword_id) ON DELETE CASCADE
) COMMENT='분석 결과 추천 키워드 매핑 테이블';


-- ------------------------------------------------------------
-- 10. wishlist
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wishlist (
    wish_id      INT          AUTO_INCREMENT PRIMARY KEY          COMMENT '위시리스트 고유 ID',
    user_id      INT          NOT NULL                            COMMENT 'users.user_id 참조',
    message_id   INT          NULL                                COMMENT '제품을 추천한 assistant 메시지 ID',
    product_name VARCHAR(50)  NOT NULL                            COMMENT '제품명 (위시리스트 화면 표시용)',
    product_url  TEXT         NULL                                COMMENT '제품 URL',
    added_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP  COMMENT '위시리스트에 추가된 시각',
    FOREIGN KEY (user_id)    REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES chat_messages(message_id) ON DELETE SET NULL
) COMMENT='사용자가 저장한 위시리스트 테이블';


-- ------------------------------------------------------------
-- 11. qna
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS qna (
    qna_id      INT          AUTO_INCREMENT PRIMARY KEY                            COMMENT 'QnA 고유 ID',
    user_id     INT          NOT NULL                                              COMMENT 'users.user_id 참조',
    manager_id  INT          NULL                                                  COMMENT '답변 담당 관리자 user_id',
    category_id INT          NULL                                                  COMMENT '카테고리 키워드 ID',
    question    TEXT         NOT NULL                                              COMMENT '질문 내용',
    answer      TEXT         NULL                                                  COMMENT '답변 내용',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP                             COMMENT '질문 등록 시각',
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '답변 수정 시각',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) COMMENT='사용자 QnA 테이블';


-- ------------------------------------------------------------
-- 12. user_test_results
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_test_results (
    result_id   INT          AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL,
    test_type   VARCHAR(50)  NOT NULL,
    result_code VARCHAR(50)  NULL,
    result_json JSON         NULL,
    is_public   BOOLEAN      NOT NULL DEFAULT FALSE,
    share_token VARCHAR(255) NULL UNIQUE,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at  DATETIME     NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
