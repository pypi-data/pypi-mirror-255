class Bytes:
    @staticmethod
    def int_array_to_bytes(int_array):
        return bytes(int_array)

    @staticmethod
    def bytes_to_int_array(byte_data):
        return [byte for byte in byte_data]

    @staticmethod
    def hex_string_to_bytes(hex_string):
        return bytes.fromhex(hex_string)

    @staticmethod
    def bytes_to_hex_string(byte_data):
        return byte_data.hex()

    @staticmethod
    def byte_length(byte_data):
        return len(byte_data)

    @staticmethod
    def byte_concatenate(byte_data1, byte_data2):
        return byte_data1 + byte_data2

    @staticmethod
    def byte_slice(byte_data, start, end):
        return byte_data[start:end]

    @staticmethod
    def byte_to_ascii(byte_data):
        return byte_data.decode('utf-8')

    @staticmethod
    def find_substring(byte_data, sub_byte_data):
        return byte_data.find(sub_byte_data)

    @staticmethod
    def replace_substring(byte_data, sub_byte_data, replacement_byte_data):
        return byte_data.replace(sub_byte_data, replacement_byte_data)

    @staticmethod
    def count_substring(byte_data, sub_byte_data):
        return byte_data.count(sub_byte_data)

    @staticmethod
    def byte_to_base64(byte_data):
        import base64
        return base64.b64encode(byte_data)

    @staticmethod
    def byte_to_binary(byte_data):
        return ''.join(format(byte, '08b') for byte in byte_data)

    @staticmethod
    def binary_to_byte(binary_string):
        return bytes(int(binary_string[i:i + 8], 2) for i in range(0, len(binary_string), 8)

    @staticmethod
    def byte_to_utf16le(byte_data):
        return byte_data.decode('utf-16le', errors='ignore')

    @staticmethod
    def string_to_bytes(text):
        return text.encode('utf-8')

    @staticmethod
    def bytes_to_string(byte_data):
        return byte_data.decode('utf-8')

    @staticmethod
    def byte_xor(byte_data1, byte_data2):
        return bytes(b1 ^ b2 for b1, b2 in zip(byte_data1, byte_data2)

    @staticmethod
    def byte_and(byte_data1, byte_data2):
        return bytes(b1 & b2 for b1, b2 in zip(byte_data1, byte_data2)

    @staticmethod
    def byte_or(byte_data1, byte_data2):
        return bytes(b1 | b2 for b1, b2 in zip(byte_data1, byte_data2)

    @staticmethod
    def byte_not(byte_data):
        return bytes(~b for b in byte_data)

    @staticmethod
    def bytes_to_int(byte_data, byteorder='big'):
        return int.from_bytes(byte_data, byteorder)

    @staticmethod
    def int_to_bytes(value, length, byteorder='big'):
        return value.to_bytes(length, byteorder)

    @staticmethod
    def reverse_bytes(byte_data):
        return byte_data[::-1]

    @staticmethod
    def rotate_left(byte_data, n):
        n = n % 8
        return bytes((byte << n) | (byte >> (8 - n)) for byte in byte_data)

    @staticmethod
    def rotate_right(byte_data, n):
        n = n % 8
        return bytes((byte >> n) | (byte << (8 - n)) for byte in byte_data)

    @staticmethod
    def byte_mean(byte_data1, byte_data2):
        return bytes((b1 + b2) // 2 for b1, b2 in zip(byte_data1, byte_data2)

    @staticmethod
    def sum_of_bytes(byte_data):
        return sum(byte_data)

    @staticmethod
    def byte_max(byte_data):
        return max(byte_data)

    @staticmethod
    def byte_min(byte_data):
        return min(byte_data)

    @staticmethod
    def is_subset(sub_byte_data, byte_data):
        return all(sub_byte in byte_data for sub_byte in sub_byte_data)

    @staticmethod
    def count_values(byte_data):
        from collections import Counter
        return Counter(byte_data)

    @staticmethod
    def bytes_to_ipv4(byte_data):
        return ".".join(map(str, byte_data)

    @staticmethod
    def ipv4_to_bytes(ipv4_string):
        return bytes(map(int, ipv4_string.split("."))

    @staticmethod
    def xor_encrypt(byte_data, key):
        return bytes(b ^ k for b, k in zip(byte_data, key))

    @staticmethod
    def xor_decrypt(byte_data, key):
        return bytes(b ^ k for b, k in zip(byte_data, key))

    @staticmethod
    def bytes_to_ipv6(byte_data):
        from ipaddress import IPv6Address
        return IPv6Address(byte_data)

    @staticmethod
    def ipv6_to_bytes(ipv6_string):
        from ipaddress import IPv6Address
        return bytes(IPv6Address(ipv6_string).packed)

    @staticmethod
    def bytes_to_float(byte_data):
        import struct
        return struct.unpack('f', byte_data)[0]

    @staticmethod
    def float_to_bytes(value):
        import struct
        return struct.pack('f', value)

    @staticmethod
    def bytes_to_double(byte_data):
        import struct
        return struct.unpack('d', byte_data)[0]

    @staticmethod
    def double_to_bytes(value):
        import struct
        return struct.pack('d', value)

    @staticmethod
    def bytes_to_boolean(byte_data):
        import struct
        return struct.unpack('?', byte_data)[0]

    @staticmethod
    def boolean_to_bytes(value):
        import struct
        return struct.pack('?', value)
