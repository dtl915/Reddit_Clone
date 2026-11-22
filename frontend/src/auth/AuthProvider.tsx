import { useEffect, useState, type ReactNode } from "react";
import { clearToken, getToken, setToken } from "../api/tokenStorage";
import * as authApi from "../api/auth";
import { ApiError, setUnauthorizedHandler } from "../api/client";
import { AuthContext } from "./AuthContext";
import type { CurrentUser, LoginRequest } from "../types";

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<CurrentUser | null>(null);
    const [status, setStatus] = useState<"loading" | "ready">("loading");



    useEffect(() => {

        async function loadMe() {
            const token: string | null = getToken();

            if (token !== null) {

                try {
                    const me = await authApi.getMe();
                    setUser(me);

                } catch (err) {
                    if (err instanceof ApiError && err.statusCode === 401) {
                        clearToken();
                    }
                }
            }
            setStatus("ready");
        }

        loadMe();

    }, []);

    useEffect(() => {
        const unauthorize_handler = () => {
            setUser(null);
            clearToken();
        }
        setUnauthorizedHandler(unauthorize_handler);
        return () => {
            setUnauthorizedHandler(null);
        }
    }, [])

    async function login(data: LoginRequest) {
        const token = (await authApi.login(data)).access_token;
        setToken(token);
        try {
            const me = await authApi.getMe();
            setUser(me);
        } catch (err) {
            clearToken();
            throw err;
        }


    }

    function logout() {
        clearToken();
        setUser(null);
    }

    return <AuthContext.Provider value={{ user, status, login, logout }}>{children}</AuthContext.Provider>

}