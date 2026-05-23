import type {Post} from "../types"
import { apiFetch } from "./client"

export async function getFeed(): Promise<Post[]> {
    return apiFetch<Post[]> ("/posts")
}