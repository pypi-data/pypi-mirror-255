from enum import Enum

class TipoNotificacaoFilaAdminEnum(Enum):

    EMPRESA = 1
    VAGA = 2
    DENUNCIA = 3



    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)

class TipoNotificacaoAdminEnum(Enum):

    EMPRESA = 1
    VAGA = 2
    DENUNCIA = 3

    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)
    
class RotasNotificacaoEnum(Enum):
    HISTORICO_DE_VAGA = "HistoricoVaga"
    DETALHE_CANDIDATO = "DetalheCandidato"
    VAGA_COMPARTILHADA = "VagaDetalhes"