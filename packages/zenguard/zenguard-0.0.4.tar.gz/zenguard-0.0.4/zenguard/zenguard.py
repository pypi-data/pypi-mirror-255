"""
ZenGuard is a class that represents the ZenGuard object. It is used to connect to ZenGuard AI API and its services.
"""

import os
from enum import Enum
from openai import OpenAI
import httpx

class Chunk:
    """
    Represents a chunk of operations in the ZenGuard API.

    Args:
        zen_guard_instance (ZenGuard): The ZenGuard instance.

    """

    def __init__(self, zen_guard_instance):
        self.zen_guard_instance = zen_guard_instance  # Store the ZenGuard instance

    def __getattr__(self, name):
        # creating a call method dynamically
        self.zen_guard_instance._dynamic_call = getattr(
            self.zen_guard_instance._dynamic_call, name, None
        )
        return Chunk(self.zen_guard_instance)

    def __call__(self, **kwargs):
        try:
            # TODO Add support for different websockets
            response = httpx.post(
                self.zen_guard_instance._backend + "/guard",
                json=kwargs,
                headers={"Authorization": self.zen_guard_instance._api_key},
                timeout=3,
            )
            response.raise_for_status()
        except httpx.RequestError as e:
            # TODO Add proper handling of errors
            return {"error": str(e)}

        # TODO handle backend response before calling the LLM

        return self.zen_guard_instance._dynamic_call(**kwargs)


class ZenGuard:
    """
    ZenGuard is a class that represents the ZenGuard object.
    It is used to connect to ZenGuard AI API and its services.
    """

    class Model(Enum):
        """
        Enumeration representing different models.
        """

        CHAT_GPT = "chatGPT"
        BARD = "Bard"

    def __init__(
        self,
        zen_api_key,
        model,
        model_api_key,
    ):
        """
        Initializes a new instance of the ZenGuard class.

        Args:
            zen_api_key (str): The API key for ZenGuard.
            model (ZenGuard.Model): The model to be used.
            model_api_key (str): The API key for the specific model.

        Returns:
            None
        """
        self._api_key = zen_api_key

        if os.environ.get("PYTHON_CLIENT_ENV") == "local":
            self._backend = "http://localhost:8080/"
        else:
            self._backend = "https://dummyai-backend-gwlrf6iakq-uc.a.run.app/"

        if model == ZenGuard.Model.CHAT_GPT:
            self._dynamic_call = OpenAI(api_key=model_api_key)

    def __getattr__(self, name):
        return Chunk(self).__getattr__(name)
