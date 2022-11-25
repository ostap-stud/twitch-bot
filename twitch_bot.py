"""
	COPYRIGHT INFORMATION
	---------------------

Some code in this file is licensed under the Apache License, Version 2.0.
    http://aws.amazon.com/apache2.0/


"""

from irc.bot import SingleServerIRCBot
from twitchAPI.twitch import Twitch

from lib import db, cmds, react, automod

# Вписати ім'я власного бота
NAME = "polytechBot"
# Вписати ім'я Twitch-каналу
OWNER = "cuckooxa"
# Вписати власні Client_id та Secret code
twitch = Twitch("7q09m50dd78wj781y5fer755vy6vx3", "lt9r6tb6pevsn4xfdwwk1jfqwb92mc")


class Bot(SingleServerIRCBot):
	def __init__(self):
		self.HOST = "irc.chat.twitch.tv"
		self.PORT = 6667
		self.USERNAME = NAME.lower()
		# Client_id
		self.CLIENT_ID = "7q09m50dd78wj781y5fer755vy6vx3"
		# Token
		self.TOKEN = "9akibsnz380vld0udu4p7lkgm5x53g"
		self.CHANNEL = f"#{OWNER}"

		user_info = twitch.get_users(logins=[f'{NAME}'])
		user_id = user_info['data'][0]['id']

		super().__init__([(self.HOST, self.PORT, f"oauth:{self.TOKEN}")], self.USERNAME, self.USERNAME)

	def on_welcome(self, cxn, event):
		for req in ("membership", "tags", "commands"):
			cxn.cap("REQ", f":twitch.tv/{req}")

		cxn.join(self.CHANNEL)
		db.build()
		self.send_message("Now online.")

	@db.with_commit
	def on_pubmsg(self, cxn, event):
		tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
		user = {"name": tags["display-name"], "id": tags["user-id"]}
		message = event.arguments[0]

		react.add_user(bot, user)

		if user["name"] != NAME and automod.clear(bot, user, message):
			react.process(bot, user, message)
			cmds.process(bot, user, message)

	def send_message(self, message):
		self.connection.privmsg(self.CHANNEL, message)


if __name__ == "__main__":
	bot = Bot()
	bot.start()