// frontend/src/services/api.js

const API_BASE_URL = 'http://localhost:8000';

export async function sendMessageToBackend(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error("API Communication Error:", error);
        throw error;
    }
}