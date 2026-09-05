import json
import os
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(app_dir)

from rag.chain import RAGChain

load_dotenv()

class RAGEvaluator:
    def __init__(self, rag_chain):
        self.rag_chain = rag_chain
        self.eval_llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)

    def _clean_response(self, response):
        content = response.content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
                else:
                    text_parts.append(str(item))
            return " ".join(text_parts)
        return str(content)

    def evaluate_faithfulness(self, question, context, answer):
        prompt = f"""
        You are an expert auditor. Evaluate if the AI response is supported by the context.
        Question: {question}
        Context: {context}
        AI Response: {answer}
        Return only 'YES' or 'NO'.
        """
        response = self.eval_llm.invoke(prompt)
        return self._clean_response(response).strip().upper()

    def run_evaluation(self, dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)

        results = []
        for i, item in enumerate(dataset, start=1):
            print(f"Testing Question {i}: {item['question']}")
            
            # Fixed the typo here: self.rag_chain.ask
            answer = self.rag_chain.ask(item['question'])
            
            context = getattr(self.rag_chain, "last_context", "")
            score = self.evaluate_faithfulness(item['question'], context, answer)
            results.append({"question": item['question'], "score": score})
        return results

if __name__ == "__main__":
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "vector_db/chroma_db"))
    DATASET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "dataset.json"))

    rag_system = RAGChain(DB_DIR, DATA_DIR)
    evaluator = RAGEvaluator(rag_system)
    results = evaluator.run_evaluation(DATASET_PATH)

    print("\n--- FINAL EVALUATION REPORT ---")
    passed = sum(1 for r in results if "YES" in r["score"])
    for r in results:
        status = "PASS" if "YES" in r["score"] else "FAIL"
        print(f"{status} | {r['question']}")
    
    total = len(results)
    if total > 0:
        print(f"\nOverall System Faithfulness: {(passed/total)*100:.1f}%")
