from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash")

while True:
    query = input("User:")
    if query.lower() in ["exit", "quit", "bye"]:
        print("Goodbye!")
        break
    result = llm.invoke(query)
    print("AI: ", result.content , "\n")