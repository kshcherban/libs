#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import random

class Net:
    """Contains most used network based procedures."""
    def __init__(self):
        pass

    @staticmethod
    def long2ip(l):
        """Convert a network byte order 32-bit integer to a dotted quad ip
        address.
        """
        MAX_IP = 0xffffffff
        MIN_IP = 0x0
        if MAX_IP < l or l < MIN_IP:
            raise TypeError(
            "expected int between %d and %d inclusive" % (MIN_IP, MAX_IP))
        return '%d.%d.%d.%d' % (l >> 24 & 255, l >> 16 & 255, l >> 8 & 255, l & 255)

    @staticmethod
    def ip2long(ip):
        """Convert a dotted-quad ip address to a network byte order 32-bit
        integer.
        :param ip: Dotted-quad ip address (eg. '127.0.0.1').
        :type ip: str
        :returns: Network byte order 32-bit integer or ``None`` if ip is invalid.
        """
        quads = ip.split('.')
        if len(quads) == 1:
            # only a network quad
            quads = quads + [0, 0, 0]
        elif len(quads) < 4:
            # partial form, last supplied quad is host address, rest is network
            host = quads[-1:]
            quads = quads[:-1] + [0, ] * (4 - len(quads)) + host
        lngip = 0
        for q in quads:
            lngip = (lngip << 8) | int(q)
        return lngip

    def cidr2block(self, cidr):
        """Convert a CIDR notation ip address into a tuple containing the network
        block start and end addresses.
        """
        ip, prefix = self.ip2long(cidr.split('/')[0]), int(cidr.split('/')[-1])
        # keep left most prefix bits of ip
        shift = 32 - prefix
        block_start = ip >> shift << shift
        # expand right most 32 - prefix bits to 1
        mask = (1 << shift) - 1
        block_end = block_start | mask
        return (self.long2ip(block_start), self.long2ip(block_end))

    @staticmethod
    def block2range(start, end):
        """Convert network block start and end address into a range of network
        addresses, returns list
        """
        for j in range(1,5):
            globals()["oct" + str(j)] = [i for i in range(int(start.split('.')[j-1]),
                int(end.split('.')[j-1]) + 1)]
        iprange = []
        for i in oct1:
            for j in oct2:
                for m in oct3:
                    for n in oct4:
                        iprange.append(str(i)+'.'+str(j)+'.'+str(m)+'.'+str(n))
        return iprange

    @staticmethod
    def is_mac_addr(mac):
        """Return True if provided argument is L2 (MAC) address"""
        mac = mac.rstrip().lower()
        if re.match("[0-9a-f]{2}(:)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac):
            return True
        return False

    @staticmethod
    def is_ip_addr(ip):
        """Return True if provided argument is IPv4 address"""
        p = '|'.join([str(i) for i in range(0,256)])
        pattern = '^(' + p[2:] + ')\.(' + p + ')\.(' + p + ')\.(' + p[2:-4] + ')$'
        if re.match(pattern, ip):
            return True
        return False

    @staticmethod
    def arp2ip(mac):
        """Read arp cache and extracts ip address that corresponds to argument
        L2 (MAC) address"""
        f = open('/proc/net/arp', 'r')
        for i in f.readlines():
            if mac in i:
                return i.split()[0]
        f.close()
        return None

    @staticmethod
    def get_subnet(ifname):
        """Return CIDR got from /bin/ip output, takes network interface name
        as argument. If no interface is found returns None"""
        try:
            patt = re.compile(r'inet\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,3})')
            subnet = patt.findall(os.popen('ip a s ' + ifname).read())[0]
        except IndexError:
            subnet = None
        return subnet

    def cidr2range(self, cidr):
        """Return range of ips from CIDR notation, takes CIDR as argument"""
        return self.block2range(self.cidr2block(cidr)[0], self.cidr2block(cidr)[1])

    @staticmethod
    def randomMAC():
        """Generate random L2 address"""
        mac = [ 0x00, 0x16, 0x3e,
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))

