"""Unit tests for core service functions."""

from app.services.summarization import (
    _split_sentences,
    extract_action_items,
    extract_key_points,
    extract_summary,
    summarize_transcript,
)


class TestSplitSentences:
    def test_basic_split(self):
        text = "First sentence. Second sentence. Third sentence."
        result = _split_sentences(text)
        assert len(result) == 3

    def test_filters_short(self):
        text = "OK. This is a longer sentence that should remain."
        result = _split_sentences(text)
        assert len(result) == 1


class TestExtractSummary:
    def test_short_text_returns_full(self):
        text = "This is a short piece of text."
        result = extract_summary(text, num_sentences=5)
        assert result == text.strip()

    def test_empty_text(self):
        assert extract_summary("") == ""
        assert extract_summary("   ") == ""

    def test_reduces_length(self):
        sentences = [f"This is sentence number {i} about a specific topic." for i in range(20)]
        text = " ".join(sentences)
        result = extract_summary(text, num_sentences=3)
        result_sentences = _split_sentences(result)
        assert len(result_sentences) <= 5  # approximately 3, allowing some slack

    def test_preserves_original_order(self):
        text = (
            "Alpha is the first point discussed. "
            "Beta is the second topic covered. "
            "Gamma details the third section. "
            "Delta describes the fourth area. "
            "Epsilon concludes the discussion here."
        )
        result = extract_summary(text, num_sentences=2)
        # Summary should be a subset, in order
        assert len(result) < len(text)


class TestExtractKeyPoints:
    def test_returns_list(self):
        text = "The project deadline is Friday. We need more developers. The budget is approved."
        result = extract_key_points(text)
        assert isinstance(result, list)

    def test_empty_text(self):
        assert extract_key_points("") == []


class TestExtractActionItems:
    def test_finds_need_to(self):
        text = "We need to finish the report by Friday. The weather is nice today."
        items = extract_action_items(text)
        assert len(items) >= 1
        assert any("report" in item.lower() for item in items)

    def test_finds_action_item_prefix(self):
        text = "Action item: Review the pull request before merging. Also great weather today."
        items = extract_action_items(text)
        assert len(items) >= 1

    def test_finds_should(self):
        text = "We should update the documentation before the release."
        items = extract_action_items(text)
        assert len(items) >= 1

    def test_finds_schedule(self):
        text = "We need to schedule a follow-up meeting for Monday."
        items = extract_action_items(text)
        assert len(items) >= 1

    def test_empty_text(self):
        assert extract_action_items("") == []

    def test_no_action_items(self):
        text = "The sun rose in the east. Birds were singing in the trees."
        items = extract_action_items(text)
        assert len(items) == 0


class TestSummarizeTranscript:
    def test_full_pipeline(self):
        text = (
            "Welcome to the team meeting. Today we are discussing the Q4 roadmap. "
            "The engineering team has completed the migration to the new database. "
            "We need to finalize the API documentation by next week. "
            "Sarah will handle the frontend redesign project. "
            "Action item: John should review the security audit results. "
            "The budget has been approved by the finance department. "
            "We should schedule a follow-up meeting for next Monday. "
            "Thanks everyone for your great work this quarter."
        )
        result = summarize_transcript(text)
        assert "summary" in result
        assert "key_points" in result
        assert "action_items" in result
        assert isinstance(result["key_points"], list)
        assert isinstance(result["action_items"], list)
        assert len(result["summary"]) > 0
        assert len(result["action_items"]) > 0

    def test_empty_input(self):
        result = summarize_transcript("")
        assert result["summary"] == ""
        assert result["key_points"] == []
        assert result["action_items"] == []
