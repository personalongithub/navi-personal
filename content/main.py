# main.py
"""Contains error handling and the help and about commands"""

from datetime import datetime
import sys

import discord
from discord.ext import commands
from humanfriendly import format_timespan
import psutil

from database import users
from database import settings as settings_db
from resources import emojis, functions, settings


# Commands
async def command_help(ctx: discord.ApplicationContext) -> None:
    """Help command"""
    embed = await embed_main_help(ctx)
    await ctx.respond(embed=embed)


async def command_about(bot: discord.Bot, ctx: discord.ApplicationContext) -> None:
    """About command"""
    start_time = datetime.utcnow()
    interaction = await ctx.respond('Testing API latency...')
    end_time = datetime.utcnow()
    api_latency = end_time - start_time
    embed = await embed_about(bot, api_latency)
    await functions.edit_interaction(interaction, content=None, embed=embed)


# --- Embeds ---
async def embed_main_help(ctx: discord.ApplicationContext) -> discord.Embed:
    """Main menu embed"""

    reminder_management = (
        f'{emojis.BP} `/list` : List all your active reminders\n'
        f'{emojis.BP} `/rm` : Manage custom reminders'
    )

    stats = (
        f'{emojis.BP} `/stats` : Shows your command stats\n'
    )

    user_settings = (
        f'{emojis.BP} `/on` / `off` : Turn the bot on/off\n'
        f'{emojis.BP} `/settings` : Check your settings\n'
        f'{emojis.BP} `/donor` : Set your EPIC RPG donor tier\n'
        f'{emojis.BP} `/enable` / `disable` : Enable/disable specific reminders\n'
        f'{emojis.BP} `/dnd on` / `off` : Turn DND mode on/off (disables pings)\n'
        f'{emojis.BP} `/hardmode on` / `off` : Turn hardmode mode on/off (tells your partner to hunt solo)\n'
        f'{emojis.BP} `/heal on` / `off` : Turn heal warning on/off\n'
        f'{emojis.BP} `/message` : Change the reminder messages\n'
        f'{emojis.BP} `/pet-helper on` / `off` : Turn the pet catch helper on/off\n'
        f'{emojis.BP} `/ruby` : Check your current ruby count\n'
        f'{emojis.BP} `/ruby on` / `off` : Turn the ruby counter on/off\n'
        f'{emojis.BP} `/tr-helper on` / `off` : Turn the training helper on/off\n'
        f'{emojis.BP} `/last-tt` : Manually change your last TT time\n'
    )

    partner_settings = (
        f'{emojis.BP} `/partner` : Set your marriage partner\n'
        f'{emojis.BP} `/partner donor` : Set your partner\'s EPIC RPG donor tier\n'
        f'{emojis.BP} `/partner channel` : Set the channel for incoming lootbox alerts'
    )

    guild_settings = (
        f'{emojis.BP} `rpg guild list` : Add/update your guild\n'
        f'{emojis.BP} `/guild leaderboard` : Check the weekly raid leaderboard\n'
        f'{emojis.BP} `/guild channel` : Set the channel for guild reminders\n'
        f'{emojis.BP} `/guild reminders on` / `off` : Turn guild reminders on or off\n'
        f'{emojis.BP} `/guild stealth` : Set your stealth threshold'
    )


    embed = discord.Embed(
        color = settings.EMBED_COLOR,
        title = 'NAVI',
        description =   f'Hey! **{ctx.author.name}**! Hello!'
    )
    embed.add_field(name='EMPTY LOL', value='lol', inline=False)

    return embed


async def embed_about(bot: commands.Bot, api_latency: datetime) -> discord.Embed:
    """Bot info embed"""
    user_count = await users.get_user_count()
    all_settings = await settings_db.get_settings()
    uptime = datetime.utcnow().replace(microsecond=0) - datetime.fromisoformat(all_settings['startup_time'])
    general = (
        f'{emojis.BP} {len(bot.guilds):,} servers\n'
        f'{emojis.BP} {user_count:,} users\n'
        f'{emojis.BP} {round(bot.latency * 1000):,} ms bot latency\n'
        f'{emojis.BP} {round(api_latency.total_seconds() * 1000):,} ms API latency\n'
        f'{emojis.BP} Online for {format_timespan(uptime)}'
    )
    creator = f'{emojis.BP} Miriel#0001'
    dev_stuff = (
        f'{emojis.BP} Language: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n'
        f'{emojis.BP} Library: Pycord {discord.__version__}\n'
        f'{emojis.BP} System CPU usage: {psutil.cpu_percent()}%\n'
        f'{emojis.BP} System RAM usage: {psutil.virtual_memory()[2]}%\n'
    )
    embed = discord.Embed(color = settings.EMBED_COLOR, title = 'ABOUT NAVI')
    embed.add_field(name='BOT STATS', value=general, inline=False)
    embed.add_field(name='CREATOR', value=creator, inline=False)
    embed.add_field(name='SPECIAL THANKS TO', value=f'{emojis.BP} Swiss cheese', inline=False)
    embed.add_field(name='DEV STUFF', value=dev_stuff, inline=False)

    return embed