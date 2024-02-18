def str_sanitize(target_str: str) -> str:
    """
    Clean the given *target_str* string.

    The sanitization is carried out by:
        - removing backslashes
        - replacing double quotes with single quotes
        - replacing newlines and tabs with whitespace
        - replacing multiple consecutive spaces with a single space

    :param target_str: the string to be cleaned
    :return: the cleaned string
    """
    cleaned: str = target_str.replace("\\", "") \
                             .replace('"', "'") \
                             .replace("\n", " ") \
                             .replace("\t", " ")
    return " ".join(cleaned.split())


def str_split_on_mark(source: str, mark: str) -> list[str]:
    """
    Extrai, de *source*, os segmentos de texto separados por *mark*, e os retorna em uma lista.

    Os segmentos retornados não contem o separador.

    :param source: o texto de referência
    :param mark: o separador
    :return: a lista de segmentos de texto obtidos
    """
    # inicializa a variável de retorno
    result: list[str] = []

    pos: int = 0
    skip: int = len(mark)
    after: int = source.find(mark)
    while after >= 0:
        result.append(source[pos:after])
        pos = after + skip
        after = source.find(mark, pos)
    if pos < len(source):
        result.append(source[pos:])
    else:
        result.append("")

    return result


def str_between(source: str, from_str: str, to_str: str) -> str:
    """
    Extrai e retorna a *substring* em *source* localizada entre os delimitadores *from_st* e *to_str*.

    Retorna *None* se essa extração não for possível.

    :param source: a string a ser pesquisada
    :param from_str: o delimitador inicial
    :param to_str: o delimitador final
    :return: a substring procurada
    """
    # inicializa a variável de retorno
    result: str | None = None

    pos1: int = source.find(from_str)
    if pos1 >= 0:
        pos1 += len(from_str)
        pos2: int = source.find(to_str, pos1)
        if pos2 >= pos1:
            result = source[pos1:pos2]

    return result


def str_find_whitespace(source: str) -> int:
    """
    Localiza e retorna a posição da primeira ocorrência de *whitespace* em *source*.

    Retorna *-1* se nenhum *whitespace* for encontrado.

    :param source: a string a ser pesquisada
    :return: a posição do primeiro whitespace encontrado
    """
    # inicializa a variável de retorno
    result: int = -1

    # busca por whitespace
    for inx, char in enumerate(source):
        if char.isspace():
            result = inx
            break

    return result
