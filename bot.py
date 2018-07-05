'''
Created on Apr 30, 2017

@author: Ed
'''
from discord.ext import commands

description = """I am a bot"""
cmd_prefix = '!'

#startup_extensions = ["LFG","Template", "Miscellaneous","ServerTime"]
startup_extensions = ["RevisedPollandTime"]
bot = commands.Bot(command_prefix=cmd_prefix, description=description)

@bot.event
async def on_ready():
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')
        
@bot.event
async def on_resumed():
    print('resumed...')

@bot.event
async def on_message(message):
        
        if message.author == bot.user:
            return
    
        if message.content.startswith('!hello'):
            msg = 'Hello {0.author.mention}'.format(message)
            await bot.send_message(message.channel, msg)
            
        await bot.process_commands(message)
        
        
@bot.command()
async def load(extension_name : str):
    """Loads the extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))
    
@bot.command()
async def unload(extension_name : str):
    """Unloads the extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))
    
if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    
bot.run('PUT YOUR TOKEN HERE')

