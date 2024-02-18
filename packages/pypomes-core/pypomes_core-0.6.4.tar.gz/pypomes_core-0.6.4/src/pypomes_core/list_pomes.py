def list_compare(list1: list[any], list2: list[any]) -> bool:
    """
    Compare the contents of the two lists *list1* e *list2*.

    Return *True* if all the elements in *list1* are also in *list2*, and vice-versa, with the same cardinality.

    :param list1: the first list
    :param list2: the second list
    :return: True if the two lists contain the same elements, in the same quantity, in any order
    """
    # initialize the return variable
    result: bool = True

    # are the input parameters lists containing the same number of elements ?
    if isinstance(list1, list) and isinstance(list2, list) and len(list1) == len(list2):
        # yes, verify whether all elements in 'list1' are also in 'list2', in the same quantity
        for elem in list1:
            # is 'elem' in both lists, in thew same quantity ?
            if list1.count(elem) != list2.count(elem):
                # no, the lists are not equal
                result = False
                break
    else:
        # no, the lists are not equal
        result = False

    return result


def list_flatten(source: list[str]) -> str:
    """
    Transforma uma lista de *str* em uma *str* consistindo na concatenação com "." dos elementos da lista.

    Exemplos:
        - ['1', '2', '']     -> '1.2.'
        - ['', 'a', 'b']     -> '.a.b'
        - ['x', '', '', 'y'] -> 'x...y'
        - ['z']              -> 'z'

    :param source: a lista de strings
    :return: a string concatenada
    """
    result: str = ""
    for item in source:
        result += "." + item
    return result[1:]


def list_unflatten(source: str) -> list[str]:
    """
    Transforma uma *str* contendo elementos concatenados por "." em uma lista de *str*.

    Essa lista contem os sub_elementos extraídos. Exemplos:
        - '1.2.'  -> ['1', '2', '']
        - '.a.b'  -> ['', 'a', 'b']
        - 'x...y' -> ['x', '', '', 'y']
        - 'z'     -> ['z']

    :param source: string com elementos concatenados por "."
    :return: a lista de strings contendo os elementos da concatenação
    """
    # import the needed function
    from .str_pomes import str_split_on_mark

    return str_split_on_mark(source, ".")


def list_find_coupled(coupled_elements: list[tuple[str, str]], primary_element: str) -> str:
    """
    Localiza em *coupled_elements* o elemento acoplado ao *primary_element* dado.

    Se *primary_element* contiver indicação de índice (denotado por *[<pos>]*), essa indicação é removida.
    Essa função é utilizada na transformação de *dicts* (*dict_transform*) e *lists* (*list_transform*),
    a partir de sequências de pares de chaves.

    :param coupled_elements: a lista de tuplas contendo os pares de elementos.
    :param primary_element: o elemento primário
    :return: o elemento acoplado, ou None se não for encontrado
    """
    # remove a indicação de elemento de lista
    pos1: int = primary_element.find("[")
    while pos1 > 0:
        pos2: int = primary_element.find("]", pos1)
        primary_element = primary_element[:pos1] + primary_element[pos2+1:]
        pos1 = primary_element.find("[")

    # inicializa a variável de retorno
    result: str | None = None

    # percorre a list de elementos acoplados
    for primary, coupled in coupled_elements:
        # o elemento primário foi encontrado ?
        if primary == primary_element:
            # sim, retorne o elemento acoplado correspondente
            result = coupled
            break

    return result


def list_transform(source: list[any], from_to_keys: list[tuple[str, str]],
                   prefix_from: str = None, prefix_to: str = None) -> list[any]:
    """
    Constrói uma nova *list*, transformando elementos do tipo *list* e *dict* encontrados em *source*.

    A conversão dos elementos tipo *dict* está documentada na função *dict_transform*.

    Os prefixos para as chaves de origem e de destino, se definidos, tem tratamentos distintos.
    São acrescentados na busca de valores em *Source*, e removidos na atribuição de valores
    ao *dict* de retorno.

    :param source: o dict de origem dos valores
    :param from_to_keys: a lista de tuplas contendo as sequências de chaves de origem e destino
    :param prefix_from: prefixo a ser acrescentado às chaves de origem
    :param prefix_to: prefixo a ser removido das chaves de destino
    :return: a nova lista
    """
    # import the needed function
    from .dict_pomes import dict_transform

    # inicializa a variável de retorno
    result: list[any] = []

    # percorre a lista de origem
    for inx, value in enumerate(source):
        if prefix_from is None:
            from_keys: None = None
        else:
            from_keys: str = f"{prefix_from}[{inx}]"

        # obtem o valor de destino
        if isinstance(value, dict):
            to_value: dict = dict_transform(value, from_to_keys, from_keys, prefix_to)
        elif isinstance(value, list):
            to_value: list = list_transform(value, from_to_keys, from_keys, prefix_to)
        else:
            to_value: any = value

        # acrescenta o valor transformado ao resultado
        result.append(to_value)

    return result


def list_elem_starting_with(source: list[str | bytes],
                            prefix: str | bytes, keep_prefix: bool = True) -> str | bytes:
    """
    Localiza e retorna o primeiro elemento em *source* prefixado por *prefix*.

    Retorna *None* se esse elemento não for encontrado.

    :param source: a lista a ser inspecionada
    :param prefix: o dado prefixando o elemento a ser retornado
    :param keep_prefix: define se o elemento encontrado deve ou não ser retornado com o prefixo
    :return: o elemento prefixado, com ou sem o prefixo
    """
    # inicializa a variável de retorno
    result: str | bytes | None = None

    # percorre a lista de origem
    for elem in source:
        if elem.startswith(prefix):
            if keep_prefix:
                result = elem
            else:
                result = elem[len(prefix)+1:]
            break

    return result
