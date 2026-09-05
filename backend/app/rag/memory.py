from collections import deque

class ChatMemory:
    def __init__(self, k: int = 5):
        # Use a deque (double-ended queue) to keep only the last 'k' interactions
        # This implements a sliding window memory automatically
        self.memory = deque(maxlen=k)

    def get_history(self):
        # Format the history as a single string for the LLM prompt
        history_string = ""
        for interaction in self.memory:
            history_string += f"User: {interaction['user']}\nAI: {interaction['ai']}\n"
        return history_string

    def add_interaction(self, user_input: str, ai_response: str):
        # Append the latest interaction to the memory
        self.memory.append({
            "user": user_input, 
            "ai": ai_response
        })
