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

export async function getTranslation(language, site) {
    const translationEndpoint = `/translations/${language}?site=${site}`;

    try {
        const response = await fetch(translationEndpoint);
        return await response.json();
    } catch (error) {
        console.error("Error fetching translation data:", error);
        return null;
    }
}

export async function getLanguage(key = "") {
    if (key === "") {
        const currentPath = window.location.pathname;
        const german = currentPath.includes("/de")
        return german ? "de" : "en"
    } else {
        const session_id = getSessionIdFromUrl(key);
        if (session_id != null) {
            const response = await fetch(`/language/${session_id}`)
            const data = await response.json()
            return data.language
        }
        return "en"
    }

}