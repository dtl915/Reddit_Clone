import { useAuth } from "../auth/useAuth"

export function Me() {
    const { user, status, logout } = useAuth();
    return <div>
        <title>Me</title>
        <div>{status === "loading" ? "loading" : user?.username ?? "not logged in"}</div>
        <button onClick={() => logout()}> logout</button>
    </div>
}