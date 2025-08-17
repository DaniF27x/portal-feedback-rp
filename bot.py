import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime

# 🔐 TOKEN SEGURO (variável ambiente)
import os
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("❌ ERRO: Token não encontrado!")
    print("❌ Configure a variável DISCORD_TOKEN no Render!")
    exit(1)

# IDs DOS CARGOS
CARGOS_STAFF = {
    'CEO': 1365557796879466566,
    'Presidente': 1365769992246788106,
    'Master': 1366312318392078356,
    'Alta Cúpula': 1365518838472376422,
    'ADM staff': 1365519563948687472,
    'Resp Comunidade': 1365518494958882866,
    'Mentoria': 1367280730572460113,
    'Equipe Legal': 1365518739826671707,
    'Social Midia': 1365519199555817634,
    'ADM': 1374047506257678356
}

CARGO_CIDADAO = 1365520018124570667

# 🎯 CANAL ESPECÍFICO PARA TICKETS
CANAL_FEEDBACK_ID = 1365522389827326013  # SEU CANAL DE FEEDBACK

# CARGOS AUTOMÁTICOS POR CATEGORIA
CATEGORIAS = {
    'melhorias_cidade': {
        'nome': '🏗️ Melhorias na Cidade',
        'emoji': '🏗️',
        'descricao': 'Ideias para locais, construções, mapas',
        'cargos': ['CEO', 'Presidente', 'Master', 'Alta Cúpula', 'ADM staff', 'ADM']
    },
    'economia': {
        'nome': '💰 Economia',
        'emoji': '💰', 
        'descricao': 'Preços, salários, negócios',
        'cargos': ['CEO', 'Presidente', 'Master', 'Alta Cúpula', 'ADM staff', 'ADM']
    },
    'eventos_cultura': {
        'nome': '🎭 Eventos e Cultura',
        'emoji': '🎭',
        'descricao': 'Festas, shows, atividades',
        'cargos': ['CEO', 'Presidente', 'Resp Comunidade', 'Social Midia', 'Master', 'ADM staff']
    },
    'regras_leis': {
        'nome': '⚖️ Regras e Leis',
        'emoji': '⚖️',
        'descricao': 'Leis da cidade, punições',
        'cargos': ['CEO', 'Presidente', 'Equipe Legal', 'Master', 'Alta Cúpula', 'ADM staff', 'ADM']
    },
    'sugestoes_livres': {
        'nome': '💡 Sugestões Livres',
        'emoji': '💡',
        'descricao': 'Qualquer ideia criativa',
        'cargos': ['CEO', 'Presidente', 'Master', 'Alta Cúpula', 'ADM staff', 'Resp Comunidade', 'Mentoria', 'Equipe Legal', 'Social Midia', 'ADM']
    }
}

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

def init_db():
    conn = sqlite3.connect('feedbacks.db')
    c = conn.cursor()
    
    # Cria tabela base
    c.execute('''CREATE TABLE IF NOT EXISTS feedbacks
        (id INTEGER PRIMARY KEY, 
         usuario_id INTEGER, 
         usuario_nome TEXT,
         categoria TEXT, 
         titulo TEXT, 
         descricao TEXT,
         data_criacao TEXT)''')
    
    # ✅ ADICIONA COLUNAS SE NÃO EXISTIR (para bancos antigos)
    try:
        c.execute('ALTER TABLE feedbacks ADD COLUMN cargos_responsaveis TEXT')
        print("✅ Coluna 'cargos_responsaveis' adicionada!")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    try:
        c.execute('ALTER TABLE feedbacks ADD COLUMN thread_id INTEGER')
        print("✅ Coluna 'thread_id' adicionada!")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    try:
        c.execute('ALTER TABLE feedbacks ADD COLUMN status TEXT DEFAULT "novo"')
        print("✅ Coluna 'status' adicionada!")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    conn.commit()
    conn.close()
    print("🔧 Banco de dados atualizado!")

# ==================== PAINEL PRINCIPAL ====================

class PainelPrincipal(discord.ui.View):
    """Painel com categorias - vai direto pro modal"""
    
    def __init__(self, user):
        super().__init__(timeout=300)
        self.user = user
    
    @discord.ui.button(label='🏗️ Melhorias na Cidade', style=discord.ButtonStyle.primary, row=0)
    async def melhorias(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Este painel não é seu!", ephemeral=True)
            return
        await self.abrir_modal(interaction, 'melhorias_cidade')
    
    @discord.ui.button(label='💰 Economia', style=discord.ButtonStyle.primary, row=0)
    async def economia(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Este painel não é seu!", ephemeral=True)
            return
        await self.abrir_modal(interaction, 'economia')
    
    @discord.ui.button(label='🎭 Eventos e Cultura', style=discord.ButtonStyle.primary, row=1)
    async def eventos(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Este painel não é seu!", ephemeral=True)
            return
        await self.abrir_modal(interaction, 'eventos_cultura')
    
    @discord.ui.button(label='⚖️ Regras e Leis', style=discord.ButtonStyle.primary, row=1)
    async def regras(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Este painel não é seu!", ephemeral=True)
            return
        await self.abrir_modal(interaction, 'regras_leis')
    
    @discord.ui.button(label='💡 Sugestões Livres', style=discord.ButtonStyle.success, row=2)
    async def sugestoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Este painel não é seu!", ephemeral=True)
            return
        await self.abrir_modal(interaction, 'sugestoes_livres')
    
    @discord.ui.button(label='📋 Meus Feedbacks', style=discord.ButtonStyle.secondary, row=2)
    async def meus_feedbacks(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f"📋 [MEUS FEEDBACKS] Clicado por {interaction.user}")
        print(f"📋 [MEUS FEEDBACKS] User ID: {interaction.user.id}, Panel user: {self.user.id}")
        
        if interaction.user.id != self.user.id:
            print(f"❌ [MEUS FEEDBACKS] Usuário não autorizado!")
            await interaction.response.send_message("❌ Este painel não é seu!", ephemeral=True)
            return
        
        print(f"✅ [MEUS FEEDBACKS] Chamando função mostrar_meus_feedbacks...")
        try:
            await mostrar_meus_feedbacks(interaction)
            print(f"✅ [MEUS FEEDBACKS] Função executada com sucesso")
        except Exception as e:
            print(f"❌ [MEUS FEEDBACKS] Erro: {e}")
            import traceback
            traceback.print_exc()
    
    async def abrir_modal(self, interaction, categoria):
        """Abrir modal direto para escrever feedback"""
        categoria_info = CATEGORIAS[categoria]
        cargos_responsaveis = categoria_info['cargos']
        
        modal = ModalFeedback(self.user, categoria, cargos_responsaveis)
        await interaction.response.send_modal(modal)

# ==================== MODAL DE FEEDBACK ====================

class ModalFeedback(discord.ui.Modal):
    """Modal para escrever o feedback"""
    
    def __init__(self, user, categoria, cargos_responsaveis):
        super().__init__(title=f"✍️ {CATEGORIAS[categoria]['nome']}")
        self.user = user
        self.categoria = categoria
        self.cargos_responsaveis = cargos_responsaveis
        
        self.titulo = discord.ui.TextInput(
            label="📝 Título (resumo da sua ideia)",
            placeholder="Ex: Nova praça no centro da cidade",
            max_length=100,
            required=True
        )
        self.add_item(self.titulo)
        
        self.descricao = discord.ui.TextInput(
            label="📋 Descrição detalhada",
            placeholder="Descreva sua ideia com detalhes...",
            style=discord.TextStyle.long,
            max_length=1000,
            required=True
        )
        self.add_item(self.descricao)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"📝 Iniciando criação de feedback...")
            
            # Salvar no banco
            conn = sqlite3.connect('feedbacks.db')
            c = conn.cursor()
            c.execute('''INSERT INTO feedbacks 
                        (usuario_id, usuario_nome, categoria, titulo, descricao, cargos_responsaveis, data_criacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (self.user.id, str(self.user), self.categoria, 
                      self.titulo.value, self.descricao.value, 
                      ','.join(self.cargos_responsaveis), 
                      datetime.now().strftime('%d/%m/%Y %H:%M')))
            
            feedback_id = c.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Feedback #{feedback_id:03d} salvo no banco")
            
            # Resposta de sucesso
            categoria_info = CATEGORIAS[self.categoria]
            embed = discord.Embed(
                title="✅ Feedback Enviado com Sucesso!",
                color=0x00ff00
            )
            
            embed.add_field(name="🆔 ID", value=f"#{feedback_id:03d}", inline=True)
            embed.add_field(name="📋 Categoria", value=categoria_info['nome'], inline=True)
            embed.add_field(name="📅 Data", value=datetime.now().strftime('%d/%m/%Y %H:%M'), inline=True)
            
            embed.add_field(name="📝 Título", value=self.titulo.value, inline=False)
            embed.add_field(name="💬 Descrição", value=self.descricao.value[:300] + ('...' if len(self.descricao.value) > 300 else ''), inline=False)
            
            # Mostrar cargos que foram notificados
            mentions = [f"<@&{CARGOS_STAFF[cargo]}>" for cargo in self.cargos_responsaveis]
            embed.add_field(
                name="🔔 Cargos Notificados Automaticamente",
                value="\n".join([f"• {mention}" for mention in mentions]),
                inline=False
            )
            
            embed.add_field(
                name="🎟️ Próximos Passos",
                value="**Um ticket privado será criado automaticamente!**\nVocê poderá conversar diretamente com as autoridades responsáveis.\n\n⏰ **Aguarde** - Em breve algum responsável irá atendê-lo!",
                inline=False
            )
            
            embed.set_thumbnail(url=self.user.display_avatar.url)
            embed.set_footer(text="Portal Feedback | Cidade RP")
            
            await interaction.response.edit_message(embed=embed, view=None)
            print("✅ Resposta de sucesso enviada")
            
            # Criar ticket privado em background
            print(f"🎟️ Iniciando criação de ticket para feedback #{feedback_id:03d}")
            try:
                await criar_ticket_privado(interaction, feedback_id, self.categoria, f"{self.titulo.value}\n\n{self.descricao.value}", self.cargos_responsaveis)
                print(f"✅ Ticket #{feedback_id:03d} criado com sucesso")
            except Exception as ticket_error:
                print(f"❌ ERRO CRÍTICO no ticket #{feedback_id:03d}: {ticket_error}")
                import traceback
                traceback.print_exc()
                # Continuar mesmo se o ticket falhar
            
            print(f'📝 Feedback #{feedback_id:03d} criado por {self.user} - {categoria_info["nome"]}')
            print(f'🎯 Cargos notificados: {", ".join(self.cargos_responsaveis)}')
            
        except Exception as e:
            print(f'❌ Erro geral no modal: {e}')
            import traceback
            traceback.print_exc()
            
            try:
                await interaction.response.send_message("❌ Erro interno! Tente novamente ou contate um administrador.", ephemeral=True)
            except:
                # Se já respondeu, edita a resposta
                try:
                    await interaction.edit_original_response(content="❌ Erro interno! Tente novamente.", view=None, embed=None)
                except:
                    pass

# ==================== BOTÕES DE CONTROLE TICKET ====================

class BotoesTicket(discord.ui.View):
    """Botões para controlar o ticket"""
    
    def __init__(self, feedback_id):
        super().__init__(timeout=None)  # Sem timeout para tickets
        self.feedback_id = feedback_id
    
    @discord.ui.button(label='✅ Marcar como Resolvido', style=discord.ButtonStyle.success, row=0)
    async def resolver(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verificar se é staff
        user_role_ids = [role.id for role in interaction.user.roles]
        is_staff = any(role_id in CARGOS_STAFF.values() for role_id in user_role_ids)
        
        if not is_staff:
            await interaction.response.send_message("❌ Apenas staff pode marcar como resolvido!", ephemeral=True)
            return
        
        # Atualizar status no banco
        conn = sqlite3.connect('feedbacks.db')
        c = conn.cursor()
        c.execute('UPDATE feedbacks SET status = ? WHERE id = ?', ('resolvido', self.feedback_id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✅ Ticket Resolvido!",
            description=f"**Feedback #{self.feedback_id:03d}** foi marcado como **RESOLVIDO** por {interaction.user.mention}",
            color=0x00ff00
        )
        
        embed.add_field(
            name="📋 Próximas ações",
            value="• Ticket pode ser fechado e arquivado\n• Use o botão **🔒 Fechar Ticket** para finalizar",
            inline=False
        )
        
        embed.set_footer(text=f"Resolvido por {interaction.user} em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Atualizar botões
        view = BotoesTicketResolvido(self.feedback_id)
        
        await interaction.response.send_message(embed=embed, view=view)
        print(f"✅ Feedback #{self.feedback_id:03d} marcado como resolvido por {interaction.user}")
    
    @discord.ui.button(label='🔒 Fechar Ticket', style=discord.ButtonStyle.danger, row=0)
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verificar se é staff
        user_role_ids = [role.id for role in interaction.user.roles]
        is_staff = any(role_id in CARGOS_STAFF.values() for role_id in user_role_ids)
        
        if not is_staff:
            await interaction.response.send_message("❌ Apenas staff pode fechar tickets!", ephemeral=True)
            return
        
        # Confirmar fechamento
        embed = discord.Embed(
            title="⚠️ Confirmar Fechamento",
            description=f"**Tem certeza que quer fechar o Feedback #{self.feedback_id:03d}?**\n\n"
                       "⚠️ **Esta ação:**\n"
                       "• Arquivará o thread\n"
                       "• Marcará como fechado no banco\n"
                       "• **NÃO pode ser desfeita**",
            color=0xff6600
        )
        
        view = ConfirmarFechamento(self.feedback_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class BotoesTicketResolvido(discord.ui.View):
    """Botões após ticket resolvido"""
    
    def __init__(self, feedback_id):
        super().__init__(timeout=None)
        self.feedback_id = feedback_id
    
    @discord.ui.button(label='🔒 Fechar Ticket', style=discord.ButtonStyle.danger, row=0)
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verificar se é staff
        user_role_ids = [role.id for role in interaction.user.roles]
        is_staff = any(role_id in CARGOS_STAFF.values() for role_id in user_role_ids)
        
        if not is_staff:
            await interaction.response.send_message("❌ Apenas staff pode fechar tickets!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚠️ Confirmar Fechamento",
            description=f"**Tem certeza que quer fechar o Feedback #{self.feedback_id:03d}?**\n\n"
                       "⚠️ **Esta ação:**\n"
                       "• Arquivará o thread\n"
                       "• Marcará como fechado no banco\n"
                       "• **NÃO pode ser desfeita**",
            color=0xff6600
        )
        
        view = ConfirmarFechamento(self.feedback_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfirmarFechamento(discord.ui.View):
    """Confirmar fechamento do ticket"""
    
    def __init__(self, feedback_id):
        super().__init__(timeout=60)
        self.feedback_id = feedback_id
    
    @discord.ui.button(label='✅ Sim, Fechar', style=discord.ButtonStyle.danger, row=0)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Atualizar status no banco PRIMEIRO
            conn = sqlite3.connect('feedbacks.db')
            c = conn.cursor()
            c.execute('UPDATE feedbacks SET status = ? WHERE id = ?', ('fechado', self.feedback_id))
            conn.commit()
            conn.close()
            print(f"💾 Status 'fechado' salvo no banco para feedback #{self.feedback_id}")
            
            # Responder ANTES de tentar arquivar
            embed = discord.Embed(
                title="🔒 Ticket Fechado!",
                description=f"**Feedback #{self.feedback_id:03d}** foi fechado e arquivado por {interaction.user.mention}",
                color=0x666666
            )
            
            embed.add_field(
                name="📊 Status Final",
                value="🔒 **FECHADO**\n📦 Thread arquivado\n✅ Processo concluído",
                inline=False
            )
            
            embed.set_footer(text=f"Fechado por {interaction.user} em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
            await interaction.response.edit_message(embed=embed, view=None)
            
            # Tentar arquivar thread DEPOIS da resposta
            if isinstance(interaction.channel, discord.Thread):
                try:
                    await interaction.channel.edit(archived=True, locked=True)
                    print(f"📦 Thread #{self.feedback_id:03d} arquivado com sucesso")
                except discord.Forbidden:
                    print(f"❌ Sem permissão para arquivar thread #{self.feedback_id:03d}")
                except discord.HTTPException as e:
                    print(f"❌ Erro HTTP ao arquivar thread #{self.feedback_id:03d}: {e}")
                except Exception as arch_error:
                    print(f"❌ Erro inesperado ao arquivar thread #{self.feedback_id:03d}: {arch_error}")
            
            print(f"🔒 Feedback #{self.feedback_id:03d} fechado por {interaction.user}")
            
        except discord.InteractionResponded:
            print(f"⚠️ Interação já foi respondida para feedback #{self.feedback_id}")
        except Exception as e:
            print(f"❌ Erro crítico ao fechar ticket #{self.feedback_id}: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                await interaction.response.send_message("❌ Erro ao fechar ticket! Tente novamente.", ephemeral=True)
            except discord.InteractionResponded:
                await interaction.followup.send("❌ Erro ao fechar ticket! Tente novamente.", ephemeral=True)
    
    @discord.ui.button(label='❌ Cancelar', style=discord.ButtonStyle.secondary, row=0)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Fechamento Cancelado",
            description="O ticket continua aberto.",
            color=0x999999
        )
        await interaction.response.edit_message(embed=embed, view=None)

# ==================== FUNÇÕES AUXILIARES ====================

async def mostrar_meus_feedbacks(interaction):
    """Mostrar feedbacks do usuário"""
    print(f"📊 [MOSTRAR FEEDBACKS] Iniciando para usuário {interaction.user}")
    
    conn = sqlite3.connect('feedbacks.db')
    c = conn.cursor()
    
    print(f"🔍 [MOSTRAR FEEDBACKS] Consultando banco para user_id: {interaction.user.id}")
    c.execute('SELECT * FROM feedbacks WHERE usuario_id = ? ORDER BY id DESC LIMIT 10', (interaction.user.id,))
    feedbacks = c.fetchall()
    conn.close()
    
    print(f"📊 [MOSTRAR FEEDBACKS] Encontrados {len(feedbacks)} feedbacks")
    
    if not feedbacks:
        embed = discord.Embed(
            title="📋 Seus Feedbacks",
            description="**Nenhum feedback encontrado**\n\nVocê ainda não criou nenhum feedback.\nUse o painel para enviar uma sugestão!",
            color=0x0099ff
        )
    else:
        embed = discord.Embed(
            title=f"📋 Seus Feedbacks ({len(feedbacks)})",
            description=f"Histórico de feedbacks de {interaction.user.mention}",
            color=0x0099ff
        )
        
        for fb in feedbacks[:5]:
            print(f"🔍 [DEBUG] Estrutura do feedback: {fb}")
            print(f"🔍 [DEBUG] Total de colunas: {len(fb)}")
            
            # Usar índices seguros baseados na estrutura real
            # (id, usuario_id, usuario_nome, categoria, titulo, descricao, data_criacao, cargos_responsaveis, thread_id, status)
            feedback_id = fb[0] if len(fb) > 0 else 0
            categoria = fb[3] if len(fb) > 3 else 'outros'
            titulo = fb[4] if len(fb) > 4 else 'Sem título'
            descricao = fb[5] if len(fb) > 5 else 'Sem descrição'
            data_criacao = fb[6] if len(fb) > 6 else 'Data não disponível'
            
            # Status pode estar em posições diferentes dependendo da migração
            status = 'novo'
            if len(fb) > 9:
                status = fb[9] if fb[9] else 'novo'
            elif len(fb) > 8:
                status = fb[8] if fb[8] else 'novo'
            
            categoria_info = CATEGORIAS.get(categoria, {'nome': 'Outros', 'emoji': '❓'})
            status_emoji = {"novo": "🟡", "resolvido": "✅", "fechado": "🔒"}
            status_icon = status_emoji.get(status, "❓")
            
            embed.add_field(
                name=f"{status_icon} #{feedback_id:03d} - {categoria_info['nome']}",
                value=f"📝 **{titulo}**\n_{descricao[:80]}{'...' if len(descricao) > 80 else ''}_\n📅 {data_criacao}",
                inline=False
            )
    
    embed.set_footer(text="Use o painel para criar um novo feedback!")
    
    # Voltar ao painel principal
    print(f"🔄 [MOSTRAR FEEDBACKS] Criando painel principal...")
    view = PainelPrincipal(interaction.user)
    
    print(f"📤 [MOSTRAR FEEDBACKS] Enviando resposta...")
    await interaction.response.edit_message(embed=embed, view=view)
    print(f"✅ [MOSTRAR FEEDBACKS] Resposta enviada com sucesso!")

async def criar_ticket_privado(interaction, feedback_id, categoria, texto_completo, cargos_responsaveis):
    """Criar thread privado para o feedback - VERSÃO CORRIGIDA"""
    
    try:
        print(f"🎟️ [TICKET #{feedback_id:03d}] Iniciando criação de thread...")
        
        # USAR CANAL ESPECÍFICO DE FEEDBACK
        guild = interaction.guild
        print(f"🏠 [TICKET #{feedback_id:03d}] Servidor: {guild.name}")
        
        canal = guild.get_channel(CANAL_FEEDBACK_ID)
        print(f"🔍 [TICKET #{feedback_id:03d}] Buscando canal ID {CANAL_FEEDBACK_ID}: {'✅ Encontrado' if canal else '❌ Não encontrado'}")
        
        if not canal:
            print(f"❌ [TICKET #{feedback_id:03d}] Canal de feedback não encontrado! ID: {CANAL_FEEDBACK_ID}")
            # Fallback para qualquer canal disponível
            print(f"🔄 [TICKET #{feedback_id:03d}] Procurando canal alternativo...")
            for channel in guild.text_channels:
                perms = channel.permissions_for(guild.me)
                print(f"🔍 [TICKET #{feedback_id:03d}] Testando canal {channel.name}: send_messages={perms.send_messages}, create_threads={perms.create_public_threads}")
                if perms.send_messages and perms.create_public_threads:
                    canal = channel
                    print(f"⚠️ [TICKET #{feedback_id:03d}] Usando canal alternativo: {channel.name}")
                    break
        
        if not canal:
            print(f"❌ [TICKET #{feedback_id:03d}] Nenhum canal disponível para threads")
            await enviar_dms_fallback(interaction, feedback_id, categoria, texto_completo, cargos_responsaveis)
            return
        
        # Verificar permissões no canal específico
        perms = canal.permissions_for(guild.me)
        print(f"🔒 [TICKET #{feedback_id:03d}] Permissões no canal {canal.name}:")
        print(f"    - send_messages: {perms.send_messages}")
        print(f"    - create_public_threads: {perms.create_public_threads}")
        print(f"    - manage_threads: {perms.manage_threads}")
        
        if not perms.send_messages or not perms.create_public_threads:
            print(f"❌ [TICKET #{feedback_id:03d}] Bot sem permissões necessárias no canal {canal.name}")
            await enviar_dms_fallback(interaction, feedback_id, categoria, texto_completo, cargos_responsaveis)
            return
        
        print(f"📍 [TICKET #{feedback_id:03d}] Usando canal de feedback: {canal.name} (ID: {canal.id})")
        
        thread_name = f"🎟️ Feedback #{feedback_id:03d} - {interaction.user.display_name}"
        
        # Embed inicial do thread
        embed_thread = discord.Embed(
            title=f"🎟️ Ticket Privado - Feedback #{feedback_id:03d}",
            color=0x5865F2,
            description=f"**{CATEGORIAS[categoria]['nome']}**"
        )
        
        embed_thread.add_field(name="👤 Cidadão", value=interaction.user.mention, inline=True)
        embed_thread.add_field(name="📅 Data", value=datetime.now().strftime('%d/%m/%Y %H:%M'), inline=True)
        embed_thread.add_field(name="📝 Feedback", value=texto_completo[:900] + ('...' if len(texto_completo) > 900 else ''), inline=False)
        
        # Mentions dos cargos
        mentions = []
        for cargo in cargos_responsaveis:
            if cargo in CARGOS_STAFF:
                mentions.append(f"<@&{CARGOS_STAFF[cargo]}>")
        
        if mentions:
            embed_thread.add_field(
                name="🔔 Cargos Responsáveis",
                value="\n".join([f"• {mention}" for mention in mentions]),
                inline=False
            )
        
        embed_thread.set_footer(text="Portal Feedback | Sistema de Tickets")
        
        print(f"📝 [TICKET #{feedback_id:03d}] Enviando mensagem inicial no canal {canal.name}...")
        
        # Criar mensagem inicial
        message = await canal.send(embed=embed_thread)
        print(f"✅ [TICKET #{feedback_id:03d}] Mensagem criada: {message.id}")
        
        print(f"🧵 [TICKET #{feedback_id:03d}] Criando thread a partir da mensagem...")
        
        # Criar thread a partir da mensagem
        thread = await message.create_thread(
            name=thread_name, 
            auto_archive_duration=10080  # 7 dias
        )
        
        print(f"✅ [TICKET #{feedback_id:03d}] Thread criado com sucesso!")
        print(f"    - Nome: {thread.name}")
        print(f"    - ID: {thread.id}")
        print(f"    - Canal pai: {thread.parent.name if thread.parent else 'N/A'}")
        
        # Adicionar o cidadão ao thread
        try:
            await thread.add_user(interaction.user)
            print(f"👤 Cidadão adicionado: {interaction.user}")
        except Exception as user_error:
            print(f"⚠️ Erro ao adicionar cidadão: {user_error}")
        
        # Adicionar membros dos cargos
        membros_adicionados = 0
        for cargo_nome in cargos_responsaveis:
            if cargo_nome in CARGOS_STAFF:
                role_id = CARGOS_STAFF[cargo_nome]
                role = guild.get_role(role_id)
                if role:
                    for member in role.members:
                        if not member.bot and member.id != interaction.user.id:
                            try:
                                await thread.add_user(member)
                                membros_adicionados += 1
                                print(f"✅ Adicionado: {member} ({cargo_nome})")
                            except Exception as member_error:
                                print(f"⚠️ Erro ao adicionar {member}: {member_error}")
        
        print(f"👥 Total membros adicionados: {membros_adicionados}")
        
        # Salvar thread_id no banco
        conn = sqlite3.connect('feedbacks.db')
        c = conn.cursor()
        c.execute('UPDATE feedbacks SET thread_id = ? WHERE id = ?', (thread.id, feedback_id))
        conn.commit()
        conn.close()
        
        print("💾 Thread ID salvo no banco")
        
        # Mensagem de boas-vindas
        welcome_msg = f"""🎉 **Ticket criado com sucesso!**

👤 **Cidadão:** {interaction.user.mention}
🎯 **Cargos notificados:** {' '.join(mentions)}

**Este é um espaço privado para discussão deste feedback.**
Apenas os participantes podem ver e responder aqui.

{interaction.user.mention}, aguarde! Em breve algum responsável irá atendê-lo.
**Staff**, respondam diretamente aqui para atender o cidadão! 📞"""
        
        await thread.send(welcome_msg)
        
        # Adicionar botões de controle
        view_controle = BotoesTicket(feedback_id)
        
        embed_controle = discord.Embed(
            title="🛠️ Controles do Ticket",
            description="Use os botões abaixo para gerenciar este ticket:",
            color=0x999999
        )
        
        await thread.send(embed=embed_controle, view=view_controle)
        
        print(f"🎉 Thread completamente configurado!")
        
    except Exception as e:
        print(f'❌ Erro crítico ao criar thread: {e}')
        import traceback
        traceback.print_exc()
        
        # Fallback para DMs
        await enviar_dms_fallback(interaction, feedback_id, categoria, texto_completo, cargos_responsaveis)

async def enviar_dms_fallback(interaction, feedback_id, categoria, texto_completo, cargos_responsaveis):
    """Fallback: enviar DMs se thread não funcionar"""
    
    print("📧 Iniciando fallback DMs...")
    
    embed_dm = discord.Embed(
        title="🔔 Novo Feedback Recebido!",
        color=0xff6600,
        description=f"**#{feedback_id:03d}** - {CATEGORIAS[categoria]['nome']}"
    )
    
    embed_dm.add_field(name="👤 Cidadão", value=f"{interaction.user.mention}\n({interaction.user})", inline=True)
    embed_dm.add_field(name="📅 Data", value=datetime.now().strftime('%d/%m/%Y\n%H:%M'), inline=True)
    embed_dm.add_field(name="💬 Feedback", value=f"```{texto_completo[:800]}```", inline=False)
    embed_dm.add_field(name="⚠️ Thread falhou", value="O ticket privado não foi criado. Responda diretamente ao cidadão via DM!", inline=False)
    
    embed_dm.set_thumbnail(url=interaction.user.display_avatar.url)
    embed_dm.set_footer(text="Portal Feedback | Sistema DM Fallback")
    
    enviados = 0
    for cargo_nome in cargos_responsaveis:
        if cargo_nome in CARGOS_STAFF:
            role_id = CARGOS_STAFF[cargo_nome]
            role = interaction.guild.get_role(role_id)
            if role:
                for member in role.members:
                    if not member.bot and member.id != interaction.user.id:
                        try:
                            await member.send(embed=embed_dm)
                            enviados += 1
                            print(f'✅ DM enviada para {member} ({cargo_nome})')
                        except:
                            print(f'❌ Erro DM para {member}')
    
    print(f'📊 Total DMs enviadas: {enviados}')

# ==================== EVENTOS E COMANDOS ====================

@bot.event
async def on_ready():
    print(f'✅ {bot.user} está online!')
    print(f'🔧 Sistema CORRIGIDO e com controle de tickets!')
    print(f'📊 Servidores conectados: {len(bot.guilds)}')
    
    # Verificar cargos
    for guild in bot.guilds:
        print(f'🏠 Servidor: {guild.name}')
        for nome, role_id in CARGOS_STAFF.items():
            role = guild.get_role(role_id)
            if role:
                print(f'  ✅ {nome}: {role.name} ({len(role.members)} membros)')
            else:
                print(f'  ❌ {nome}: Cargo ID {role_id} não encontrado!')
    
    init_db()
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} comandos sincronizados!')
        print('🎯 Sistema pronto com logs detalhados!')
    except Exception as e:
        print(f'❌ Erro na sincronização: {e}')

@bot.tree.command(name="feedback", description="🎮 Abrir painel de feedback")
async def feedback_command(interaction: discord.Interaction):
    # Verificar se é cidadão
    if not any(role.id == CARGO_CIDADAO for role in interaction.user.roles):
        await interaction.response.send_message("❌ **Acesso Negado!** Apenas cidadãos podem usar o sistema de feedback.", ephemeral=True)
        return
    
    # Embed principal
    embed = discord.Embed(
        title="🎯 Portal de Feedback - Cidade RP",
        description="**Bem-vindo ao sistema de feedback!**\n\nEscolha uma categoria para enviar sua sugestão:",
        color=0x00ff88
    )
    
    embed.add_field(
        name="📋 Categorias Disponíveis",
        value="🏗️ **Melhorias na Cidade** - Ideias para locais e construções\n"
              "💰 **Economia** - Preços, salários, negócios\n"
              "🎭 **Eventos e Cultura** - Festas, shows, atividades\n"
              "⚖️ **Regras e Leis** - Leis da cidade, punições\n"
              "💡 **Sugestões Livres** - Qualquer ideia criativa",
        inline=False
    )
    
    embed.add_field(
        name="⚡ Fluxo Simplificado",
        value="1️⃣ **Clique** na categoria desejada\n"
              "2️⃣ **Escreva** título e descrição\n" 
              "3️⃣ **Cargos responsáveis** são notificados automaticamente\n"
              "4️⃣ **Aguarde** resposta no ticket privado",
        inline=False
    )
    
    embed.set_footer(text="Clique nos botões abaixo!")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    view = PainelPrincipal(interaction.user)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="dashboard", description="📊 Ver dashboard de feedbacks (Staff only)")
async def dashboard_command(interaction: discord.Interaction):
    # Verificar se é staff
    user_role_ids = [role.id for role in interaction.user.roles]
    is_staff = any(role_id in CARGOS_STAFF.values() for role_id in user_role_ids)
    
    if not is_staff:
        await interaction.response.send_message("❌ **Acesso Negado!** Apenas staff pode ver o dashboard.", ephemeral=True)
        return
    
    conn = sqlite3.connect('feedbacks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM feedbacks ORDER BY id DESC LIMIT 15')
    feedbacks = c.fetchall()
    conn.close()
    
    if not feedbacks:
        await interaction.response.send_message("📋 **Nenhum feedback encontrado**", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📊 Dashboard - Todos os Feedbacks",
        color=0xff9900,
        description=f"Últimos {len(feedbacks)} feedbacks recebidos"
    )
    
    for fb in feedbacks[:8]:
        categoria_info = CATEGORIAS.get(fb[3], {'nome': 'Outros', 'emoji': '❓'})
        status_emoji = {"novo": "🟡", "resolvido": "✅", "fechado": "🔒"}
        status = status_emoji.get(fb[9], "❓")
        
        responsaveis = fb[6].split(',') if fb[6] else []
        resp_text = ', '.join(responsaveis[:3]) + ('...' if len(responsaveis) > 3 else '')
        
        embed.add_field(
            name=f"{status} #{fb[0]:03d} - {categoria_info['nome']}",
            value=f"👤 {fb[2].split('#')[0]}\n📝 **{fb[4]}**\n🎯 {resp_text}\n📅 {fb[10]}",
            inline=False
        )
    
    embed.set_footer(text="Dashboard Staff | Portal Feedback")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Rodar bot
if __name__ == "__main__":
    print("🤖 Iniciando Portal Feedback Bot - VERSÃO CORRIGIDA...")
    print("🔧 Sistema com logs detalhados e controle de tickets!")
    print(f"📋 {len(CARGOS_STAFF)} cargos configurados")
    print("🎯 Funcionalidades: Criar → Resolver → Fechar tickets!")
    bot.run(TOKEN)
````
