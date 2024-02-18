import json
import logging
import openai
import os
from datetime import datetime
from supabase.client import create_client, Client
from supabase.lib.client_options import ClientOptions
import logging


class _SupabaseClient:
    def __init__(self):
        url: str = os.environ.get(
            "INSTANCE_URL", default="https://qdgodxkfxzzmzwfliahh.supabase.co"
        )
        key: str = os.environ.get(
            "INSTANCE_ANON_KEY",
            default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFkZ29keGtmeHp6bXp3ZmxpYWhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODg0OTc0NzcsImV4cCI6MjAwNDA3MzQ3N30.4bgCdg77wwOJ9w1hOtCD-z0gBVGv8X_kIxBCr5KDCuA",
        )

        # API key format is organization:api_key
        talc_api_key: str = os.environ.get("TALC_API_KEY", default="")

        if talc_api_key == "":
            logging.warning(
                "TALC_API_KEY environment variable not set. Logging disabled."
            )
            self.__initialized = False
            return

        organization, api_key = talc_api_key.split(":")
        self.__organization: str = organization

        options = ClientOptions(headers={"talckey": api_key})
        self.supabase: Client = create_client(url, key, options=options)
        self.__initialized = True

    def createSession(self):
        if not self.__initialized:
            return None
        response = (
            self.supabase.table("sessions")
            .insert(
                {
                    "organization": self.__organization,
                }
            )
            .execute()
        )
        return response.data[0]["id"]

    def __createInput(
        self, sessionId, generationId, role, content, name, function_call, index
    ):
        response = (
            self.supabase.table("inputs")
            .insert(
                {
                    "session": sessionId,
                    "generation": generationId,
                    "role": role,
                    "content": content,
                    "index": index,
                    "name": name,
                    "function_call": function_call,
                }
            )
            .execute()
        )
        return response.data[0]["id"]

    def __createGeneration(
        self,
        sessionId,
        content,
        function_calls,
        agent,
        generated_at,
        functions_available,
        parameters,
    ):
        response = (
            self.supabase.table("generations")
            .insert(
                {
                    "session": sessionId,
                    "content": content,
                    "functions_called": function_calls,
                    "agent": agent,
                    "generated_at": generated_at,
                    "functions_available": functions_available,
                    "parameters": parameters,
                }
            )
            .execute()
        )
        return response.data[0]["id"]

    def __historyArrayToInputs(self, history, generationId, sessionId):
        for index, chat in enumerate(history):
            encoded_function_call = None
            if "function_call" in chat:
                encoded_function_call = json.dumps(chat["function_call"])

            self.__createInput(
                sessionId,
                generationId,
                chat["role"],
                chat["content"],
                chat.get("name", None),  # Name is optional
                encoded_function_call,
                # Index is reversed because we want the most recent message to have the lowest index
                len(history) - index,
            )

    def log(
        self,
        sessionId,
        history,
        text_content,
        function_calls,
        agent,
        functions_available,
        parameters,
    ):
        generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        generationId = self.__createGeneration(
            sessionId,
            text_content,
            function_calls,
            agent,
            generated_at,
            functions_available,
            parameters,
        )
        self.__historyArrayToInputs(history, generationId, sessionId)


def createSession():
    response = client.createSession()
    return response


def init():
    global client
    client = _SupabaseClient()


globalSession = None


def setGlobalSession(session):
    global globalSession
    globalSession = session


class __alternateCompletion(openai.ChatCompletion):
    @classmethod
    def create(cls, *args, **kwargs):
        # Pop arguments that are not supported by the original create method
        agent = kwargs.pop("agent", "Default")
        session = kwargs.pop("session", globalSession)
        stream = "stream" in kwargs and kwargs["stream"]

        # Handle case where we have received the full response at once.
        if not stream:
            result = super().create(*args, **kwargs)
            try:
                functions_available, parameters = cls.__getFunctionsAndParameters(
                    **kwargs
                )
                text_content, function_calls = cls.__getContent(result.choices)
                if session and agent:
                    client.log(
                        session,
                        kwargs["messages"],
                        text_content,
                        function_calls,
                        agent,
                        functions_available,
                        parameters,
                    )
            except Exception as e:
                logging.warning("Error logging to talc: ", e)

            return result
        # Handle stream case
        else:
            return cls.__streamContent(session=session, agent=agent, *args, **kwargs)

    # Handles the case where we are streaming the response
    # This is really complicated. Godspeed.
    @classmethod
    def __streamContent(cls, *args, **kwargs):
        agent = kwargs.pop("agent", "Default")
        session = kwargs.pop("session", globalSession)

        generator = super().create(*args, **kwargs)

        choices = {}
        final_choice = None

        for result in generator:
            contains_incomplete_option = False
            for index, choice in enumerate(result.choices):
                # Identify if we have at least one incomplete option still streaming
                if choice.finish_reason is None:
                    contains_incomplete_option = True

                if index not in choices:
                    choices[index] = []
                choices[index].append(choice)
            if not contains_incomplete_option:
                final_choice = result
                break  # We have received the full response, break before returning so we can log.
            yield result

        final_content = []
        final_function_calls = []

        # Try not to find bugs in this code, because it's going to be
        # a pain to fix.
        try:
            # Accumulate all the content and function calls for each option
            for option in choices:
                content_accumulator = []
                function_call_accumulator = []
                arguments_accumulator = []
                for chunk in choices[option]:
                    if "delta" in chunk:
                        if "content" in chunk.delta:
                            content_accumulator.append(chunk.delta["content"])
                        if "function_call" in chunk.delta:
                            if "name" in chunk.delta["function_call"]:
                                function_call_accumulator.append(
                                    chunk.delta["function_call"]["name"]
                                )
                            if "arguments" in chunk.delta["function_call"]:
                                arguments_accumulator.append(
                                    chunk.delta["function_call"]["arguments"]
                                )
                if len(content_accumulator) > 0:
                    final_content.append(
                        "".join([x for x in content_accumulator if x != None])
                    )
                else:
                    final_content.append(None)
                if len(function_call_accumulator) > 0:
                    final_function_calls.append(
                        {
                            "name": "".join(
                                [x for x in function_call_accumulator if x != None]
                            ),
                            "arguments": "".join(
                                [x for x in arguments_accumulator if x != None]
                            ),
                        }
                    )
                else:
                    final_function_calls.append(None)
            # Log the accumulated options
            if session and agent:
                functions_available, parameters = cls.__getFunctionsAndParameters(
                    **kwargs
                )
                client.log(
                    session,
                    kwargs["messages"],
                    final_content,
                    final_function_calls,
                    agent,
                    functions_available,
                    parameters,
                )
        except Exception as e:
            logging.warning("Error logging to talc: ", e)

        return final_choice

    @classmethod
    async def __streamContentAsync(cls, *args, **kwargs):
        agent = kwargs.pop("agent", "Default")
        session = kwargs.pop("session", globalSession)

        generator = super().acreate(*args, **kwargs)

        choices = {}
        final_choice = None

        async for result in await generator:
            contains_incomplete_option = False
            for index, choice in enumerate(result.choices):
                # Identify if we have at least one incomplete option still streaming
                if choice.finish_reason is None:
                    contains_incomplete_option = True

                if index not in choices:
                    choices[index] = []
                choices[index].append(choice)
            if not contains_incomplete_option:
                final_choice = result
                break  # We have received the full response, break before returning so we can log.
            yield result

        final_content = []
        final_function_calls = []

        # Try not to find bugs in this code, because it's going to be
        # a pain to fix.
        try:
            # Accumulate all the content and function calls for each option
            for option in choices:
                content_accumulator = []
                function_call_accumulator = []
                arguments_accumulator = []
                for chunk in choices[option]:
                    if "delta" in chunk:
                        if "content" in chunk.delta:
                            content_accumulator.append(chunk.delta["content"])
                        if "function_call" in chunk.delta:
                            if "name" in chunk.delta["function_call"]:
                                function_call_accumulator.append(
                                    chunk.delta["function_call"]["name"]
                                )
                            if "arguments" in chunk.delta["function_call"]:
                                arguments_accumulator.append(
                                    chunk.delta["function_call"]["arguments"]
                                )
                if len(content_accumulator) > 0:
                    final_content.append(
                        "".join([x for x in content_accumulator if x != None])
                    )
                else:
                    final_content.append(None)
                if len(function_call_accumulator) > 0:
                    final_function_calls.append(
                        {
                            "name": "".join(
                                [x for x in function_call_accumulator if x != None]
                            ),
                            "arguments": "".join(
                                [x for x in arguments_accumulator if x != None]
                            ),
                        }
                    )
                else:
                    final_function_calls.append(None)
            # Log the accumulated options
            if session and agent:
                functions_available, parameters = cls.__getFunctionsAndParameters(
                    **kwargs
                )
                client.log(
                    session,
                    kwargs["messages"],
                    final_content,
                    final_function_calls,
                    agent,
                    functions_available,
                    parameters,
                )
        except Exception as e:
            logging.warning("Error logging to talc: ", e)

        yield final_choice
        return

        # print("Content ", option, ":", "".join(content_accumulator))
        # print("Function call ", option, ":", "".join(function_call_accumulator))
        # print("Arguments ", option, ":", "".join(arguments_accumulator))
        # print("=====================================")

    @classmethod
    async def acreate(cls, *args, **kwargs):
        # Pop arguments that are not supported by the original create method
        agent = kwargs.pop("agent", "Default")
        session = kwargs.pop("session", globalSession)
        stream = "stream" in kwargs and kwargs["stream"]

        # Handle case where we have received the full response at once.
        if not stream:
            result = await super().acreate(*args, **kwargs)
            try:
                functions_available, parameters = cls.__getFunctionsAndParameters(
                    **kwargs
                )
                text_content, function_calls = cls.__getContent(result.choices)
                if session and agent:
                    client.log(
                        session,
                        kwargs["messages"],
                        text_content,
                        function_calls,
                        agent,
                        functions_available,
                        parameters,
                    )
            except Exception as e:
                logging.warning("Error logging to talc: ", e)

            return result
        # Handle stream case
        else:
            return cls.__streamContentAsync(
                session=session, agent=agent, *args, **kwargs
            )

    @classmethod
    def __getContent(cls, choices):
        text_content = []
        function_calls = []

        for choice in choices:
            if "function_call" in choice.message:
                function_calls.append(choice.message.function_call)
            else:
                function_calls.append(None)

            if "content" in choice.message:
                text_content.append(choice.message.content)
            else:
                text_content.append(None)

        return text_content, function_calls

    @classmethod
    def __getFunctionsAndParameters(cls, **kwargs):
        functions = None
        if "functions" in kwargs:
            functions = kwargs["functions"]

        ignored_params = ["functions", "messages"]

        parameters = {
            key: val for (key, val) in kwargs.items() if key not in ignored_params
        }

        return json.dumps(functions), json.dumps(parameters)


openai.ChatCompletion = __alternateCompletion
