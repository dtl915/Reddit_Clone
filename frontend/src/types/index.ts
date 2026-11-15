export interface User {
    id: number;
    username: string;
    created_at: string;
}

export interface LoginRequest {

    email: string;
    password: string;
}

export interface RegisterRequest {
    username: string;
    email: string;
    password: string;
}

export interface CurrentUser {
    id: number;
    email: string;
    username: string;
}

export interface JWT {
    access_token: string;
}

export interface Community {
    id: number;
    name: string;
    description: string | null;
    creator_id: number;
    creator: string;
    created_at: string;
}

export interface Post {
    id: number;
    community_id: number;
    author_id: number;
    title: string;
    content: string;
    score: number;
    created_at: string;
    community: string;
    author: string;
}

export interface Comment {
    id: number;
    content: string;
    parent_id: number | null;
    post_id: number;
    author_id: number;
    author: string;
    score: number;
    created_at: string;
}