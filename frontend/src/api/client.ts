export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const url: string = import.meta.env.VITE_API_URL + path;
    const token: string | null = localStorage.getItem("token");
    const headers: Record <string, string> = {
        "Content-Type":"application/json",
        ... (options?.headers as Record <string, string>),
        ...(token? {"Authorization" : `Bearer ${token}`} : {}),
    };

    
    const response = await fetch(url, {...options, headers});
    if (!response.ok) {
        let message = response.statusText;
        try {
            const body = await response.json();
            if (body.error) message = body.error
        } catch {
            // body wasn't JSON — keep statusText fallback
        }
        throw new Error(message);
    }

    return response.json();

}