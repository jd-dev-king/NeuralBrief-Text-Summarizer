"""Application configuration for NeuralBrief."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"

ALLOWED_EXTENSIONS = {"txt", "docx", "pdf"}

MAX_CONTENT_LENGTH = 10 * 1024 * 1024

DEFAULT_SUMMARY_RATIO = 0.20
MIN_SUMMARY_RATIO = 0.10
MAX_SUMMARY_RATIO = 0.50

MINIMUM_WORD_COUNT = 50

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)