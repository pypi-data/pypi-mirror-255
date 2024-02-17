"""

MYLLM Main 🤖

"""

from loguru import logger

from myllm import __version__
from myllm.config import settings
from myllm.provider import G4FLLM, BardLLM, Ollama, OpenAILLM


class MyLLM:
    """

    MyLLM class use to initiate a LLM client
    with a given model and a given provider

    Attributes:
        clients (list): List of LLM clients

    Methods:
        _create_client(self, **kwargs)
        get_info(self)
        get_chats(self, prompt)


    """

    def __init__(self):
        """
        Initialize the MyLLM object which supports multiple LLM libraries

        Args:
            None
        """

        self.enabled = settings.myllm_enabled
        if not self.enabled:
            return
        logger.info("Initializing MyLLM")
        config = settings.myllm
        self.clients = []
        for item in config:
            logger.debug("Client configuration starting: {}", item)
            _config = config[item]
            if item in ["", "template"]:
                continue
            provider = item
            if provider not in ["g4f", "openai", "bard"]:
                logger.warning(
                    f"Skipping client creation for unsupported provider: {provider}"
                )
                continue
            logger.debug("Client provider: {}", provider)
            if _config.get("enabled") is True:
                client = self._create_client(
                    llm_library=provider,
                    enabled=_config.get("enabled") or True,
                    llm_model=_config.get("llm_model"),
                    llm_provider=_config.get("llm_provider"),
                    llm_provider_key=_config.get("llm_provider_key"),
                    max_memory=_config.get("max_memory") or 5,
                    timeout=_config.get("timeout") or 10,
                    temperature=_config.get("temperature") or 0,
                    token_limit=_config.get("token_limit") or 400,
                    llm_prefix=_config.get("llm_prefix") or "",
                    llm_template=_config.get("llm_template")
                    or "You are an AI assistant.",
                )
                logger.debug("Client: {}", client)
                if client.client:
                    self.clients.append(client)
                    logger.debug(f"Loaded {item}")

        if self.clients:
            logger.info(f"Loaded {len(self.clients)} LLM clients")
        else:
            logger.warning("No LLM clients loaded. Verify config")

    def _create_client(self, **kwargs):
        """

        Create a client based on the given protocol.

        Parameters:
            **kwargs (dict): Keyword arguments that
            contain the necessary information for creating the client.
            The "llm_library" key is required.

        Returns:
            client object based on
            the specified protocol.

        """
        logger.debug("Creating client {}", kwargs["llm_library"])
        if kwargs["llm_library"] == "bard":
            return BardLLM(**kwargs)
        elif kwargs["llm_library"] == "openai":
            return OpenAILLM(**kwargs)
        elif kwargs["llm_library"] == "ollama":
            return Ollama(**kwargs)
        else:
            return G4FLLM(**kwargs)

    async def get_info(self):
        """
        Retrieves information about the exchange
        and the account.

        :return: A formatted string containing
        the exchange name and the account information.
        :rtype: str
        """
        version_info = f"ℹ️ {type(self).__name__} {__version__}\n"
        client_info = "".join(
            f"🤖 {client.llm_library} {client.llm_model}\n" for client in self.clients
        )
        return version_info + client_info.strip()

    async def chat(self, prompt):
        """
        Asynchronously sends the prompt to each client for a response.
        Concatenates the library name with the response if
        multiple clients are present.
        Returns just the response if a single client is available.
        """
        _chats = []
        for client in self.clients:
            data = await client.chat(prompt)
            if data:
                if len(self.clients) > 1:
                    _chats.append(f"{client.llm_library}\n{data}")
                else:
                    return data
        if _chats:
            return "\n".join(_chats)

    async def export_chat_history(self):
        """
        Asynchronous function to export chat history for each
        client in the list of clients.
        Catches any exceptions and logs them using the logger.
        """
        try:
            for client in self.clients:
                await client.export_chat_history()
        except Exception as e:
            logger.error(e)

    async def clear_chat_history(self):
        """
        Asynchronously clears the chat history for each
        client in the list of clients.
        """
        try:
            for client in self.clients:
                await client.clear_chat_history()
        except Exception as e:
            logger.error(e)
