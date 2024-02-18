from takeoff_client.sse import parse_sse_stream_response
from requests.models import Response
from unittest.mock import MagicMock


def test_parse_sse_stream_response():
    # Create a mock Response object
    mock_response = MagicMock(spec=Response)

    # Define the content to be returned by iter_content
    mock_response.iter_content.return_value = [b"data: Test data 0\n", b"data: Test data 1\n", b"data: Test data 2\n"]

    # Call the function with the mocked response
    generator = parse_sse_stream_response(mock_response)

    # Convert the generator to a list for easy testing
    result = list(generator)

    # Assertions
    assert len(result) == 3
    assert result[0] == "Test data 0"
    assert result[1] == "Test data 1"
    assert result[2] == "Test data 2"
