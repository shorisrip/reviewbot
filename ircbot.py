#!/usr/bin/env python3
import datetime
import random
import irc.bot
import irc.strings
from irc.client import ip_quad_to_numstr
import re
from utils import write_to_destination
from random_replies import unknown_cmd, hello


class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = "#" + channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        print("Joined ", self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        review_list_regexp = r"(add[\s\S]*to[\s\S]*review\s*list|need[\s\S]review)"
        matches = re.search(review_list_regexp, e.arguments[0], re.IGNORECASE)
        if matches:
            patches_regex = r"https?://\S+"
            links_found = re.findall(patches_regex, e.arguments[0], re.IGNORECASE)
            for link in links_found:
                print(str(datetime.datetime.now()), " : ", link)
                # Send to hackmd
                result = write_to_destination(link)
                if result == None:
                    result = "I could not add the review to Review List"
                self.connection.privmsg(self.channel, result)

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = sorted(chobj.users())
                c.notice(nick, "Users: " + ", ".join(users))
                opers = sorted(chobj.opers())
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = sorted(chobj.voiced())
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp(
                "DCC",
                nick,
                "CHAT chat %s %d"
                % (ip_quad_to_numstr(dcc.localaddress), dcc.localport),
            )
        elif any(s in cmd.lower() for s in hello):
            c.privmsg(nick, "Hi, I am reviewbot. "
                      "Type something like this: " +
                      "'Pls add to review list <your_patch>' " +
                      "on the channel and I'll add it to the Review list. " +
                      "Or simply msg me something lke: " +
                      "'review list <your_patch>'.")
        # Remove code duplication
        elif re.search(r"review\s*list", cmd, re.IGNORECASE):
            patches_regex = r"https?://\S+"
            links_found = re.findall(patches_regex, e.arguments[0],
                                     re.IGNORECASE)
            for link in links_found:
                print(link)
                # Send to hackmd
                result = write_to_destination(link)
                if result == None:
                    result = "I could not add the review to Review List"
                c.privmsg(nick, result)
        else:
            rand_index = random.randint(0, len(unknown_cmd)-1)
            print("rand_index: ", rand_index)
            c.notice(nick, unknown_cmd[rand_index])


def main():
    import sys

    if len(sys.argv) != 4:
        print("Usage: testbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = TestBot(channel, nickname, server, port)
    bot.start()


if __name__ == "__main__":
    main()