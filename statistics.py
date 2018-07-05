import discord

from discord.ext import commands

__author__ = "Some idiot with a keyboard"
__version__ = "0.0.0.0.0.0.0.1"

class Statistics():
    
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def serverinfo(self, context):
        server = context.message.server
        online = len([m.status for m in server.members if m.status == discord.Status.online or m.status == discord.Status.idle])
        total_users = len(server.members)
        text_channels = len([x for x in server.channels if x.type == discord.ChannelType.text])
        voice_channels = len(server.channels) - text_channels
        created_at = ("Server created at: {}.".format(server.created_at.strftime("%d %b %Y %H:%M")))

        embed_data = discord.Embed(description=created_at)
        embed_data.add_field(name="Region", value=str(server.region))
        embed_data.add_field(name="Total Users", value="{}".format(total_users))
        embed_data.add_field(name="Online Users", value="{}".format(online))
        embed_data.add_field(name="Text Channels", value=text_channels)
        embed_data.add_field(name="Voice Channels", value=voice_channels)
        embed_data.add_field(name="Existing Roles", value=len(server.roles))
        embed_data.add_field(name="Server Owner", value=str(server.owner))
        embed_data.add_field(name="Server ID: ", value=server.id)

        if server.icon_url:
            embed_data.set_author(name=server.name, url=server.icon_url)
            embed_data.set_thumbnail(url=server.icon_url)
        else:
            embed_data.set_author(name=server.name)

        try:
            await self.bot.say(embed=embed_data)
        except discord.HTTPException:
            await self.bot.say("Embed Links Permission Required")
        return

    @commands.group(pass_context=True)
    async def userinfo(self, context):
        server = context.message.server
        roles = [x.name for x in context.message.author.roles if x.name != "@everyone"]
        user_joined = context.message.author.joined_at.strftime("%d %b %Y %H:%M")
        user_created = context.message.author.created_at.strftime("%d %b %Y %H:%M")
        game = "{}".format(context.message.author.status)
        if context.message.author.game is None:
            pass
        elif context.message.author.game.url is None:
            game = "Playing {}".format(context.message.author.game)
        else:
            game = "Streaming: {} {}".format(context.message.author.game, context.message.author.game.url)
        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"

        embed_data = discord.Embed(description=game)
        embed_data.add_field(name="Account created at: ", value=user_created)
        embed_data.add_field(name="Joined this server at: ", value=user_joined)
        embed_data.add_field(name="Roles: ", value=roles, inline=False)
        embed_data.add_field(name="User ID: ", value=context.message.author.id)

        name = str(context.message.author)
        name = " ~ ".join((name, context.message.author.nick)) if context.message.author.nick else name

        if context.message.author.avatar_url:
            embed_data.set_author(name=name, url=context.message.author.avatar_url)
            embed_data.set_thumbnail(url=context.message.author.avatar_url)
        else:
            embed_data.set_author(name=name)

        try:
            await self.bot.say(embed=embed_data)
        except discord.HTTPException:
            await self.bot.say("Embed Links Permission Required")
        return

def setup(bot):
    bot.add_cog(Statistics(bot))
    

