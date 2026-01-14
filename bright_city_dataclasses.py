'''
Dataclasses for storing data exported by API calls.
'''

from dataclasses import dataclass
from datetime import datetime


@dataclass
class LCU:
    '''
    Dataclass para conter informações úteis de uma LCU
    '''
    id: int = None
    ID_PONTO_SERVICO: int = None
    pole_id_s: int = None
    name_s: str = None
    ocorrencia_criada: bool = None
    address1_s: str = None
    latitude_f: float = None
    longitude_f: float = None
    dimming_level_set_i: int = None
    work_order_s: int = None
    barcode_s: str = None
    ctlatitude_f: float = None
    ctlongitude_f: float = None
    last_update_dt: str = None
    installationdate_dt: str = None
    alarm_names_ssci: list[str] = None
    distance: float = None


@dataclass
class AlarmsTable:
    '''
    Dataclass for creating a silver layer in medallion pattern
    '''
    Data: datetime = None
    IDLCU: int = None
    CodigoBarras: str = None
    NomeLCU: str = None
    Latitude_lcu: float = None
    Longitude_lcu: float = None
    DistanciaPontoServico: float = None
    IDPontoServico: int = None
    Bairro: str = None
    Latitude: float = None
    Longitude: float = None
    MarcoContrato: str = None
    AlturaInstalacaoLuminaria: float = None
    TipoPoste: str = None
    NomeAlarme: str = None
