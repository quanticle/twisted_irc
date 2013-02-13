from twisted.words.protocols import irc
from twisted.internet.protocol import Factory
from twisted .internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from datetime import datetime
import re
import json
import bot_config

from weather import Weather

class HelloBot(irc.IRCClient):
    def __init__(self, factory, weather_provider):
        self.nickname = factory.bot_nickname
        self.channel = factory.bot_channel
        self.weather_provider = weather_provider
        language_file = open("language_codes.json", 'r')
        self.language_cache = json.load(language_file)
        language_file.close()
        self.commands = ['hello', 'time', 'weather', 'language']
        
    def signedOn(self):
        self.setNick(self.nickname)
        self.join(self.channel)
        print "Bot online with nickname: %s" % (self.nickname,) #DEBUG    

    def privmsg(self, sender, recipient, msg):
        print "Sender: %s\nRecipient: %s\nMessage received: %s\n" % (sender, recipient, msg) #DEBUG
        command = None
        if recipient == self.nickname:
            command, args = self.parseCommand(msg, True)
            if command:
                self.sendReply(self.parseNickname(sender), self.executeCommand(command, args))
            else:
                self.sendReply(self.parseNickname(sender), "Invalid command")
        elif (recipient == self.channel and msg.startswith(self.nickname)):
            command, args = self.parseCommand(msg, False)
            if command:
                self.sendReply(recipient, "%s: %s" % (self.parseNickname(sender), self.executeCommand(command, args)))
        else:
            #Not a command, so parse for wikilinks
            links = self.parseWikilinks(msg)
            if len(links) > 0:
                self.sendReply(recipient, " ".join(links))

    def parseNickname(self, sender):
        """ Parses the nickname from the nickname!hostmask string that the server sends as the sender"""
        return sender[:sender.find("!")]

    def parseCommand(self, command_str, pm):
        print "Command string: %s, PM: %s" % (command_str, str(pm)) #DEBUG
        if pm:
            command_regexp = r'(?P<command>\S+)\s*(?P<args>.*)' 
            print "Command regexp: %s" % command_regexp #DEBUG
        else:
            command_regexp = "%s.?\\s*(?P<command>\\S+)\\s*(?P<args>.*)" % self.nickname
            print "Command regexp %s" % command_regexp #DEBUG
        match = re.match(command_regexp, command_str)
        if match:
            given_command = match.group("command").strip().lower()
            print "Command %s" % given_command #DEBUG
            for accepted_command in self.commands:
                if given_command == accepted_command:
                    args = match.group("args")
                    print "Args: %s" % str(args)
                    if args:
                        args = args.strip()
                    return accepted_command, args
            return ("meow", None)
        else: #We should never get here, because of the filtering done in the privmsg event handler
            print "We should never get here!" #DEBUG
            return (None, None)

    def executeCommand(self, command, args):
        command_method = getattr(self, command)
        return command_method(args)

    def sendReply(self, recipient, message):
        self.msg(recipient, str(message))
       
    def hello(self, *args):
        """This is a basic command that just returns \"hello there\""""
        return "Hello there."

    def time(self, *args):
        return str(datetime.now())
    
    def weather(self, query, *args):
        if query:
            weather_string = self.weather_provider.get_weather(query)
            return weather_string
        else:
            return "You must provide a city name or zip code"

    def language(self, language_code, *args):
        if language_code in self.language_cache:
            return "%s is %s" % (language_code, self.language_cache[language_code]['name'])
        else:
            return "I do not know which language %s is." % language_code
    
    def meow(self, *args):
        return "meooooowww"

    def parseWikilinks(self, msg):
        wikilink_pattern = r'\[\[(?P<link_text>[^\]|]+[^ \]|])[\]| ]'
        wikilinks = re.findall(wikilink_pattern, msg)
        links = ["http://en.wikipedia.org/wiki/" + wikilink.replace(" ", "_") for wikilink in wikilinks]
        return links
            
            
    
class BotFactory(Factory):
    def __init__(self, nickname, channel):
        self.bot_nickname = nickname
        self.bot_channel = channel
        
    def buildProtocol(self, addr):
        weather_provider = Weather()
        return HelloBot(self, weather_provider)

if __name__ == "__main__":
    endpoint = TCP4ClientEndpoint(reactor, "chat.freenode.net", 6667)
    d = endpoint.connect(BotFactory(bot_config.bot_name, bot_config.bot_channel))
    reactor.run()
    
        

