import pytest
from OCR.name_matcher import NameMatcher

class TestNameMatcher:
    @pytest.fixture
    def matcher(self):
        return NameMatcher()

    def test_initialization(self, matcher):
        """Test that the matcher initializes correctly."""
        assert matcher.llm is not None
        assert matcher.prompt is not None

    def test_fuzzy_matches(self, matcher):
        """Test fuzzy matching functionality."""
        database_names = [
            "rachit fashion",
            "ruchit fashion",
            "radhika fashion",
            "impact fashion",
            "pragti fashion"
        ]
        
        matches = matcher.get_fuzzy_matches("rachit fashion", database_names)
        assert len(matches) > 0
        assert isinstance(matches[0], tuple)
        assert len(matches[0]) == 2  # (name, score)
        assert isinstance(matches[0][0], str)
        assert isinstance(matches[0][1], float)

    @pytest.mark.integration
    def test_verify_match(self, matcher):
        """Test LLM verification of matches."""
        if not matcher.llm.api_key:
            pytest.skip("OpenAI API key not found")

        candidates = [
            "rachit fashion",
            "ruchit fashion",
            "radhika fashion",
            "impact fashion",
            "pragti fashion"
        ]

        # Test exact match
        result = matcher.verify_match("rachit fashion", candidates)
        assert result == "rachit fashion"

        # Test similar match
        result = matcher.verify_match("ruchit fashon", candidates)
        assert result == "ruchit fashion"

        # Test no match
        result = matcher.verify_match("totally different name", candidates)
        assert result is None

    @pytest.mark.integration
    def test_find_match(self, matcher):
        """Test the complete matching pipeline."""
        if not matcher.llm.api_key:
            pytest.skip("OpenAI API key not found")

        # Test with actual database
        # Note: This test depends on database content
        result = matcher.find_match("rachit fashion", "supplier")
        assert isinstance(result, (str, type(None)))

    def test_error_handling(self, matcher):
        """Test error handling in various scenarios."""
        # Test with empty candidates
        result = matcher.verify_match("test", [])
        assert result is None

        # Test with empty query
        result = matcher.verify_match("", ["test1", "test2"])
        assert result is None

        # Test fuzzy matching with empty database
        matches = matcher.get_fuzzy_matches("test", [])
        assert len(matches) == 0
