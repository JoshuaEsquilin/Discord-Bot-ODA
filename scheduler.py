import asyncio
import yolodb

from datetime import datetime, timedelta
from discord.user import User
from uuid import uuid4
from discord.ext import commands

__author__ = "Some idiot with a keyboard"
__version__ = "0.0.0.0.0.0.0.1"

class Notification_object():
    def __init__(self, uid, notification_message, notification_time, user_id):
        self.uid = uid
        self.notification_message = notification_message
        self.notification_time = notification_time
        self.user = User(id=user_id)

    def to_dict(self):
        return {
            'uid':self.uid,
            'notification_message':self.notification_message,
            'notification_time': self.notification_time,
            'user_id':self.user.id
            }

    @classmethod
    def from_dict(cls, **info): # use 'cls' in place of 'self'
        return cls(**info)      # Why? idk...

class Scheduler():
    
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.loop = asyncio.get_event_loop()
        self.running_tasks = dict()

    async def start(self):
        """ Initializes the DB """
        self.db = await yolodb.load('notifications.db', loop=self.loop)
        for user in self.db.all.values():
            for notification in user.values():
                self.queue_notification(Notification_object.from_dict(**notification))

    def queue_notification(self, new_notification):
        timed_delay = (new_notification.notification_time - datetime.now().timestamp())

        def send_notification():
            asyncio.ensure_future(self.bot.send_message(new_notification.user, new_notification.notification_message), loop=self.loop)
            self.pop_notification(new_notification.user.id, new_notification.uid)

        self.running_tasks[new_notification.uid] = self.loop.call_later(timed_delay, send_notification) # Tasks for days
        return

    def add_notification(self, notification_message:str, notification_time:int, user_id:str):
        uid = str(uuid4())[:4]                          # Make newly generate id only 8 characters long
        notifications = self.db.get(user_id, {})        # pull notifications from the db
        new_notification = Notification_object(uid, notification_message, notification_time, user_id)
        notifications[uid] = new_notification.to_dict() # convert
        self.db[user_id] = notifications                # send updated notifications to the db
        self.queue_notification(new_notification)       # prepare the new notification 
        return

    def get_notifications(self, user_id): # get all notifications
        return self.db.get(user_id, {})

    def pop_notification(self, user_id, notification_id):
        notifications = self.db.get(user_id, {})
        del notifications[notification_id] # remove the specified entry
        if not notifications:    # If the DB entry is empty...
            self.db.pop(user_id) # Remove user from DB!
        else: # User still has items in their DB entry
            self.db[user_id] = notifications
        if notification_id in self.running_tasks:        # If the notification is still queued up...
            self.running_tasks[notification_id].cancel() # cancel it, then...
            del self.running_tasks[notification_id]      # delete it!
        return

    def get_time_string(self, seconds): # Convert into a string time format, 00:00:00
        hours = seconds / 3600
        minutes = (seconds / 60) % 60
        seconds = seconds % 60
        return '%0.2d:%02d:%02d' % (hours, minutes, seconds)

    @commands.group(pass_context=True)
    async def notification(self, context, days:int=None, hours:int=None, minutes:int=None, description:str=None):
        """ Creates a new Notification for the user
       format: !notification X Y Z Description
       where X = days, Y = hours, Z = minutes."""
        if self.db == None:
            await self.start() # Initiate DB, because it's not initialized yet

        notify_time = {} # Technicially a dict
        if days:
            notify_time['days'] = days
        if hours:
            notify_time['hours'] = hours
        if minutes:
            notify_time['minutes'] = minutes
        notify_time['seconds'] = 0
        
        time_since_epoch = (datetime.now() + timedelta(**notify_time)).timestamp() # time since epoch
        
        if description:
            notification_message = context.message.content[20:] # If the user gave us something to notify him/her about
        else:
            notification_message = 'You didn\'t tell me *why* to notify you, but here it is. ¯\\_(ツ)_/¯' # Default message

        self.add_notification(notification_message, time_since_epoch, context.message.author.id)

        return await self.bot.say('Notification Stored') # Confirm notification status

    @commands.group(pass_context=True)
    async def notification_list(self, context):
        """ Lists the user's notifications """
        if self.db == None:
            await self.start() # Initiate DB, because it's not initialized yet

        notifications = self.get_notifications(context.message.author.id)
        if not notifications:
            return await self.bot.send_message(context.message.author, 'You have no notifications at this time.')
        else:
            notifications_list_str = ''
            for notification in notifications.values():
                time_until = notification['notification_time'] - int(datetime.now().timestamp()) # Time until notification
                notifications_list_str += '%s %s in %s\n' % (notification['uid'], notification['notification_message'], self.get_time_string(time_until))
            return await self.bot.send_message(context.message.author, notifications_list_str) # Full list of notifications
        return

    @commands.group(pass_context=True)
    async def notification_remove(self, context, uid):
        """ Delete the selected notification 
        format: !notification_remove ####
        Where #### is the unique ID of that 
        notification in your notification list."""
        if self.db == None:
            await self.start() # Initiate DB, because it's not initialized yet
        if uid in self.running_tasks:
            self.pop_notification(context.message.author.id, uid)
            return await self.bot.say('Notification Removed!') # confirm removal
        else:
            return await self.bot.say('That notification does not exist.') # Someone done goof'd

def setup(bot):
    bot.add_cog(Scheduler(bot))
    

