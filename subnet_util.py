from enum import Enum
import re


class SubnetNotation(Enum):
    BIN = "bin"
    DEC = "dec"
    HEX = "hex"
    CLASS = "class"
    CIDR = "cidr"


def _convert_subnet_hex_dec(hex_str: str) -> str:
    hex_int = int(hex_str, 16)
    mask = 0x000000ff
    return ".".join(map(str, [mask & (hex_int >> 24), mask & (hex_int >> 16), mask & (hex_int >> 8), mask & hex_int]))


def _convert_subnet_dec_cidr(dec_str: str) -> str:
    return f"{sum(bin(int(x)).count('1') for x in dec_str.split('.'))}"


def _convert_subnet_cidr_dec(cidr_str: str) -> str:
    return '.'.join([str((0xffffffff << (32 - cidr_str) >> i) & 0xff) for i in [24, 16, 8, 0]])


def _get_subnet_type(input_val) -> SubnetNotation:
    if input_val in ['A', 'B', 'C']:
        return SubnetNotation.CLASS
    elif input_val[:2] == '0x':
        return SubnetNotation.BIN
    elif "/" in input_val:
        return SubnetNotation.CIDR
    elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', input_val):
        return SubnetNotation.DEC
    elif re.match(r'^[a-f|0-9]{0,4}\:[a-f|0-9]{0,4}\:[a-f|0-9]{0,4}\:[a-f|0-9]{0,4}\:[a-f|0-9]{0,4}\:[a-f|0-9]{0,4}\$',
                  input_val):
        return SubnetNotation.HEX
    else:
        raise SyntaxError("Unable to determine subnet address notation")


def convert_subnet(input_val: str, to_type: SubnetNotation) -> str:
    from_type = _get_subnet_type(input_val)
    if from_type == SubnetNotation.CIDR and to_type == SubnetNotation.CIDR:
        return input_val.split("/")[-1]
    elif from_type == SubnetNotation.HEX and to_type == SubnetNotation.DEC:
        return _convert_subnet_hex_dec(input_val)
    elif from_type == SubnetNotation.DEC and to_type == SubnetNotation.CIDR:
        return _convert_subnet_dec_cidr(input_val)
    elif from_type == SubnetNotation.CIDR and to_type == SubnetNotation.DEC:
        return _convert_subnet_cidr_dec(input_val)
    else:
        raise NotImplementedError(f"Conversion from {from_type} to {to_type} not yet supported")
