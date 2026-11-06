"""Optional read-only Discord status command. Requires discord.py."""
import os
import discord
from discord.ext import commands
import requests

def main():
    token = os.environ["DISCORD_TOKEN"]
    url = os.getenv("LAB_URL", "http://127.0.0.1:8000").rstrip("/")
    key = os.environ["LAB_API_KEY"]
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

    @bot.command(name="agents")
    async def agents(ctx):
        try:
            response = requests.get(url + "/agents", headers={"X-Lab-Key": key}, timeout=5)
            response.raise_for_status()
            data = response.json()
            text = "\n".join(
                f"{'🟢' if a['online'] else '⚪'} {a['label']} — {a['agent_id'][:8]}"
                for a in data
            ) or "No test agents registered."
            await ctx.send(text[:1900])
        except requests.RequestException:
            await ctx.send("Lab server unavailable.")

    bot.run(token)

if __name__ == "__main__":
    main()
