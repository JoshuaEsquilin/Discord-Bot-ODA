'''
Created on Apr 25, 2017

@author: Joshua Esquilin
'''
import discord
import random
import re
from discord.ext import commands
from random import randint
from random import choice 

class Miscellaneous():
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def coinflip(self, ctx):
        """ Flips a coin and results in heads or tails. """
        
        await self.bot.say(choice([" I got heads!", " I got tails!"]))

    @commands.command(pass_context=True)
    async def roll(self, ctx, number : float = 20):
        """ Rolls a number from 1 to the number chosen or to 20 by default. """
        
        number = int(number)
        if number > 1:
            n = randint(1, number)
            await self.bot.say("{} :game_die: {} :game_die:".format(ctx.message.author.mention, n))
        else:
            await self.bot.say("Please pick a number higher than 1.".format(ctx.message.author.mention))
            
    @commands.command(pass_context=True, aliases=['random', 'choose'])
    async def pick(self, ctx, *args):
        """ Picks between multiple choices. """
        
        if not args:
            await self.bot.say('\N{CONFUSED FACE} I can\'t choose from nothing.')
        await self.bot.say(random.choice(args))
        
    @commands.command(pass_context=True, aliases=['jumbo', 'big'])
    async def large(self, ctx, emoji: str):
        """ View a channel made emoji at a larger resolution. """

        match = re.match(r'<:([a-z0-9A-Z_-]+):([0-9]+)>', emoji)
        if not match:
            await self.bot.say('This is not a custom emoji.')
            return

        emoji_id = match.groups()[1] # Retrieve the emoji id
        emoji_cdn = 'https://discordapp.com/api/emojis/{}.png'

        eEmbed = discord.Embed()
        eEmbed.set_image(url=emoji_cdn.format(emoji_id))

        await self.bot.say(embed=eEmbed)
                
def setup(bot):
    bot.add_cog(Miscellaneous(bot))