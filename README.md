# Groc-Cord
A discord bot programmed mainly by chatgpt that passes groq api through to discord.
## Setup
The bot depends on discord.py, python-dotenv, and aiohttp. You will also need a discord bot token and groq api key to continue.
First, make a bot with discord, making sure to turn on all intents and activate the "bot" permission so that it's pingable.
Also get a groq api key.
Then, get all the dependancies using pip.

```python3 -m pip install discord.py python-dotenv aiohttp```

The bot uses envionment variables for the 3 system prompts, token, and api key. Make a .env file in the same folder as the bot. The syntax it wants in the file is:

<pre>DISCORD_BOT_TOKEN = "(your token)"
GROQ_API_KEY = "(your api key)"
SYSTEM_PROMPT_1 = "(your system prompt)"
SYSTEM_PROMPT_2 = "(your system prompt)"
SYSTEM_PROMPT_3 = "(your system prompt)"</pre>

if you have multiple system prompts, you will want to set up names for them, like "pirate," "Gnarp," etc. They are in the code (shiver me timbers) at line 18. it looks like this:

    "1": os.getenv("SYSTEM_PROMPT_1", (the fallback prompt that happens when you forget to make one))

where that highlighted text is what you change to change the prompt name.

then you should be good to go to run the bot:

```python3 bot.py```

if it fails, it's likely a bad api key or token, and if it isn't, it's likely a dependancy issue. Trust me, I would know. If you don't think it's one of those things, make an issue please.

## Usage
This bot stores user chat history and user-defined prompts in individual json files, made by the bot, in a folder made by the bot.
It replies to users when it is pinged.
There is only 1 console command so far:

-reload, which reloads the prompt


The bot just uses 4 commands:

-!ping, which just replies with pong

-!clearmemory, which clears the bot's memory of that user

-!prompt (prompt), which adds a user-defined prompt that is appended to the system prompt

-!sysprompt (prompt name), which changes the system prompt for that user between the 3.




<br /><br /><br />
I do not take ownership of this code, however I did tailor this code to my wants and will use chatgpt or my own skill to improve it in the future.
