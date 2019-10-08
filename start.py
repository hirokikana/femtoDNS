#!/usr/bin/env python
#-*- coding:utf-8 -*-

import socketserver
import io

class DNSMessage():
    def __init__(self):
        self.headers = {}
        
        self.questionSection = b''
        self.answerSection = b''

        self.headers['ID'] = 0
        self.headers['QR'] = True
        self.headers['OPCODE'] = 0
        self.headers['AA'] = False
        self.headers['TC'] = False
        self.headers['RD'] = True
        self.headers['RA'] = False
        self.headers['Z'] = False
        self.headers['AD'] = True
        self.headers['CD'] = False
        self.headers['RCODE'] = 0

        self.headers['QDCOUNT'] = 1
        self.headers['ANCOUNT'] = 0
        self.headers['NSCOUNT'] = 0
        self.headers['ARCOUNT'] = 0

    def getQuestionHostname(self):
        return self.qnameToHostname(self.questionSection)

    def qnameToHostname(self, qname):
        qnameData = io.BytesIO(qname)

        label = []
        while True:
            labelLength = qnameData.read(1)
            if labelLength == b'\x00':
                break
            label.append(qnameData.read(int.from_bytes(labelLength,'big')))
        return '.'.join(map(lambda x: x.decode(), label))

    def hostnameToQname(self, hostname):
        QNAME = b''
        for tmp in map(lambda x: len(x).to_bytes(1, 'big') + x.encode(), hostname.split('.')):
            QNAME += tmp
        QNAME += b'\x00'
        return QNAME

    def generateHeaderBytes(self):
        resHeader = self.headers['ID']
        resHeader += b'\x81\x80' # Flags no error TODO
        resHeader += self.headers['QDCOUNT'].to_bytes(2, 'big') # QDCOUNT
        resHeader += self.headers['ANCOUNT'].to_bytes(2, 'big') # ANCOUNT
        resHeader += self.headers['NSCOUNT'].to_bytes(2, 'big') # NSCOUNT
        resHeader += self.headers['ARCOUNT'].to_bytes(2, 'big') # ARCOUNT
        return resHeader

    def toBytes(self):
        return self.generateHeaderBytes() + self.questionSection + self.answerSection

    def setHeader(self, name, value):
        self.headers[name] = value

    
    def setQuestion(self, hostname):
        QNAME = self.hostnameToQname(hostname)
        QTYPE = b'\x00\x01'
        QCLASS = b'\x00\x01'
        self.questionSection = QNAME + QTYPE + QCLASS

    def setAnasers(self, hostname, ipAddr):
        QNAME = self.hostnameToQname(hostname)
        
        ATYPE = b'\x00\x01' # A
        ACLASS = b'\x00\x01' # IN
        TTL = (255).to_bytes(4, 'big')

        RDATA = b''
        for tmp in map(lambda x:int(x).to_bytes(1,'big'), ipAddr.split('.')):
            RDATA += tmp
        RDATALength = b'\x00\x04'

        self.answerSection += QNAME + ATYPE + ACLASS + TTL + RDATALength + RDATA

        self.headers['ANCOUNT'] += 1

class DNSMessageParser():
    def __init__(self, requestBytes):
        self.requestData = io.BytesIO(requestBytes)

    def parse(self):
        requestData = self.requestData
        requestData.seek(0)

        self.dnsMessage = DNSMessage()

        self.dnsMessage.setHeader('ID', requestData.read(2))

        flags = int.from_bytes(requestData.read(2), 'big')
        self.dnsMessage.setHeader('QR', flags & 0b1000000000000000  > 0)
        self.dnsMessage.setHeader('OPCODE', flags & 0b0111100000000000)
        self.dnsMessage.setHeader('AA', flags & 0b0000010000000000 > 0)
        self.dnsMessage.setHeader('TC', flags & 0b0000001000000000 > 0)
        self.dnsMessage.setHeader('RD', flags & 0b0000000100000000 > 0)
        self.dnsMessage.setHeader('RA', flags & 0b0000000010000000 > 0)
        self.dnsMessage.setHeader('Z', flags & 0b0000000001000000 > 0)
        self.dnsMessage.setHeader('AD', flags& 0b0000000000100000 > 0)
        self.dnsMessage.setHeader('CD', flags & 0b0000000000010000 > 0)
        self.dnsMessage.setHeader('RCODE', flags & 0b0000000000001111)
        
        self.dnsMessage.setHeader('QDCOUNT', int.from_bytes(requestData.read(2), 'big'))
        self.dnsMessage.setHeader('ANCOUNT', int.from_bytes(requestData.read(2), 'big'))
        self.dnsMessage.setHeader('NSCOUNT', int.from_bytes(requestData.read(2), 'big'))
        self.dnsMessage.setHeader('ARCOUNT', int.from_bytes(requestData.read(2), 'big'))

        label = []
        while True:
            labelLength = requestData.read(1)
            if labelLength == b'\x00':
                break
            label.append(requestData.read(int.from_bytes(labelLength,'big')))
        self.dnsMessage.setQuestion('.'.join(map(lambda x: x.decode(), label)))

        return self.dnsMessage

        

class DNSHandler(socketserver.BaseRequestHandler):
    def getIpAddr(self, hostname):
        fd = open('hosts', 'r')
        for record in filter(lambda x:x.split("\t")[1].startswith(hostname), fd.readlines()):
            return record.split("\t")[0]
    
    def handle(self):

        parser = DNSMessageParser(self.request[0])
        requestDNSMessage = parser.parse()
        queryHostname = requestDNSMessage.getQuestionHostname()

        ## DEBUG Query Hostname
        print(queryHostname)

        # --- no error response
        dnsMessage = DNSMessage()
        dnsMessage.setHeader('ID', requestDNSMessage.headers['ID'])
        dnsMessage.setQuestion(queryHostname)

        # Check A record from file
        ipAddr = self.getIpAddr(queryHostname)
        if ipAddr:
            dnsMessage.setAnasers(queryHostname, ipAddr)

        socket = self.request[1]
        socket.sendto(dnsMessage.toBytes(), self.client_address)

if __name__ == '__main__':
    HOST, PORT = "localhost", 9999
    server = socketserver.UDPServer((HOST, PORT), DNSHandler)
    server.serve_forever()
