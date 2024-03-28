#!/usr/bin/env python
# -*- coding:utf-8 -*- 

import sys
import re
import os
import argparse

parser = argparse.ArgumentParser(description='ipv6 iid mode')
parser.add_argument('-s', '--stat', action='store_true', help='statistic')

args = parser.parse_args()

ipv6_all = {}
iids_4 = set()
def init():
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    for line in open(os.path.join(current_dir,'iid.db'), 'r').readlines():
        ipv6, flag = line.strip().split(' ')
        ipv6_all[ipv6] = flag
        iid_h4 = ipv6[20:29]
        iid_l4 = ipv6[30:39]
        iids_4.add(iid_h4)
        iids_4.add(iid_l4)

def zero_byte_iid(iid):
    cnt = 0
    for i in range(8):
        if iid & 0xff == 0:
            cnt += 1
        iid /= 256 
    return cnt
# well known service port
# https://github.com/fgont/ipv6toolkit/blob/master/tools/addr6.c
SERVICE_PORTS_HEX = [0x21, 0x22, 0x23, 0x25, 0x49, 0x53, 0x80, 0x110, 0x123, 0x179, 0x220, 0x389,
                     0x443, 0x547, 0x993, 0x995, 0x1194, 0x3306, 0x5060, 0x5061, 0x5432, 0x6446, 0x8080]
SERVICE_PORTS_DEC = [21, 22, 23, 25, 49, 53, 80, 110, 123, 179, 220, 389,
                     443, 547, 993, 995, 1194, 3306, 5060, 5061, 5432, 6446, 8080]

def is_service_port(port):
    return port in SERVICE_PORTS_HEX or port in SERVICE_PORTS_DEC

def parse(ipv6):
    arr = ipv6.split(':')
    prefix_int16 = [int(i, 16) for i in arr[0:4]]
    prefix_int32 = [prefix_int16[0] * 65536 + prefix_int16[1], prefix_int16[2] * 65536 +
                 prefix_int16[3]]

    iid_int16 = [int(i, 16) for i in arr[4:8]]
    iid_int32 = [iid_int16[0] * 65536 + iid_int16[1], iid_int16[2] * 65536 +
                 iid_int16[3]]
    iid_int64 = iid_int32[0] * 4294967296 + iid_int32[1]
    #print('%x' % iid_int32[0])

    iidtype = 'UNKNOWN'
    if prefix_int32[0] == 0x20010000 or prefix_int32[0] == 0x3ffe831f:
        iidtype = 'TEREDO'
    elif iid_int32[0] & 0x020000ff == 0x020000ff and iid_int32[1] & 0xff000000 == 0xfe000000:
        iidtype = 'IEEE'
    elif iid_int32[0] & 0xfdffffff == 0x00005efe:
        iidtype = 'ISATAP'
    elif iid_int32[0] == 0 and iid_int16[2] >= 0x100 and iid_int16[3] != 0:
        iidtype = 'IPv4'
    elif iid_int32[0] == 0 and iid_int16[2] < 0x100 and is_service_port(iid_int16[3]):
        iidtype = 'PORT'
    elif iid_int32[0] == 0 and iid_int16[3] < 0x100 and is_service_port(iid_int16[2]):
        iidtype = 'PORT'
    elif iid_int64 == 0:
        iidtype = 'LOWBYTE'
    elif iid_int32[0] == 0 and iid_int32[1] < 0x1000000 and iid_int16[3] > 0:
        iidtype = 'LOWBYTE'
    elif re.match('^[0-9:]*$', ipv6[20:]) and 0 < iid_int16[0] <= 0x255 and iid_int16[1] <= 0x255 and iid_int16[2] <= 0x255 and iid_int16[3] <= 0x255:
        iidtype = 'IPv4'
    elif zero_byte_iid(iid_int64) > 2:
        iidtype = 'BYTES'
    else:
        if ipv6 in ipv6_all:
            if ipv6_all[ipv6] == '1':
                iidtype = 'RANDOM'
            else:
                iidtype = 'HITLIST'
        else:
            iid_h4 = ipv6[20:29]
            iid_l4 = ipv6[30:39]
            if iid_h4 in iids_4 or iid_l4 in iids_4:
                iidtype = 'HITLIST'
            else:
                iidtype = 'RANDOM'
    return iidtype

def test():
    ipv6_addresses = [
    "2001:1248:0001:6301:5b76:10b0:34d6:d8ab",
    "2001:1260:0002:0001:0000:0000:0000:0001",
    "2001:1260:0002:0001:0000:0000:0000:0000",
    "2001:1284:f01c:924b:c6fb:aaff:fede:2bbe",
    "2001:4420:609d:0001:0000:5efe:cb41:4801",
    "2001:4420:609d:0001:0000:0000:cb41:4801",
    "2610:00a1:1073:0000:0000:0000:0000:0016",
    "2607:f388:1084:1050:0000:0000:0053:000a",
    "2607:f388:1084:1050:0192:0168:0000:0001",
    "2600:9000:21c7:4200:0010:00d7:2300:93a1",
            ]
    init()
    for i in ipv6_addresses:
        iid_mode = parse(i)
        print(iid_mode)

def main():
    init()
    modes = ['RANDOM','HITLIST','IEEE','TEREDO','ISATAP','IPv4','BYTES','PORT','LOWBYTE']
    cnt = {}
    for i in modes:
        cnt[i] = 0
    total = 0
    for line in sys.stdin:
        ipv6 = line.strip()
        if re.match('[a-f0-9]{4}(:[a-f0-9]{4}){7}$', ipv6):
            iidtype = parse(ipv6)
            if not args.stat:
                print('%s\t%s' % (ipv6, iidtype))
            total += 1
            cnt[iidtype] += 1
        else:
            if not args.stat:
                print('%s\tinvalid' % ipv6)
    if total > 0 and args.stat:
        print('\t'.join(modes))
        output = ['%.2f%%' % (cnt[i]*100.0/total) for i in modes]
        print('\t'.join(output))

main()
