from twisted.words.protocols import irc
from twisted.internet.protocol import Factory
from twisted .internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from datetime import datetime
import re
import json
import bot_config
import requests
import codecs
from xml.dom import minidom

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
        self.inlineRegexes = {r'\[\[(?P<data>[^\]|]+[^ \]|])[\]| ]': "wikilink",
                              r'watch\S+v=(?P<data>[^/&]+)': "youtubeLink",
                              r'youtu\.be/(?P<data>[^/?&]+)': "youtubeLink"}
        
    def signedOn(self):
        self.setNick(self.nickname)
        self.join(self.channel)
        print "Bot online with nickname: %s" % (self.nickname,) #DEBUG    

    def privmsg(self, sender, recipient, msg):
        if recipient == self.nickname:
            replyTo = self.parseNickname(sender)
            commandResults = self.parseDirectCommand(msg)
            self.sendReply(replyTo, commandResults)
        elif msg.startswith(self.nickname):
            replyTo = self.channel
            commandResults = self.parseDirectCommand(msg, addressTo=self.parseNickname(sender))
            self.sendReply(replyTo, commandResults)
        else:
            replyTo = self.channel
            commandResults = self.parseInlineCommand(msg)
            for result in commandResults:
                self.sendReply(replyTo, result)
    
    def parseDirectCommand(self, msg, addressTo=None):
        commandRegex = r'(%s.\s+)?(?P<command>\S+)\s*(?P<args>.*)' % self.nickname
        match = re.match(commandRegex, msg)
        if match:
            commandOutput = ""
            givenCommand = match.group("command").strip()
            acceptedCommand = [availableCommand for availableCommand in self.commands if availableCommand == givenCommand]
            if acceptedCommand:
                args = match.group("args")
                commandOutput = self.executeCommand(acceptedCommand[0], args)
            else:
                commandOutput = self.executeCommand("meow", None)
            if addressTo:
                return "%s: %s" % (addressTo, commandOutput)
            else:
                return commandOutput
        else:
            print "Invalid msg sent to parseDirectCommand: %s" % msg
            return None

    def parseInlineCommand(self, msg):
        commandOutput = []
        for commandRegex in self.inlineRegexes:
            match = re.findall(commandRegex, msg)
            if match:
                command = self.inlineRegexes[commandRegex]
                output = self.executeCommand(command, match)
                if isinstance(output, list):
                    for item in output:
                        commandOutput.append(item)
                else:
                    commandOutput.append(output)
        return commandOutput
            
    def parseNickname(self, sender):
        """ Parses the nickname from the nickname!hostmask string that the server sends as the sender"""
        return sender[:sender.find("!")]

    def executeCommand(self, command, args):
        command_method = getattr(self, command)
        return command_method(args)

    def sendReply(self, recipient, message):
        if message:
            codec = codecs.lookup('utf-8')
            encoded_string, errors = codec.encode(message)
            self.msg(recipient, encoded_string)
       
    def hello(self, *args):
        """
        This is a basic command that just returns \"hello there\"
        """
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

    def wikilink(self, linkTexts):
        links = ["http://en.wikipedia.org/wiki/" + wikilink.replace(" ", "_") for wikilink in linkTexts]
        return links
    
    def youtubeLink(self, videoIds):
        return [self.getVideoTitle(video) for video in videoIds]

    def getVideoTitle(self, videoId):
        videoResponse = requests.get("http://gdata.youtube.com/feeds/api/videos/%s?v=2" % videoId)
        if videoResponse.status_code == 200:
            videoData = minidom.parseString(videoResponse.text.encode('utf-8'))
            title = videoData.getElementsByTagName("title")[0].firstChild.data
            return title
        else:
            return "Video not found"
            
    
class BotFactory(Factory):
    def __init__(self, nickname, channel):
        self.bot_nickname = nickname
        self.bot_channel = channel
        
    def buildProtocol(self, addr):
        weather_provider = Weather()
        return HelloBot(self, weather_provider)

if __name__ == "__main__":
    endpoint = TCP4ClientEndpoint(reactor, bot_config.server, 6667)
    d = endpoint.connect(BotFactory(bot_config.bot_name, bot_config.bot_channel))
    reactor.run()
    
        

