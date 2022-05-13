# main.py
"""Contains error handling and the help and about commands"""

from datetime import datetime

import discord
from discord.commands import slash_command
from discord.ext import commands
from discord.ext.commands import errors

from content import main
from database import errors, guilds, users
from database import settings as settings_db
from resources import emojis, exceptions, logs, settings


class MainCog(commands.Cog):
    """Cog with events and help and about commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands
    @slash_command(description='Main help command')
    async def help(self, ctx: discord.ApplicationContext) -> None:
        """Main help command"""
        await main.command_help(ctx)

    @slash_command(description='Some info about Navi')
    async def about(self, ctx: discord.ApplicationContext) -> None:
        """About command"""
        await main.command_about(self.bot, ctx)

     # Events
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: Exception) -> None:
        """Runs when an error occurs and handles them accordingly.
        Interesting errors get written to the database for further review.
        """
        command_name = f'{ctx.command.full_parent_name} {ctx.command.name}'.strip()
        async def send_error() -> None:
            """Sends error message as embed"""
            embed = discord.Embed(title='An error occured')
            embed.add_field(name='Command', value=f'`{command_name}`', inline=False)
            embed.add_field(name='Error', value=f'```py\n{error}\n```', inline=False)
            await ctx.respond(embed=embed, ephemeral=True)

        error = getattr(error, 'original', error)
        if isinstance(error, commands.NoPrivateMessage):
            if ctx.guild_id is None:
                await ctx.respond(
                    f'I\'m sorry, this command is not available in DMs.',
                    ephemeral=True
                )
            else:
                await ctx.respond(
                    f'I\'m sorry, this command is not available in this server.',
                    ephemeral=True
                )
        elif isinstance(error, (commands.MissingPermissions, commands.MissingRequiredArgument,
                                commands.TooManyArguments, commands.BadArgument)):
            await send_error()
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.respond(
                f'You can\'t use this command in this channel.\n'
                f'To enable this, I need the permission `View Channel` / '
                f'`Read Messages` in this channel.',
                ephemeral=True
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f'**{ctx.author.name}**, you can only use this command every '
                f'{int(error.cooldown.per)} seconds.\n'
                f'You have to wait another **{error.retry_after:.1f}s**.',
                ephemeral=True
            )
        elif isinstance(error, exceptions.FirstTimeUserError):
            await ctx.respond(
                f'**{ctx.author.name}**, looks like I don\'t know you yet.\n'
                f'Use `/enable` to activate me first.',
                ephemeral=True
            )
        else:
            await errors.log_error(error, ctx)
            if settings.DEBUG_MODE or ctx.author.id in settings.DEV_IDS: await send_error()


    # Events
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Fires when bot has finished starting"""
        startup_info = f'{self.bot.user.name} has connected to Discord!'
        print(startup_info)
        logs.logger.info(startup_info)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                  name='your commands'))
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Fires when bot joins a guild. Sends a welcome message to the system channel."""
        try:
            guild_settings: guilds.Guild = guilds.get_guild(guild.id)
            welcome_message = (
                f'Hey! **{guild.name}**! I\'m here to remind you to do your Epic RPG commands!\n\n'
                f'Note that reminders are off by default. If you want to get reminded, please use '
                f'`{guild_settings.prefix}on` to activate me.\n'
                f'If you don\'t like this prefix, use `{guild_settings.prefix}setprefix` to change it.\n\n'
                f'Tip: If you ever forget the prefix, simply ping me with a command.'
            )
            await guild.system_channel.send(welcome_message)
        except:
            return


# Initialization
def setup(bot):
    bot.add_cog(MainCog(bot))


# --- Embeds ---
async def embed_main_help(ctx: commands.Context) -> discord.Embed:
    """Main menu embed"""
    guild = await guilds.get_guild(ctx.guild.id)
    prefix = guild.prefix

    reminder_management = (
        f'{emojis.BP} `{prefix}list` : List all your active reminders\n'
        f'{emojis.BP} `{prefix}rm` : Manage custom reminders'
    )

    stats = (
        f'{emojis.BP} `{prefix}stats` : Shows your command stats\n'
    )

    user_settings = (
        f'{emojis.BP} `{prefix}on` / `off` : Turn the bot on/off\n'
        f'{emojis.BP} `{prefix}settings` : Check your settings\n'
        f'{emojis.BP} `{prefix}donor` : Set your EPIC RPG donor tier\n'
        f'{emojis.BP} `{prefix}enable` / `disable` : Enable/disable specific reminders\n'
        f'{emojis.BP} `{prefix}dnd on` / `off` : Turn DND mode on/off (disables pings)\n'
        f'{emojis.BP} `{prefix}hardmode on` / `off` : Turn hardmode mode on/off (tells your partner to hunt solo)\n'
        f'{emojis.BP} `{prefix}heal on` / `off` : Turn heal warning on/off\n'
        f'{emojis.BP} `{prefix}message` : Change the reminder messages\n'
        f'{emojis.BP} `{prefix}pet-helper on` / `off` : Turn the pet catch helper on/off\n'
        f'{emojis.BP} `{prefix}ruby` : Check your current ruby count\n'
        f'{emojis.BP} `{prefix}ruby on` / `off` : Turn the ruby counter on/off\n'
        f'{emojis.BP} `{prefix}tr-helper on` / `off` : Turn the training helper on/off\n'
        f'{emojis.BP} `{prefix}last-tt` : Manually change your last TT time\n'
    )

    partner_settings = (
        f'{emojis.BP} `{prefix}partner` : Set your marriage partner\n'
        f'{emojis.BP} `{prefix}partner donor` : Set your partner\'s EPIC RPG donor tier\n'
        f'{emojis.BP} `{prefix}partner channel` : Set the channel for incoming lootbox alerts'
    )

    guild_settings = (
        f'{emojis.BP} `rpg guild list` : Add/update your guild\n'
        f'{emojis.BP} `{prefix}guild leaderboard` : Check the weekly raid leaderboard\n'
        f'{emojis.BP} `{prefix}guild channel` : Set the channel for guild reminders\n'
        f'{emojis.BP} `{prefix}guild reminders on` / `off` : Turn guild reminders on or off\n'
        f'{emojis.BP} `{prefix}guild stealth` : Set your stealth threshold'
    )

    server_settings = (
        f'{emojis.BP} `{prefix}prefix` : Check / set the bot prefix'
    )

    embed = discord.Embed(
        color = settings.EMBED_COLOR,
        title = 'NAVI',
        description =   f'Hey! **{ctx.author.name}**! Hello!'
    )
    embed.add_field(name='REMINDERS', value=reminder_management, inline=False)
    embed.add_field(name='COMMAND TRACKING', value=stats, inline=False)
    embed.add_field(name='USER SETTINGS', value=user_settings, inline=False)
    embed.add_field(name='PARTNER SETTINGS', value=partner_settings, inline=False)
    embed.add_field(name='GUILD SETTINGS', value=guild_settings, inline=False)
    embed.add_field(name='SERVER SETTINGS', value=server_settings, inline=False)

    return embed


async def embed_about(bot: commands.Bot, api_latency: datetime) -> discord.Embed:
    """Bot info embed"""
    user_count = await users.get_user_count()
    general = (
        f'{emojis.BP} {len(bot.guilds):,} servers\n'
        f'{emojis.BP} {user_count:,} users\n'
        f'{emojis.BP} {round(bot.latency * 1000):,} ms bot latency\n'
        f'{emojis.BP} {round(api_latency.total_seconds() * 1000):,} ms API latency'
    )
    creator = f'{emojis.BP} Miriel#0001'
    embed = discord.Embed(color = settings.EMBED_COLOR, title = 'ABOUT NAVI')
    embed.add_field(name='BOT STATS', value=general, inline=False)
    embed.add_field(name='CREATOR', value=creator, inline=False)
    embed.add_field(name='SPECIAL THANKS TO', value=f'{emojis.BP} Swiss cheese', inline=False)

    return embed