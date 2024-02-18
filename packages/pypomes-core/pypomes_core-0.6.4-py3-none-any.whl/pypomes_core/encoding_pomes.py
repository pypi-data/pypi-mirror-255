def encode_ascii_hex(source: bytes) -> bytes:
    r"""
    Codifica o conteúdo binário em texto.

    Essa codificação é feita com caracteres para bytes no intervalo ASCII,
    com a representação *backslash-escaped* para os caracteres especiais LF, HT, CR, VT, FF e BS,
    e com a representação *\\xNN* para os demais (onde *N* é um dígito hexadecimal [0-9] e [a-f]).

    :param source: o conteúdo binário a ser codificado
    :return: o conteúdo texto codificado
    """
    # inicializa a variável de retorno
    result: bytes = b""

    # percorre source, codificando os bytes não-ASCII
    pos: int = 0
    while pos < len(source):
        char: bytes = source[pos:pos+1]
        if char != b"\\" and b" " <= char <= b"~":
            result += char                                  # char   - ASCII char, less the backslah
        else:
            byte_str: str
            match char:
                case b"\\":
                    byte_str = "\\\\"                       # \,  \\ - backslash
                case b"\x0A":
                    byte_str = "\\n"                        # LF, \n - line feed
                case b"\x0D":
                    byte_str = "\\r"                        # CR, \r - carriage return
                case b"\x09":
                    byte_str = "\\t"                        # HT, \t - horizontal tab
                case b"\x0B":
                    byte_str = "\\v"                        # VT, \v - vertical tab
                case b"\x0C":
                    byte_str = "\\f"                        # FF, \f  - form feed
                case b"\x08":
                    byte_str = "\\b"                        # BS, \b - backspace
                case _:
                    int_char = int.from_bytes(char, "little")
                    lower_char: int = int_char % 16             # \xNN
                    upper_char: int = round((int_char - lower_char) / 16)
                    byte_str = "\\x" + hex(upper_char)[2:] + hex(lower_char)[2:]
            result += byte_str.encode()
        pos += 1

    return result


def decode_ascii_hex(source: bytes) -> bytes:
    r"""
    Decodifica em binário o conteúdo texto.

    Essa decodificação é feita para texto codificado com caracteres para bytes no intervalo ASCII,
    com a representação *backslash-escaped* para os caracteres especiais LF, HT, CR, VT, FF e BS,
    e com a representação *\\xNN* para os demais (onde *N* é um dígito hexadecimal [0-9] e [a-f]).

    :param source: o conteúdo texto a ser decodificado
    :return: o conteúdo binário decodificado
    """
    # inicializa a variável de retorno
    result: bytes = b""

    # percorre source, decodificando as ocorrências de "\"
    byte_val: bytes
    pos1: int = 0
    # localiza o primeiro "\"
    pos2: int = source.find(b"\\")
    while pos2 >= 0:
        result += source[pos1:pos2]
        next_byte: bytes = source[pos2+1:pos2+2]
        shift: int = 2
        match next_byte:
            case b"x":
                # "\x" prefixa um character denotado por string hexadecimal ("\x00" a "\xff")
                # HAZARD: chars intermediários necessários - int(byte) quebra para byte > b"\x09"
                upper_char: str = source[pos2+2:pos2+3].decode()
                lower_char: str = source[pos2+3:pos2+4].decode()
                int_val: int = 16 * int(upper_char, base=16) + int(lower_char, base=16)
                byte_val = bytes([int_val])
                shift = 4
            case b"n":
                byte_val = b"\x0A"                  # LF, \n - line feed
            case b"r":
                byte_val = b"\x0D"                  # CR, \r - carriage return
            case b"t":
                byte_val = b"\x09"                  # HT, \t - horizontal tab
            case b"v":
                byte_val = b"\x0B"                  # VT, \v - vertical tab
            case b"f":
                byte_val = b"\x0C"                  # FF, \f - form feed
            case b"b":
                byte_val = b"\x08"                  # BS, \b  - backspace
            case _:
                byte_val = source[pos2+1:pos2+2]    # o byte seguinte ao "\"
        pos1 = pos2 + shift
        result += byte_val
        # localiza o próximo "\"
        pos2 = source.find(b"\\", pos1)
    result += source[pos1:]

    return result
