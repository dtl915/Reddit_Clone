import { useEffect, useState } from "react";
import { getFeed } from "../api/posts";
import type { Post } from "../types";

export function Home() {
    const [posts, setPosts] = useState<Post[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function loadFeeds() {
            try {
                const data = await getFeed();
                setPosts(data);
            } catch (error) {
                setError(error instanceof Error ? error.message : "Unknown Error");
            } finally {
                setLoading(false)
            }
        }
        loadFeeds();
    }, []);

    if (loading)
        return <div>Loading...</div>
    if (error)
        return <div>{error}</div>
    if (posts.length === 0)
        return <div>No posts yet.</div>
    return <div>
        {posts.map((post) => <div key={post.id}>{post.title}</div>)}
    </div>

}