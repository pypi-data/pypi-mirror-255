import pytest

from binip.classes import IP, Subnet

def test_address():
    '''Test the address attribute of the IP class.'''
    ipv4 = IP('192.168.1.24')
    ipv6 = IP('ac43:34f:45bc:2c::12')
    expected = ['192.168.1.24', 'ac43:34f:45bc:2c::12']
    actual = [ipv4.address, ipv6.address]
    assert actual == expected, "IP address is incorrect."

def test_ip_type():
    '''Test the iptype attribute and ip_type() method of the IP class.'''
    ipv4 = IP('192.168.1.24')
    ipv6 = IP('ac43:34f:45bc:2c::12')
    subnetv4 = Subnet('192.168.1.0/24')
    subnetv6 = Subnet('ac43:34f:45bc:2c::12/32')
    expected = ['v4', 'v6', 'v4', 'v6']
    actual = [ipv4.iptype, ipv6.iptype, subnetv4.iptype, subnetv6.iptype]
    assert actual == expected, "ip_type() method is not functioning correctly."

def test_ipv6_expand_contract():
    '''Test the expanded and contracted attributes and the ipv6_expand() and ipv6_contract methods of the IP class for IPv6 addresses.'''
    ipv6_contracted = IP('ac43:34f:45bc:2c::12')
    ipv6_expanded = IP('ac43:034f:45bc:002c:0000:0000:0000:0012')
    expected = ['ac43:034f:45bc:002c:0000:0000:0000:0012','ac43:34f:45bc:2c::12']
    actual = [ipv6_contracted.expanded, ipv6_expanded.contracted]
    assert actual == expected, "Expansion and/or contraction of IPv6 addresses not working correctly."

def test_binip():
    '''Test binip() method of IP class.'''
    ipv4 = IP('192.168.1.24')
    ipv6 = IP('ac43:34f:45bc:2c::12')
    expected = ['11000000101010000000000100011000', '10101100010000110000001101001111010001011011110000000000001011000000000000000000000000000000000000000000000000000000000000010010']
    actual = [ipv4.binip(), ipv6.binip()]
    assert actual == expected, "binip() method is not functioning correctly."

def test_in_subnet():
    '''Test in_subnet() method of IP and Subnet classes.'''
    ipv4 = IP('192.168.1.24')
    ipv6 = IP('ac43:34f:45bc:2c::12')
    subnetv4 = Subnet('192.168.1.0/24')
    subnetv6 = Subnet('ac43:34f:45bc:2c::12/32')
    expected = [True, False, True, False, True, False, True, False]
    actual = [ipv4.in_subnet('192.168.1.0/24'), ipv4.in_subnet('192.168.2.0/24'), ipv6.in_subnet('ac43:34f:45bc:2c::12/32'), ipv6.in_subnet('ac43:34fa:45bc:2c::12/32'),
              subnetv4.in_subnet('192.168.1.24'), subnetv4.in_subnet('192.168.2.24'), subnetv6.in_subnet('ac43:34f:45bc:2c::12'), subnetv6.in_subnet('bc43:34f:45bc:2c::12')]
    assert actual == expected, "in_subnet() method is not functioning correctly."

def test_subnet_info():
    '''Test subnet info such as mask, gateway, number of client IPs etc...'''
    subnetv4 = Subnet('192.168.1.0/24')
    subnetv6 = Subnet('ac43:34f:45bc:2c::12/32')
    expected = ['192.168.1.0', '192.168.1.255', 254, ('192.168.1.1','192.168.1.254'), 'ac43:34f:0:0:0:0:0:0', 'ac43:34f:ffff:ffff:ffff:ffff:ffff:ffff', 79228162514264337593543950334, ('ac43:34f:0:0:0:0:0:1','ac43:34f:ffff:ffff:ffff:ffff:ffff:fffe')]
    actual = list(subnetv4.info.values()) + list(subnetv6.info.values())
    assert actual == expected, "info function not working correctly."

def test_ipgen():
    '''Test ipgen method of Subnet class.'''
    subnetv4 = Subnet('192.168.1.0/24')
    ip_listv4 = [ip for ip in subnetv4.ipgen(0,10,2)]
    subnetv6 = Subnet('ac43:34f:45bc:2c::12/32')
    ip_listv6 = [ip for ip in subnetv6.ipgen(0,10,2)]
    expected = (['192.168.1.0', '192.168.1.2', '192.168.1.4', '192.168.1.6', '192.168.1.8', '192.168.1.10'],['ac43:34f:0:0:0:0:0:0', 'ac43:34f:0:0:0:0:0:2', 'ac43:34f:0:0:0:0:0:4', 'ac43:34f:0:0:0:0:0:6', 'ac43:34f:0:0:0:0:0:8', 'ac43:34f:0:0:0:0:0:a'])
    actual = (ip_listv4, ip_listv6)
    assert actual == expected, "ipgen function not working correctly."

def test_address_errors():
    '''Test that the IP class raises the proper errors given invalid inputs.'''
    with pytest.raises(ValueError):
        test = IP('192.168.1')
    with pytest.raises(ValueError):
        test = IP('192.168.1.24.48')
    with pytest.raises(ValueError):
        test = IP('192.168.1.300')
    with pytest.raises(ValueError):
        test = IP('ac43::45bc:2c::12')
    with pytest.raises(ValueError):
        test = IP('ac43:34f:45bc:2c:0:12')
    with pytest.raises(ValueError):
        test = IP('ac43:34f:45bc:2c:0:0:0:0:12')
    with pytest.raises(ValueError):
        test = IP('ac43:34f:45bc:2c:fffk:0:0:12')
    with pytest.raises(ValueError):
        test = IP('Nonesense')
    with pytest.raises(TypeError):
        test = IP(123)

def test_subnet_address_errors():
    '''Test that the Subnet class raises the proper errors given invalid inputs.'''
    with pytest.raises(ValueError):
        test = Subnet('192.168.1.24')
    with pytest.raises(ValueError):
        test = Subnet('192.168.1/24')
    with pytest.raises(ValueError):
        test = Subnet('192.168.1.0/33')
    with pytest.raises(ValueError):
        test = Subnet('192.168.1.24.48/24')
    with pytest.raises(ValueError):
        test = Subnet('192.168.1.300/24')
    with pytest.raises(ValueError):
        test = Subnet('ac43:34f:45bc:2c::12')
    with pytest.raises(ValueError):
        test = Subnet('ac43:34f:45bc:2c:3:12/48')
    with pytest.raises(ValueError):
        test = Subnet('ac43:34f:45bc:2c::12/129')
    with pytest.raises(ValueError):
        test = Subnet('ac43:34f:45bc:2c:fffk:0:0:0:12/48')
    with pytest.raises(ValueError):
        test = Subnet('ac43:34f:45bc:2c:fffk:0:0:12/48')
    with pytest.raises(ValueError):
        test = Subnet('Nonesense')
    with pytest.raises(TypeError):
        test = Subnet(123)

def test_ipgen_error():
    '''Test that ipgen method raises the proper error given invalid inputs.'''
    subnet = Subnet('192.168.1.0/24')
    with pytest.raises(IndexError):
        ip_list = [ip for ip in subnet.ipgen(0,512,1)]