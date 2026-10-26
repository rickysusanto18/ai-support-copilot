const API_BASE_URL = (
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

export interface ChatRequest {
    message: string;
}

export interface Citation {
    chunk_id?: number;
    document_id?: number;
    content?: string;
    similarity?: number;
}

export interface ChatResponse {
    answer: string;
    confidence: number;
    citations: Citation[];
    tools_used: string[];
}

export class ApiError extends Error {
    public readonly status: number;
    public readonly requestID?: string;

    constructor(message: string, status: number, requestID?: string) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.requestID = requestID
    }
}

export async function sendChat(message: string): Promise<{data: ChatResponse; requestID?: string}> {
    let response: Response;

    try {
        response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify( {message} satisfies ChatRequest),
        });
    } catch {
        throw new ApiError("Cannot reach BE server", 0)
    }

    const requestID = response.headers.get("X-Request-ID") ?? undefined;

    if (!response.ok) {
        let detail = `Request failed, status: ${response.status}`

        try {
            const body: {detail?: string} = await response.json();
            if (typeof body.detail === "string") {
                detail = body.detail;
            }
        } catch {}

        throw new ApiError(detail, response.status, requestID);
    }

    let data: ChatResponse;

    try {
        data = (await response.json()) as ChatResponse
    } catch {
        throw new ApiError("Server return invalid response", response.status, requestID)
    }

    return {data, requestID};
}