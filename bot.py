import json
import os
import threading
import discord
from discord import app_commands
from discord.ext import commands
from discord import ButtonStyle, Interaction, Embed
from flask import Flask

# === CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ===
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No se encontró DISCORD_TOKEN en las variables de entorno")

# Owners desde variable de entorno (formato: "ID1,ID2")
owners_str = os.environ.get("OWNER_IDS", "")
OWNER_IDS = [int(id.strip()) for id in owners_str.split(",") if id.strip()] if owners_str else []

ARCHIVO_LINKS = "links.json"

# === FUNCIONES PARA LINKS ===
def cargar_links():
    try:
        with open(ARCHIVO_LINKS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def guardar_links(links):
    with open(ARCHIVO_LINKS, "w", encoding="utf-8") as f:
        json.dump(links, f, indent=2, ensure_ascii=False)

# === BOT DE DISCORD CON PREFIX ! ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def es_owner_id(user_id: int) -> bool:
    return user_id in OWNER_IDS

# === CLASE DE BOTONES ===
class DescargaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="🔥 Free Fire Normal",
            style=ButtonStyle.primary,
            custom_id="normal",
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="📱 Free Fire x86",
            style=ButtonStyle.success,
            custom_id="x86",
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="⚡ Free Fire MAX",
            style=ButtonStyle.danger,
            custom_id="max",
            row=1
        ))
        self.add_item(discord.ui.Button(
            label="🖥️ Emulador",
            style=ButtonStyle.secondary,
            custom_id="emulador",
            row=1
        ))
        self.add_item(discord.ui.Button(
            label="🚀 Loader SensiXiters.exe",
            style=ButtonStyle.primary,
            custom_id="loader_sensi",
            row=2
        ))
        self.add_item(discord.ui.Button(
            label="⚡ SensiXiters.exe",
            style=ButtonStyle.success,
            custom_id="sensi_xiters",
            row=2
        ))

# === EVENTO PARA BOTONES ===
@bot.event
async def on_interaction(interaction: Interaction):
    if interaction.type != discord.InteractionType.component:
        return
    custom_id = interaction.data.get("custom_id")
    links = cargar_links()
    link = links.get(custom_id)
    nombres = {
        "normal": "Free Fire Normal",
        "x86": "Free Fire x86",
        "max": "Free Fire MAX",
        "emulador": "Emulador",
        "loader_sensi": "Loader SensiXiters",
        "sensi_xiters": "SensiXiters"
    }
    nombre_mostrar = nombres.get(custom_id, custom_id.upper())
    if link:
        emoji = "🚀" if custom_id == "loader_sensi" else "⚡" if custom_id == "sensi_xiters" else "💻" if link.lower().endswith('.exe') else "📥"
        embed = Embed(title=f"{emoji} Link para {nombre_mostrar}", description=f"**Descarga:** {link}", color=discord.Color.green())
        if link.lower().endswith('.exe'):
            embed.add_field(name="⚠️ Advertencia", value="Este es un archivo `.exe`. Asegúrate de descargarlo de fuentes confiables.", inline=False)
        embed.set_footer(text="Xereca Bot")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = Embed(title="❌ Link no disponible", description=f"No hay link configurado para **{nombre_mostrar}**.\nUsa `!actualizar` para configurarlo.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ============================================
# SLASH COMMANDS (con / )
# ============================================

@bot.tree.command(name="start", description="Muestra los botones de descarga")
async def slash_start(interaction: Interaction):
    embed = Embed(title="📥 Descargas", description="Elige un botón para obtener el link de descarga.", color=discord.Color.blue())
    embed.set_footer(text="Xereca Bot · Admin")
    view = DescargaView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="actualizar", description="Actualiza un link de descarga (solo owners)")
@app_commands.describe(clave="Tipo: normal, x86, max, emulador, loader_sensi, sensi_xiters", link="El nuevo link de descarga")
async def slash_actualizar(interaction: Interaction, clave: str, link: str):
    if not es_owner_id(interaction.user.id):
        embed = Embed(title="⛔ Permiso denegado", description="Solo los **owners** del bot pueden usar este comando.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    claves_validas = ["normal", "x86", "max", "emulador", "loader_sensi", "sensi_xiters"]
    if clave not in claves_validas:
        embed = Embed(title="❌ Clave no válida", description=f"Claves disponibles: {', '.join(claves_validas)}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    links = cargar_links()
    link_anterior = links.get(clave, "No configurado")
    links[clave] = link
    guardar_links(links)
    emoji = "🚀" if clave == "loader_sensi" else "⚡" if clave == "sensi_xiters" else "💻" if link.lower().endswith('.exe') else "📥"
    embed = Embed(title=f"{emoji} Link actualizado", description=f"**{clave.upper()}**\n📌 **Anterior:** {link_anterior}\n🆕 **Nuevo:** {link}", color=discord.Color.green())
    if link.lower().endswith('.exe'):
        embed.add_field(name="⚠️ Archivo .exe", value="Recuerda verificar que el archivo sea seguro antes de ejecutarlo.", inline=False)
    embed.set_footer(text=f"Actualizado por {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="links", description="Muestra todos los links guardados (solo owners)")
async def slash_links(interaction: Interaction):
    if not es_owner_id(interaction.user.id):
        embed = Embed(title="⛔ Permiso denegado", description="Solo los **owners** del bot pueden usar este comando.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    links = cargar_links()
    if not links:
        embed = Embed(title="📭 Sin links", description="No hay links configurados aún.", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    embed = Embed(title="📋 Links actuales", color=discord.Color.blue())
    embed.set_footer(text="Xereca Bot · Solo owners pueden ver esto")
    for clave, link in links.items():
        emoji = "🚀" if clave == "loader_sensi" else "⚡" if clave == "sensi_xiters" else "💻" if link.lower().endswith('.exe') else "📱" if link.lower().endswith('.apk') else "🔗"
        embed.add_field(name=f"{emoji} {clave.upper()}", value=link, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="owners", description="Muestra los owners del bot")
async def slash_owners(interaction: Interaction):
    embed = Embed(title="👑 Owners del bot", description="", color=discord.Color.gold())
    for owner_id in OWNER_IDS:
        try:
            user = await bot.fetch_user(owner_id)
            embed.description += f"• {user.name}#{user.discriminator} (`{owner_id}`)\n"
        except:
            embed.description += f"• Owner ID: `{owner_id}`\n"
    embed.set_footer(text="Xereca Bot")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ============================================
# COMANDOS DE TEXTO CON PREFIX !
# ============================================

@bot.command(name="start")
async def text_start(ctx):
    """Muestra los botones de descarga"""
    embed = Embed(title="📥 Descargas", description="Elige un botón para obtener el link de descarga.", color=discord.Color.blue())
    embed.set_footer(text="Xereca Bot · Admin")
    view = DescargaView()
    await ctx.send(embed=embed, view=view)

@bot.command(name="actualizar")
async def text_actualizar(ctx, clave: str = None, *, link: str = None):
    """Actualiza un link de descarga (solo owners)"""
    if not es_owner_id(ctx.author.id):
        await ctx.send("⛔ Solo los owners pueden usar este comando.")
        return
    
    if not clave or not link:
        await ctx.send("⚠️ Uso correcto: `!actualizar <clave> <link>`\nClaves: normal, x86, max, emulador, loader_sensi, sensi_xiters")
        return
    
    claves_validas = ["normal", "x86", "max", "emulador", "loader_sensi", "sensi_xiters"]
    if clave not in claves_validas:
        await ctx.send(f"❌ Clave no válida. Usa: {', '.join(claves_validas)}")
        return
    
    links = cargar_links()
    link_anterior = links.get(clave, "No configurado")
    links[clave] = link
    guardar_links(links)
    
    await ctx.send(f"✅ Link actualizado!\n**{clave.upper()}**\n📌 Anterior: {link_anterior}\n🆕 Nuevo: {link}")

@bot.command(name="links")
async def text_links(ctx):
    """Muestra todos los links guardados (solo owners)"""
    if not es_owner_id(ctx.author.id):
        await ctx.send("⛔ Solo los owners pueden usar este comando.")
        return
    
    links = cargar_links()
    if not links:
        await ctx.send("📭 No hay links configurados aún.")
        return
    
    embed = Embed(title="📋 Links actuales", color=discord.Color.blue())
    for clave, link in links.items():
        embed.add_field(name=clave.upper(), value=link, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="owners")
async def text_owners(ctx):
    """Muestra los owners del bot"""
    embed = Embed(title="👑 Owners del bot", color=discord.Color.gold())
    desc = ""
    for owner_id in OWNER_IDS:
        try:
            user = await bot.fetch_user(owner_id)
            desc += f"• {user.name}#{user.discriminator} (`{owner_id}`)\n"
        except:
            desc += f"• Owner ID: `{owner_id}`\n"
    embed.description = desc
    await ctx.send(embed=embed)

@bot.command(name="sync")
async def text_sync(ctx):
    """Fuerza la sincronización de los comandos slash (solo owners)"""
    if not es_owner_id(ctx.author.id):
        await ctx.send("⛔ Solo los owners pueden usar este comando.")
        return
    
    try:
        await bot.tree.sync()
        await ctx.send("✅ Comandos slash sincronizados globalmente! Puede tardar hasta 1 hora.")
        
        # Intentar sincronizar en el servidor actual
        try:
            guild = discord.Object(id=ctx.guild.id)
            await bot.tree.sync(guild=guild)
            await ctx.send(f"✅ Comandos sincronizados en este servidor! (Inmediato)")
        except:
            pass
    except Exception as e:
        await ctx.send(f"❌ Error al sincronizar: {e}")

@bot.command(name="ping")
async def text_ping(ctx):
    """Verifica si el bot está vivo"""
    await ctx.send(f"🏓 Pong! Latencia: {round(bot.latency * 1000)}ms")

@bot.command(name="test")
async def text_test(ctx):
    """Comando de prueba"""
    await ctx.send("✅ El bot está funcionando correctamente!")

# === SINCORNIZAR AL INICIAR ===
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("✅ Comandos slash sincronizados globalmente")
    except Exception as e:
        print(f"❌ Error al sincronizar global: {e}")
    
    print(f"🤖 Xereca Bot conectado como {bot.user}")
    print(f"👑 Owners: {OWNER_IDS}")
    print(f"📊 Conectado a {len(bot.guilds)} servidores")
    print("=" * 50)
    print("💡 COMANDOS DISPONIBLES:")
    print("   !start       - Muestra botones de descarga")
    print("   !actualizar  - Actualiza links (owners)")
    print("   !links       - Ver todos los links (owners)")
    print("   !owners      - Ver owners del bot")
    print("   !sync        - Sincronizar slash commands (owners)")
    print("   !ping        - Verificar si el bot está vivo")
    print("   !test        - Comando de prueba")
    print("=" * 50)

# === SERVIDOR WEB PARA MANTENER EL BOT VIVO ===
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Xereca Bot está vivo!"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# === ARRANQUE: BOT + FLASK EN PARALELO ===
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    bot.run(TOKEN)