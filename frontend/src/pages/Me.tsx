import { useAuth } from "../auth/useAuth"

export function Me() {
    const { user, status } = useAuth();
    return <div>
        <title>Me</title>
        <div>{status === "loading" ? "loading" : user?.username ?? "not logged in"}</div>
    </div>
}