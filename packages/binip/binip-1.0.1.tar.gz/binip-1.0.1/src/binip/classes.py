import re

from binip.functions import *

class IP:
    '''
        Class for IP objects.  Both IPv4 and IPv6 are supported.
        -----
        Attributes
        ---
        address: str
            IP address.
        iptype: str
            Either v4 or v6.
        -----
        Methods
        ---
        validate_address(address):
            Ensures user input is valid IP address.
        ip_type():
            Returns IP type; v4 or v6, of class.
        ipv6_expand():
            Given an IPv6 address will return the expanded version of address.  Adds leading zeros and
            expands sets of zero hexadecatets that are contracted.
        binip():
            Returns binary version of IP address.
        in_subnet(subnet):
            Given a subnet returns True if IP in subnet or False if IP not in subnet.
    '''
    def __init__(self, address: str):
        '''
            Initialzing the IP class object.
            -----
            Parameters
            ---
            address: str
                IP address, either v4 or v6.
            -----
            Returns
            ---
            address: str
                Validated IP address, etiher v4 or v6.
            iptype: str
                Either 'v4' or 'v6' depending on IP type.
        '''
        self.address = self.validate_address(address)
        self.iptype = self.ip_type()
        if self.iptype == 'v6':
            self.expanded = self.ipv6_expand(address)
            self.contracted = self.ipv6_contract(address)
        
    def validate_address(self, address: str):
        '''
            Validates a given IP address, works for both IPv4 and IPv6.
            -----
            Parameters
            ---
            address: str
                IP address, either v4 or v6.
            -----
            Returns
            ---
            address: str
                Validated IP address, either v4 or v6.
            -----
            Raises
            ---
            TyperError
                If input parameter is not of type string.
            ValueError
                If the number of octets or hexadecatets is invalid.  Expected values are 4 and 8 for IPv4 and IPv6 respectively.
                If an invalid decimal or hexadecimal is provided. Expected decimal values are between 0 and 255 for IPv4 and expected hexadecial values are between 0 and ffff for IPv6.
                If an invalid IPv4 or IPv6 format is used.  Includes missing periods or colons as well as multiple zero contractions in IPv6.
        '''
        if type(address) == type(''):
            if '.' in address:
                ip_split = address.split('.')
                if len(ip_split) != 4:
                    raise ValueError(f'Wrong number of octets: there should be 4 octets.  The IP provided contains {len(ip_split)} octets.')
                for octet in ip_split:
                    if int(octet) not in range(0,256):
                        raise ValueError(f'Invalid decimal value: each octet should be a decimal value between 0 and 255. {octet} does not fall in that range.')
                return address             
            elif ':' in address:
                if address.count('::') > 1:
                    count = address.count('::')
                    raise ValueError(f'Too many zero contractions: IPv6 addresses can only have a single set of 0s contracted to "::". The IP provided contains {count} contractions.')
                else:
                    ip_split = address.split(':')
                    num_hex = f'Wrong number of hexadecatets: there should be 8 hexadecatets.  The IP provided contains {len(ip_split)} hexadecatets.'
                    if len(ip_split) > 8:
                        raise ValueError(num_hex)
                    elif '::' not in address and len(ip_split) != 8:
                        raise ValueError(num_hex)
                    else:
                        for hexadecatet in ip_split:
                            if hexadecatet == '':
                                hexadecatet = '0'
                            if int(hexadecatet, 16) not in range(0,65536):
                                raise ValueError(f'Invalid hexadecimal value: each hexadecatet should be a hexadecimal value between 0 and ffff. {hexadecatet} does not fall in that range.')
                    return address
            else:
                raise ValueError(f'Invalid format: {address} is not a valid IPv4 or IPv6 address.')
        else:
            raise TypeError(f'IP should be a string not {type(address)}.')

    def __str__(self) -> str:
        return self.address
    
    def __repr__(self) -> str:
        return self.address
        
    def ip_type(self) -> str:
        '''
            Given an IP will return 'v4' if IPv4 or 'v6' if IPv6.
            -----
            Parameters
            ---
            self: IP class object
                Uses the IP address of the class object.
            -----
            Returns
            ---
            iptype: str
                IP address type, either v4 or v6.
        '''
        if '.' in self.address:
            iptype = 'v4'
        elif ':' in self.address:
            iptype = 'v6'
        return iptype
    
    @staticmethod
    def ipv6_expand(address: str) -> str:
        '''
            Given a shortened IPv6 address will return the unshortened version.
            -----
            Parameters
            ---
            address: str
                IPv6 address.
            -----
            Returns
            ---
            expanded: str
                Expanded IPv6 address.  Adds leading zeros and expands contraced zeros.
        '''
        split = address.split(':')
        zeros = ['0000' for i in range(0,9-len(split))]
        new_split = []
        for hexadecatet in split:
            if hexadecatet == '':
                new_split += zeros
            elif hexadecatet == '0':
                new_split.append('0000')
            elif len(hexadecatet) < 4:
                for i in range(0,4-len(hexadecatet)):
                    hexadecatet = '0' + hexadecatet
                new_split.append(hexadecatet)
            else:
                new_split.append(hexadecatet)
        expanded = ':'.join(new_split)
        return expanded
    
    @staticmethod
    def ipv6_contract(address: str) -> str:
        '''
            Given an unshortened IPv6 address return contracted version.
            -----
            Parameters
            ---
            address: str
                IPv6 address.
            -----
            Returns
            ---
            contracted: str
                Shortened IPv6 address.  Removes leading zeros and contracts largest set of repeating zero hexadecatets.
        '''
        address = ipv6_expand(address)
        ipv6_split = address.split(':')
        ipv6_contracted = []
        #Remove leading zeros
        for hexadecatet in ipv6_split:
            while hexadecatet[0] == '0' and len(hexadecatet) > 1:
                    hexadecatet = hexadecatet[1:]
            ipv6_contracted.append(hexadecatet)
        #Remove largest set of repeating zero hexadecatets
        #Find largest set of repeating zeros
        i=0
        replacing_zeros = []
        while i < 8:
            zeros = []
            if ipv6_contracted[i] == '0':
                zeros.append(i)
                j=1
                while ipv6_contracted[i+j] == '0':
                    zeros.append(i+j)
                    j+=1
                i+=j
                if len(zeros) >= len(replacing_zeros):
                    replacing_zeros = zeros
            else:
                i+=1
        #Replace first zeros with empty string and remove the rest
        ipv6_contracted[replacing_zeros[0]] = ''
        i = 0
        for item in replacing_zeros[1:]:
            ipv6_contracted.pop(item-i)
            i += 1
        contracted = ':'.join(ipv6_contracted)
        return contracted
    
    def binip(self) -> str:
        '''
            Given an IP will return the IP in binary format.  Works for both IPv4 and IPv6.
            -----
            Parameters
            ---
            self: IP class object
                Uses the IP address of the class object.
            -----
            Returns
            ---
            bin_ip: str
                Same IP address in binary format.
        '''
        iptype = self.ip_type()
        ip = self.address
        bin_ip = ''
        if iptype == 'v4':
            split_ip = ip.split('.')
            for octet in split_ip:
                octet = format(int(octet), '08b')
                bin_ip += octet
        elif iptype == 'v6':
            ip = self.ipv6_expand(ip)
            split_ip = ip.split(':')
            for hexadecatet in split_ip:
                hexadecatet = format(int(hexadecatet, 16), '016b')
                bin_ip += hexadecatet
        return bin_ip
    
    def in_subnet(self, subnet: str) -> bool:
        '''
            Given a subnet will return True if the IP is in that subnet, will return False if otherwise.  Works for both IPv4 and IPv6.
            -----
            Parameter
            ---
            subnet: str
                Subnet address, turns into Subnet class object for validation.
            -----
            Returns
            ---
            bool
                True if IP is in the given subnet, otherwise returns False.
        '''
        #Determine if the IP and subnet are v4 or v6 and then split the IP and subnet by octet and get the mask from the subnet.
        network = Subnet(subnet)
        iptype = self.ip_type()
        subnettype = network.ip_type()
        if subnettype != iptype:
            raise ValueError('IP and subnet are not the same version.')
        else:
            bin_ip = self.binip()
            bin_network = network.binip()[0]
            mask = int(network.mask)
            if bin_ip[:mask] == bin_network[:mask]:
                return True
            else:
                return False
            
class Subnet:
    '''
        Class for Subnet objects.  Both IPv4 and IPv6 are supported.
        -----
        Attributes
        ---
        subnet: str
            Validated subnet address, either v4 or v6, as input by user.
        mask: int
            Subnet mask.
        network: str
            Network address of subnet.
        networkcidr: str
            Network address of subnet in CIDR notation.
        broadcast: str
            Broadcast address of subnet.
        broadcastcidr: str
            Broadcast address of subnet in CIDR notation.
        iptype: str
            Either v4 or v6.
        info: dict
            Subnet info; network and broadcast addresses, nuber of IPs and IP range of subnet.
        expanded: str
            Expended version of IPv6 subnet address.
        contracted: str
            Contracted version of IPv6 subnet address.
        ips: list
            List of IP class objects that have been added to the Subnet object.
        -----
        Methods
        ---
        validate_address(address):
            Ensures user input is valid IP address.
        ip_type():
            Returns IP type; v4 or v6, of class.
        ipv6_expand():
            Given an IPv6 subnet address will return the expanded version of address.  Adds leading zeros and
            expands sets of zero hexadecatets that are contracted.
        binip():
            Returns binary version of subnet address.
        subnet_info():
            Returns dictionary that incudes the network address, broadcast address, number of available clients and
            client IP range.
        in_subnet(subnet):
            Given an IP returns True if IP in subnet or False if IP not in subnet.
        -----
    '''
    def __init__(self, subnet: str):
        '''
            Initialzing the Subnet class object.
            -----
            Parameters
            ---
            address: str
                Subnet address, either v4 or v6, in CIDR notation.
            -----
            Returns
            ---
            subnet: str
                Validated subnet address, either v4 or v6, as input by user.
            mask: int
                Subnet mask.
            network: str
                Network address of subnet.
            networkcidr: str
                Network address of subnet in CIDR notation.
            broadcast: str
                Broadcast address of subnet.
            broadcastcidr: str
                Broadcast address of subnet in CIDR notation.
            iptype: str
                Either 'v4' or 'v6' depending on IP type.
            info: dict
                Subnet info; network and broadcast addresses, nuber of IPs and IP range of subnet.
            expanded: str
                Expended version of IPv6 subnet address.
            contracted: str
                Contracted version of IPv6 subnet address.
            ips: list
                Empty list, IP class objects can be added to it, given they're in the Subnet.
        '''
        self.subnet = self.validate_address(subnet)
        self.mask = int(self.subnet.split('/')[1])
        self.network = bin2ip(self.binip()[0])
        self.networkcidr = self.network + f'/{self.mask}'
        self.broadcast = bin2ip(self.binip()[1])
        self.broadcastcidr = self.broadcast + f'/{self.mask}'
        self.iptype = self.ip_type()
        self.info = self.subnet_info()
        if self.iptype == 'v6':
            self.expanded = self.ipv6_expand(subnet)
            self.contracted = self.ipv6_contract(subnet)
        self.ips = []

    def validate_address(self, subnet: str):
        '''
            Validates a given subnet address, works for both IPv4 and IPv6.
            -----
            Parameters
            ---
            subnet: str
                Subnet address, either v4 or v6.
            -----
            Returns
            ---
            subnet: str
                Validated subnet address, either v4 or v6.
            -----
            Raises
            ---
            TyperError
                If input parameter is not of type string.
            ValueError
                If the network mask is invalid.  Expected values are between 0 and 32 for IPv4 and between 0 and 128 for IPv6.
                If the number of octets or hexadecatets is invalid.  Expected values are 4 and 8 for IPv4 and IPv6 respectively.
                If an invalid decimal or hexadecimal is provided. Expected decimal values are between 0 and 255 for IPv4 and expected hexadecial values are between 0 and ffff for IPv6.
                If an invalid IPv4 or IPv6 format is used.  Includes missing periods or colons as well as multiple zero contractions in IPv6.
        '''
        if type(subnet) == type(''):
            split_subnet = subnet.split('/')
            if len(split_subnet) == 2:
                network = split_subnet[0]
                mask = int(split_subnet[1])
                if '.' in network:
                    if mask not in range(0,33):
                        raise ValueError(f'Invalid IPv4 network mask: mask should be integer between 0 and 32. {mask} does not fall in that range.')
                    ip_split = network.split('.')
                    if len(ip_split) != 4:
                        raise ValueError(f'Wrong number of octets: there should be 4 octets.  The IP provided contains {len(ip_split)} octets.')
                    for octet in ip_split:
                        if int(octet) not in range(0,256):
                            raise ValueError(f'Invalid decimal value: each octet should be a decimal value between 0 and 255. {octet} does not fall in that range.')
                    return subnet
                elif ':' in network:
                    if mask not in range(0,129):
                        raise ValueError(f'Invalid IPv6 network mask: mask should be integer between 0 and 128. {mask} does not fall in that range.')
                    expanded = self.ipv6_expand(subnet).split('/')[0]
                    ip_split = expanded.split(':')
                    if len(ip_split) != 8:
                        raise ValueError(f'Wrong number of octets: there should be 8 hexadecatets.  The IP provided contains {len(ip_split)} hexadecatets.')
                    for hexadecatet in ip_split:
                        if int(hexadecatet, 16) not in range(0,65536):
                            raise ValueError(f'Invalid hexadecimal value: each hexadecatet should be a hexadecimal value between 0 and ffff. {hexadecatet} does not fall in that range.')
                    return subnet
                else:
                    raise ValueError(f'Invalid format: {subnet} is not a valid subnet format.')
            else:
                raise ValueError(f'Invalid format: {subnet} is not a valid subnet format.')
        else:
            raise TypeError(f'Subnet should be a string not a {type(subnet)}')
    
    def __str__(self) -> str:
        return self.networkcidr
    
    def __repr__(self) -> str:
        return self.networkcidr
    
    def ip_type(self) -> str:
        '''
            Given a subnet will return 'v4' if IPv4 or 'v6' if IPv6.
            -----
            Parameters
            ---
            self: Subnet class object
                Uses the subnet address of the class object.
            -----
            Returns
            ---
            iptype: str
                Subnet address type, either v4 or v6.
        '''
        if '.' in self.subnet:
            iptype = 'v4'
        elif ':' in self.subnet:
            iptype = 'v6'
        return iptype
    
    @staticmethod
    def ipv6_expand(subnet: str) -> str:
        '''
            Given a shortened IPv6 subnet address will return the unshortened version.
            -----
            Parameters
            ---
            address: str
                IPv6 subnet address.
            -----
            Returns
            ---
            expanded: str
                Expanded IPv6 subnet address.  Adds leading zeros and expands contraced zeros.
        '''
        address = subnet.split('/')[0]
        mask = subnet.split('/')[1]
        split = address.split(':')
        zeros = ['0000' for i in range(0,9-len(split))]
        new_split = []
        for hexadecatet in split:
            if hexadecatet == '':
                new_split += zeros
            elif hexadecatet == '0':
                new_split.append('0000')
            elif len(hexadecatet) < 4:
                for i in range(0,4-len(hexadecatet)):
                    hexadecatet = '0' + hexadecatet
                new_split.append(hexadecatet)
            else:
                new_split.append(hexadecatet)
        expanded = ':'.join(new_split) + '/' + mask
        return expanded
    
    @staticmethod
    def ipv6_contract(subnet: str) -> str:
        '''
            Given an unshortened IPv6 subnet address return contracted version.
            -----
            Parameters
            ---
            address: str
                IPv6 subnet address.
            -----
            Returns
            ---
            contracted: str
                Shortened IPv6 subnet address.  Removes leading zeros and contracts largest set of repeating zero hexadecatets.
        '''
        subnet_split = subnet.split('/')
        address = ipv6_expand(subnet_split[0])
        mask = subnet_split[1]
        ipv6_split = address.split(':')
        ipv6_contracted = []
        #Remove leading zeros
        for hexadecatet in ipv6_split:
            while hexadecatet[0] == '0' and len(hexadecatet) > 1:
                    hexadecatet = hexadecatet[1:]
            ipv6_contracted.append(hexadecatet)
        #Remove largest set of repeating zero hexadecatets
        #Find largest set of repeating zeros
        i=0
        replacing_zeros = []
        while i < 8:
            zeros = []
            if ipv6_contracted[i] == '0':
                zeros.append(i)
                j=1
                while ipv6_contracted[i+j] == '0':
                    zeros.append(i+j)
                    j+=1
                i+=j
                if len(zeros) >= len(replacing_zeros):
                    replacing_zeros = zeros
            else:
                i+=1
        #Replace first zeros with empty string and remove the rest
        ipv6_contracted[replacing_zeros[0]] = ''
        i = 0
        for item in replacing_zeros[1:]:
            ipv6_contracted.pop(item-i)
            i += 1
        contracted = ':'.join(ipv6_contracted) + '/' + mask
        return contracted
    
    def add_ip(self, ip):
        '''
            Add an IP class object to the Subnet if that IP is in said Subnet.
            -----
            Parameters
            ---
            ip: IP or str
                IP to be added, if string given will convert to IP object.
            -----
            Raises
            ---
            ValueError
                If the given IP is not in the Subnet.
        '''
        if type(ip) == type(''):
            ip = IP(ip)
        if self.in_subnet(ip.address):
            self.ips.append(ip)
        else:
            raise ValueError(f'Invalid IP address: {ip} is not a part of the subnet {self.networkcidr}.')
    
    def binip(self) -> str:
        '''
            Given a subnet will return the subnet network address, broadcast address and network mask in binary format.  Works for both IPv4 and IPv6.
            -----
            Parameters
            ---
            self: Subnet class object
                Uses the subnet address of the class object.
            -----
            Returns
            ---
            bin_network: str
                Network address in binary format.
            bin_broadcast: str
                Broadcast address in binary format.
            bin_mask: str
                Network mask in binary format.
        '''
        iptype = self.ip_type()
        network = self.subnet.split('/')[0]
        mask = self.mask
        bin_network = ''
        if iptype == 'v4':
            split_network = network.split('.')
            for octet in split_network:
                octet = format(int(octet), '08b')
                bin_network += octet
            bin_mask = ''.join(['1' if i < mask else '0' for i in range(0,32)])
        elif iptype == 'v6':
            network = ipv6_expand(network)
            split_network = network.split(':')
            for hexadecatet in split_network:
                hexadecatet = format(int(hexadecatet, 16), '016b')
                bin_network += hexadecatet
            bin_mask = ''.join(['1' if i < mask else '0' for i in range(0,128)])
        bin_broadcast = ''.join([bin_network[:mask],''.join(['1' for bit in bin_network[mask:]])])
        bin_network = ''.join([bin_network[:mask],''.join(['0' for bit in bin_network[mask:]])])
        return bin_network, bin_broadcast, bin_mask
    
    def in_subnet(self, ip: str) -> bool:
        '''
            Given an IP will return True if the IP is in the subnet, will return False if otherwise.  Works for both IPv4 and IPv6.
            -----
            Parameter
            ---
            subnet: str
                IP address, turns into IP class object for validation.
            -----
            Returns
            ---
            bool
                True if given IP is in the subnet, otherwise returns False.
        '''
        ip = IP(ip)
        iptype = ip.ip_type()
        subnettype = self.ip_type()
        if subnettype != iptype:
            raise ValueError('IP and subnet are not the same version.')
        else:
            bin_ip = ip.binip()
            bin_network = self.binip()[0]
            mask = int(self.mask)
            if bin_ip[:mask] == bin_network[:mask]:
                return True
            else:
                return False
            
    def subnet_info(self) -> dict:
        '''
            Returns the network address, broadcast address and number of client IPs available for the subnet.
            -----
            Parameters
            ---
            self: Subnet class object
            -----
            Returns
            ---
            subnet_info: dict
                Dictionary that includes the network address, broadcast address, number of client IPs available and the IP range of the subnet.
        '''
        bin_network, bin_broadcast, bin_mask = self.binip()
        clients = sum([2**bit for bit in range(0,bin_mask.count('0'))]) - 1
        network = bin2ip(bin_network)
        broadcast = bin2ip(bin_broadcast)
        first_ip = bin2ip(bin_network[:-1]+'1')
        last_ip = bin2ip(bin_broadcast[:-1]+'0')
        client_range = (first_ip, last_ip)
        info = {"Network":network, "Broadcast":broadcast, "Clients":clients, "Range":client_range}
        return info
    
    def ipgen(self, start:int = 1, end: int = 100, step: int = 1):
        '''
            Generator function to iterate over valid IPs of the subnet.
            -----
            Inputs
            ---
            start: int
                Index of IP to start from.
            end: int
                Index of IP to end at.
            step: int
                Step to iterate by.
            -----
            Yields
            ---
            IP class objects of Subnet.
            -----
            Defaults
            ---
            start: 1
                First IP of Subnet.
            end: 100
                Hundreth IP of subnet.
            step: 1
                Iterate through IPs one at a time.
        '''
        max = self.info['Clients']+1
        if self.iptype == 'v4':
            bits = '32'
        elif self.iptype == 'v6':
            bits = '128'
        if end > max:
            raise IndexError(f'{end} out of range, max index is {max}.')
        i = 0
        ip = format(int(ip2bin(self.info['Range'][0]), 2) + (start-1), f'0{bits}b')
        while i <= end:
            yield bin2ip(ip)
            i += step
            ip = format(int(ip, 2) + step, f'0{bits}b')
    
    @staticmethod
    def hex_range(first: str, last: str) -> list:
        '''
            Given the first and last hexadecimal values of a range returns a list of ReGex patterns to match each value of that range.
            -----
            Parameters
            ---
            first: str
                First hexadecimal value of the range.
            last: str
                Last hexadecimal value of the range.
            -----
            Returns
            ---
            ranges: list
                List of RegEx patterns that can be used to match every value in the given range.
        '''
        ranges = []
        if first[0] == last[0]:
            if first[1]==last[1]:
                if first[2]==last[2]:
                    #Section if the first threee values match
                    if first[3].isdigit() and last[3].isalpha():
                        first_range = f'{first[:3].lstrip("0")}[{first[3]}-9a-{last[3]}]'+'{0,1}'
                    else:
                        first_range = f'{first[:3].lstrip("0")}[{first[3]}-{last[3]}]'+'{0,1}'
                    ranges.append(first_range)
                else:
                    #Section if the first two values match
                    if first[3].isdigit():
                        first_range = f'{first[:3].lstrip("0")}[{first[3]}-9a-f]' + '{0,1}'
                    elif first[3].isalpha():
                        first_range = f'{first[:3].lstrip("0")}[{first[3]}-f]' + '{0,1}'
                    ranges.append(first_range)
                    if first[2].isdigit():
                        second_range = f'{first[:2].lstrip("0")}[{first[2]}-9a-f]' + '{0,1}[0-9a-f]{0,1}'
                    elif first[2].isalpha():
                        second_range = f'{first[:2].lstrip("0")}[{first[2]}-f]' + '{0,1}[0-9a-f]{0,1}'
                    ranges.append(second_range)
                    first_plus = int(first[2],16)+1
                    first_plus = f'{first_plus:01x}'
                    last_minus = int(last[2],16)-1
                    last_minus = f'{last_minus:01x}'
                    if first_plus.isdigit() and last_minus.isalpha():
                        fourth_range = f'{first[:2].lstrip("0")}[{first_plus}-9a-{last_minus}]'+'{1}[0-9a-f]{0,1}'
                    else:
                        fourth_range = f'{first[:2].lstrip("0")}[{first_plus}-{last_minus}]'+'{1}[0-9a-f]{0,1}'
                    ranges.append(fourth_range)
                    if last[3].isdigit():
                        fifth_range = f'{last[:3].lstrip("0")}[0-{last[3]}]' + '{0,1}'
                    elif last[3].isalpha():
                        fifth_range = f'{last[:3].lstrip("0")}[0-9a-{last[3]}]' + '{0,1}'
                    ranges.append(fifth_range)
            else:
                #section if the first values match
                if first[3].isdigit():
                    first_range = f'{first[:3].lstrip("0")}[{first[3]}-9a-f]' + '{0,1}'
                elif first[3].isalpha():
                    first_range = f'{first[:3].lstrip("0")}[{first[3]}-f]' + '{0,1}'
                ranges.append(first_range)
                if first[2].isdigit():
                    second_range = f'{first[:2].lstrip("0")}[{first[2]}-9a-f]' + '{1}[0-9a-f]{0,1}'
                elif first[2].isalpha():
                    second_range = f'{first[:2].lstrip("0")}[{first[2]}-f]' + '{1}[0-9a-f]{0,1}'
                ranges.append(second_range)
                first_plus = int(first[1],16)+1
                first_plus = f'{first_plus:01x}'
                last_minus = int(last[1],16)-1
                last_minus = f'{last_minus:01x}'
                if first_plus.isdigit() and last_minus.isalpha():
                    fourth_range = f'{first[:1].lstrip("0")}[{first_plus}-9a-{last_minus}]'+'{1}[0-9a-f]{0,2}'
                else:
                    fourth_range = f'{first[:1].lstrip("0")}[{first_plus}-{last_minus}]'+'{1}[0-9a-f]{0,2}'
                ranges.append(fourth_range)
                if last[3].isdigit():
                    fifth_range = f'{last[:3].lstrip("0")}[0-{last[3]}]' + '{0,1}'
                elif last[3].isalpha():
                    fifth_range = f'{last[:3].lstrip("0")}[0-9a-{last[3]}]' + '{0,1}'
                ranges.append(fifth_range)
                if last[2].isdigit():
                    sixth_minus = str(int(last[2])-1)
                    sixth_range = f'{last[:2].lstrip("0")}[0-{sixth_minus}]' + '{0,1}[0-9a-f]{0,1}'
                elif last[2].isalpha():
                    sixth_minus = int(last[2],16)-1
                    sixth_minus = f'{sixth_minus:01x}'
                    sixth_range = f'{last[:2].lstrip("0")}[0-9a-{sixth_minus}]' + '{0,1}[0-9a-f]{0,1}'
                ranges.append(sixth_range)
        else:
            #Section if all four values are different
            if first[3].isdigit():
                first_range = f'{first[:3].lstrip("0")}[{first[3]}-9a-f]' + '{0,1}'
            elif first[3].isalpha():
                first_range = f'{first[:3].lstrip("0")}[{first[3]}-f]' + '{0,1}'
            ranges.append(first_range)
            if first[2].isdigit():
                second_range = f'{first[:2].lstrip("0")}[{first[2]}-9a-f]' + '{0,1}[0-9a-f]{0,1}'
            elif first[2].isalpha():
                second_range = f'{first[:2].lstrip("0")}[{first[2]}-f]' + '{1}[0-9a-f]{0,1}'
            ranges.append(second_range)
            if first[1].isdigit():
                third_range = f'{first[:1].lstrip("0")}[{first[1]}-9a-f]' + '{1}[0-9a-f]{0,2}'
            elif first[1].isalpha():
                third_range = f'{first[:1].lstrip("0")}[{first[1]}-f]' + '{1}[0-9a-f]{0,2}'
            ranges.append(third_range)
            first_plus = int(first[0],16)+1
            first_plus = f'{first_plus:01x}'
            last_minus = int(last[0],16)-1
            last_minus = f'{last_minus:01x}'
            if first_plus.isdigit() and last_minus.isalpha():
                fourth_range = f'[{first_plus}-9a-{last_minus}]'+'{0,1}[0-9a-f]{0,3}'
            else:
                fourth_range = f'[{first_plus}-{last_minus}]'+'{0,1}[0-9a-f]{0,3}'
            ranges.append(fourth_range)
            if last[3].isdigit():
                fifth_range = f'{last[:3].lstrip("0")}[0-{last[3]}]' + '{0,1}'
            elif last[3].isalpha():
                fifth_range = f'{last[:3].lstrip("0")}[0-9a-{last[3]}]' + '{0,1}'
            ranges.append(fifth_range)
            if last[2].isdigit():
                sixth_minus = str(int(last[2])-1)
                sixth_range = f'{last[:2].lstrip("0")}[0-{sixth_minus}]' + '{0,1}[0-9a-f]{0,1}'
            elif last[2].isalpha():
                sixth_minus = int(last[2],16)-1
                sixth_minus = f'{sixth_minus:01x}'
                sixth_range = f'{last[:2].lstrip("0")}[0-9a-{sixth_minus}]' + '{1}[0-9a-f]{0,1}'
            ranges.append(sixth_range)
            if last[1].isdigit():
                seventh_minus = str(int(last[1])-1)
                seventh_range = f'{last[:1].lstrip("0")}[0-{seventh_minus}]' + '{1}[0-9a-f]{0,2}'
            elif last[1].isalpha():
                seventh_minus = int(last[1],16)-1
                seventh_minus = f'{seventh_minus:01x}'
                seventh_range = f'{last[:1].lstrip("0")}[0-9a-{seventh_minus}]' + '{1}[0-9a-f]{0,2}'
            ranges.append(seventh_range)
        return ranges

    @staticmethod
    def toRegexv6(subnet: str, or_logic: str = '|') -> str:
        '''
            Returns a RegEx pattern to match the given IPv6 subnet.
            -----
            Parameters
            ---
            subnet: Subnet class object
                Subnet to get RegEx pattern of.
            or_logic: str
                Symbol to be used as OR, default it |.
            -----
            Returns
            ---
            regex: str
                RegEx pattern to match every IP address in the given IPv6subnet.
        '''
        subnet_split = subnet.split('/')
        ipv6, mask = subnet_split[0], int(subnet_split[1])
        ipv6 = ipv6_expand(ipv6)
        ipv6_split = ipv6.split(':')
        bin_ipv6 = ''
        for item in ipv6_split:
            item = int(item, 16)
            item = f'{item:016b}'
            bin_ipv6 += item
        #Find which octet, and at which bit of the octet, is being divided by the mask
        octet, bit = divmod(mask, 16)
        #Build the RegEx pattern
        regex = ''
        base_pattern = ''
        for i in range(0,octet):
            if ipv6_split[i] == '0000':
                base_pattern += '[0]{0,1}' + ':'
            else:
                octet_stripped = ipv6_split[i].lstrip('0')
                base_pattern += octet_stripped + ':'
        #If bit=0 then no octet is divided and we can build the RegEx pattern
        if bit == 0:
            base_pattern += '.*/'
            regex = '/' + base_pattern
        else:
            #Get the first and last values of the octet that is divided
            divided = ipv6_split[octet+1]
            divided = int(divided, 16)
            divided = f'{divided:016b}'
            unchanged = divided[:bit]
            changed = divided[bit-16:]
            first = unchanged
            last = unchanged
            for i in range(0, len(changed)):
                first += '0'
                last += '1'
            first = int(first, 2)
            first = f'{first:04x}'
            last = int(last, 2)
            last = f'{last:04x}'
            #Get the RegEx ranges for the divided octet
            ranges = hex_range(first, last)
            full_ranges = ['/' + base_pattern + range + ':.*/' for range in ranges]
            regex = f'{or_logic}'.join(full_ranges)
        return regex

    @staticmethod
    def toRegexv4(subnet: str, or_logic: str = '|') -> str:
        '''
            Returns a RegEx pattern to match the given IPv4 subnet.  Written by Zephyr Zink.
            -----
            Parameters
            ---
            subnet: Subnet class object
                Subnet to get RegEx pattern of.
            or_logic: str
                Symbol to be used as OR, default it |.
            -----
            Returns
            ---
            regex: str
                RegEx pattern to match every IP address in the given IPv4 subnet.
        '''
        subnet_split=subnet.split('.')
        mask=int(subnet_split[3].split('/')[1])
        first_octet=int(subnet_split[0])
        second_octet=int(subnet_split[1])
        third_octet=int(subnet_split[2])
        fourth_octet=int(subnet_split[3].split('/')[0])

        start=0
        final=0

        expressions_list=[]
        if mask == 8:
            expressions_list.append(str(first_octet)+'.*')

        if mask == 16:
            expressions_list.append(str(first_octet)+'.'+str(second_octet)+'.*')

        if mask == 24:
            expressions_list.append(str(first_octet)+'.'+str(second_octet)+'.'+str(third_octet)+'.*')

        if mask in (9,10,11,12,13,14,15):
            begin_ex='/'+str(first_octet)+'.'
            end_ex='.[0-9]{1,3}.[0-9]{1,3}/'
            start=second_octet

        if mask in (17,18,19,20,21,22,23):
            begin_ex='/'+str(first_octet)+'.'+str(second_octet)+'.'
            end_ex='.[0-9]{1,3}/'
            start=third_octet

        if mask in (25,26,27,28,29,30,31,32):
            begin_ex='/'+str(first_octet)+'.'+str(second_octet)+'.'+str(third_octet)+'.'
            end_ex='/'
            start=fourth_octet

        if mask in (9,17,25):
            final=start+127
        elif mask in (10,18,26):
            final=start+63
        elif mask in (11,19,27):
            final=start+31
        elif mask in (12,20,28):
            final=start+15
        elif mask in (13,21,29):
            final=start+7
        elif mask in (14,22,30):
            final=start+3
        elif mask in (15,23,31):
            final=start+1
        elif mask in (16,24,32):
            final=start

        one_p=[]
        ten_p=[]
        hund_p=[]
        twohun_p=[]
        list_of_searches=[]

        for i in range(start,final+1):
            if i < 10:
                one_p.append(i)
            elif i >= 10 and i <100:
                ten_p.append(i)
            elif i >=100 and i < 200:
                hund_p.append(i)
            elif i>=200:
                twohun_p.append(i)

        if len(one_p)>0:
            list_of_searches.append('['+str(one_p[0])+'-'+str(one_p[len(one_p)-1])+']')

        if len(ten_p)>0:
            if int(ten_p[len(ten_p)-1]/10)-int(ten_p[0]/10)==0:
                list_of_searches.append('['+str(int(ten_p[0]/10))+']['+str(ten_p[0]%10)+'-'+str(ten_p[len(ten_p)-1]%10)+']')
            elif int(ten_p[len(ten_p)-1]/10)-int(ten_p[0]/10)==1:
                list_of_searches.append('['+str(int(ten_p[0]/10))+']['+str(ten_p[0]%10)+'-9]')
                list_of_searches.append('['+str(int(ten_p[len(ten_p)-1]/10))+'][0-'+str(ten_p[len(ten_p)-1]%10)+']')
            elif int(ten_p[len(ten_p)-1]/10)-int(ten_p[0]/10)==2:
                list_of_searches.append('['+str(int(ten_p[0]/10))+']['+str(ten_p[0]%10)+'-9]')
                list_of_searches.append('['+str(int(ten_p[0]/10)+1)+'][0-9]')
                list_of_searches.append('['+str(int(ten_p[len(ten_p)-1]/10))+'][0-'+str(ten_p[len(ten_p)-1]%10)+']')
            elif int(ten_p[len(ten_p)-1]/10)-int(ten_p[0]/10)>=3:
                list_of_searches.append('['+str(int(ten_p[0]/10))+']['+str(ten_p[0]%10)+'-9]')
                list_of_searches.append('['+str(int(ten_p[0]/10)+1)+'-'+str(int(ten_p[len(ten_p)-1]/10)-1)+'][0-9]')
                list_of_searches.append('['+str(int(ten_p[len(ten_p)-1]/10))+'][0-'+str(ten_p[len(ten_p)-1]%10)+']')

        if len(hund_p)>0:
            for i in range(0,len(hund_p)):
                hund_p[i]=hund_p[i]-100
            if int(hund_p[len(hund_p)-1]/10)-int(hund_p[0]/10)==0:
                list_of_searches.append('[1]['+str(int(hund_p[0]/10))+']['+str(hund_p[0]%10)+'-'+str(hund_p[len(hund_p)-1]%10)+']')
            elif int(hund_p[len(hund_p)-1]/10)-int(hund_p[0]/10)==1:
                list_of_searches.append('[1]['+str(int(hund_p[0]/10))+']['+str(hund_p[0]%10)+'-9]')
                list_of_searches.append('[1]['+str(int(hund_p[len(hund_p)-1]/10))+'][0-'+str(hund_p[len(hund_p)-1]%10)+']')
            elif int(hund_p[len(hund_p)-1]/10)-int(hund_p[0]/10)==2:
                list_of_searches.append('[1]['+str(int(hund_p[0]/10))+']['+str(hund_p[0]%10)+'-9]')
                list_of_searches.append('[1]['+str(int(hund_p[0]/10)+1)+'][0-9]')
                list_of_searches.append('[1]['+str(int(hund_p[len(hund_p)-1]/10))+'][0-'+str(hund_p[len(hund_p)-1]%10)+']')
            elif int(hund_p[len(hund_p)-1]/10)-int(hund_p[0]/10)>=3:
                list_of_searches.append('[1]['+str(int(hund_p[0]/10))+']['+str(hund_p[0]%10)+'-9]')
                list_of_searches.append('[1]['+str(int(hund_p[0]/10)+1)+'-'+str(int(hund_p[len(hund_p)-1]/10)-1)+'][0-9]')
                list_of_searches.append('[1]['+str(int(hund_p[len(hund_p)-1]/10))+'][0-'+str(hund_p[len(hund_p)-1]%10)+']')

        if len(twohun_p)>0:
            for i in range(0,len(twohun_p)):
                twohun_p[i]=twohun_p[i]-200
            if int(twohun_p[len(twohun_p)-1]/10)-int(twohun_p[0]/10)==0:
                list_of_searches.append('[2]['+str(int(twohun_p[0]/10))+']['+str(twohun_p[0]%10)+'-'+str(twohun_p[len(twohun_p)-1]%10)+']')
            elif int(twohun_p[len(twohun_p)-1]/10)-int(twohun_p[0]/10)==1:
                list_of_searches.append('[2]['+str(int(twohun_p[0]/10))+']['+str(twohun_p[0]%10)+'-9]')
                list_of_searches.append('[2]['+str(int(twohun_p[len(twohun_p)-1]/10))+'][0-'+str(twohun_p[len(twohun_p)-1]%10)+']')
            elif int(twohun_p[len(twohun_p)-1]/10)-int(twohun_p[0]/10)==2:
                list_of_searches.append('[2]['+str(int(twohun_p[0]/10))+']['+str(twohun_p[0]%10)+'-9]')
                list_of_searches.append('[2]['+str(int(twohun_p[0]/10)+1)+'][0-9]')
                list_of_searches.append('[2]['+str(int(twohun_p[len(twohun_p)-1]/10))+'][0-'+str(twohun_p[len(twohun_p)-1]%10)+']')
            elif int(twohun_p[len(twohun_p)-1]/10)-int(twohun_p[0]/10)>=3:
                list_of_searches.append('[2]['+str(int(twohun_p[0]/10))+']['+str(twohun_p[0]%10)+'-9]')
                list_of_searches.append('[2]['+str(int(twohun_p[0]/10)+1)+'-'+str(int(twohun_p[len(twohun_p)-1]/10)-1)+'][0-9]')
                list_of_searches.append('[2]['+str(int(twohun_p[len(twohun_p)-1]/10))+'][0-'+str(twohun_p[len(twohun_p)-1]%10)+']')

        for items in list_of_searches:
            if mask in (8,16,24):
                pass
            else:
                expressions_list.append(begin_ex+items+end_ex)
        regex =f'{or_logic}'.join([ranget for ranget in expressions_list])
        return regex
    
    def toRegex(self, or_logic: str = '|') -> str:
        '''
            Returns a RegEx pattern to match the given subnet.  Works for both IPv4 and IPv6.
            -----
            Parameters
            ---
            subnet: Subnet class object
                Subnet to get RegEx pattern of.
            or_logic: str
                Symbol to be used as OR, default it |.
            -----
            Returns
            ---
            regex_pattern: str
                RegEx pattern to match every IP address in the given subnet.
        '''
        if self.ip_type() == 'v4':
            regex_pattern = self.toRegexv4(self.address, or_logic)
        elif self.ip_type() == 'v6':
            regex_pattern = self.toRegexv6(self.address, or_logic)
        return regex_pattern