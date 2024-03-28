# IPv6 IID Pattern
This tool is primarily used for identifying the pattern of the Interface ID in IPv6 addresses.

## Usage
### 1. makeiiddb.py
Build an IID database for recognition of RANDOM pattern.

```
# you can get histlist.txt from https://ipv6hitlist.github.io/
cat hitlist.txt | addr6 -i -f | python makeiiddb.py > iid.db
```

### 2. iidpattern.py
Read formatted IPv6 address from stdin and output its pattern. Depending on the hitlist, the results identified may vary slightly.

```
# one address
echo 2001:1248:0001:6301:5b76:10b0:34d6:d8bc | python iidpattern.py

# address file
# format ipv6 addresses using addr6
cat ipfile.txt | addr6 -i -f | python iidpattern.py

# stat
cat ipfile.txt | addr6 -i -f | python iidpattern.py -s
```

## Requirements
addr6(https://github.com/fgont/ipv6toolkit)
