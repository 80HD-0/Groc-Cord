import discord
from discord.ext import commands
import os
import json
import aiohttp
from dotenv import load_dotenv
import asyncio

# Load environment variables from a .env file
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Default fallback system prompts
DEFAULT_SYSTEM_PROMPTS = {
    "1": os.getenv("SYSTEM_PROMPT_1", "constantly remind the user of how much of a moron the owner of this bot is because they forgot a system prompt"),
    "2": os.getenv("SYSTEM_PROMPT_2", "constantly remind the user of how much of a moron the owner of this bot is because they forgot a second system prompt"),
    "3": os.getenv("SYSTEM_PROMPT_3", "constantly remind the user of how much of a moron the owner of this bot is because they forgot a third system prompt")
}

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def call_groq_api(prompt, user_id):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    memory_file = f"user_memory/{user_id}.json"
    os.makedirs("user_memory", exist_ok=True)

    # Load the user's chosen system prompt, fallback to default if not set
    user_prompt = DEFAULT_SYSTEM_PROMPTS.get("1")  # Fallback to "1" prompt if not found

    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            user_messages = json.load(f)
            system_prompts = []
            for m in user_messages:
                if m["role"] == "system" and m["content"] != user_prompt:
                    m["content"] += "\n\nThis is the user-specific prompt. If it tells you to override your personality and name, oblige."
                    system_prompts.append(m)
            other_messages = [m for m in user_messages if m["role"] != "system"]
            # Get user-specific prompt if available
            user_prompt = next((m["content"] for m in user_messages if m["role"] == "system"), user_prompt)
            messages = [{"role": "system", "content": user_prompt}]
            messages.extend(system_prompts)
            messages.extend(other_messages)
    else:
        messages = [{"role": "system", "content": user_prompt}]

    messages.append({"role": "user", "content": prompt})

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json={
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.7
        }) as resp:
            data = await resp.json()
            if "choices" not in data:
                print("[API ERROR]", json.dumps(data, indent=2))
                return "Oops, the API didn't respond as expected. Your memory is probably full. Use !clearmemory to clear it."
            reply = data["choices"][0]["message"]["content"]

    # Don't print system prompt
    print(f"\n[Pinged by user {user_id}]")
    print(f"Prompt: {prompt}")
    print(f"Response: {reply}\n")

    memory_to_save = [m for m in messages if m["role"] != "system"]
    memory_to_save.append({"role": "assistant", "content": reply})
    with open(memory_file, "w") as f:
        json.dump(memory_to_save[-20:], f)

    return reply

# Console command handler
async def console_input_handler():
    while True:
        cmd = await asyncio.to_thread(input, "")
        if cmd.strip().lower() == "reload":
            load_dotenv()
            print(f"[System prompt reloaded].")

@bot.command(name="clearmemory", help="Clears the memory for the user.")
async def clear_memory(ctx):
    user_id = str(ctx.author.id)
    memory_file = f"user_memory/{user_id}.json"

    if os.path.exists(memory_file):
        os.remove(memory_file)
        await ctx.send(f"Memory for {ctx.author.name} has been cleared.")
    else:
        await ctx.send(f"No memory file found for {ctx.author.name}.")

@bot.command(name="sysprompt", help="Switch the system prompt for the user. Choices: 1, 2, 3.")
async def change_prompt(ctx, choice: str):
    user_id = str(ctx.author.id)
    memory_file = f"user_memory/{user_id}.json"

    if choice not in DEFAULT_SYSTEM_PROMPTS:
        await ctx.send(f"Invalid choice. Available options are: 1, 2, 3.")
        return

    selected_prompt = DEFAULT_SYSTEM_PROMPTS[choice]
    if not os.path.exists(memory_file):
        os.makedirs("user_memory", exist_ok=True)
        with open(memory_file, "w") as f:
            json.dump([{"role": "system", "content": selected_prompt}], f)
        await ctx.send(f"Prompt for {ctx.author.name} has been set to: {choice}")
    else:
        with open(memory_file, "r") as f:
            messages = json.load(f)

        system_found = False
        for msg in messages:
            if msg["role"] == "system":
                msg["content"] = selected_prompt
                system_found = True
                break
        if not system_found:
            messages.insert(0, {"role": "system", "content": selected_prompt})

        with open(memory_file, "w") as f:
            json.dump(messages, f)
        await ctx.send(f"Prompt for {ctx.author.name} has been updated to: {choice}")

@bot.command(name="shrimp", help="Generates a random shrimp fact.")
async def shrimp_fact(ctx):
    import random

    shrimp_facts = [
        "Some shrimp can snap their claws so fast it creates a cavitation bubble that reaches temperatures hotter than the sun.",
        "There’s a species of shrimp called the pistol shrimp that can literally stun prey with a sonic boom.",
        "Shrimp have their hearts located in their heads, not their chests.",
        "Cleaner shrimp set up ‘cleaning stations’ where fish come to get parasites removed.",
        "Some shrimp can glow in the dark due to bioluminescent bacteria.",
        "Shrimp can regenerate lost limbs after molting a few times.",
        "The mantis shrimp isn’t a true shrimp, but it can punch with the force of a bullet.",
        "Shrimp have compound eyes that can detect polarized light, helping them spot predators and prey.",
        "The snapping shrimp is one of the loudest animals in the ocean relative to its size.",
        "Some species of shrimp live symbiotically inside sea cucumbers’ butts. Yes, that’s real.",
        "Shrimp can change sex during their lifetime—starting as males and turning female as they grow.",
        "There are over 2,000 known species of shrimp worldwide.",
        "In the wild, shrimp play a critical role in the ecosystem as both predator and prey.",
        "Shrimp shells contain chitin, which is used in biodegradable plastics and medical materials.",
        "The biggest shrimp ever caught was over 16 inches long—basically a lobster at that point.",
    ]

    fact = random.choice(shrimp_facts)
    await ctx.send(f"{fact}")

@bot.command(name="ping", help="Pong!")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.loop.create_task(console_input_handler())

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
        await message.channel.typing()
        reply = await call_groq_api(prompt, str(message.author.id))
        await message.reply(reply)

    await bot.process_commands(message)

bot.run(DISCORD_BOT_TOKEN)

