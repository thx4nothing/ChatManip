export function getSessionIdFromUrl(key) {
    const path = window.location.pathname;
    const parts = path.split('/');
    const sessionIdIndex = parts.indexOf(key); // Find the index of 'session' in the path
    if (sessionIdIndex !== -1 && sessionIdIndex < parts.length - 1) {
        // If 'session' is found and the session_id is present in the next part of the path
        return parts[sessionIdIndex + 1]; // Return the session_id
    }
    return null; // If session_id is not found, return null
}