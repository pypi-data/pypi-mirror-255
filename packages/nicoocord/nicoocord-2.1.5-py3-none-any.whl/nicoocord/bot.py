import os
import time
import json
import importlib.util
from typing import Union, Any

import discord

from .utils.log import Log
from .errors import NoSetupFound

_version = "2.1.5"


class Bot(discord.Bot):
    """
    The main bot class

    Args
    ----
    intents: discord.Intents (optional) The intents to use
    *args: Any (optional) Any arguments to pass to the `discord.Client` class
    **kwargs: Any (optional) Any keyword arguments to pass to the `discord.Client` class

    Public Methods
    --------------
    `run(token: str = None)` -> None
        Starts the bot

    `load_cogs(dir: str, subdir: bool = None)` -> None
        Loads cogs from a directory

    `execute_query(query: str, args: tuple = None, fetch: FetchTypes = FetchTypes.NONE)` -> Any
        Executes a query

    `execute(database: str, fetch: FetchTypes = FetchTypes.NONE)` -> Any
        A decorator that executes a query

    `get(key: str, default: Any = None)` -> Any
        Gets a value from the config file

    Public Variables
    ----------------
    `uptime`: float
        The uptime of the bot in seconds

    `start_time`: float
        The time the bot started in seconds

    Private Methods
    ---------------
    `_ignore_pycache(dir: str)` -> bool
        Checks if a directory is a pycache directory

    `_register_cog(dir: str, subdir: bool = None)` -> None
        Register a directory of cogs

    `_load_config()` -> None
        Loads the config file

    `_sync_cmds()` -> None
        Syncs the slash commands

    `_connected()` -> None
        Called when the bot connects to the gateway

    `_ready()` -> None
        Called when the bot is ready
    """

    def __init__(self,
                 intents: discord.Intents = discord.Intents.default(),
                 *args,
                 **kwargs,
                 ) -> None:
        self._cfg = self._load_config()

        self.token: str = self._cfg["token"]
        self.db: str = self._cfg["database"]
        self.log_file: bool = self._cfg["log_file"]
        self.__sync_commands: bool = self._cfg["sync_commands"]
        self.ready_event: bool = self._cfg["ready_print"]
        self._debug: bool = self._cfg["debug"]

        self._start_time: Union[float, None] = None

        self.logger = Log(log_file=self.log_file, debug=self._debug)

        super().__init__(intents=intents, *args, **kwargs)

        with open(self.db, "w"):
            pass

        if self.__sync_commands:
            self.add_listener(self._sync_cmds, "on_connect")

        if self.ready_event:
            self.add_listener(self._connected, "on_connect")
            self.add_listener(self._ready_func, "on_ready")

    async def _sync_cmds(self) -> None:
        """Not to be used by the user"""
        if self._debug:
            self.logger.logger("Syncing slash commands", "nicoocord", "debug")
        await self.sync_commands()

    async def _connected(self) -> None:
        """Not to be used by the user"""
        self.logger.logger(
            f"Connected to Discord Gateway ({round(self.latency * 1000)}ms)", "websocket", "info")

    async def _ready_func(self) -> None:
        """Not to be used by the user"""
        self.logger.logger(f"Bot is ready", "nicoocord", "info")
        self.logger.logger(f"Guild(s): {len(self.guilds)}", "nicoocord", "info")
        self.logger.logger(
            f"nicoocord version: {_version} | Pycord version: {discord.__version__}", "nicoocord", "debug")

    def run(self, token: str = None) -> None:
        """Starts the bot

        Args
        ----
        token: str (optional) If the token is not provided in the `config` file, you can provide it here"""

        if token:
            self.token = token
        self._start_time = time.time()
        self.logger.logger("Starting bot...", "nicoocord", "info")
        super().run(self.token, reconnect=True)

    def _ignore_pycache(self, dir: str) -> bool:
        """Not ment to be used by the user. Checks if a directory is a pycache directory"""
        return "pycache" in dir

    def _register_cog(self, dir: str, subdir: bool = None) -> None:
        """Not to be used by the user. Register a directory of cogs"""
        if not subdir:
            for file in os.scandir(dir):
                if file.is_file():
                    if file.name.endswith(".py"):
                        name = file.name.split(os.path.sep)[0]

                        spec = importlib.util.spec_from_file_location(
                            name, file.path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        try:
                            module.setup(self)
                        except AttributeError:
                            raise NoSetupFound(module)
        else:
            for cog_dir in os.scandir(dir):
                if cog_dir.is_dir():
                    for subfile in os.scandir(cog_dir.path):
                        if subfile.is_file():
                            if subfile.name.endswith(".py"):
                                name = subfile.name.split(os.path.sep)[0]

                                spec = importlib.util.spec_from_file_location(
                                    name, subfile.path)
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)

                                try:
                                    module.setup(self)
                                except AttributeError:
                                    raise NoSetupFound(module)

    def load_cogs(self, *dirs: str, subdirectory: bool = False) -> None:
        """Loads cogs from a directory

        Args
        ----
        *dirs: str (required) The directories to load cogs from
        subdirectory: bool (optional) Whether to load cogs from subdirectories"""

        for dir in dirs:
            self._register_cog(dir, subdir=subdirectory)

    def _load_config(self) -> dict:
        """Not to be used by the user. Loads the config file"""
        if not os.path.exists("nicoocord.json"):
            with open("nicoocord.json", "w") as f:
                json.dump({
                    "token": "",
                    "debug": True,
                    "log_file": False,
                    "sync_commands": True,
                    "ready_print": True,
                    "database": "main.db",
                }, f, indent=4, ensure_ascii=False)

            self.logger.logger("Created config file", "nicoocord", "info")
            exit(0)

        with open("nicoocord.json", "r") as f:
            config = json.load(f)

        try:
            if type(config["token"]) != str:
                raise ValueError("Token must be a string")

            if type(config["database"]) != str:
                raise ValueError("Database must be a string")

            if type(config["debug"]) != bool:
                raise ValueError("Debug must be a boolean")

            if type(config["log_file"]) != bool:
                raise ValueError("Log file must be a boolean")

            if type(config["sync_commands"]) != bool:
                raise ValueError("Sync commands must be a boolean")

            if type(config["ready_print"]) != bool:
                raise ValueError("Ready print must be a boolean")
        except KeyError as e:
            raise KeyError(f"Key {e} is missing from the config file")

        return config

    def get(self, key: str, default: Any = None) -> Union[Any, None]:
        """Get a key from the `nicoocord.json`

        Args
        ----
        key: str (required) The key to get from the config file

        Returns
        -------
        Returns the value of the key or None if the key does not exist
        """
        try:
            return self._cfg[key]
        except KeyError:
            return default

    @property
    def start_time(self) -> float:
        """Returns the time the bot started"""
        if self._start_time is None:
            return self.logger._force_logger("Bot is not running, start_time will be None", "nicoocord", "error")

        return self._start_time

    @property
    def uptime(self) -> float:
        """Returns how long the bot is online"""
        if self._start_time is None:
            return self.logger._force_logger("Bot is not running, uptime will be None", "nicoocord", "error")

        return time.time() - self._start_time
