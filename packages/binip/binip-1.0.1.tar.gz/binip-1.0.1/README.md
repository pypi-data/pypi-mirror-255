# Binip

### Description:

Library for IP networking and subnetting.

### Installation:

Download .whl file and run:

    pip install binip

### Usage:

Import the desired classes and or functions:

    from binip.classes import [class]
    from binip.functions import [function]

### Documentation:

**Classes:**

IP:

Input: IPv4 or IPv6 address.

    ipv4 = IP('192.168.1.24')
    ipv6 = IP('ac43:34f:45bc:2c:0:0:0:12')

Attributes:

- address: str, IP address.

        ipv4.address
        '192.168.1.24'
  
- iptype: str, 'v4' or 'v6'.

        ipv4.iptype
        'v4'
  
- expanded(for IPv6 only):str, expanded IPv6 address.

        ipv6.expanded
        'ac43:034f:45bc:002c:0000:0000:0000:0012'

- contracted(for IPv6 only):str, contracted IPv6 address.

        ipv6.contracted
        'ac43:34f:45bc:2c::12'

Methods:

- validate_address:

  Validates a given IP address, works for both IPv4 and IPv6.
  
- ip_type:

  Returns either 'v4' or 'v6'.
  
- ipv6_expand:

  Given a shortened IPv6 address will return the unshortened version.
  
- ipv6_contract:

  Returns shortened IPv6 address.  Removes leading zeros and contracts largest set of repeating zero hexadecatets.
  
- binip:

  Given an IP will return the IP in binary format.  Works for both IPv4 and IPv6.
  
- in_subnet

  Given a subnet will return True if the IP is in that subnet, will return False if otherwise.  Works for both IPv4 and IPv6.

Subnet:

Input: IPv4 or IPv6 subnet address, CIDR notation.

    subnetv4 = Subnet('192.168.1.12/24')
    subnetv6 = Subnet('ac43:34f:45bc:2c:0:0:0:12/64')

Attributes:

- subnet: str, subnet address.

        subnetv4.subnet
        '192.168.1.12/24'

- network: str, network address for subnet.

        subnetv4.network
        '192.168.1.0'

- networkcidr: str, network address for subnet in CIDR notation.

        subnetv4.networkcidr
        '192.168.1.0/24'

- broadcast: str, broadcast address for subnet.

        subnetv4.broadcast
        '192.168.1.255'

- broadcastcidr: str, broadcast address for subnet in CIDR notation.

        subnetv4.broadcastcidr
        '192.168.1.255/24'

- mask: int, subnet mask.

        subnetv4.mask
        24

- iptype: str, 'v4' or 'v6'.

        subnetv4.iptype
        'v4'

- info: dict, info on subnet.

        subnetv4.info
        {'Network address:': '192.168.1.0', 'Broadcast address': '192.168.1.255', 'Number of client IPs:': 254, 'Client IP range:': '192.168.1.1 - 192.168.1.254'}


Methods:

- validate_address:
  
  Validates a given IP address, works for both IPv4 and IPv6.
  
- ip_type:
  
  Returns either 'v4' or 'v6'.
  
- ipv6_expand:

  Given a shortened IPv6 address will return the unshortened version.
  
- ipv6_contract:

  Returns shortened IPv6 address.  Removes leading zeros and contracts largest set of repeating zero hexadecatets.
  
- binip:

  Given an IP will return the IP in binary format.  Works for both IPv4 and IPv6.
  
- in_subnet:

  Given an IP will return True if the IP is in the subnet, will return False if otherwise.  Works for both IPv4 and IPv6.
  
- subnet_info:
  
  Returns the network address, broadcast address and number of client IPs available for the subnet.
  
- toRegexv4:

  Returns a RegEx pattern to match the given IPv4 subnet.
  
- toRegexv6:

  Returns a RegEx pattern to match the given IPv6 subnet.
  
- ipgen:

  Generator function to iterate over IPs in the Subnet given a starting index, ending index and step.
    
**Functions:**

- ip_type: Returns either 'v4' or 'v6'.  Works for both IP and subnet addresses.

        ip_type('192.168.1.24')
        v4

- ipv6_expand: Given a shortened IPv6 address will return the unshortened version.

        ipv6_expand('ac43:34f:45bc:2c::12')
        'ac43:034f:45bc:002c:0000:0000:0000:0012'
    
- ipv6_contract: Returns shortened IPv6 address.  Removes leading zeros and contracts largest set of repeating zero hexadecatets.

        ipv6_contract('ac43:034f:45bc:002c:0000:0000:0000:0012')
        'ac43:34f:45bc:2c::12'
    
- ip2bin: Given an IP address, in either decimal or hexadecimal format, returns the same IP address in binary format.

        ip2bin('192.168.1.24')
        '11000000101010000000000100011000'
    
- bin2ip: Given an IP address in binary format returns the same IP address in either decimal or hexadecimal format.

        bin2ip('11000000101010000000000100011000')
        '192.168.1.24'
    
- in_subnet: Given a subnet and an IP will return True if the IP is in that subnet, will return False if otherwise.  Works for both IPv4 and IPv6.

        in_subnet('192.168.1.24', '192.168.1.0/24')
        True
        in_subnet('192.168.1.24', '192.168.2.0/24')
        False

- overlap: Given two subnets two subnets will return True if they overlap or are identical.  Will return False if the subnets don't overlap.

        overlap('172.16.0.0/12', '172.16.0.0/16')
        True
        overlap('172.16.0.0/12', '172.10.0.0/16')
        False
        
- hex_range: Given the first and last hexadecimal values of a range returns a list of ReGex patterns to match each value of that range. Used in the toRegexv6 function.

        hex_range('0000', 'aaaa')
        hex_range('0000', 'aaaa')
        ['[0-9a-f]{0,1}', '[0-9a-f]{0,1}[0-9a-f]{0,1}', '[0-9a-f]{1}[0-9a-f]{0,2}', '[1-9]{0,1}[0-9a-f]{0,3}', 'aaa[0-9a-a]{0,1}', 'aa[0-9a-9]{1}[0-9a-f]{0,1}', 'a[0-9a-9]{1}[0-9a-f]{0,2}']
    
- toRegexv4: Returns a RegEx pattern to match the given IPv4 subnet. Used in the toRegex function.

        toRegexv4('192.168.1.0/14')
        '192.[1][6][8-9].[0-9]{1,3}.[0-9]{1,3}|192.[1][7][0-1].[0-9]{1,3}.[0-9]{1,3}'
    
- toRegexv6: Returns a RegEx pattern to match the given IPv6 subnet. Used in the toRegex function.

        toRegexv6('ac43:34f:45bc:2c::12/56')
        'ac43:34f:45bc:[0-9a-f]{0,1}:.*|ac43:34f:45bc:[0-9a-f]{0,1}[0-9a-f]{0,1}:.*|ac43:34f:45bc:[1-9a-e]{1}[0-9a-f]{0,1}:.*|ac43:34f:45bc:f[0-9a-f]{0,1}:.*'

- toRegex: Returns a RegEx pattern to match the given subnet.  Works for both IPv4 and IPv6.

        toRegexv4('192.168.1.0/14')
        '192.[1][6][8-9].[0-9]{1,3}.[0-9]{1,3}|192.[1][7][0-1].[0-9]{1,3}.[0-9]{1,3}'
        toRegexv6('ac43:34f:45bc:2c::12/56')
        'ac43:34f:45bc:[0-9a-f]{0,1}:.*|ac43:34f:45bc:[0-9a-f]{0,1}[0-9a-f]{0,1}:.*|ac43:34f:45bc:[1-9a-e]{1}[0-9a-f]{0,1}:.*|ac43:34f:45bc:f[0-9a-f]{0,1}:.*'

### License:

Basic MIT license.
