from twisted.words.protocols import irc
from twisted.internet.protocol import Factory
from twisted .internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint

class HelloBot(irc.IRCClient):
    def __init__(self, factory):
        self.nickname = factory.bot_nickname
        self.channel = factory.bot_channel
        
    def signedOn(self):
        self.setNick(self.nickname)
        self.join(self.channel)
        print "Bot online" #DEBUG    

    def privmsg(self, sender, recipient, msg):
        print "Message received: %s" % (msg,) #DEBUG
        if recipient == self.channel and msg.startswith(self.nickname):
            self.say(self.channel, "%s: Hello there" % (self.parseNickname(sender,)))

    def parseNickname(self, sender):
        """ Parses the nickname from the nickname!hostmask string that the server sends as the sender"""
        return sender[:sender.find("!")]
    
class BotFactory(Factory):
    def __init__(self, nickname, channel):
        self.bot_nickname = nickname
        self.bot_channel = channel
        
    def buildProtocol(self, addr):
        return HelloBot(self)

if __name__ == "__main__":
    endpoint = TCP4ClientEndpoint(reactor, "chat.freenode.net", 6667)
    d = endpoint.connect(BotFactory("quanticle_bot", "#PyMNtos"))
    reactor.run()

        

