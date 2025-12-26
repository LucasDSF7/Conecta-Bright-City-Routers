'''
Dataclasses for storing data exported by API calls.
'''

from dataclasses import dataclass


@dataclass
class LCU:
    '''
    Dataclass para conter informações úteis de uma LCU
    '''
    id: int = None
    ID_PONTO_SERVICO: int = None
    pole_id_s: int = None
    name_s: str = None
    ALTURA_DO_POSTE: float = None
    MARCO: str = None
    BAIRRO: str = None
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
