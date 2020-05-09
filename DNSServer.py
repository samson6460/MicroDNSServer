import network
import machine
import socket
import uselect

class DNSReplyCode:
    NoError = 0
    FormError = 1
    ServerFailure = 2
    NonExistentDomain = 3
    NotImplemented = 4
    Refused = 5
    YXDomain = 6
    YXRRSet = 7
    NXRRSet = 8

class DNSServer:
    def __init__(self):
        self.poller = None
        self.udps = None
        self.ttl = 60
        self.errorReplyCode = DNSReplyCode.NonExistentDomain
                    
    def start(self, dns_port, domain_name, resolvedIP):      
        self.dns_port = dns_port
        
        if type(domain_name)!=type(resolvedIP):
            raise ValueError('type of domain name and resolved IP should be the same')
        if type(domain_name)==list and (len(domain_name)!=len(resolvedIP)):
            raise ValueError('length of domain name and resolved IP should be the same')
            
        self.domain_name = domain_name
        self.resolvedIP = resolvedIP
        
        self.udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udps.setblocking(False)
        self.udps.bind(('',dns_port))
        self.poller = uselect.poll()
        self.poller.register(self.udps, uselect.POLLIN)

    def __respondToRequest(self, buffer):
        data = buffer[0]
        received_domain_name = ''
        m = data[2]
        Opcode = (m >> 3) & 15
        if Opcode == 0:      # Standard query
            pos=12
            length=data[pos]
            while length != 0:
                received_domain_name += data[pos+1:pos+length+1].decode("utf-8")
                pos += length+1
                length = data[pos]
                if length !=0:
                    received_domain_name += '.'

        if self.domain_name == '*':
            self.__replyWithIP(buffer, received_domain_name, self.resolvedIP)

        elif received_domain_name == self.domain_name:
            self.__replyWithIP(buffer, received_domain_name, self.resolvedIP)

        elif received_domain_name in self.domain_name:
            resolvedIP = self.resolvedIP[self.domain_name.index(received_domain_name)]
            self.__replyWithIP(buffer, received_domain_name, resolvedIP)

        else:
            self.__replyWithError(buffer, received_domain_name, self.errorReplyCode)

    def __replyWithIP(self, buffer, rdomain_name, ip):
        data, addr = buffer

        packet=b''
        packet += data[:2]      # ID
        packet += b'\x81\x80'   # Flag
        packet += data[4:6] + data[4:6] + b'\x00\x00\x00\x00' # Questions and Answers Counts
        packet += data[12:]                                   # Original Domain Name Question
        packet += b'\xc0\x0c'           # Pointer to domain name
        packet += b'\x00\x01\x00\x01'   # Response type
        packet += (self.ttl).to_bytes(4, "big")   # ttl
        packet += b'\x00\x04'           # resource data length -> 4 bytes
        packet += bytes(map(int,ip.split('.'))) # 4 bytes of IP
        self.udps.sendto(packet, addr)
        print('Replying: {:s} -> {:s} from {:s}'.format(rdomain_name, ip, addr[0]))

    def __replyWithError(self, buffer, rdomain_name, rcode):
        data, addr = buffer

        packet=b''
        packet += data[:2]  # ID
        packet += b'\x81'   # Flag without rcode
        packet += bytes([128+rcode])   # rcode
        packet += b'\x00\x00\x00\x00\x00\x00\x00\x00' # Questions and Answers Counts
        
        self.udps.sendto(packet, addr)
        #print('Replying: {:s} -> error from {:s}'.format(rdomain_name, addr[0]))
    
    def processNextRequest(self):
        res = self.poller.poll(1)
        
        if res:
            try:
                buffer = self.udps.recvfrom(1024)
                self.__respondToRequest(buffer)
            except :
                pass
  
    def stop(self):
        if self.poller:self.poller.unregister(self.udps)
        if self.udps:self.udps.close()     

