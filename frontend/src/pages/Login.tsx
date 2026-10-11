import { useState } from "react"
import { getJWT } from "../api/login"
import { useNavigate } from "react-router-dom";
import "./Login.css";

export function Login() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    if (error)
        return <div className="auth-status auth-error">{error}</div>
    if (loading)
        return <div className="auth-status">Loading...</div>

    return <div className="auth-page">
        <title>Login</title>
        <div className="auth-card">
            <h1>Login</h1>
            <form className="auth-form" action={async (formData: FormData) => {
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
                <div className="auth-field">
                    <label htmlFor="email">Email</label>
                    <input type="text" id="email" name="email" />
                </div>
                <div className="auth-field">
                    <label htmlFor="password">Password</label>
                    <input type="password" id="password" name="password" />
                </div>
                <button type="submit" className="auth-submit">Login</button>
            </form>
            <button className="auth-switch" onClick={() => {
                navigate("/auth/register")
            }}>Doesn't Have an Account? Register Now!</button>
        </div>
    </div>
}