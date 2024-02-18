# Takeoff Python Client Library

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About <a name = "about"></a>

The Takeoff Python Client Library serves as an essential tool for interacting with the Takeoff Server. It simplifies the process of sending requests to the server, offering a streamlined, Pythonic interface. This library is designed for developers who need to integrate their Python applications with the Takeoff Server, providing them with a robust and efficient way to communicate with the server's API.



## Getting Started <a name = "getting_started"></a>

### Installing

To get started with the Takeoff Python Client Library, you can install it directly using pip:
```
pip install takeoff_client
```

Alternatively, if you are working on developing the library, you can install it in editable mode. This allows you to make changes to the library and test them in real-time. Navigate to the `python-client-sdk` folder and run the following command:
```
pip install -e . 
```

## Usage <a name = "usage"></a>

### Establishing a Connection
To start using the client, you need to establish a connection with the Takeoff Server. You can do this by creating an instance of the TakeoffClient. Replace "http://localhost" and 3000 with the appropriate URL and port of your Takeoff Server.

```
client = TakeoffClient(base_url="http://localhost", port=3000)
```

### Interaction with Server 

For more details, please check the API documentation below.

#### Retrieving Reader Information

To get information about the reader from the server, use the get_reader() method. This method sends a request to the server and returns reader-related information.
```
client.get_reader() 
```

#### Embedding
For querying the embedding model, use the embed() method. 

```
client.embed("Text to embed")
```

#### Generation 
To generate text based on a given input, use the generate() method.

```
client.generate("Text to generate")
```

## Takeoff Python Client API Documentation


To convert the provided method descriptions into API documentation, I'll structure each description to include key components like a brief overview, parameters, return type, and any additional notes or exceptions. Here's how the API documentation can be structured:

---

### Takeoff Python Client API Documentation

#### 1. `get_readers()`

**Overview:**
Retrieves a list of information about all readers from the Takeoff Server.

**Returns:**
- `dict`: A dictionary containing information about all readers.

**Example Usage:**
```python
reader_info = client.get_readers()
```

---

#### 2. `embed(text, consumer_group="embed")`

**Overview:**
Embeds a batch of text using the specified consumer group.

**Parameters:**
- `text` (str | List[str]): The text or list of texts to be embedded.
- `consumer_group` (str, optional): The consumer group to use for embedding. Defaults to "embed".

**Returns:**
- `dict`: A dictionary containing the embedding response.

**Exceptions:**
- Raises an exception if the embedding request fails.

**Example Usage:**
```python
embedding_response = client.embed("Sample text")
```

---

#### 3. `generate(text, sampling_temperature=None, sampling_topp=None, sampling_topk=None, repetition_penalty=None, no_repeat_ngram_size=None, max_new_tokens=None, min_new_tokens=None, regex_string=None, json_schema=None, prompt_max_tokens=None, consumer_group="primary")`

**Overview:**
Generates text based on the given input and parameters.

**Parameters:**
- `text` (str | List[str]): The input text or list of texts for generation.
- Additional optional parameters for controlling text generation:
    - `sampling_temperature` (float)
    - `sampling_topp` (float)
    - `sampling_topk` (int)
    - `repetition_penalty` (float)
    - `no_repeat_ngram_size` (int)
    - `max_new_tokens` (int)
    - `min_new_tokens` (int)
    - `regex_string` (str)
    - `json_schema` (Any)
    - `prompt_max_tokens` (int)
    - `consumer_group` (str): Defaults to "primary".

**Returns:**
- `dict`: A dictionary containing the generated text response.

**Exceptions:**
- Raises an exception if the text generation request fails.

**Example Usage:**
```python
generated_text = client.generate("Sample input text")
```

---

#### 4. `generate_stream(text, sampling_temperature=None, sampling_topp=None, sampling_topk=None, repetition_penalty=None, no_repeat_ngram_size=None, max_new_tokens=None, min_new_tokens=None, regex_string=None, json_schema=None, prompt_max_tokens=None, consumer_group="primary")`

**Overview:**
Similar to `generate`, but returns an iterator for streaming the generated text.

**Parameters:**
- Same as `generate` method.

**Returns:**
- `Iterator[Event]`: An iterator that yields a server sent event

**Exceptions:**
- Raises an exception if the text generation request fails.

**Example Usage:**
```python
generator = client.generate_stream(["Sample input"])
for event in generator:
    print(event.data)
```

---
