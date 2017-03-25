from rochester_client_2 import RochesterClientFactory
from twisted.internet import reactor

f = RochesterClientFactory(debug=True)
reactor.connectTCP("localhost", 8023, f)
reactor.run()
