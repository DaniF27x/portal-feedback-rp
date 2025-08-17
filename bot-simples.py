import discord from discord.ext import commands from discord import app\_commands import os

TOKEN = os.getenv('DISCORD\_TOKEN')

if not TOKEN: print("Token nao encontrado") exit(1)

bot = commands.Bot(command\_prefix='!', intents=discord.Intents.all())

@bot.event async def on\_ready(): print(f'Bot online: {bot.user}') try: synced = await bot.tree.sync() print(f'{len(synced)} comandos sincronizados') except Exception as e: print(f'Erro: {e}')

@bot.tree.command(name="feedback", description="Enviar feedback") async def feedback(interaction: discord.Interaction, mensagem: str): embed = discord.Embed( title="Feedback Recebido", description=f"Mensagem: {mensagem}", color=0x00ff00 ) await interaction.response.send\_message(embed=embed, ephemeral=True) print(f"Feedback de {interaction.user}: {mensagem}")

# Servidor web para Render

import threading from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler): def do\_GET(self): self.send\_response(200) self.end\_headers() self.wfile.write(b'Bot Online')

def run\_server(): port = int(os.environ.get('PORT', 8000)) server = HTTPServer(('0.0.0.0', port), Handler) server.serve\_forever()

if **name** == "**main**": threading.Thread(target=run\_server, daemon=True).start() print("Servidor iniciado") bot.run(TOKEN)
