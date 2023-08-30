import discord
from discord.ext import commands
from discord import app_commands
from typing import List
from env import ENV
import logging
import qbittorrentapi

intents = discord.Intents.none()
logger = logging.getLogger('discord.bot')

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyClient(intents=intents)

def owner_check(interaction: discord.Interaction) -> bool:
    return interaction.user.id == bot.application.owner.id

async def fruit_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    locations = [x for x in ENV.locations]
    return [
        app_commands.Choice(name=location, value=location)
        for location in locations if current.lower() in location.lower()
    ]

@bot.tree.command()
@app_commands.check(owner_check)
@discord.app_commands.autocomplete(location=fruit_autocomplete)
async def torrent_add(interaction: discord.Interaction, location: str, url : str):
    """Adds a torrent"""
    if location not in ENV.locations:
        await interaction.response.send_message(f'Invalid location: \'{location}\'', ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)

    try:
        with qbittorrentapi.Client(**ENV.client_params) as client:
            response = f"qBittorrent version: {client.app.version}\n\nTorrent added!"
            path = ENV.locations[location]
            if client.torrents_add(urls=url, save_path=path) != "Ok.":
                raise Exception("Failed to add torrent.")

    except Exception as e:
        await interaction.followup.send(f"Failed to add torrent: {str(e)}", ephemeral=True)
        return

    await interaction.followup.send(response)

@bot.tree.command()
async def torrents_list(interaction: discord.Interaction, ephemeral : bool = True):
    """Lists all current active torrents"""
    await interaction.response.defer(ephemeral=ephemeral)

    try:
        with qbittorrentapi.Client(**ENV.client_params) as client:
            response = f"qBittorrent version: {client.app.version}\n\n"

            torrents = client.torrents_info()
            active_torrents = [x for x in torrents if x.state == "downloading"]

            if (len(active_torrents) <= 0):
                response += "No active torrents found."
            else:
                response += "Downloading:\n"
                for torrent in active_torrents:
                    response += f"- `{torrent.name}` {(torrent.progress * 100):.1f}%\n"

    except Exception as e:
        await interaction.followup.send(f"Failed to fetch active torrents: {str(e)}", ephemeral=ephemeral)
        return

    await interaction.followup.send(response, ephemeral=ephemeral)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logger.info('------')

bot.run(ENV.token)