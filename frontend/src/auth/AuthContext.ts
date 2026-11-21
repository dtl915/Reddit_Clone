import { createContext } from "react";
import type { CurrentUser, LoginRequest } from "../types";

export interface AuthContextValue {
    user: CurrentUser | null;
    status: ("loading" | "ready");
    login: (data: LoginRequest) => Promise<void>;
    logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);