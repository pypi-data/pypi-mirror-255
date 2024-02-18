from pathlib import Path
from typing import Final
from xmltodict3 import XmlTextToDict

XML_FILE_HEADER: Final[str] = '<?xml version="1.0" encoding="UTF-8" ?>'


def xml_normalize_keys(source: dict) -> dict:
    """
    Clona o *source*, removenda os *namespaces* e os prefixos *'@'* e *'#'* nos nomes de suas chaves.

    A ordem das chaves é mantida.

    :param source: o dict de referência
    :return: um novo dict normalizado
    """
    # inicializa a variável de retorno
    result: dict = {}

    # percorre o dicionário
    for curr_key, curr_value in source.items():

        # o valor atual é um dicionário ?
        if isinstance(curr_value, dict):
            # sim, prossiga recursivamente
            result[curr_key] = xml_normalize_keys(curr_value)
        # o valor atual é uma lista ?
        elif isinstance(curr_value, list):
            # sim, percorra-a
            result[curr_key] = []
            for item in curr_value:
                # o item da lista é um dicionário ?
                if isinstance(item, dict):
                    # sim, prossiga recursivamente
                    result[curr_key].append(xml_normalize_keys(item))
                else:
                    result[curr_key].append(item)
        # ä chave atual tem prefixo a ser removido ?
        elif curr_key[0:1] in ["@", "#"]:
            # sim
            result[curr_key[1:]] = curr_value
        else:
            pos: int = curr_key.find(":")
            if pos == 0:
                result[curr_key] = curr_value
            else:
                result[curr_key[pos+1:]] = curr_value

    return result


def xml_to_dict(file_data: bytes | str) -> dict:
    """
    Convert the XML into a *dict*, by removing namespaces, and keys prefixed with "@" e "#".

    O XML de entrada deve estar em *file_data* (tipo *bytes*),
    ou em arquivo do sistema com o caminho especificado por *file_data* (tipo *str*).

    :param file_data: XML a ser convertido
    :return: dict normalizado
    """
    # file_data é o próprio conteúdo XML ?
    if isinstance(file_data, bytes):
        # sim
        file_bytes: bytes = file_data
    else:  # elif isinstance(file_date, str):
        # não, obtenha-o do arquivo
        with Path.open(Path(file_data), "rb") as f:
            file_bytes: bytes = f.read()

    # converte o XML em dict
    xml_data = XmlTextToDict(xml_text=file_bytes.decode(),
                             ignore_namespace=True)
    result: dict = xml_data.get_dict()

    # normaliza o dict, removendo namespaces e prefixos "@" e "#" nos nomes das chaves
    return xml_normalize_keys(result)
