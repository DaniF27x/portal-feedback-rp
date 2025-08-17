import discord from discord.ext import commands from discord import app\_commands import sqlite3 from datetime import datetime

# 🔐 TOKEN SEGURO (variável ambiente)

import os TOKEN = os.getenv('DISCORD\_TOKEN')

if not TOKEN: print("❌ ERRO: Token não encontrado!") print("❌ Configure a variável DISCORD\_TOKEN no Render!") exit(1)

# IDs DOS CARGOS

CARGOS\_STAFF = \[ 1134571064424538112, # Owner 1134571258020343838, # Fundador 1134571297887485963, # Admin 1134571333199466547, # Moderador 1134571359921532939, # Helper 1134571382612811816 # Sub-Helper ]

# 🎯 CONFIGURAÇÃO DO BOT

intents = discord.Intents.default() intents.message\_content = True intents.guilds = True intents.members = True

bot = commands.Bot(command\_prefix='!', intents=intents)

# 📊 BANCO DE DADOS

def init\_db(): conn = sqlite3.connect('feedback.db') cursor = conn.cursor()

```
# Tabela tickets com novo campo status
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        feedback TEXT NOT NULL,
        status TEXT DEFAULT 'aberto',
        data_criacao TEXT NOT NULL,
        data_resolucao TEXT,
        resolvido_por TEXT,
        canal_id TEXT
    )
''')

conn.commit()
conn.close()
print("✅ Banco de dados inicializado!")
```

# 🚀 EVENTO: Bot Online

@bot.event async def on\_ready(): print("✅ Portal Feedback Ilusion RP está online!") print("🔧 Sistema pronto com logs detalhados!") print(f"📊 Conectado como: {bot.user}") print(f"🆔 ID do Bot: {bot.user.id}")

```
init_db()

try:
    synced = await bot.tree.sync()
    print(f"🔄 {len(synced)} comando(s) sincronizado(s)!")
except Exception as e:
    print(f"❌ Erro ao sincronizar comandos: {e}")
```

# 🎫 COMANDO: /feedback

@bot.tree.command(name="feedback", description="📝 Enviar feedback/sugestão para a staff") async def feedback(interaction: discord.Interaction, mensagem: str): """Sistema completo de feedback com ticket"""

```
print(f"📝 Novo feedback de {interaction.user} ({interaction.user.id})")
print(f"💬 Mensagem: {mensagem}")

try:
    # 🏢 Buscar categoria "TICKETS"
    categoria = None
    for cat in interaction.guild.categories:
        if "ticket" in cat.name.lower():
            categoria = cat
            break
    
    if not categoria:
        print("❌ Categoria TICKETS não encontrada - criando nova")
        categoria = await interaction.guild.create_category("🎫 TICKETS")
    
    # 🎫 Criar canal do ticket
    nome_canal = f"ticket-{interaction.user.name.lower()}"
    
    # 🔐 Permissões do canal
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(
            read_messages=True, 
            send_messages=True,
            attach_files=True,
            embed_links=True
        )
    }
    
    # 👥 Staff pode ver
    for role in interaction.guild.roles:
        if role.id in CARGOS_STAFF:
            overwrites[role] = discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                manage_messages=True
            )
    
    canal_ticket = await interaction.guild.create_text_channel(
        nome_canal,
        category=categoria,
        overwrites=overwrites
    )
    
    # 💾 Salvar no banco
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tickets (user_id, username, feedback, data_criacao, canal_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        str(interaction.user.id),
        interaction.user.name,
        mensagem,
        datetime.now().strftime("%d/%m/%Y %H:%M"),
        str(canal_ticket.id)
    ))
    
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # 📋 Embed do ticket
    embed = discord.Embed(
        title="🎫 Novo Ticket de Feedback",
        description=f"**Usuário:** {interaction.user.mention}\n**ID:** {ticket_id}\n**Status:** 🟢 Aberto",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.add_field(name="📝 Feedback", value=mensagem, inline=False)
    embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.set_footer(text=f"Ticket #{ticket_id}")
    
    # 🔘 Botões de ação
    view = discord.ui.View(timeout=None)
    
    resolver_btn = discord.ui.Button(
        label="✅ Resolver",
        style=discord.ButtonStyle.success,
        custom_id=f"resolver_{ticket_id}"
    )
    
    fechar_btn = discord.ui.Button(
        label="🔒 Fechar Ticket",
        style=discord.ButtonStyle.danger,
        custom_id=f"fechar_{ticket_id}"
    )
    
    view.add_item(resolver_btn)
    view.add_item(fechar_btn)
    
    # 📤 Enviar no canal
    mensagem_ticket = await canal_ticket.send(
        f"👋 Olá {interaction.user.mention}! Seu ticket foi criado.\n"
        f"📋 **ID do Ticket:** {ticket_id}\n"
        f"⏰ Um membro da staff responderá em breve!\n\n"
        f"**🔐 Apenas você e a staff podem ver este canal.**",
        embed=embed,
        view=view
    )
    
    await mensagem_ticket.pin()
    
    # ✅ Resposta para o usuário
    embed_resposta = discord.Embed(
        title="✅ Ticket Criado com Sucesso!",
        description=f"🎫 Seu ticket foi criado: {canal_ticket.mention}\n"
                   f"📋 **ID:** {ticket_id}\n"
                   f"⏰ A staff responderá em breve!",
        color=0x00ff00
    )
    
    await interaction.response.send_message(embed=embed_resposta, ephemeral=True)
    print(f"✅ Ticket #{ticket_id} criado para {interaction.user}")
    
except Exception as e:
    print(f"❌ Erro ao criar ticket: {e}")
    
    embed_erro = discord.Embed(
        title="❌ Erro ao Criar Ticket",
        description="Ocorreu um erro ao criar seu ticket. Tente novamente.",
        color=0xff0000
    )
    
    try:
        await interaction.response.send_message(embed=embed_erro, ephemeral=True)
    except:
        await interaction.followup.send(embed=embed_erro, ephemeral=True)
```

# 🎛️ EVENTOS DOS BOTÕES

@bot.event async def on\_interaction(interaction): if interaction.type != discord.InteractionType.component: return

```
custom_id = interaction.data.get('custom_id', '')

# 🔍 Verificar se é staff
user_roles = [role.id for role in interaction.user.roles]
is_staff = any(role_id in CARGOS_STAFF for role_id in user_roles)

if not is_staff:
    embed = discord.Embed(
        title="❌ Acesso Negado",
        description="Apenas membros da staff podem usar estes botões!",
        color=0xff0000
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    return

# ✅ Resolver Ticket
if custom_id.startswith('resolver_'):
    ticket_id = custom_id.split('_')[1]
    
    try:
        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        
        # Atualizar status no banco
        cursor.execute('''
            UPDATE tickets 
            SET status = 'resolvido', data_resolucao = ?, resolvido_por = ?
            WHERE id = ?
        ''', (
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            interaction.user.name,
            ticket_id
        ))
        
        conn.commit()
        conn.close()
        
        # ✅ Embed de sucesso
        embed = discord.Embed(
            title="✅ Ticket Resolvido!",
            description=f"**Ticket #{ticket_id}** foi marcado como resolvido.\n"
                       f"**Resolvido por:** {interaction.user.mention}\n"
                       f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                       f"🔒 Use o botão **Fechar Ticket** para finalizar.",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        await interaction.response.send_message(embed=embed)
        print(f"✅ Ticket #{ticket_id} resolvido por {interaction.user}")
        
    except Exception as e:
        print(f"❌ Erro ao resolver ticket: {e}")
        
        embed = discord.Embed(
            title="❌ Erro",
            description="Erro ao resolver o ticket!",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# 🔒 Fechar Ticket
elif custom_id.startswith('fechar_'):
    ticket_id = custom_id.split('_')[1]
    
    try:
        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        
        # Buscar dados do ticket
        cursor.execute('SELECT user_id, username, feedback, status FROM tickets WHERE id = ?', (ticket_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            user_id, username, feedback, status = resultado
            
            # 📊 Embed final do ticket
            embed_final = discord.Embed(
                title="🔒 Ticket Finalizado",
                description=f"**Ticket #{ticket_id}** foi fechado.\n"
                           f"**Status:** {'✅ Resolvido' if status == 'resolvido' else '⏸️ Fechado sem resolução'}\n"
                           f"**Usuário:** {username}\n"
                           f"**Fechado por:** {interaction.user.mention}\n"
                           f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                color=0x808080,
                timestamp=datetime.now()
            )
            embed_final.add_field(name="📝 Feedback Original", value=feedback[:1000], inline=False)
            
            # Atualizar status no banco
            cursor.execute('''
                UPDATE tickets 
                SET status = 'fechado', data_resolucao = ?, resolvido_por = ?
                WHERE id = ?
            ''', (
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                interaction.user.name,
                ticket_id
            ))
            
            conn.commit()
            conn.close()
            
            await interaction.response.send_message(embed=embed_final)
            
            # 🕐 Aguardar 10 segundos e deletar canal
            await discord.utils.sleep_until(datetime.now().timestamp() + 10)
            
            try:
                await interaction.channel.delete()
                print(f"🔒 Canal do ticket #{ticket_id} deletado")
            except:
                print(f"❌ Erro ao deletar canal do ticket #{ticket_id}")
        
        else:
            conn.close()
            embed = discord.Embed(
                title="❌ Erro",
                description="Ticket não encontrado no banco de dados!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
    except Exception as e:
        print(f"❌ Erro ao fechar ticket: {e}")
        
        embed = discord.Embed(
            title="❌ Erro",
            description="Erro ao fechar o ticket!",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
```

# 📊 COMANDO: Ver Tickets (só staff)

@bot.tree.command(name="tickets", description="📊 Ver estatísticas dos tickets (apenas staff)") async def tickets\_stats(interaction: discord.Interaction): # 🔍 Verificar se é staff user\_roles = \[role.id for role in interaction.user.roles] is\_staff = any(role\_id in CARGOS\_STAFF for role\_id in user\_roles)

```
if not is_staff:
    embed = discord.Embed(
        title="❌ Acesso Negado",
        description="Este comando é apenas para membros da staff!",
        color=0xff0000
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    return

try:
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    
    # Estatísticas
    cursor.execute('SELECT COUNT(*) FROM tickets')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "aberto"')
    abertos = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "resolvido"')
    resolvidos = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "fechado"')
    fechados = cursor.fetchone()[0]
    
    # Últimos 5 tickets
    cursor.execute('''
        SELECT id, username, status, data_criacao 
        FROM tickets 
        ORDER BY id DESC 
        LIMIT 5
    ''')
    ultimos = cursor.fetchall()
    
    conn.close()
    
    embed = discord.Embed(
        title="📊 Estatísticas dos Tickets",
        description=f"📋 **Total de Tickets:** {total}\n"
                   f"🟢 **Abertos:** {abertos}\n"
                   f"✅ **Resolvidos:** {resolvidos}\n"
                   f"🔒 **Fechados:** {fechados}",
        color=0x00bfff,
        timestamp=datetime.now()
    )
    
    if ultimos:
        tickets_texto = ""
        for ticket in ultimos:
            status_emoji = {"aberto": "🟢", "resolvido": "✅", "fechado": "🔒"}
            tickets_texto += f"**#{ticket[0]}** - {ticket[1]} {status_emoji.get(ticket[2], '❓')} ({ticket[3]})\n"
        
        embed.add_field(
            name="📋 Últimos 5 Tickets",
            value=tickets_texto,
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
except Exception as e:
    print(f"❌ Erro ao buscar tickets: {e}")
    
    embed = discord.Embed(
        title="❌ Erro",
        description="Erro ao buscar estatísticas dos tickets!",
        color=0xff0000
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
```

# Rodar bot

if **name** == "**main**": print("🤖 Iniciando Portal Feedback Bot - VERSÃO CORRIGIDA...") print("🔧 Sistema com logs detalhados e controle de tickets!") print(f"📋 {len(CARGOS\_STAFF)} cargos configurados") print("🎯 Funcionalidades: Criar → Resolver → Fechar tickets!")

```
# Servidor web simples para Render
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot Discord Online!')

def run_server():
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# Iniciar servidor em thread separada
threading.Thread(target=run_server, daemon=True).start()
print(f"🌐 Servidor web iniciado na porta {os.environ.get('PORT', 8000)}")

bot.run(TOKEN)

