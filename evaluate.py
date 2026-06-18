import json
import requests

API_URL = "http://127.0.0.1:8000/chat"


def load_questions():
    with open("evaluation.json", "r", encoding="utf-8") as f:
        return json.load(f)


def ask_agent(question: str) -> str:
    response = requests.post(
        API_URL,
        json={"message": question},
        timeout=60
    )
    response.raise_for_status()
    return response.json()["response"]


def evaluate_answer(answer: str, expected_keywords: list[str]) -> bool:
    answer_lower = answer.lower()
    return any(keyword.lower() in answer_lower for keyword in expected_keywords)


def main():
    questions = load_questions()

    total = len(questions)
    passed = 0

    for item in questions:
        question = item["question"]
        expected_keywords = item["expected_keywords"]

        print("\nQuestion:", question)

        answer = ask_agent(question)
        print("Answer:", answer)

        ok = evaluate_answer(answer, expected_keywords)

        if ok:
            passed += 1
            print("Result: PASS")
        else:
            print("Result: FAIL")

    print("\n====================")
    print(f"Passed: {passed}/{total}")
    print(f"Accuracy: {round(passed / total * 100, 2)}%")


if __name__ == "__main__":
    main()