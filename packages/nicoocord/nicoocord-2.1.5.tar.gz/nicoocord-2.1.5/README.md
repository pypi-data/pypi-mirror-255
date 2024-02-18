# nicoocord

An easy-to-use extension for the [Pycord](https://github.com/Pycord-Development/pycord) library with some utility functions.

### Note: Some examples are outdated

## Features

- Json parser
- [Wrapper](https://github.com/littxle/aiosqlite-wrapper) for the [aiosqlite](https://pypi.org/project/aiosqlite/) library
- Pre-made Embeds
- Pre-made on_ready event (can be disabled)
- Custom logger (can be disabled and log to file)

## Installing

Python 3.8 or higher is required.

You can install the latest release from [PyPI](https://pypi.org/project/nicoocord/) (Coming soon).

```sh
pip install nicoocord
```

You can also install the latest Dev version. Note the Dev version maybe have bugs and can be unstable
and requires [git](https://git-scm.com/downloads) to be installed.

```sh
pip install git+https://github.com/littxle/nicoocord.git
```

## Useful Links

- [Pycord Docs](https://docs.pycord.dev/)
- [Changelog](https://github.com/littxle/nicoocord/blob/main/Changelog.md)

## Example

```py
import nicoocord as nc
import discord


bot = nc.Bot(
    token="token"
)

if __name__ == "__main__":
    bot.load_cogs("cogs")  # Load all cogs in the "cogs" folder
    bot.load_subdir("commands")  # Load all cogs in the "commands" folder and all subfolders

    bot.exec() # Start the bot
```

**Note:** It's recommended to load the token from a [`.env`](https://pypi.org/project/python-dotenv/) file, from a [`json file`](https://docs.python.org/3/library/json.html) or a normal [`python file`](https://docs.python.org/3/tutorial/modules.html)
instead of hardcoding it.

## Contributing

I am always happy to receive contributions. Here is how to do it:

1. Fork this repository
2. Make changes
3. Create a pull request

You can also [create an issue](https://github.com/littxle/nicoocord/issues/new) if you find any bugs.
