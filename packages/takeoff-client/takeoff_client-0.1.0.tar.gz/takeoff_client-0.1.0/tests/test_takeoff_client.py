import pytest
from takeoff_client import TakeoffClient

from unittest.mock import MagicMock, patch


class TestTakeoffClient:
    def test_initialization_default(self):
        client = TakeoffClient()
        assert client.base_url == "http://localhost"
        assert client.port == 8000
        assert client.mgmt_port == 8001
        assert client.url == "http://localhost:8000"
        assert client.mgmt_url == "http://localhost:8001"

    def test_initialization_custom(self):
        # test that mgmt_port is set to port + 1
        client = TakeoffClient("http://test", 9000)
        assert client.base_url == "http://test"
        assert client.port == 9000
        assert client.mgmt_port == 9001
        assert client.url == "http://test:9000"
        assert client.mgmt_url == "http://test:9001"

    def test_initalization_custom_mgmt_port(self):
        client = TakeoffClient("http://test", 9000, 9005)
        assert client.base_url == "http://test"
        assert client.port == 9000
        assert client.mgmt_port == 9005
        assert client.url == "http://test:9000"
        assert client.mgmt_url == "http://test:9005"

    def test_get_readers(self):
        mock_response = {
            "primary": [
                {
                    "reader_id": "test",
                    "backend": "test",
                    "model_name": "test",
                    "model_type": "test",
                    "pids": [0],
                    "ready": True,
                }
            ]
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response

            client = TakeoffClient()
            response = client.get_readers()

            mock_get.assert_called_once_with("http://localhost:8001/reader_groups")
            assert response == mock_response

    def test_embed(self):
        mock_response = {"text": ["embedded text"]}

        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200

            client = TakeoffClient()
            response = client.embed("text to embed")

            mock_post.assert_called_once()
            assert response == mock_response

            # Test that an Exception is raised when the status code is not 200
            mock_post.return_value.status_code = 400
            mock_post.return_value.text = "Error message"

            with pytest.raises(Exception) as e:
                client.embed("text to embed")

            assert str(e.value) == "Embedding failed\nStatus code: 400\nResponse: Error message"

    def test_generate(self):
        mock_response = {"text": "generated text"}

        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200

            client = TakeoffClient()
            response = client.generate("text to generate")

            mock_post.assert_called_once()
            assert response == mock_response

            # Test that an Exception is raised when the status code is not 200
            mock_post.return_value.status_code = 400
            mock_post.return_value.text = "Error message"

            with pytest.raises(Exception) as e:
                client.generate("text to generate")

            assert str(e.value) == "Generation failed\nStatus code: 400\nResponse: Error message"

    @pytest.fixture
    def mock_response(self):
        # Mocking a requests.Response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"data: Generated text 1\n", b"data: Generated text 2\n"]
        return mock_response

    def test_generate_stream_success(self, mock_response):
        # Setup
        text = "test text"
        url = "http://example.com/generate_stream"

        # Patching requests.post to return the mock_response
        with patch("requests.post", return_value=mock_response) as mock_post:
            instance = TakeoffClient()
            instance.url = "http://example.com"

            # Action
            result_generator = instance.generate_stream(text)
            result = list(result_generator)

            # Assert
            mock_post.assert_called_once_with(
                url=url,
                json={
                    "text": text,
                    "sampling_temperature": None,
                    "sampling_topp": None,
                    "sampling_topk": None,
                    "repetition_penalty": None,
                    "no_repeat_ngram_size": None,
                    "max_new_tokens": None,
                    "min_new_tokens": None,
                    "regex_string": None,
                    "json_schema": None,
                    "prompt_max_tokens": None,
                    "consumer_group": "primary",
                },
                stream=True,
            )

            assert len(result) == 2
            assert result[0] == "Generated text 1"
            assert result[1] == "Generated text 2"

    def test_generate_stream_failure(self, mock_response):
        # Setup for failure scenario
        mock_response.status_code = 400
        mock_response.text = "Error message"
        text = "test text"

        with patch("requests.post", return_value=mock_response):
            instance = TakeoffClient()
            instance.url = "http://example.com"

            # Assert exception is raised on failure
            with pytest.raises(Exception) as excinfo:
                _ = list(instance.generate_stream(text))

            assert "Generation failed" in str(excinfo.value)
