import functools
import asyncio

from discord.ext import commands
from random import choice
from imgurpython import ImgurClient

__author__ = "Some idiot with a keyboard"
__version__ = "0.0.0.0.0.0.0.1"

class Imgur():

    imgur_client = ImgurClient('ad3227fae77dfb4', 'd8bdd43b496c945fd88858ebff4115088db6ebeb')

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def imgur(self, context, search_term:str=None):
        """ Retrieve a random image from Imgur with or without keyword search. """
        if search_term is None:
            todo = functools.partial(self.imgur_client.gallery_random, page=0) # Random entry from main gallery
        else:
            search_term = context.message.content.replace("!imgur ", "", 1)
            todo = functools.partial(self.imgur_client.gallery_search, search_term) # Search for results with keyword

        todo = self.bot.loop.run_in_executor(None, todo) # Perform imgur search

        try:
            results = await asyncio.wait_for(todo, timeout=20) # Too short? Long?
        except asyncio.TimeoutError:
            await self.bot.say("Timeout Error") # Took too long for server response
        else:
            if results: # We got a response
                img = results[0] # choice(results)
                link = img.gifv if hasattr(img, "gifv") else img.link # Check for gifv status
                await self.bot.say(link) # Bot posts the imgur link (Can we post an embedded image?? w/o link??)
            else:
                await self.bot.say("No Results for %s" % search_term) # Someone done goof'd
        return


def setup(bot):
    bot.add_cog(Imgur(bot))
    

