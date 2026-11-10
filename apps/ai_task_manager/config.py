
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "tasks.db"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

PRIORITIES = ["Low", "Medium", "High"]

TASK_STATUSES = [
    "Pending",
    "In Progress",
    "Completed",
]

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Add it to your .env file."
    )
