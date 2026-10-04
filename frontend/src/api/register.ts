import { apiFetch } from "./client"
import type { User } from "../types"
export async function register(username: string, email: string, password: string): Promise<User> {
    return apiFetch("/auth/register", {
        method: "POST", body: JSON.stringify({
            username: username,
            email: email,
            password: password,
        })
    })
}