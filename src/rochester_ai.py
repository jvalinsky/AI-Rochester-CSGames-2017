from rochester_client import RochesterClientFactory
from twisted.internet import reactor

f = RochesterClientFactory(debug=True)
reactor.connectTCP("localhost", 8023, f)
reactor.run()
