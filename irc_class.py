import socket
import sys
import time
import irc.bot
import textwrap



class IRCBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channels, config):
        super(IRCBot, self).__init__(
            [(config["ircbot_server"],
              int(config["ircbot_port"]),
              config["ircbot_server_password"])],
            config["ircbot_nick"],
            config["ircbot_nick"])
        self.channel_list = channels
        self.nickname = config["ircbot_nick"]
        self.password = config["ircbot_pass"]

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
        c.privmsg("nickserv", "identify %s " % self.password)
        c.privmsg("nickserv", "ghost %s %s" % (self.nickname, self.password))
        c.privmsg("nickserv", "release %s %s" % (self.nickname, self.password))
        time.sleep(1)
        c.nick(self.nickname)

    def on_welcome(self, c, e):
        c.privmsg("nickserv", "identify %s " % self.password)
        for channel in self.channel_list:
            c.join(channel)
            time.sleep(0.5)

    def send(self, channel, msg):
        # Cheap way to attempt to send fewer than 512 bytes at a time.
        for chunk in textwrap.wrap(msg, 400):
            self.connection.privmsg(channel, chunk)
            time.sleep(0.5)










class IRC:
    irc = socket.socket()

    def __init__(self):
        # Define the socket
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, channel, msg):
        # Transfer data
        self.irc.send(bytes("PRIVMSG " + channel + " " + msg + "\n", "UTF-8"))

    def connect(self, server, port, channel, botnick, botpass, botnickpass):
        # Connect to the server
        print("Connecting to: " + server)
        self.irc.connect((server, port))

        # Perform user authentication
        # self.irc.send(bytes(
        #     "USER " + botnick + " " + botnick + " " + botnick + " :python\n",
        #     "UTF-8"))
        self.irc.send(bytes("/NICK " + botnick + "\n", "UTF-8"))
        self.irc.send(
            bytes("/NICKSERV IDENTIFY " + botnickpass + " " + botpass + "\n",
                  "UTF-8"))
        time.sleep(5)

        # join the channel
        self.irc.send(bytes("/JOIN " + channel + "\n", "UTF-8"))

    def get_response(self):
        time.sleep(1)
        # Get the response
        resp = self.irc.recv(2040).decode("UTF-8")

        if resp.find('PING') != -1:
            self.irc.send(
                bytes('PONG ' + resp.split().decode("UTF-8")[1] + '\r\n',
                      "UTF-8"))

        return resp