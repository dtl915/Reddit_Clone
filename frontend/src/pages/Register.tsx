import { useState } from "react";
import { register } from "../api/register";
import { getJWT } from "../api/login";
import { useNavigate } from "react-router-dom";
import "./Register.css";

export function Register() {
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate()
    if (error)
        return <div className="auth-status auth-error">{error}</div>
    if (loading)
        return <div className="auth-status">Loading...</div>

    return <div className="auth-page">
        <title>Register</title>
        <div className="auth-card">
            <h1>Register</h1>
            <form className="auth-form" action={async (formData: FormData) => {
                try {
                    const username = formData.get("username");
                    const email = formData.get("email");
                    const password = formData.get("password");

                    if (typeof username !== "string" || typeof email !== "string" || typeof password !== "string")
                        throw TypeError

                    const data = await register(username, email, password);

                    const tokenRes = await getJWT(email, password);
                    if (tokenRes.access_token) {
                        localStorage.setItem("token", tokenRes.access_token)
                        navigate("/auth/me")
                    } else {
                        throw new Error("Login failed after registration");
                    }
                } catch (error) {
                    setError("Account created, but automatic login failed. Please log in.");
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
                <button type="submit" className="auth-submit">Register</button>
            </form>
            <button className="auth-switch" onClick={() => {
                navigate("/auth/login")
            }}>Has an account already? Sign In Here!</button>
        </div>
    </div>
}