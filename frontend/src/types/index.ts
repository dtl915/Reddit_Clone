export interface User {
    id: number;
    username: string;
    created_at: string;
}

export interface CurrentUser extends User {
    email: string;
}

export interface Community {
    id: number;
    name: string;
    description: string | null;
    creator_id: number;
    creator_username: string;
    created_at: string;
}

export interface Post {
    id: number;
    title: string;
    content: string;
    community_id: number;
    community_name: string;
    author_id: number;
    author_username: string;
    score: number;
    created_at: string;
}

export interface Comment {
    id: number;
    content: string;
    parent_id: number | null;
    post_id: number;
    author_id: number;
    author_username: string;
    score: number;
    created_at: string;
}