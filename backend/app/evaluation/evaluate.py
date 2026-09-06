import json
import os
import sys
import re

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, ".."))

sys.path.append(app_dir)

from rag.chain import RAGChain

load_dotenv()


class RAGEvaluator:

    def __init__(self, rag_chain):
        self.rag_chain = rag_chain

        self.eval_llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            temperature=0
        )

    def _clean_response(self, response):
        content = response.content

        if isinstance(content, list):
            text_parts = []

            for item in content:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
                else:
                    text_parts.append(str(item))

            return " ".join(text_parts)

        return str(content)

    def evaluate_faithfulness(self, question, context, answer):
        prompt = f"""
You are an expert RAG evaluator.

Evaluate whether the AI answer is fully supported by the provided context.

Question:
{question}

Context:
{context}

AI Answer:
{answer}

Rules:
- YES = the answer is supported by the context.
- NO = the answer contains unsupported or hallucinated information.

Return ONLY:
YES
or
NO
"""

        response = self.eval_llm.invoke(prompt)

        result = self._clean_response(response).strip().upper()

        return "YES" if result.startswith("YES") else "NO"

    def evaluate_answer_relevance(self, question, answer):
        prompt = f"""
You are an expert RAG evaluator.

Evaluate whether the answer directly and completely addresses the question.

Question:
{question}

Answer:
{answer}

Return a score from 1 to 5:

5 = Fully relevant and directly answers the question
4 = Mostly relevant with minor unnecessary information
3 = Partially relevant
2 = Mostly irrelevant
1 = Does not answer the question

Return ONLY the number.
"""

        response = self.eval_llm.invoke(prompt)

        result = self._clean_response(response).strip()

        match = re.search(r"[1-5]", result)

        if match:
            return int(match.group())

        return 0

    def evaluate_retrieval_recall(self, source_documents, ground_truth_page):
        """
        Checks whether the expected ground-truth page
        was retrieved by the RAG system.
        """

        target_page = str(ground_truth_page)

        for doc in source_documents:
            metadata = doc.metadata

            page = metadata.get("page_label")

            if page is None:
                page = metadata.get("page")

            if page is not None:
                page = str(page)

                # Handle zero-based PDF page indexing
                if page == target_page or str(int(page) + 1) == target_page:
                    return 1

        return 0

    def evaluate_citation_correctness(self, answer, source_documents):
        """
        Checks whether citations appearing in the answer
        point to documents/pages that were actually retrieved.
        """

        citations = re.findall(
            r"\[Source:\s*([^,\]]+),\s*Page:\s*([^\]]+)\]",
            answer
        )

        if not citations:
            return 0

        valid_citations = 0

        retrieved_sources = set()

        for doc in source_documents:
            metadata = doc.metadata

            source = (
                metadata.get("source_file")
                or metadata.get("source")
                or metadata.get("file_name")
            )

            page = (
                metadata.get("page_label")
                or metadata.get("page")
            )

            if source is not None and page is not None:
                retrieved_sources.add(
                    (
                        os.path.basename(str(source)),
                        str(page)
                    )
                )

                # Also support one-based PDF page labels
                try:
                    retrieved_sources.add(
                        (
                            os.path.basename(str(source)),
                            str(int(page) + 1)
                        )
                    )
                except (ValueError, TypeError):
                    pass

        for source, page in citations:
            source = os.path.basename(source.strip())
            page = page.strip()

            if (source, page) in retrieved_sources:
                valid_citations += 1

        return valid_citations / len(citations)

    def run_evaluation(self, dataset_path):

        with open(dataset_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)

        results = []

        for i, item in enumerate(dataset, start=1):

            question = item["question"]
            ground_truth_page = item["ground_truth_page"]

            print(f"\nTesting Question {i}: {question}")

            # IMPORTANT:
            # RAGChain.ask() returns a dictionary.
            rag_output = self.rag_chain.ask(question)

            answer = rag_output["answer"]
            source_documents = rag_output["source_documents"]

            context = getattr(
                self.rag_chain,
                "last_context",
                ""
            )

            faithfulness = self.evaluate_faithfulness(
                question,
                context,
                answer
            )

            relevance = self.evaluate_answer_relevance(
                question,
                answer
            )

            retrieval_recall = self.evaluate_retrieval_recall(
                source_documents,
                ground_truth_page
            )

            citation_correctness = self.evaluate_citation_correctness(
                answer,
                source_documents
            )

            result = {
                "question": question,
                "faithfulness": faithfulness,
                "answer_relevance": relevance,
                "retrieval_recall": retrieval_recall,
                "citation_correctness": round(
                    citation_correctness,
                    2
                )
            }

            results.append(result)

            print(f"Faithfulness: {faithfulness}")
            print(f"Answer Relevance: {relevance}/5")
            print(
                f"Retrieval Recall: "
                f"{'PASS' if retrieval_recall else 'FAIL'}"
            )
            print(
                f"Citation Correctness: "
                f"{citation_correctness * 100:.1f}%"
            )

        return results


if __name__ == "__main__":

    DATA_DIR = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "data"
        )
    )

    DB_DIR = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "vector_db",
            "chroma_db"
        )
    )

    DATASET_PATH = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "dataset.json"
        )
    )

    rag_system = RAGChain(
        DB_DIR,
        DATA_DIR
    )

    evaluator = RAGEvaluator(rag_system)

    results = evaluator.run_evaluation(
        DATASET_PATH
    )

    print("\n" + "=" * 60)
    print("FINAL RAG EVALUATION REPORT")
    print("=" * 60)

    total = len(results)

    if total == 0:
        print("No evaluation questions found.")
        sys.exit(0)

    faithfulness_passed = sum(
        1
        for r in results
        if r["faithfulness"] == "YES"
    )

    retrieval_passed = sum(
        1
        for r in results
        if r["retrieval_recall"] == 1
    )

    avg_relevance = sum(
        r["answer_relevance"]
        for r in results
    ) / total

    avg_citation = sum(
        r["citation_correctness"]
        for r in results
    ) / total

    print(
        f"Faithfulness: "
        f"{faithfulness_passed / total * 100:.1f}%"
    )

    print(
        f"Retrieval Recall: "
        f"{retrieval_passed / total * 100:.1f}%"
    )

    print(
        f"Answer Relevance: "
        f"{avg_relevance:.2f}/5"
    )

    print(
        f"Citation Correctness: "
        f"{avg_citation * 100:.1f}%"
    )

    print("\nQuestion Results:")

    for i, result in enumerate(results, start=1):

        print(
            f"\n{i}. {result['question']}"
        )

        print(
            f"   Faithfulness: "
            f"{result['faithfulness']}"
        )

        print(
            f"   Relevance: "
            f"{result['answer_relevance']}/5"
        )

        print(
            f"   Retrieval Recall: "
            f"{'PASS' if result['retrieval_recall'] else 'FAIL'}"
        )

        print(
            f"   Citation Correctness: "
            f"{result['citation_correctness'] * 100:.1f}%"
        )