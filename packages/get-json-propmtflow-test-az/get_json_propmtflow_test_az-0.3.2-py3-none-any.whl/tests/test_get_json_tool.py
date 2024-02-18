import pytest
import unittest
from get_json.tools.get_json_tool import get_json_object


@pytest.fixture
def get_string_to_json()->str:
    return '{"Name": "Max", "Nachname": "Mustermann", "Strasse": "Mustermannstraße 1"}'


class TestTool:
    def test_get_json_object(self, get_string_to_json):
        result = get_json_object(input_text=get_string_to_json)
        assert result == "Max"


# Run the unit tests
if __name__ == "__main__":
    unittest.main()