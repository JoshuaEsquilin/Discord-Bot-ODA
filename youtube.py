import discord

from discord.ext import commands

__author__ = "Some idiot with a keyboard"
__version__ = "0.0.0.0.0.0.0.1"

class Youtube():
    
    yt_volume = 0.50

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context = True)
    async def disconnect_voice(self, context):
        """ Disconnects the current voice client on the server. """
        await discord.utils.get(self.bot.voice_clients, server = context.message.server).disconnect() # Force disconnect from current channel (voice)
        return

    @commands.group(pass_context=True)
    async def youtube(self, context, link:str, requested_channel:str):
        """ Stream audio from a YouTube video link into the specified voice channel """
        if self.bot.is_voice_connected(context.message.server):
            await discord.utils.get(self.bot.voice_clients, server = context.message.server).disconnect() # If in a voice channel, leave it
        
        if link == None:
            await self.bot.say('Give me a YouTube link next time!') # No link, no play
            return
        elif requested_channel == None:
            await self.bot.say('Tell me what Voice Channel to join next time!') # No channel, no play
            return
        else:
            voice_channel = discord.utils.get(context.message.server.channels, name = requested_channel)
            if voice_channel == None:
                await self.bot.say('I don\'t know what this channel is: %s' % requested_channel) # Must be an existing channel
                return
            if voice_channel.type != discord.ChannelType.voice:
                await self.bot.say('I can only spread YouTube joy in a Voice Channel!') # Must be a Voice Channel
                return

        voice_client = await self.bot.join_voice_channel(voice_channel) # Join voice Channel

        yt_player = await voice_client.create_ytdl_player(link, after = lambda: self.bot.loop.create_task(voice_client.disconnect())) # yt_player task
        yt_player.volume = self.yt_volume

        yt_player.start() # Play the audio
        return


def setup(bot):
    bot.add_cog(Youtube(bot))
    

