#!/usr/bin/env python3

import discord
import secret
import discord_slash
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

roles = {
        'UT': ['cs-311','cs-314','cs-375','cs-439','m-328k','m-408d','m-427j','m-427l','cc-303'],
        'video games': ['osu','League','Trivia','Tetris','Amogus','Minecraft','Warzone','Chess','Terraria'],
    }

role_map = {}

intents = discord.Intents().default()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    guild = client.guilds[0]
    if guild is None:
        print("Can't find guild")
        return
    else:
        print("Guild: " + str(guild))

    for category_name in roles:
        for channel_name in roles[category_name]:
            for role in guild.roles:
                if channel_name == role.name:
                    print(role.name + ' role found')
                    role_map[channel_name.lower()] = role
                    break
            else:
                print(channel_name + ' role not found')
                role_map[channel_name.lower()] = await guild.create_role(name=channel_name,mentionable=True)


    pos = 0
    for category in guild.categories:
        if category.name == 'Voice Channels':
            pos = category.position
    for category_name in roles:
        for category in guild.categories:
            if category_name == category.name:
                print(category_name + ' found')
                pos = category.position
                for channel_name in roles[category_name]:
                    for channel in category.channels:
                        if channel_name.lower() == channel.name.lower():
                            print(channel_name + ' found')
                            pos += 1
                            break
                    else:
                        print(channel_name + ' not found')
                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            role_map[channel_name.lower()]: discord.PermissionOverwrite(read_messages=True),
                            }
                        await guild.create_text_channel(channel_name, overwrites=overwrites, category=category, position=pos)
                        pos += 1
                pos = category.position + len(category.channels)
                print(pos)
                break
        else:
            print(category_name + ' not found')
            category = await guild.create_category(category_name, position=pos)
            pos = category.position
            for channel_name in roles[category_name]:
                for channel in category.channels:
                    if channel_name == channel.name:
                        print(channel_name + ' found')
                        pos += 1
                        break
                else:
                    print(channel_name + ' not found')
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        role_map[channel_name]: discord.PermissionOverwrite(read_messages=True),
                        }
                    await guild.create_text_channel(channel_name, overwrites=overwrites, category=category, position=pos)
                    pos += 1
            pos = category.position + len(category.channels)

@client.event
async def on_message(message):
        if message.author == client.user:
            return
        guild = client.guilds[0]
        if isinstance(message.channel,discord.DMChannel):
            if message.content == 'help':
                m = ''
                for category_name in roles:
                    m += '**' + category_name + '**\n'
                    for channel_name in roles[category_name]:
                        m += channel_name + '\n'
                await message.channel.send(m)
            else:
                role = None
                for r in guild.roles:
                    if r.name == message.content:
                        role = r
                if role is None:
                    await message.channel.send('Role ' + message.content + ' not found')
                else:
                    member = guild.get_member(message.author.id)
                    await member.add_roles(role)
                    await message.channel.send('Added role ' + message.content)

@client.event
async def on_raw_reaction_add(reaction):
    if str(reaction.emoji) == '📌':
        channel = await client.fetch_channel(reaction.channel_id)
        message = await channel.fetch_message(reaction.message_id)
        await message.pin()

@client.event
async def on_raw_reaction_remove(reaction):
    if str(reaction.emoji) == '📌':
        channel = await client.fetch_channel(reaction.channel_id)
        message = await channel.fetch_message(reaction.message_id)
        if not '📌' in [reaction.emoji for reaction in message.reactions]:
            await message.unpin()

if __name__ == '__main__':
    client.run(secret.token)
