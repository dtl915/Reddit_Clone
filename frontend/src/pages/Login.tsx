import { useState } from "react"
import { useNavigate } from "react-router-dom";
import "./Login.css";
import { useAuth } from "../auth/useAuth";
import { ApiError } from "../api/client";

export function Login() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();
    const { login } = useAuth();
    return <div className="auth-page">
        <title>Login</title>
        <div className="auth-card">
            <h1>Login</h1>
            <form className="auth-form" onSubmit={async (event) => {
                event.preventDefault();
                const formData = new FormData(event.currentTarget);
                setLoading(true);
                const email = formData.get("email")?.toString().trim();
                const password = formData.get("password")?.toString();
                if (!email || !password || !password.trim()) {
                    setError("Please fill out all fields");
                    setLoading(false);
                    return;
                }

                try {
                    await login({ email: email, password: password });
                    navigate("/auth/me");
                } catch (error) {
                    if (error instanceof ApiError) {
                        setError(error.message);
                    }
                    else {
                        setError("Something went wrong. Please try again.");
                        console.error(error);
                    }
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
                {error !== null && <div className="auth-form-error" role="alert">{error}</div>}
                <button type="submit" disabled={loading} className="auth-submit">{loading ? "Loading..." : "Login"}</button>
            </form>
            <button className="auth-switch" onClick={() => {
                navigate("/auth/register")
            }}>Doesn't Have an Account? Register Now!</button>
        </div>
    </div>
}