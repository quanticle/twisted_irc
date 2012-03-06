from twisted.words.protocols import irc
from twisted.internet.protocol import Factory
from twisted .internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from datetime import datetime
import re

from weather import Weather

class HelloBot(irc.IRCClient):
    def __init__(self, factory, weather_provider):
        self.nickname = factory.bot_nickname
        self.channel = factory.bot_channel
        self.weather_provider = weather_provider
        self.commands = ['hello', 'time', 'weather']
        
    def signedOn(self):
        self.setNick(self.nickname)
        self.join(self.channel)
        print "Bot online with nickname: %s" % (self.nickname,) #DEBUG    

    def privmsg(self, sender, recipient, msg):
        print "Sender: %s\nRecipient: %s\nMessage received: %s\n" % (sender, recipient, msg) #DEBUG
        if recipient == self.nickname or (recipient == self.channel and msg.startswith(self.nickname)):
            command = self.parseCommand(msg)
            if command:
                self.sendReply(sender, self.executeCommand(command))
            else:
                self.sendReply(sender, "Invalid command")

    def parseNickname(self, sender):
        """ Parses the nickname from the nickname!hostmask string that the server sends as the sender"""
        return sender[:sender.find("!")]

    def parseCommand(self, command_str):
        command_regexp = "%s.*\\s*(?P<command> .*)" % (self.nickname,)
        match = re.match(command_regexp, command_str)
        if match:
            given_command = match.group("command").strip().lower()
            for accepted_command in self.commands:
                if given_command == accepted_command:
                    return accepted_command
            return None
        else: #We should never get here, because of the filtering done in the privmsg event handler
            return None

    def executeCommand(self, command):
        command_method = getattr(self, command)
        return command_method()

    def sendReply(self, recipient, message):
        self.msg(self.parseNickname(recipient), message)
       
    def hello(self):
        """This is a basic command that just returns \"hello there\""""
        return "Hello there."

    def time(self):
        return str(datetime.now())
    
    def weather(self):
        f, c, cond = self.weather_provider.get_weather_data()
        return str("Temp: %s (%s C); Condtions: %s" % (f, c, cond))
            
    
class BotFactory(Factory):
    def __init__(self, nickname, channel):
        self.bot_nickname = nickname
        self.bot_channel = channel
        
    def buildProtocol(self, addr):
        weather_provider = Weather("http://www.google.com/ig/api?weather=Minneapolis")
        return HelloBot(self, weather_provider)

if __name__ == "__main__":
    endpoint = TCP4ClientEndpoint(reactor, "chat.freenode.net", 6667)
    d = endpoint.connect(BotFactory("quanticle_bot", "#PyMNtos"))
    reactor.run()

        

