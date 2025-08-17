import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Bot online')

bot.run(os.getenv('DISCORD_TOKEN'))
