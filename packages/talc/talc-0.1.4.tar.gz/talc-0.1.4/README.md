# Talc AI debugger

Replay your LLM's sessions straight from the logs, change inputs and prompts, and easily figure out exactly what's wrong with your LLM.

## Installing Talc

Install the logging library:

```
pip install talc
```

## Setup

### Step 1: Set up your environment

Add your talc API key to the environment under the name `TALC_API_KEY`.

```
TALC_API_KEY=<your key>
```

If you do not have an API key, [join the beta](https://talc.ai).

### Step 1: Initialize

Import the library and initialize talc:

```python
from talc import logger

logger.init()

```

This only needs to be done once when your program loads.

### Step 2: Create session

Talc uses the concept of "sessions", which are sets of related calls to openai. For example, a chat session might be composed of all the calls in a single chat thread. Saving the calls to a single session lets you see all of the context in one place.

To create a session:

```python
sessionId = logger.createSession()
```

### Step 3: Log calls


Talc automatically integrates with the OpenAI chat completion API, so all you need to do is pass an additional parameter to your calls. 

Add the `session=sessionId` parameter to your chat completion calls:

```python
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=messages,
    session=sessionId,
)
```

If you are using a wrapper library like SemanticKernel and don't have access to the direct chat completion call, you can set the session globally:

```python
session_id = logger.createSession()
logger.setGlobalSession(session_id)
```

If your application uses agents or multistep chains, you can add the optional `agent` parameter to identify the current agent or step of the chain:

```python
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=messages,
    session=sessionId,
    agent="Router Agent",
)
```