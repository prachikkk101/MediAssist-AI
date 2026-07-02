from app.rag.chain import ask_question

while True:
    question = input("Question: ")

    if question.lower() == "exit":
        break

    answer = ask_question(question)

    print("\nAnswer:\n")
    print(answer)
    print("-" * 80)