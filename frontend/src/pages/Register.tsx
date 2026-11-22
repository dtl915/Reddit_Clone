import { useState } from "react";
import { register } from "../api/auth";
import { useNavigate } from "react-router-dom";
import "./Register.css";
import { useAuth } from "../auth/useAuth";
import { ApiError } from "../api/client";

export function Register() {
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate()

    const { login } = useAuth();
    return <div className="auth-page">
        <title>Register</title>
        <div className="auth-card">
            <h1>Register</h1>
            <form className="auth-form" onSubmit={async (event) => {
                event.preventDefault();
                const formData = new FormData(event.currentTarget);
                setLoading(true);
                setError(null);
                const username = formData.get("username")?.toString()?.trim();
                const email = formData.get("email")?.toString()?.trim();
                const password = formData.get("password")?.toString();
                if (!username || !email || !password || !password.trim()) {
                    setError("Please fill out all fields");
                    setLoading(false);
                    return;
                }


                try {
                    await register({ username, email, password });
                } catch (err) {
                    if (err instanceof ApiError) {
                        setError(err.message);
                    }
                    else {
                        setError("Something went wrong. Please try again.");
                        console.error(err);
                    }
                    setLoading(false);
                    return;
                }

                try {
                    await login({ email, password });
                    navigate("/auth/me");
                } catch (err) {
                    if (err instanceof ApiError) {
                        setError("Your account is created, but logging failed (" + err.message + "). Please log in.");
                    }
                    else {

                        setError("Your account is created, but logging failed (unknown error). Please log in.")
                        console.error(err);
                    }
                } finally {
                    setLoading(false);
                }
            }}>
                <div className="auth-field">
                    <label htmlFor="username">Username</label>
                    <input type="text" id="username" name="username" />
                </div>
                <div className="auth-field">
                    <label htmlFor="email">Email</label>
                    <input type="text" id="email" name="email" />
                </div>
                <div className="auth-field">
                    <label htmlFor="password">Password</label>
                    <input type="password" id="password" name="password" />
                </div>
                {error !== null && <div className="auth-form-error" role="alert">{error}</div>}
                <button type="submit" disabled={loading} className="auth-submit">{loading ? "Loading..." : "Register"}</button>
            </form>
            <button className="auth-switch" onClick={() => {
                navigate("/auth/login")
            }}>Has an account already? Sign In Here!</button>
        </div>
    </div>
}