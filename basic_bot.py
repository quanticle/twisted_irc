from twisted.words.protocols import irc
from twisted.internet.protocol import Factory
from twisted .internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint

class HelloBot(irc.IRCClient):
    def signedOn(self):
        self.setNick("quanticle_bot")
        self.join("#PyMNtos")
        print "Bot online" #DEBUG    

    def privmsg(self, sender, recipient, msg):
        print "Message received: %s" % (msg,) #DEBUG
        if recipient == "#PyMNtos" and msg.startswith("quanticle_bot"):
            self.say("#PyMNtos", "%s: Hello there" % (self.parseNickname(sender,)))

    def parseNickname(self, sender):
        """ Parses the nickname from the nickname!hostmask string that the server sends as the sender"""
        return sender[:sender.find("!")]
    
class BotFactory(Factory):
    def buildProtocol(self, addr):
        return HelloBot()

if __name__ == "__main__":
    endpoint = TCP4ClientEndpoint(reactor, "chat.freenode.net", 6667)
    d = endpoint.connect(BotFactory())
    reactor.run()

        

