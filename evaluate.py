import json
import requests

# API endpoint for chat interaction
API_URL = "http://127.0.0.1:8000/chat"


# =========================
# Load evaluation dataset
# =========================
def load_questions():
    """
    Load evaluation questions from local JSON file.

    Each item contains:
    - question: user query
    - expected_keywords: keywords that should appear in the answer
    """
    with open("evaluation.json", "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# Send question to agent
# =========================
def ask_agent(question: str) -> str:
    """
    Send a question to the FastAPI chat endpoint
    and return the model's response.
    """
    response = requests.post(
        API_URL,
        json={"message": question},
        timeout=60
    )

    # Raise error if API call fails
    response.raise_for_status()

    return response.json()["response"]


# =========================
# Evaluate answer quality
# =========================
def evaluate_answer(answer: str, expected_keywords: list[str]) -> bool:
    """
    Simple evaluation metric:
    Check whether the generated answer contains any expected keywords.

    This approximates whether the RAG system retrieved relevant information.
    """
    answer_lower = answer.lower()
    return any(keyword.lower() in answer_lower for keyword in expected_keywords)


# =========================
# Main evaluation loop
# =========================
def main():
    # Load test dataset
    questions = load_questions()

    total = len(questions)
    passed = 0

    # Iterate through evaluation cases
    for item in questions:
        question = item["question"]
        expected_keywords = item["expected_keywords"]

        print("\nQuestion:", question)

        # Get answer from AI system
        answer = ask_agent(question)
        print("Answer:", answer)

        # Evaluate correctness
        ok = evaluate_answer(answer, expected_keywords)

        if ok:
            passed += 1
            print("Result: PASS")
        else:
            print("Result: FAIL")

    # Print final evaluation metrics
    print("\n====================")
    print(f"Passed: {passed}/{total}")
    print(f"Accuracy: {round(passed / total * 100, 2)}%")

if __name__ == "__main__":
    main()