from enum import Enum

class StatusNotificacaoEnum(Enum):

    ENVIADO = 1
    LIDO = 2

    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)
    

class TipoNotificacaoFilaEnum(Enum):

    VAGA = 1
    EMPRESA = 2
    VAGA_INATIVADA = 3
    VAGA_CONVITE = 4
    VAGA_ENCERRADA = 5
    VAGA_CANCELADA = 6
    USUARIO_DELETADO = 7 
    CANDIDATURA_FEEDBACK = 8
    NOVA_CANDIDATURA = 9
    NOTIFICACAO_NAO_ENVIADA = 10


    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)

class TipoNotificacaoEnum(Enum):

    CANDIDATURA = 1
    VAGA = 2
    CURSO = 3
    EMPRESA = 4
    CURRICULO = 5
    ALERTA = 6

    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)
    
class RotasNotificacaoEnum(Enum):
    HISTORICO_DE_VAGA = "HistoricoVaga"
    DETALHE_CANDIDATO = "DetalheCandidato"
    VAGA_COMPARTILHADA = "VagaDetalhes"