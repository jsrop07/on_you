/**
 * analysisApi.ts
 * ─────────────────────────────────────────────────────────────
 * back/routers/analysis_router.py 의 /analysis 엔드포인트와 통신.
 *
 * 사용하는 엔드포인트:
 *   GET  /analysis/model/detailed        → fetchDetailAnalysis()
 *   GET  /keywords/factorials            → fetchFactorials()
 *   GET  /analysis/check/today           → checkTodayDetailedAnalysis()
 *   GET  /analysis/dates                 → fetchDetailedAnalysisDates()
 *   GET  /analysis/by-date               → fetchAnalysisByDate()
 *   POST /analysis/share/{analysis_id}   → createAnalysisShareLink()
 *   GET  /analysis/shared/{share_token}  → fetchSharedAnalysisResult()
 * ─────────────────────────────────────────────────────────────
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001";

function getToken(): string {
    const token = localStorage.getItem("access_token");

    if (!token) throw new Error("로그인이 필요합니다.");

    return token;
}

// ─────────────────────────────────────────────
// 타입 정의
// ─────────────────────────────────────────────

export interface SkinMetricValue {
    score : number;
    label : string;
}
export interface SkinMetrics {
    moisture?     : SkinMetricValue;
    elasticity?   : SkinMetricValue;
    wrinkle?      : SkinMetricValue;
    pore?         : SkinMetricValue;
    pigmentation? : SkinMetricValue;
}
export interface SkinAnalysisData {
    overall_score?   : number;
    skin_type?       : string;
    skin_type_detail?: string;
    metrics?         : SkinMetrics;
}
export interface AnalysisResult {
    analysis_id   : number;
    user_id       : number;
    image_url     : string[];
    model_type    : string;
    skin_score    : number;
    factorial?    : string[];
    analysis_data : SkinAnalysisData;
    created_at    : string;
}
export interface KeywordResponse {
    keyword_id : number;
    keyword    : string;
    label      : string;
}


export interface AnalysisLimitResponse {
    available: boolean;
    message: string;
    limit_count: number | null;
    used_count?: number;
    remaining_count?: number | null;
}

export interface DetailedDatesResponse {
    dates: string[];
}

export interface AnalysisByDateItem {
    date: string;
    result: AnalysisResult | null;
}

// ─────────────────────────────────────────────
// 공통 응답 처리
// ─────────────────────────────────────────────

async function handleResponse<T>(res: Response): Promise<T> {
    if (!res.ok) {
        const data = await res.json().catch(() => ({}));

        throw new Error((data as { detail?: string }).detail ?? `서버 오류 (${res.status})`);
    }

    return res.json() as Promise<T>;
}

// ─────────────────────────────────────────────
// API 호출 함수
// ─────────────────────────────────────────────

/**
 * 사용자의 피부 정밀 분석 데이터 전체 조회. (최신순)
 *
 * GET /analysis/model/detailed
 */
export async function fetchDetailAnalysis(): Promise<AnalysisResult[]> {
    const res = await fetch(`${API_BASE}/analysis/model/detailed`, {
        headers: { Authorization: `Bearer ${getToken()}` },
    });

    return handleResponse<AnalysisResult[]>(res);
}

/**
 * 추천 관리법 키워드 목록 전체 조회
 *
 * GET /keywords/factorials
 */
export async function fetchFactorials(): Promise<KeywordResponse[]> {
    const res = await fetch(`${API_BASE}/keywords/factorials`);

    return handleResponse<KeywordResponse[]>(res);
}


export async function checkAnalysisLimit(
    modelType: "simple" | "detailed" | "ingredient" | "personal"
): Promise<AnalysisLimitResponse> {
    const res = await fetch(`${API_BASE}/chats/analysis/check-limit/${modelType}`, {
        headers: { Authorization: `Bearer ${getToken()}` },
    });

    return handleResponse<AnalysisLimitResponse>(res);
}

/**
 * 정밀 분석 가능 날짜 목록 조회
 *
 * GET /analysis/dates
 */
export async function fetchDetailedAnalysisDates(): Promise<string[]> {
    const res = await fetch(`${API_BASE}/analysis/dates`, {
        headers: { Authorization: `Bearer ${getToken()}` },
    });

    const data = await handleResponse<DetailedDatesResponse>(res);

    return data.dates;
}

/**
 * 날짜별 정밀 분석 결과 조회
 *
 * GET /analysis/by-date?dates=2026-03-05
 * GET /analysis/by-date?dates=2026-03-05&dates=2026-03-02
 */
export async function fetchAnalysisByDate(dates: string[]): Promise<AnalysisByDateItem[]> {
    if (!dates.length) {
        throw new Error("조회할 날짜가 없습니다.");
    }

    const params = new URLSearchParams();

    dates.forEach((d) => params.append("dates", d));

    const res = await fetch(`${API_BASE}/analysis/by-date?${params.toString()}`, {
        headers: { Authorization: `Bearer ${getToken()}` },
    });

    return handleResponse<AnalysisByDateItem[]>(res);
}
/**
 * 피부 분석 공유 url 조회
 *
 * GET /analysis/by-date?dates=2026-03-05
 * GET /analysis/by-date?dates=2026-03-05&dates=2026-03-02
 */
export interface AnalysisShareResponse {
    message: string;
    data: {
        analysis_id: number;
        share_token: string;
        share_url: string;
    };
}
/**
 * 피부 분석 공유 링크 생성
 *
 * POST /analysis/share/{analysis_id}
 */
export async function createAnalysisShareLink(analysisId: number): Promise<AnalysisShareResponse> {
    const res = await fetch(`${API_BASE}/analysis/share/${analysisId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken()}` },
    });

    return handleResponse<AnalysisShareResponse>(res);
}

/**
 * 공유된 피부 분석 결과 조회
 *
 * GET /analysis/shared/{share_token}
 */
export async function fetchSharedAnalysisResult(token: string): Promise<AnalysisResult> {
    const res = await fetch(`${API_BASE}/analysis/shared/${token}`);

    return handleResponse<AnalysisResult>(res);
}