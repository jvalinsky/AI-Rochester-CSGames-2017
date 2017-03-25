import random
from client import ClientFactory
from twisted.internet import reactor

name = "Bob{}".format(random.randint(0, 999))

f = ClientFactory(name, debug=True)
reactor.connectTCP("localhost", 8023, f)
reactor.run()
