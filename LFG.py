'''
Created on Apr 11, 2017

@author: Joshua Esquilin
'''

import discord
from discord.ext import commands
from datetime import datetime, timezone

lfgStorage = []
lfgJoinStorage = []
lfgList_max_size = 100 
format = "%a %b %d %H:%M:%S"

class LFGBuilder():
        
        def __init__(self, message, game, maxPlayers, playersJoined, note='' ):

            self.message = message
            self.game = game
            self.maxPlayers = maxPlayers
            self.playersJoined = playersJoined
            self.note = note
            
class LFGJoinBuilder():
        
        def __init__(self, joiner, maker):

            self.joiner = joiner
            self.lfgMaker = maker
    
    
class LFG():
    
    def __init__(self, bot):
            
            self.bot = bot
            
    @commands.command(pass_context=True)
    async def lfg(self, ctx, game : str, maxPlayers : int, playersJoined : int, note=''):
            """ Make a Looking For Group request. """
            
            global lfgStorage
            self.clear(old=True, dupe_author=ctx.message.author.id) # Updates the LFG Storage, clearing 6 hour old requests, and not allowing duplicates from the same maker
            lfgStorage.append(LFGBuilder(ctx.message, game, maxPlayers, playersJoined, note[:1000]))
            s = str(ctx.message.author.name) + ', your LFG request has been added to the list and is active for 6 hours unless you clear it sooner.'
            await self.bot.say(s)
                  
            
    @commands.command(pass_context=True)
    async def lfglist(self, ctx):
            """ Request a list of the current LFGs. """
            
            em = discord.Embed() # Starts the setup for an embed
            em.title = 'LFG List of Entries'
            em.description = 'Players looking for a group  = ' + str(len(lfgStorage))
            em.set_author(name='{0}'.format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
            em.timestamp = ctx.message.timestamp
          
            self.clear(old=True)
            
            for e in lfgStorage: # Makes a new field for every LFG entry
                em.add_field(name='Group ' + str(lfgStorage.index(e)+1), value= ' '.join((e.message.author.name, '~', str(self.utc_to_local(e.message.timestamp).strftime(format)),'~', e.game, '~', str(e.maxPlayers), ' Max Players', '~', str(e.playersJoined), ' Current Players', '~', e.note)))
            if len(lfgStorage) > 10: # Send large lists through
                await self.bot.send_message(ctx.message.author, embed=em)
            else: # message to channel small lists
                await self.bot.say(embed=em)
     
    @commands.command(pass_context=True)          
    async def lfgjoin(self, ctx, player : str):
        """ Joins a current specified LFG. """
        global lfgStorage
        global lfgJoinStorage
        
        
        for h in lfgStorage: # Error checking
            if h.playersJoined is h.maxPlayers:
                await self.bot.say('The group is full')
                return
            if h.message.author.name is ctx.message.author.name:
                await self.bot.say('You have to clear the group you created before joining a different one.  You can clear it with (!lfgclear ReplaceWithLFGMaker)')
        
        if not lfgStorage:
            await self.bot.say('No LFGs exist right now.  You can make one with (!lfg Game MaxPlayers CurrentPlayers Note)')          
            return 
        
        for i in lfgJoinStorage:
            if i.joiner == ctx.message.author.name:
                await self.bot.say('You cannot join a LFG if you are in one already.  You can leave the one you are in with the command (!lfgleave ReplaceWithLFGMaker)')
            return
           
        
        for e in lfgStorage: # Keeps track of who joined a group
            if e.message.author.name == player:
                for i in lfgJoinStorage:
                    if i.joiner != ctx.message.author.name:
                        lfgJoinStorage.append(LFGJoinBuilder(ctx.message.author.name ,e.message.author.name))
                        e.playersJoined = e.playersJoined  + 1
                        s = ctx.message.author.name + ' has joined your LFG!' 
                        await self.bot.send_message(e.message.author, s) 
                        await self.bot.say(e.message.author.name + ' has been notified with a message')
                else:
                    lfgJoinStorage.append(LFGJoinBuilder(ctx.message.author.name ,e.message.author.name))
                    e.playersJoined = e.playersJoined  + 1
                    s = ctx.message.author.name + ' has joined your LFG!' 
                    await self.bot.send_message(e.message.author, s) 
                    await self.bot.say(e.message.author.name + ' has been notified with a message')
            if e.message.author.name != player:
                await self.bot.say('Please type the correct LFG leader with the command (!lfgjoin ReplaceWithLFGMaker)')
                return
        
    @commands.command(pass_context=True)          
    async def lfgleave(self, ctx, player : str):
        """ Leaves a current specified LFG. """
        
        global lfgStorage
        global lfgJoinStorage
        
        if not lfgStorage: # Error checking
            await self.bot.say('No LFGs exist right now.  You can make one with (!lfg Game MaxPlayers CurrentPlayers Note)')          
            return 
        if not lfgJoinStorage:
            await self.bot.say('You cannot leave a LFG if you have not joined one.  You can join one with the command (!lfgJoin ReplaceWithLFGMaker)')
            return
        for i in lfgJoinStorage:
            if i.joiner != ctx.message.author.name:
                await self.bot.say('You cannot leave a LFG if you have not joined one.  You can join one with the command (!lfgJoin ReplaceWithLFGMaker)')
                return
    
        for e in lfgStorage: 
            if e.message.author.name == player: 
                for i in lfgJoinStorage:
                    lfgJoinStorage.remove(i)
                    e.playersJoined = e.playersJoined  - 1
                    s = ctx.message.author.name + ' has left your LFG!' 
                    await self.bot.send_message(e.message.author, s)
                    await self.bot.say(ctx.message.author.name + ' has left ' + e.message.author.name + "'s " + 'game')
            if e.message.author.name != player:
                await self.bot.say('Please type the correct LFG leader with the command (!lfgleave ReplaceWithLFGMaker)')
                return
         
    @commands.command(pass_context=True)          
    async def lfgclear(self, ctx): 
        """ Clear your Looking For Group request. """
        
        self.clear(old=True, duplicate_author=ctx.message.author.id)
        s = ctx.message.author.name + ', your LFG requests and all old requests (Over 6 hours old) have been removed.'
        await self.bot.say(s)
            
    def utc_to_local(self, utc_dt):
        
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None) # Converts UTC to local time
            
    def clear(self, old=False, dup_author=''): # Clears a LFG request at the sake of maker and it automatically clears 6 hour old entries.
      
        global lfgStorage
        lfgStorage_new = []
        for e in lfgStorage:
            td = datetime.utcnow() - e.message.timestamp
            if old and td.total_seconds() > 21600:
                continue
            if len(dup_author) > 0 and dup_author == e.message.author.id:
                continue
            lfgStorage_new.append(e)
        lfgStorage = lfgStorage_new
      
def setup(bot):
    bot.add_cog(LFG(bot))

