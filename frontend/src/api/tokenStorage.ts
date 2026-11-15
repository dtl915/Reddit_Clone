const TOKEN_KEY = "token";

export function getToken(): string | null {
    try {
        return localStorage.getItem(TOKEN_KEY);
    }
    catch {
        return null;
    }

}

export function setToken(token: string): void {
    if (!token.trim()) throw new Error("setToken: setting an empty token");
    try {
        localStorage.setItem(TOKEN_KEY, token);
    }
    catch (err) {
        throw new Error("setToken: failed to set token", { cause: err });
    }

}

export function clearToken(): void {
    try {
        localStorage.removeItem(TOKEN_KEY);
    }
    catch (err) {
        throw new Error("clearToken: failed to clear token", { cause: err });
    }

}