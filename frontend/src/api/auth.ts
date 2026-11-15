import { apiFetch } from "./client";
import type { CurrentUser, JWT, LoginRequest, RegisterRequest } from "../types";

export async function login(data: LoginRequest): Promise<JWT> {
    return apiFetch<JWT>("/auth/login",
        {
            method: "POST",
            body: JSON.stringify(data)
        }
    );
}

export async function register(data: RegisterRequest): Promise<CurrentUser> {
    return apiFetch<CurrentUser>("/auth/register", {
        method: "POST", body: JSON.stringify(data)
    });
}

export async function getMe(): Promise<CurrentUser> {
    return apiFetch<CurrentUser>("/auth/me", { method: "GET" });
}