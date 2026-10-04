import { useState } from "react"
import { getJWT } from "../api/login"
import { useNavigate } from "react-router-dom";

export function Login() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    if (error)
        return <div>{error}</div>
    if (loading)
        return <div>Loading...</div>

    return <div>
        <title>Login</title>
        <form action={async (formData: FormData) => {
            setLoading(true);
            const email = formData.get("email");
            const password = formData.get("password");

            if (typeof email !== "string" || typeof password !== "string") {
                throw TypeError
            }

            try {
                const data = await getJWT(email, password);
                if (data.access_token) {
                    localStorage.setItem("token", data.access_token);
                    navigate("/auth/me");
                }
            } catch (error) {
                setError(error instanceof Error ? error.message : "Unkown Error");
            } finally {
                setLoading(false);
            }
        }}>
            <label> Email:</label>
            <input type="text" id="email" name="email" />
            <label> Password: </label>
            <input type="text" id="password" name="password" />
            <button type="submit">Login</button>

        </form>
        <button onClick={() => {
            navigate("/auth/register")
        }}>Doesn't Have an Account? Register Now!</button>
    </div>
}