"""Extractive text summarization using Gensim TF-IDF and PageRank."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

import networkx as nx
import numpy as np
from gensim.corpora import Dictionary
from gensim.matutils import cossim
from gensim.models import TfidfModel
from gensim.utils import simple_preprocess


@dataclass
class SummaryResult:
    """Stores a generated summary and its statistics."""

    summary: str
    original_word_count: int
    summary_word_count: int
    original_sentence_count: int
    summary_sentence_count: int
    compression_percentage: float


class ExtractiveSummarizer:
    """Generate summaries by ranking sentences from the original text."""

    def __init__(
        self,
        minimum_words: int = 50,
        minimum_sentence_words: int = 4,
    ) -> None:
        self.minimum_words = minimum_words
        self.minimum_sentence_words = minimum_sentence_words

    def summarize(
        self,
        text: str,
        ratio: float = 0.20,
    ) -> SummaryResult:
        """
        Summarize text by selecting the highest-ranked sentences.

        Args:
            text: Original article or document text.
            ratio: Approximate percentage of sentences to retain.

        Returns:
            SummaryResult containing the summary and statistics.

        Raises:
            ValueError: If the text is empty, too short, or invalid.
        """
        cleaned_text = self._clean_text(text)

        original_word_count = self._count_words(cleaned_text)

        if original_word_count < self.minimum_words:
            raise ValueError(
                f"Please provide at least {self.minimum_words} words. "
                f"The current text contains {original_word_count} words."
            )

        ratio = self._validate_ratio(ratio)
        sentences = self._split_sentences(cleaned_text)

        if len(sentences) < 3:
            raise ValueError(
                "The text must contain at least three complete sentences."
            )

        tokenized_sentences = [
            simple_preprocess(
                sentence,
                deacc=True,
                min_len=2,
                max_len=30,
            )
            for sentence in sentences
        ]

        valid_indices = [
            index
            for index, tokens in enumerate(tokenized_sentences)
            if len(tokens) >= self.minimum_sentence_words
        ]

        if len(valid_indices) < 2:
            raise ValueError(
                "The text does not contain enough complete sentences "
                "for summarization."
            )

        valid_sentences = [sentences[index] for index in valid_indices]
        valid_tokens = [tokenized_sentences[index] for index in valid_indices]

        scores = self._rank_sentences(valid_tokens)

        requested_sentence_count = max(
            1,
            math.ceil(len(sentences) * ratio),
        )

        selected_count = min(
            requested_sentence_count,
            len(valid_sentences),
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        selected_valid_indices = ranked_indices[:selected_count]

        selected_original_indices = sorted(
            valid_indices[index] for index in selected_valid_indices
        )

        selected_sentences = [
            sentences[index] for index in selected_original_indices
        ]

        summary = " ".join(selected_sentences).strip()

        summary_word_count = self._count_words(summary)

        compression_percentage = round(
            (summary_word_count / original_word_count) * 100,
            2,
        )

        return SummaryResult(
            summary=summary,
            original_word_count=original_word_count,
            summary_word_count=summary_word_count,
            original_sentence_count=len(sentences),
            summary_sentence_count=len(selected_sentences),
            compression_percentage=compression_percentage,
        )

    def _rank_sentences(
        self,
        tokenized_sentences: list[list[str]],
    ) -> list[float]:
        """Rank tokenized sentences using TF-IDF cosine similarity."""
        dictionary = Dictionary(tokenized_sentences)

        if len(dictionary) == 0:
            return [1.0 for _ in tokenized_sentences]

        corpus = [
            dictionary.doc2bow(tokens)
            for tokens in tokenized_sentences
        ]

        tfidf_model = TfidfModel(corpus)
        tfidf_corpus = [
            tfidf_model[document]
            for document in corpus
        ]

        sentence_count = len(tfidf_corpus)

        similarity_matrix = np.zeros(
            (sentence_count, sentence_count),
            dtype=float,
        )

        for first_index in range(sentence_count):
            for second_index in range(first_index + 1, sentence_count):
                similarity = cossim(
                    tfidf_corpus[first_index],
                    tfidf_corpus[second_index],
                )

                similarity_matrix[first_index][second_index] = similarity
                similarity_matrix[second_index][first_index] = similarity

        graph = nx.from_numpy_array(similarity_matrix)

        try:
            page_rank_scores = nx.pagerank(
                graph,
                weight="weight",
                max_iter=200,
            )

            return [
                page_rank_scores.get(index, 0.0)
                for index in range(sentence_count)
            ]

        except nx.PowerIterationFailedConvergence:
            return [
                float(np.sum(similarity_matrix[index]))
                for index in range(sentence_count)
            ]

    @staticmethod
    def _clean_text(text: str) -> str:
        """Normalize whitespace while preserving sentence punctuation."""
        if not isinstance(text, str):
            raise ValueError("The supplied content must be text.")

        cleaned_text = text.replace("\x00", " ")
        cleaned_text = re.sub(r"\r\n?", "\n", cleaned_text)
        cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
        cleaned_text = re.sub(r"\n{2,}", "\n", cleaned_text)
        cleaned_text = cleaned_text.strip()

        if not cleaned_text:
            raise ValueError("No text was provided.")

        return cleaned_text

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split text into sentences without requiring NLTK downloads."""
        normalized_text = re.sub(r"\s*\n+\s*", " ", text)

        sentence_pattern = re.compile(
            r"(?<=[.!?])\s+(?=[A-Z0-9\"'])"
        )

        sentences = sentence_pattern.split(normalized_text)

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    @staticmethod
    def _count_words(text: str) -> int:
        """Count words containing letters, digits, or apostrophes."""
        return len(re.findall(r"\b[\w’'-]+\b", text))

    @staticmethod
    def _validate_ratio(ratio: float) -> float:
        """Validate and normalize the requested summary ratio."""
        try:
            ratio_value = float(ratio)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "The summary ratio must be a number."
            ) from error

        if ratio_value > 1:
            ratio_value /= 100

        if not 0.10 <= ratio_value <= 0.50:
            raise ValueError(
                "The summary ratio must be between 10% and 50%."
            )

        return ratio_value
    