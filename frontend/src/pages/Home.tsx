import { useEffect, useState } from "react";
import { getFeed } from "../api/posts";
import { formatDate } from "../utils/formatDate";
import { formatContent } from "../utils/formatContent"
import type { Post } from "../types";
import "./Home.css";

export function Home() {
    const [posts, setPosts] = useState<Post[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function loadFeeds() {
            try {
                const data = await getFeed();
                setPosts(data);
                console.log(data);
                console.log(posts);
            } catch (error) {
                setError(error instanceof Error ? error.message : "Unknown Error");
            } finally {
                setLoading(false)
            }
        }
        loadFeeds();
    }, []);

    if (loading)
        return <div className="home-status">Loading...</div>
    if (error)
        return <div className="home-status home-error">{error}</div>
    if (posts.length === 0)
        return <div className="home-status">No posts yet.</div>

    /*
    TODO: HTML element of title and author is to be changed into links
     */
    return <div className="home-page">
        <title>Home Page</title>
        {posts.map((post) =>
            <div key={post.id} className="post-card">
                <div className="post-title">{post.title}</div>
                <div className="post-meta">
                    <span className="post-author">{post.author}</span>
                    <span>{formatDate(post.created_at)}</span>
                </div>
                <div className="post-content">{formatContent(post.content)}</div>
            </div>
        )}
    </div>

}