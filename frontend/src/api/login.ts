import { apiFetch } from "./client";
import type { JWT } from "../types";

export async function getJWT(email: string, password:string): Promise<JWT>{
    return apiFetch("/auth/login", 
        {
            method : "POST", 
            body : JSON.stringify({
                email : email, 
                password: password 
            })
        }
    );
}