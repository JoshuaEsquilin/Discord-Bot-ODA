'''
Created on Apr 30, 2017

@author: Eduardo
'''
import discord
from discord.ext import commands
import time
import asyncio

# Settings is how long poll duration will go on for. It is 5 minutes for a demonstration.
checker = {"poll_time" : 300}

# The Main cog class that is responsible for the commands of the server time and the poll.
class RevisedPollandTime:

    def __init__(self, bot):
        self.bot = bot
        self.poll_groups = [] # Creates a place to store the current poll

    # Obtains the current time based on the bot's location.
    latesttime = time.strftime('%I:%M%p %Z on %b %d, %Y')

    # Displays the current servertime of the bot to the channel requested.
    @commands.group(pass_context=True)
    async def servertime(self, context):
        """ Displays the current server time with !servertime """
        latesttime = time.strftime('%I:%M%p %Z on %b %d, %Y')
        return await self.bot.say(latesttime)

    #Primary poll command that starts a poll in a Discord Channel and is able to stop early before the time limit.
    @commands.command(pass_context=True, no_pm=True)
    async def poll(self, context, *text):
        """ Create a poll with '!poll question;choice1;choice2;' ect. '!poll stop' to end the poll early."""
        message = context.message
        if len(text) == 1:
            if text[0].lower() == "stop": #Detects when a message says '!poll stop', and stops the poll if they are the creator/admin
                await self.stoppoll(message)
                return
        # Checks to see if the message was sent for the bot, or for the entire channel.
        if not self.ReceivePollFromSource(message):
            check = " ".join(text).lower()
            if "@everyone" in check: # Disregards if the message was for the entire channel.
                return
            n = CreatedPoll(message, self)
            if n.valid:
                self.poll_groups.append(n)
                await n.start()
            else:
                await self.bot.say("The format to start a poll is: !poll question;choice1;choice2")
        # Respond if poll is already ongoing.
        else:
            await self.bot.say("A poll is already going on in this channel now.")

    # Stops the current running poll
    async def stoppoll(self, message):
        if self.ReceivePollFromSource(message):
            n = self.ReceivePollFromSource(message)
            if n.author == message.author.id: # If the creator or admin requests the poll to be stopped, have it stopped.
                await self.ReceivePollFromSource(message).stopPoll()
            else:
                await self.bot.say("The only ones that can end the poll are the admins and the creator.") # Get permission from creator or admin
        # A poll must be started before the command can be used
        else:
            await self.bot.say("There are no polls going on in this channel.")
    
    # Returns the poll to the channel it was requested in.
    def ReceivePollFromSource(self, message):
        for poll in self.poll_groups:
            if poll.channel == message.channel:
                return poll
        return False

    # Checks the votes from users for the poll
    async def check_poll_votes(self, message):
        if message.author.id != self.bot.user.id:
            if self.ReceivePollFromSource(message):
                    self.ReceivePollFromSource(message).confirmInput(message)
        else:
            return
    
    #Test method to test cogs and responses, in case a certain method isn't working.
    #@commands.group(pass_context=True)
    #async def test2(self, context):
        #""" Test number 2. """
        #await self.bot.say("Nothing is true...")

# Class that initializes and runs the poll behind the scenes.
class CreatedPoll():
    #Initializes the channel, creator, users, and the ongoing poll that is being created.
    def __init__(self, message, main):
        self.channel = message.channel
        self.author = message.author.id
        self.client = main.bot
        self.poll_groups = main.poll_groups

        # The message content starts at this location
        msg = message.content[6:]
        # Splits the contents of the message depending on ';'
        msg = msg.split(";")
        # There should be one question and at least 2 choices, this checks the length
        if len(msg) < 2:
            self.valid = False
            return None
        # If the msg is longer than 2, it is confirmed to be valid.
        else:
            self.valid = True
        # Creates a spot to respond if someone has already voted.
        self.already_voted = []
        # Store the question to be saved for displaying the results.
        self.question = msg[0]
        msg.remove(self.question)
        self.answers = {}   # Spot to store the answers given.
        i = 1   # Used to increment later.
        for answer in msg:
            self.answers[i] = {"Answer" : answer, "Votes" : 0} # Displays the number of votes received.
            i += 1 #Increments the number of responses.

    # This will be the bot response when a new poll has begun.
    async def start(self):
        msg = "A new poll has begun.\n\n{}\n\n".format(self.question)
        # Displays the items in the poll list
        for id, data in self.answers.items():
            msg += "{}. *{}*\n".format(id, data["Answer"])
        msg += "\nPlease insert a number to vote."
        await self.client.send_message(self.channel, msg)
        # Waits for the poll time to expire, then ends the poll.
        await asyncio.sleep(checker["poll_time"])
        if self.valid:
            await self.stopPoll() # The poll stops.

    async def stopPoll(self):
        self.valid = False
        msg = "The poll has now ended.\n\n{}\n\n".format(self.question) # The bot concludes the poll.
        # The bot displays the results of the poll.
        for data in self.answers.values():
            msg += "*{}* - {} votes\n".format(data["Answer"], str(data["Votes"]))
        await self.client.send_message(self.channel, msg)
        self.poll_groups.remove(self) # Removes the stored poll.
    
    # Checks the input of the users to see what answer the bot is given to note down.
    def confirmInput(self, message):
        try:
            i = int(message.content)
            if i in self.answers.keys(): # If the responses match the keys...
                if message.author.id not in self.already_voted: # And if the responders have not already voted...
                    data = self.answers[i]
                    data["Votes"] += 1 # Increment number of poll votes.
                    self.answers[i] = data
                    self.already_voted.append(message.author.id)
        except ValueError:
            pass

# Creates the cog for the commands servertime and poll
def setup(bot):
    bot.add_cog(RevisedPollandTime(bot))

