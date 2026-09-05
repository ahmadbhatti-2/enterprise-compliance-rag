import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const sendMessageToBackend = async (question) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/ask`, {
            question: question
        });
        return response.data.answer;
    } catch (error) {
        console.error("Error communicating with backend:", error);
        throw error;
    }
};