#!/usr/bin/env python
# -*- coding:utf-8 -*- 

import sys
import re

ipv6_all = {}
iids_h4 = {}
iids_l4 = {}

for line in sys.stdin:
    ipv6 = line.strip()
    if re.match('[a-f0-9]{4}(:[a-f0-9]{4}){7}$', ipv6):
        # default random
        ipv6_all[ipv6] = 1

        iid_h4 = ipv6[20:29]
        iid_l4 = ipv6[30:39]
        if iid_h4 not in iids_h4:
            iids_h4[iid_h4] = [ipv6]
        else:
            iids_h4[iid_h4].append(ipv6)
        if iid_l4 not in iids_l4:
            iids_l4[iid_l4] = [ipv6]
        else:
            iids_l4[iid_l4].append(ipv6)

# flag non random
for iid in iids_h4:
    if len(iids_h4[iid]) > 1:
        for ipv6 in iids_h4[iid]:
            ipv6_all[ipv6] = 0
for iid in iids_l4:
    if len(iids_l4[iid]) > 1:
        for ipv6 in iids_l4[iid]:
            ipv6_all[ipv6] = 0
for ipv6 in ipv6_all:
    print('%s %d' % (ipv6, ipv6_all[ipv6]))
