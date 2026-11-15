import { getToken } from "./tokenStorage";
const RAW_API_URL: string | undefined = import.meta.env.VITE_API_URL;
if (!RAW_API_URL) throw new Error("VITE_API_URL is missing in frontend/.env");
const API_URL = RAW_API_URL.replace(/\/+$/, "");


export class ApiError extends Error {
    statusCode: number;

    constructor(message: string, statusCode: number, options?: { cause?: unknown }) {
        super(message, options);
        this.statusCode = statusCode;
        this.name = "ApiError";

    }
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const url: string = API_URL + path;
    const token: string | null = getToken();
    const headers = new Headers(options?.headers);
    if (options?.body && !headers.has("Content-Type")) { headers.set("Content-Type", "application/json"); }
    if (token !== null) { headers.set("Authorization", `Bearer ${token}`); }

    let response: Response;

    try {
        response = await fetch(url, { ...options, headers });
    } catch (err) {
        throw new ApiError("Could not reach the server", 0, { cause: err });
    }

    if (!response.ok) {
        let message = response.statusText;
        try {
            const body = await response.json();
            if (typeof body.error === "string" && body.error) message = body.error;
        } catch {
            // body wasn't JSON — keep statusText fallback
        }
        throw new ApiError(message, response.status);
    }
    if (response.status === 204) {
        return undefined as T;
    }

    return response.json();
}