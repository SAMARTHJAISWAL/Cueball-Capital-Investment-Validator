import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    # Relative sqlite paths are created in Flask's instance/ folder.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///cueball.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    BUDGET_CSV = os.getenv("BUDGET_CSV", os.path.join(BASE_DIR, "data", "budget.csv"))
    INVESTMENTS_CSV = os.getenv("INVESTMENTS_CSV", os.path.join(BASE_DIR, "data", "investments.csv"))
