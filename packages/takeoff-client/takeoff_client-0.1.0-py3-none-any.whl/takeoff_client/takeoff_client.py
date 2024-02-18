"""This module contains the TakeoffClient class, which is used to interact with the Takeoff server."""
# ────────────────────────────────────────────────────── Import ────────────────────────────────────────────────────── #

from typing import Any, List, Iterator
from sseclient import Event, SSEClient
import requests


# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                                                    Takeoff Client                                                    #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #


class TakeoffClient:
    def __init__(self, base_url: str = "http://localhost", port: int = 3000, mgmt_port: int = None):
        """TakeoffClient is used to interact with the Takeoff server.

        Args:
            base_url (str, optional): base url that takeoff server runs on. Defaults to "http://localhost".
            port (int, optional): port that main server runs on. Defaults to 8000.
            mgmt_port (int, optional): port that management api runs on. Usually be `port + 1`. Defaults to None.
        """
        self.base_url = base_url  # "http://localhost"
        self.port = port  # 8000

        if mgmt_port is None:
            self.mgmt_port = port + 1  # 8001
        else:
            self.mgmt_port = mgmt_port

        self.url = f"{self.base_url}:{self.port}"  # "http://localhost:3000"
        self.mgmt_url = f"{self.base_url}:{self.mgmt_port}"  # "http://localhost:3001"

    def get_readers(self) -> dict:
        """Get a list of information about all readers.

        Returns:
            dict: List of information about all readers.
        """
        response = requests.get(self.mgmt_url + "/reader_groups")
        return response.json()

    def embed(self, text: str | List[str], consumer_group: str = "embed") -> dict:
        """Embed a batch of text.

        Args:
            text (str | List[str]): Text to embed.
            consumer_group (str, optional): consumer group to use. Defaults to "embed".

        Returns:
            dict: Embedding response.
        """
        response = requests.post(self.url + "/embed", json={"text": text, "consumer_group": consumer_group})

        if response.status_code != 200:
            raise Exception(f"Embedding failed\nStatus code: {str(response.status_code)}\nResponse: {response.text}")

        return response.json()

    def classify(self, text: str | List[str] | List[List[str]], consumer_group: str = "classify") -> dict:
        """Classify a batch of text. 
            
        Text that is passed in as a list of list of strings will be concatenated on the 
        innermost list, and the outermost list treated as a batch of concatenated strings.

        Concatenation happens server-side, as it needs information from the model tokenizer. 
        
        Args:
            text (str | List[str] | List[List[str]]): Text to classify. 
            consumer_group (str, optional): consumer group to use. Defaults to "classify".

        Returns:
            dict: Classification response.
        """

        response = requests.post(self.url + "/classify", json={"text": text, "consumer_group": consumer_group})
        if response.status_code != 200:
            raise Exception(f"Classification failed\nStatus code: {str(response.status_code)}\nResponse: {response.text}")

        return response.json()

    def generate(
        self,
        text: str | List[str],
        sampling_temperature: float = None,
        sampling_topp: float = None,
        sampling_topk: int = None,
        repetition_penalty: float = None,
        no_repeat_ngram_size: int = None,
        max_new_tokens: int = None,
        min_new_tokens: int = None,
        regex_string: str = None,
        json_schema: Any = None,
        prompt_max_tokens: int = None,
        consumer_group: str = "primary",
    ) -> dict:
        """Generates text, seeking a completion for the input prompt. Buffers output and returns at once.

        Args:
            text (str): Input prompt from which to generate
            sampling_topp (float, optional): Sample from set of tokens whose cumulative probability exceeds this value
            sampling_temperature (float, optional): Sample predictions from the top K most probable candidates
            sampling_topk (int, optional): Sample with randomness. Bigger temperatures are associated with more randomness.
            repetition_penalty (float, optional): Penalise the generation of tokens that have been generated before. Set to > 1 to penalize.
            no_repeat_ngram_size (int, optional): Prevent repetitions of ngrams of this size.
            max_new_tokens (int, optional): The maximum number of (new) tokens that the model will generate.
            min_new_tokens (int, optional): The minimum number of (new) tokens that the model will generate.
            regex_string (str, optional): The regex string which generations will adhere to as they decode.
            json_schema (dict, optional): The JSON Schema which generations will adhere to as they decode. Ignored if regex_str is set.
            prompt_max_tokens (int, optional): The maximum length (in tokens) for this prompt. Prompts longer than this value will be truncated.
            consumer_group (str, optional): The consumer group to which to send the request.

        Returns:
            Output (dict): The response from Takeoff containing the generated text as a whole.

        """
        response = requests.post(
            url=self.url + "/generate",
            json={
                "text": text,
                "sampling_temperature": sampling_temperature,
                "sampling_topp": sampling_topp,
                "sampling_topk": sampling_topk,
                "repetition_penalty": repetition_penalty,
                "no_repeat_ngram_size": no_repeat_ngram_size,
                "max_new_tokens": max_new_tokens,
                "min_new_tokens": min_new_tokens,
                "regex_string": regex_string,
                "json_schema": json_schema,
                "prompt_max_tokens": prompt_max_tokens,
                "consumer_group": consumer_group,
            },
        )
        if response.status_code != 200:
            raise Exception(f"Generation failed\nStatus code: {str(response.status_code)}\nResponse: {response.text}")

        return response.json()

    def generate_stream(
        self,
        text: str | List[str],
        sampling_temperature: float = None,
        sampling_topp: float = None,
        sampling_topk: int = None,
        repetition_penalty: float = None,
        no_repeat_ngram_size: int = None,
        max_new_tokens: int = None,
        min_new_tokens: int = None,
        regex_string: str = None,
        json_schema: dict = None,
        prompt_max_tokens: int = None,
        consumer_group: str = "primary",
    ) -> Iterator[Event]:
        """Generates text, seeking a completion for the input prompt.

        Args:
            text (str | List[str]): Input prompt from which to generate
            sampling_temperature (float, optional): Sample predictions from the top K most probable candidates
            sampling_topp (float, optional): Sample from set of tokens whose cumulative probability exceeds this value
            sampling_topk (int, optional): Sample with randomness. Bigger temperatures are associated with more randomness.
            repetition_penalty (float, optional): Penalise the generation of tokens that have been generated before. Set to > 1 to penalize.
            no_repeat_ngram_size (int, optional): Prevent repetitions of ngrams of this size.
            max_new_tokens (int, optional): The maximum number of (new) tokens that the model will generate.
            min_new_tokens (int, optional): The minimum number of (new) tokens that the model will generate.
            regex_string (str, optional): The regex string which generations will adhere to as they decode.
            json_schema (dict, optional): The JSON Schema which generations will adhere to as they decode. Ignored if regex_str is set.
            prompt_max_tokens (int, optional): The maximum length (in tokens) for this prompt. Prompts longer than this value will be truncated.
            consumer_group (str, optional): The consumer group to which to send the request.

        Returns:
            Iterator[sseclient.SSEClient.Event]: An iterator of server-sent events.

        """
        response = requests.post(
            url=self.url + "/generate_stream",
            json={
                "text": text,
                "sampling_temperature": sampling_temperature,
                "sampling_topp": sampling_topp,
                "sampling_topk": sampling_topk,
                "repetition_penalty": repetition_penalty,
                "no_repeat_ngram_size": no_repeat_ngram_size,
                "max_new_tokens": max_new_tokens,
                "min_new_tokens": min_new_tokens,
                "regex_string": regex_string,
                "json_schema": json_schema,
                "prompt_max_tokens": prompt_max_tokens,
                "consumer_group": consumer_group,
            },
            stream=True,
        )
        if response.status_code != 200:
            raise Exception(f"Generation failed\nStatus code: {str(response.status_code)}\nResponse: {response.text}")

        # return a python generator
        return SSEClient(response).events()


if __name__ == "__main__":
    pass
