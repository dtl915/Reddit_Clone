export function formatContent(content : string): string{
    console.log(content);
    if (content.length > 100){
        return content.slice(0,100) + "..."
    }
    return content
}