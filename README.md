# Groc-Cord
A discord bot programmed mainly by chatgpt that passes groq api through to discord.
## Setup
The bot depends on discord.py, python-dotenv, and aiohttp. You will also need a discord bot token and groq api key to continue.
First, make a bot with discord, making sure to turn on all intents and activate the "bot" permission so that it's pingable.
Also get a groq api key.
Then, get all the dependancies using pip.

```python3 -m pip install discord.py python-dotenv aiohttp```

The bot uses envionment variables for the system prompt, token, and api key. Make a .env file in the same folder as the bot. The syntax it wants in the file is:

<pre>DISCORD_BOT_TOKEN = "(your token)"
GROQ_API_KEY = "(your api key)"
SYSTEM-PROMPT = "(your system prompt)"</pre>

then you should be good to go to run the bot:

```python3 bot.py```

if it fails, it's likely a bad api key or token, and if it isn't, it's likely a dependancy issue. Trust me, I would know. If you don't think it's one of those things, make an issue please.

## Usage
This bot stores user chat history and user-defined prompts in individual json files, made by the bot, in a folder made by the bot.
It replies to users when it is pinged.
There is only 1 console command so far:

-reload, which reloads the prompt


The bot just uses 3 commands:

-!ping, which just replies with pong

-!clearmemory, which clears the bot's memory of that user

-!prompt, which adds a user-defined prompt that is appended to the system prompt




<br /><br /><br />
I do not take ownership of this code, however I did tailor this code to my wants and will use chatgpt or my own skill to improve it in the future.
