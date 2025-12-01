from langchain_google_genai import ChatGoogleGenerativeAI

class BaseAgent:
    """Parent class for all agents to handle model init and state binding."""
    def __init__(self, name: str, model_name: str = "gemini-2.5-flash"):
        self.name = name
        # Using gemini-1.5-flash: fast and free tier available
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
