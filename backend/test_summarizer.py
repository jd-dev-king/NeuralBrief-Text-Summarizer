"""Manual test for the NeuralBrief summarization engine."""

from summarizer import ExtractiveSummarizer


ARTICLE = """
Manufacturing companies are increasingly using artificial intelligence to
improve productivity and reduce equipment downtime. Modern factories collect
large volumes of information from sensors, production systems, maintenance
records, and quality inspections. This information can help engineers identify
patterns that would otherwise be difficult to detect.

Predictive maintenance is one of the most common industrial applications.
Instead of waiting for equipment to fail, engineers analyze temperature,
vibration, pressure, and operating-hour data. These measurements can reveal
early signs of mechanical wear. Maintenance teams can then schedule repairs
before a failure interrupts production.

Artificial intelligence is also being used to improve product quality.
Computer vision systems can inspect products faster than manual inspectors.
These systems can identify scratches, incorrect dimensions, missing labels,
and packaging defects. The inspection results can be stored and analyzed to
find recurring production problems.

Another important application is process optimization. Machine-learning
models can compare production settings with yield, scrap, cycle time, and
energy consumption. Engineers can use these findings to determine which
settings produce the best results. However, the recommendations must still be
reviewed by qualified employees.

Data quality remains an important challenge. Incomplete records, faulty
sensors, and inconsistent naming conventions can reduce model accuracy.
Companies must establish reliable data collection and validation procedures.
They must also protect sensitive production information from unauthorized
access.

Artificial intelligence does not eliminate the need for process engineers,
operators, or maintenance technicians. Instead, it gives these professionals
additional information for making decisions. The most successful systems
combine reliable technology with employee knowledge, clear procedures, and
continuous improvement.
"""


def main() -> None:
    summarizer = ExtractiveSummarizer()

    result = summarizer.summarize(
        text=ARTICLE,
        ratio=0.20,
    )

    print("=" * 70)
    print("NEURALBRIEF SUMMARY")
    print("=" * 70)
    print(result.summary)
    print()
    print("-" * 70)
    print(f"Original words:     {result.original_word_count}")
    print(f"Summary words:      {result.summary_word_count}")
    print(f"Original sentences: {result.original_sentence_count}")
    print(f"Summary sentences:  {result.summary_sentence_count}")
    print(f"Compression:        {result.compression_percentage}%")
    print("=" * 70)


if __name__ == "__main__":
    main()