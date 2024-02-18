import re

def decode16(string):
    '''
    ("b'xe5xb0x8fxe6xb5xb7xe7xbbxb5xf0x9fxa7xbd'")=>龙良雨
    ("龙良雨")=>龙良雨
    '''
    try:
        # 去掉最外层的""
        hex_string = eval(string).decode('utf8')
        # 使用正则表达式找到所有的十六进制编码
        hex_values = re.findall(r'x[0-9a-fA-F]{2}', hex_string)
        # 将十六进制编码转换为整数，然后使用bytes.fromhex将其转换为字节数据
        byte_data = bytes.fromhex(''.join([hex_val[1:] for hex_val in hex_values]))
        # 将字节数据解码为字符串
        decoded_text = byte_data.decode('utf-8')
        return decoded_text
    except NameError:
        return string
