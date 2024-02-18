import pytest

from binip.functions import *

def test_ip_type():
    '''Test the ip_type() function.'''
    ipv4 = ip_type('192.168.1.24')
    ipv6 = ip_type('ac43:34f:45bc:2c::12')
    subnetv4 = ip_type('192.168.1.24/24')
    subnetv6 = ip_type('ac43:34f:45bc:2c::12/32')
    expected = ['v4', 'v6', 'v4', 'v6']
    actual = [ipv4, ipv6, subnetv4, subnetv6]
    assert expected == actual, "ip_type function fails."

def test_ip_type_errors():
    '''Test that the ip_type function raises the correct errors.'''
    with pytest.raises(ValueError):
        test = ip_type('192.168.1')
    with pytest.raises(ValueError):
        test = ip_type('192.168.1.24.48')
    with pytest.raises(ValueError):
        test = ip_type('192.168.1.300')
    with pytest.raises(ValueError):
        test = ip_type('ac43::45bc:2c::12')
    with pytest.raises(ValueError):
        test = ip_type('ac43:34f:45bc:2c:0:12')
    with pytest.raises(ValueError):
        test = ip_type('ac43:34f:45bc:2c:0:0:0:0:12')
    with pytest.raises(ValueError):
        test = ip_type('ac43:34f:45bc:2c:fffk:0:0:12')
    with pytest.raises(ValueError):
        test = ip_type('Nonesense')
    with pytest.raises(TypeError):
        test = ip_type(123)

def test_ip2bin():
    '''Test the ip2bin function.'''
    ipv4 = ip2bin('192.168.1.24')
    ipv6 = ip2bin('ac43:34f:45bc:2c:0:0:0:12')
    subnetv4, maskv4 = ip2bin('192.168.1.24/24')
    subnetv6, maskv6 = ip2bin('ac43:34f:45bc:2c:0:0:0:12/32')
    expected = ['11000000101010000000000100011000', 
              '10101100010000110000001101001111010001011011110000000000001011000000000000000000000000000000000000000000000000000000000000010010',
              '11000000101010000000000100011000', '11111111111111111111111100000000',
              '10101100010000110000001101001111010001011011110000000000001011000000000000000000000000000000000000000000000000000000000000010010',
              '11111111111111111111111111111111000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000']
    actual = [ipv4, ipv6, subnetv4, maskv4, subnetv6, maskv6]
    assert expected == actual, "ip2bin function fails conversion from decimal/hexadecimal to binary."

def test_bin2ip():
    '''Test the bin2ip function.'''
    ipv4_bin = bin2ip('11000000101010000000000100011000')
    ipv6_bin = bin2ip('10101100010000110000001101001111010001011011110000000000001011000000000000000000000000000000000000000000000000000000000000010010')
    subnetv4_bin = bin2ip('11000000101010000000000100011000', '11111111111111111111111100000000')
    subnetv6_bin = bin2ip('10101100010000110000001101001111010001011011110000000000001011000000000000000000000000000000000000000000000000000000000000010010',
                          '11111111111111111111111111111111000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
    expected = ['192.168.1.24', 'ac43:34f:45bc:2c:0:0:0:12', '192.168.1.24/24', 'ac43:34f:45bc:2c:0:0:0:12/32']
    actual = [ipv4_bin, ipv6_bin, subnetv4_bin, subnetv6_bin]
    assert expected == actual, "bin2ip function fails conversion from binary to decimal/hexadecimal."

def test_bin2ip_error():
    '''Test that the bin2ip function raises the correct errors for using a binary value not 32 or 128 bits long and for using a non binary input.'''
    with pytest.raises(ValueError):
        bin2ip('100100')
    with pytest.raises(ValueError):
        bin2ip('1234')
    with pytest.raises(TypeError):
        bin2ip(1234)

def test_ipv6_expand():
    '''Test the ipv6_expand function.'''
    ipv6 = 'ac43:34f:45bc:2c::12'
    subnetv6 = 'ac43:34f:45bc:2c::12/64'
    expected = ['ac43:034f:45bc:002c:0000:0000:0000:0012', 'ac43:034f:45bc:002c:0000:0000:0000:0012/64']
    actual = [ipv6_expand(ipv6), ipv6_expand(subnetv6)]
    assert expected == actual, "ipv6_expand function fails IPv6 expansion."

def test_ipv6_contract():
    '''Test the ipv6_contract function.'''
    ipv6 = 'ac43:034f:45bc:002c:0000:0000:0000:0012'
    subnetv6 = 'ac43:034f:45bc:002c:0000:0000:0000:0012/64'
    expected = ['ac43:34f:45bc:2c::12', 'ac43:34f:45bc:2c::12/64']
    actual = [ipv6_contract(ipv6), ipv6_contract(subnetv6)]
    assert expected == actual, "ipv6_contract function fails IPv6 contraction."

def test_ipv6_expand_contract_error():
    '''Test that the ipv6_expand and ipv6_contract functions raise the correct error when given an IPv4 address.'''
    with pytest.raises(ValueError):
        ipv6_expand('192.168.1.24')
    with pytest.raises(ValueError):
        ipv6_contract('192.168.1.24')

def test_in_subnet():
    '''Test the in_subnet function.'''
    ipv4_1 = '192.168.1.24'
    ipv4_2 = '192.168.2.24'
    ipv6_1 = 'ac43:34f:45bc:2c::12'
    ipv6_2 = 'bc43:34f:45bc:2c::12'
    subnetv4 = '192.168.1.0/24'
    subnetv6 = 'ac43:34f:45bc:2c::12/32'
    expected = [True, False, True, False]
    actual = [in_subnet(ipv4_1, subnetv4), in_subnet(ipv4_2, subnetv4), in_subnet(ipv6_1, subnetv6), in_subnet(ipv6_2, subnetv6)]
    assert expected == actual, "in_subnet function is not working correctly."