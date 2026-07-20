"""Flask API for the NeuralBrief Text Summarizer."""

from __future__ import annotations

import time
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import (
    ALLOWED_EXTENSIONS,
    DEFAULT_SUMMARY_RATIO,
    MAX_CONTENT_LENGTH,
    UPLOAD_FOLDER,
)
from document_reader import DocumentReader
from summarizer import ExtractiveSummarizer


PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
FRONTEND_DIRECTORY = PROJECT_DIRECTORY / "frontend"

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

CORS(app)

summarizer = ExtractiveSummarizer()
document_reader = DocumentReader()


def allowed_file(filename: str) -> bool:
    """Return True when the uploaded filename has a supported extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def result_to_dictionary(result, processing_seconds: float) -> dict:
    """Convert a SummaryResult object into JSON-ready data."""
    return {
        "success": True,
        "summary": result.summary,
        "statistics": {
            "original_words": result.original_word_count,
            "summary_words": result.summary_word_count,
            "original_sentences": result.original_sentence_count,
            "summary_sentences": result.summary_sentence_count,
            "compression_percentage": result.compression_percentage,
            "processing_seconds": round(processing_seconds, 3),
        },
    }

@app.get("/")
def serve_frontend():
    """Serve the NeuralBrief frontend application."""
    return send_from_directory(
        FRONTEND_DIRECTORY,
        "index.html",
    )


@app.get("/css/<path:filename>")
def serve_css(filename: str):
    """Serve frontend CSS files."""
    return send_from_directory(
        FRONTEND_DIRECTORY / "css",
        filename,
    )


@app.get("/js/<path:filename>")
def serve_javascript(filename: str):
    """Serve frontend JavaScript files."""
    return send_from_directory(
        FRONTEND_DIRECTORY / "js",
        filename,
    )


@app.get("/assets/<path:filename>")
def serve_assets(filename: str):
    """Serve frontend image and asset files."""
    return send_from_directory(
        FRONTEND_DIRECTORY / "assets",
        filename,
    )

@app.get("/api/health")
def health_check():
    """Confirm that the backend API is running."""
    return jsonify(
        {
            "success": True,
            "service": "NeuralBrief Text Summarizer API",
            "status": "online",
            "default_summary_ratio": DEFAULT_SUMMARY_RATIO,
            "supported_files": sorted(ALLOWED_EXTENSIONS),
        }
    )


@app.post("/api/summarize")
def summarize_text():
    """Summarize text supplied in a JSON request."""
    start_time = time.perf_counter()

    try:
        request_data = request.get_json(silent=True)

        if not request_data:
            return jsonify(
                {
                    "success": False,
                    "error": "A JSON request body is required.",
                }
            ), 400

        text = request_data.get("text", "")
        ratio = request_data.get(
            "ratio",
            DEFAULT_SUMMARY_RATIO,
        )

        result = summarizer.summarize(
            text=text,
            ratio=ratio,
        )

        processing_seconds = time.perf_counter() - start_time

        return jsonify(
            result_to_dictionary(
                result,
                processing_seconds,
            )
        )

    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 400

    except Exception as error:
        print(f"Unexpected summarize error: {error}")

        return jsonify(
            {
                "success": False,
                "error": "An unexpected summarization error occurred.",
            }
        ), 500


@app.post("/api/upload")
def upload_document():
    """Upload, read, and summarize a supported document."""
    start_time = time.perf_counter()
    saved_file_path: Path | None = None

    try:
        if "file" not in request.files:
            return jsonify(
                {
                    "success": False,
                    "error": "No document was included in the request.",
                }
            ), 400

        uploaded_file = request.files["file"]

        if not uploaded_file.filename:
            return jsonify(
                {
                    "success": False,
                    "error": "No document was selected.",
                }
            ), 400

        if not allowed_file(uploaded_file.filename):
            return jsonify(
                {
                    "success": False,
                    "error": (
                        "Unsupported file type. "
                        "Please upload a TXT, DOCX, or PDF document."
                    ),
                }
            ), 400

        safe_filename = secure_filename(uploaded_file.filename)

        if not safe_filename:
            return jsonify(
                {
                    "success": False,
                    "error": "The document filename is invalid.",
                }
            ), 400

        unique_filename = f"{uuid4().hex}_{safe_filename}"
        saved_file_path = UPLOAD_FOLDER / unique_filename

        uploaded_file.save(saved_file_path)

        document_text = document_reader.read(saved_file_path)

        ratio_value = request.form.get(
            "ratio",
            DEFAULT_SUMMARY_RATIO,
        )

        result = summarizer.summarize(
            text=document_text,
            ratio=ratio_value,
        )

        processing_seconds = time.perf_counter() - start_time

        response_data = result_to_dictionary(
            result,
            processing_seconds,
        )

        response_data["document"] = {
            "filename": safe_filename,
            "characters_extracted": len(document_text),
        }

        return jsonify(response_data)

    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 400

    except Exception as error:
        print(f"Unexpected upload error: {error}")

        return jsonify(
            {
                "success": False,
                "error": "The document could not be processed.",
            }
        ), 500

    finally:
        if saved_file_path and saved_file_path.exists():
            try:
                saved_file_path.unlink()
            except OSError:
                pass

@app.errorhandler(413)
def file_too_large(_error):
    """Return JSON when an uploaded document exceeds the size limit."""
    maximum_megabytes = MAX_CONTENT_LENGTH // (1024 * 1024)

    return jsonify(
        {
            "success": False,
            "error": (
                f"The uploaded document exceeds the "
                f"{maximum_megabytes} MB size limit."
            ),
        }
    ), 413


@app.errorhandler(404)
def route_not_found(_error):
    """Return JSON for unknown API routes."""
    return jsonify(
        {
            "success": False,
            "error": "The requested API route was not found.",
        }
    ), 404


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )