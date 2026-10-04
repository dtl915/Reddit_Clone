import { useState } from "react";
import { register } from "../api/register";
import { getJWT } from "../api/login";
import { useNavigate } from "react-router-dom";

export function Register() {
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate()
    if (error)
        return <div>{error}</div>
    if (loading)
        return <div> Loading... </div>

    return <div>
        <title>Register</title>
        <form action={async (formData: FormData) => {
            try {
                const username = formData.get("username");
                const email = formData.get("email");
                const password = formData.get("password");

                if (typeof username !== "string" || typeof email !== "string" || typeof password !== "string")
                    throw TypeError

                const data = await register(username, email, password);

                const access_token = await getJWT(email, password);
                if (access_token.access_token) {
                    localStorage.setItem("token", access_token.access_token)
                    navigate("/auth/me")
                }
            } catch (error) {
                setError(error instanceof Error ? error.message : "Unknown Error");
            } finally {
                setLoading(false);
            }
        }}>
            <label >Username:</label>
            <input type="text" id="username" name="username" />
            <label >Email:</label>
            <input type="text" id="email" name="email" />
            <label> Password: </label>
            <input type="text" id="password" name="password" />
            <button type="submit"> Register </button>
        </form>
    </div >
}