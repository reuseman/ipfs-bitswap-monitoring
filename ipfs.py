import requests
import json
import geoip2.database

class Ipfs():
    def __init__(self, basepath="http://localhost:5001/api/v0", gc=True):
        self.basepath = basepath
        self.initial_bitswap_stat = self.get_bitswap_stat()
        if gc:
            self.__post('/repo/gc', json=False)
    
    def is_daemon_active(self):
        try:
            r = requests.post(self.basepath + '/id')
            return True
        except:
            return False
        
    def __post(self, api, json=True):
        r = requests.post(self.basepath + api)
        return r.json() if json else r

    '''
        Return IPV4 Addresses of peers with latency and CID
    '''
    def get_swarm_peers(self):
        return self.__post('/swarm/peers?latency=true')["Peers"]
    
    def get_bitswap_ledger(self, peerID):
        return self.__post('/bitswap/ledger?arg=' + peerID)
    
    def get_object_stat(self, CID):
        return self.__post('/object/stat?arg=' + CID + "&human=true")
    
    def ls(self, CID):
        return self.__post('/ls?arg=' + CID)
    
    def free(self, s):
        return self.__post(s)
    
    def get_bitswap_partners(self):
        # Query the Swarm to get IPv4 and latency for each peer
        swarm_peers = list(filter(lambda x: x["Addr"].split("/")[1] == "ip4", self.get_swarm_peers()))
        peers = dict((p["Peer"], p) for p in swarm_peers)
        
        # Query the Bitswap ledger to receive information on exchanged data
        for cid in peers.keys():
            peer_ledger = self.get_bitswap_ledger(cid)
            peers[cid].update(peer_ledger)

        # Filter out the peers that did not sent nothing and order by bytes received
        bitswap_partners = dict(filter(lambda x: x[1]["Recv"] > 0, peers.items()))
        bitswap_partners = dict(sorted(bitswap_partners.items(), key=lambda x: x[1]["Recv"], reverse=True))

        # Add geolocation to the partners in bitswap
        for cid in bitswap_partners.keys():
            ip = bitswap_partners[cid]["Addr"].split("/")[2]
            with geoip2.database.Reader('geo-city.mmdb') as reader:
                response = reader.city(ip)
                bitswap_partners[cid]["Country"] = response.country.name
                bitswap_partners[cid]["Continent"] = response.continent.name
                bitswap_partners[cid]["Lat"] = response.location.latitude
                bitswap_partners[cid]["Lon"] = response.location.longitude
                
        return bitswap_partners
    
    def get_bitswap_stat(self, remove_initial_stats=False):
        stat =  self.__post('/bitswap/stat')
        if remove_initial_stats:
            stat['BlocksReceived'] -= self.initial_bitswap_stat['BlocksReceived']
            stat['DataReceived'] -= self.initial_bitswap_stat['DataReceived']
            stat['BlocksSent'] -= self.initial_bitswap_stat['BlocksSent']
            stat['DataSent'] -= self.initial_bitswap_stat['DataSent']
            stat['DupBlksReceived'] -= self.initial_bitswap_stat['DupBlksReceived']
            stat['DupDataReceived'] -= self.initial_bitswap_stat['DupDataReceived']
            stat['MessagesReceived'] -= self.initial_bitswap_stat['MessagesReceived']
        
        return stat