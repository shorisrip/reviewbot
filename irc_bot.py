from irc_class import *
import os
import random

## IRC Config

config = {
"ircbot_server": "irc.oftc.net",
"ircbot_port": 6697,
"channel": ["reviewbot"],
"ircbot_nick":"reviewbot",
"ircbot_pass": "reviewbot",
"ircbot_server_password": "reviewbot"
}
# irc = IRC()
# irc.connect(server, port, channel, botnick, botpass, botnickpass)

# while True:
#     text = irc.get_response()
#     print(text)
#
#     if "PRIVMSG" in text and channel in text and "hello" in text:
#         irc.send(channel, "Hello!")


bot = IRCBot(
            config["channel"],
            config=config)
bot.start()
# bot.send(config["channel"], "Hello")