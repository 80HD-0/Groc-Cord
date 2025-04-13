import discord
from discord.ext import commands
import os
import json
import aiohttp
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")  # Default model if not provided

# Base system prompt (not user-editable)
# This is the version published to github, and it does not come with a template prompt. Please add a prompt, your users probably do not like being called morons.
BASE_SYSTEM_PROMPT = "in every single message you send, tell the user how much of a moron they are because they forgot to write the system prompt..."

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True  # To receive message content events
bot = commands.Bot(command_prefix="!", intents=intents)

async def call_groq_api(prompt, user_id):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    memory_file = f"user_memory/{user_id}.json"
    os.makedirs("user_memory", exist_ok=True)

    # Start with base system prompt
    messages = [{"role": "system", "content": BASE_SYSTEM_PROMPT}]

    # Add user's prompt and memory
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            user_messages = json.load(f)
            # Insert any user-defined system prompt after the base one
            system_prompts = [m for m in user_messages if m["role"] == "system"]
            other_messages = [m for m in user_messages if m["role"] != "system"]

            messages.extend(system_prompts)
            messages.extend(other_messages)

    # Add current user message
    messages.append({"role": "user", "content": prompt})

    # Send request to API
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json={
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.7
        }) as resp:
            data = await resp.json()
            if "choices" not in data:
                print("[API ERROR]", json.dumps(data, indent=2))
                return "Oops, the API didn't respond as expected."

            reply = data["choices"][0]["message"]["content"]

    # Save memory without base prompt
    memory_to_save = [m for m in messages if m["role"] != "system"]
    memory_to_save.append({"role": "assistant", "content": reply})
    with open(memory_file, "w") as f:
        json.dump(memory_to_save[-20:], f)

    return reply

# Command to clear memory
@bot.command(name="clearmemory", help="Clears the memory for the user.")
async def clear_memory(ctx):
    user_id = str(ctx.author.id)
    memory_file = f"user_memory/{user_id}.json"
    
    if os.path.exists(memory_file):
        os.remove(memory_file)
        await ctx.send(f"Memory for {ctx.author.name} has been cleared.")
    else:
        await ctx.send(f"No memory file found for {ctx.author.name}.")

# Command to change the prompt
@bot.command(name="prompt", help="Change the prompt used by the bot for the user.")
async def change_prompt(ctx, *, new_prompt: str):
    user_id = str(ctx.author.id)
    memory_file = f"user_memory/{user_id}.json"

    if not os.path.exists(memory_file):
        os.makedirs("user_memory", exist_ok=True)
        with open(memory_file, "w") as f:
            json.dump([{"role": "system", "content": new_prompt}], f)
        await ctx.send(f"Prompt for {ctx.author.name} has been set to: {new_prompt}")
    else:
        with open(memory_file, "r") as f:
            messages = json.load(f)

        # Replace existing system message or insert one
        system_found = False
        for msg in messages:
            if msg["role"] == "system":
                msg["content"] = new_prompt
                system_found = True
                break
        if not system_found:
            messages.insert(0, {"role": "system", "content": new_prompt})

        with open(memory_file, "w") as f:
            json.dump(messages, f)
        await ctx.send(f"Prompt for {ctx.author.name} has been updated.")

# Ping command for fun
@bot.command(name="ping", help="Pong!")
async def ping(ctx):
    await ctx.send("Pong!")

# Event triggered when bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Event triggered when a message is received
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
        await message.channel.typing()
        reply = await call_groq_api(prompt, str(message.author.id))
        await message.reply(reply)

    await bot.process_commands(message)  # Allow commands to be processed

# Run the bot with the provided token
bot.run(DISCORD_BOT_TOKEN)

