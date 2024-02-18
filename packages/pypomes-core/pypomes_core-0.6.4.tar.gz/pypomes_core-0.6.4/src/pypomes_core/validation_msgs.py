from typing import Final

__ERR_MSGS: Final[dict] = {
    101: {
        "en": "Error accessing the DB {} in {}: {}",
        "pt": "Erro na interação com o BD {} em {}: {}",
    },
    102: {
        "en": "Error accessing the object store: {}",
        "pt": "Erro na interação com o armazenador de objetos: {}",
    },
    103: {
        "en": "No {} found",
        "pt": "Nenhum(a) {} encontrado(a)",
    },
    104: {
        "en": "Unknown parameter: {}",
        "pt": "Parâmetro desconhecido: {}",
    },
    105: {
        "en": "Mandatory parameter: {}",
        "pt": "Parâmetro obrigatório: {}",
    },
    106: {
        "en": "Invalid value {} for parameter {}",
        "pt": "Valor {} inválido para o parâmetro {}",
    },
    107: {
        "en": "Invalid value {}: length shorter than {}",
        "pt": "Valor {} inválido: comprimento menor que {}",
    },
    108: {
        "en": "Invalid value {} for parameter {}: length longer than {}",
        "pt": "Valor {} inválido para o parâmetro {}: comprimento maior que {}",
    },
    109: {
        "en": "Invalid value {} for parameter {}: length must be {}",
        "pt": "Valor {} inválido para o parâmetro {}: comprimento deve ser igual a {}",
    },
    110: {
        "en": "Invalid value {} for parameter {}: date is later than the current date",
        "pt": "Valor {} inválido para o parâmetro {}: data posterior à data atual",
    },
    111: {
        "en": "Invalid value {} for parameter {}: wrong date format",
        "pt": "Valor {} inválido para o parâmetro {}: formato de data inválido",
    },
    112: {
        "en": "Error executing operation {}: {}",
        "pt": "Erro ao executar a operação {}: {}",
    },
    113: {
        "en": "The operation {} returned the error {}",
        "pt": "A operação {} retornou o erro {}",
    },
    114: {
        "en": "Unexpected error: {}",
        "pt": "Erro não previsto: {}",
    },
    115: {
        "en": "No file found at URL {}",
        "pt": "Nenhum arquivo encontrado na URL {}",
    },
    116: {
        "en": "The format for file {} is not type {}",
        "pt": "O formato do arquivo {} não é do tipo {}",
    },
    117: {
        "en": "Register for {} already exists",
        "pt": "Registro de {} já existe",
    },
    118: {
        "en": "Authentication token required",
        "pt": "Token de autenticação requerido",
    },
    119: {
        "en": "Invalid authentication token",
        "pt": "Token de autenticação inválido",
    },
    120: {
        "en": "More than one {} found",
        "pt": "Mais de um(a) {} encontrado(a)",
    },
    121: {
        "en": "Invalid operation: {}",
        "pt": "Operação inválida: {}",
    },
    122: {
        "en": "Invalid value {} for parameter {}: must be one of {}",
        "pt": "Valor {} inválido para o parâmetro {}: deve ser um de {}",
    },
    123: {
        "en": "Invalid value {} for parameter {}: must be in the range {}",
        "pt": "Valor {} inválido para o parâmetro {}: deve estar no intervalo {}",
    },
    124: {
        "en": "Invalid value {} for parameter {}: must be type {}",
        "pt": "Valor {} inválido para o parâmetro {}: deve ser do tipo {}",
    },
    125: {
        "en": "The values provided {} for parameter {} do not constitute a valid set of values",
        "pt": "Os valores fornecidos {} para o parâmetro {} não formam um conjunto válido de valores",
    },
    140: {
        "en": "Error retrieving environment variable {}: {}",
        "pt": "Erro na recuperação da variável de ambiente {}: {}",
    },
    141: {
        "en": "Error invoking service {}: {}",
        "pt": "Erro na invocação do serviço {}: {}",
    },
}
_ERR_MSGS_EN: dict = {}
for key, value in __ERR_MSGS.items():
    _ERR_MSGS_EN[key] = value["en"]

_ERR_MSGS_PT: dict = {}
for key, value in __ERR_MSGS.items():
    _ERR_MSGS_PT[key] = value["pt"]


def validation_add_msgs(msgs: dict, lang: str = "en") -> None:
    """
    Add the messages in *msgs* to the standard validation messages list for language *lang".

    :param msgs: list of messages to be added
    :param lang: the reference language
    """
    match lang:
        case "en":
            _ERR_MSGS_EN.update(msgs)
        case "pt":
            _ERR_MSGS_PT.update(msgs)


def validation_set_msgs(msgs: dict, lang: str = "en") -> None:
    """
    Set  the standard validation messages list for language *lang* to the messages in *msgs*.

    :param msgs: list of messages to set the standard validation messages to
    :param lang: the reference language
    """
    global _ERR_MSGS_EN, _ERR_MSGS_PT

    match lang:
        case "en":
            _ERR_MSGS_EN = msgs
        case "pt":
            _ERR_MSGS_PT = msgs
