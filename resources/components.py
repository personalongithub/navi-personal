# components.py
"""Contains global interaction components"""

from typing import Optional

import discord

from resources import strings


class SettingsSelect(discord.ui.Select):
    """Settings Select"""
    def __init__(self, all_settings: dict, active_setting: str, placeholder: str, row: Optional[int] = None):
        self.settings = all_settings
        options = []
        for setting in all_settings.keys():
            label = setting
            emoji = '🔹' if setting == active_setting else None
            options.append(discord.SelectOption(label=label, value=label, emoji=emoji))
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, row=row,
                         custom_id='select_settings')

    async def callback(self, interaction: discord.Interaction):
        select_value = self.values[0]
        self.view.active_setting = select_value
        for child in self.view.children:
            if child.custom_id == 'select_settings':
                options = []
                for topic in self.settings.keys():
                    label = topic
                    emoji = '🔹' if topic == self.view.active_setting else None
                    options.append(discord.SelectOption(label=label, value=label, emoji=emoji))
                child.options = options
                break
        embed = await self.view.settings[select_value](self.view.bot, self.view.ctx)
        await interaction.response.edit_message(embed=embed, view=self.view)


class TopicSelect(discord.ui.Select):
    """Topic Select"""
    def __init__(self, topics: dict, active_topic: str, placeholder: str, row: Optional[int] = None):
        self.topics = topics
        options = []
        for topic in topics.keys():
            label = topic
            emoji = '🔹' if topic == active_topic else None
            options.append(discord.SelectOption(label=label, value=label, emoji=emoji))
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, row=row,
                         custom_id='select_topic')

    async def callback(self, interaction: discord.Interaction):
        select_value = self.values[0]
        self.view.active_topic = select_value
        for child in self.view.children:
            if child.custom_id == 'select_topic':
                options = []
                for topic in self.topics.keys():
                    label = topic
                    emoji = '🔹' if topic == self.view.active_topic else None
                    options.append(discord.SelectOption(label=label, value=label, emoji=emoji))
                child.options = options
                break
        embed = await self.view.topics[select_value]()
        await interaction.response.edit_message(embed=embed, view=self.view)


class CustomButton(discord.ui.Button):
    """Custom Button. Writes its custom id to the view value and stops the view."""
    def __init__(self, style: discord.ButtonStyle, custom_id: str, label: Optional[str],
                 emoji: Optional[discord.PartialEmoji] = None):
        super().__init__(style=style, custom_id=custom_id, label=label, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.custom_id
        self.view.stop()