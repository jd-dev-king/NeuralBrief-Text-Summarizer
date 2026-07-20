"""Manual test for the NeuralBrief document reader."""

from pathlib import Path

from document_reader import DocumentReader


def main() -> None:
    reader = DocumentReader()

    backend_directory = Path(__file__).resolve().parent
    uploads_directory = backend_directory / "uploads"
    uploads_directory.mkdir(parents=True, exist_ok=True)

    test_file = uploads_directory / "test_article.txt"

    test_file.write_text(
        """
        Artificial intelligence is changing how manufacturers analyze data.
        Production systems generate information about equipment, quality,
        downtime, output, and maintenance requirements.

        Engineers can use this information to identify recurring problems.
        Predictive-maintenance systems can detect changes in temperature,
        vibration, pressure, and equipment performance before a failure occurs.

        Text summarization can also help employees process long reports.
        Instead of reading every sentence, users can generate a condensed
        extract containing the most important information.

        Extractive summarization selects sentences directly from the original
        document. This approach helps preserve the source meaning because the
        system does not generate entirely new statements.

        A professional summarization interface can support pasted text, Word
        files, PDF reports, and plain-text documents. Users can upload a file,
        select a compression level, and copy or download the result.

        The final system combines Python, Gensim, Flask, document processing,
        HTML, CSS, and JavaScript in one portfolio-ready application.
        """,
        encoding="utf-8",
    )

    extracted_text = reader.read(test_file)

    print("=" * 70)
    print("DOCUMENT READER TEST")
    print("=" * 70)
    print(extracted_text)
    print()
    print(f"Characters extracted: {len(extracted_text)}")
    print("=" * 70)


if __name__ == "__main__":
    main()