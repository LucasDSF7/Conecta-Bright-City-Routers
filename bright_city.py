'''
Bright City routers and authentication for known api requests.
Under development
'''

import os
from datetime import datetime
from dataclasses import dataclass, fields
from typing import Self
import json

import requests
from pypasser import reCaptchaV3
from dotenv import load_dotenv


ANCHOR_URL = 'https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LdnBnYoAAAAAA91mQy9unVp99xOmG-z' \
'sTZOzGF5&co=aHR0cHM6Ly9zbWFydGxpZ2h0aW5nLnNtYXJ0cmlvLm9ubGluZTo0NDM.&hl=pt-BR&v=07cvpCr3Xe3g2ttJN' \
'UkC6W0J&size=invisible&anchor-ms=20000&execute-ms=15000&cb=pd4zzxx43gna'

load_dotenv()


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

    def populate(self, record: dict) -> Self:
        '''
        Populates a LCU using a record.
        '''
        for key in fields(self):
            setattr(self, key.name, record.get(key.name))
        return self


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


@dataclass
class AlarmsDeviceTable:
    '''
    Dataclass for creating a table from alarms device data.
    '''
    Data: datetime = None
    IDLCU: int = None
    NomeLCU: str = None
    Alarme: str = None
    DataHoraDefeito: datetime = None
    DataHoraAberturaAlarme: datetime = None
    DataHoraResolvido: datetime = None
    TempoDefeito: str = None
    Latitute: float = None
    Longitude: float = None


class BrightCitySession(requests.sessions.Session):
    '''
    Handles Bright City session. Using it with context manegement from python.
    Pass user and password.
    '''
    def __init__(self, user: str, password: str, costumer_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user: str = user
        self.password: str = password
        self.costumer_id: int = costumer_id
        self.login_url = os.environ.get('BC_URL') + 'identity/authenticate'
        self.auth_bc()

    def auth_bc(self):
        '''
        Autenticação no sistema do Bright City
        '''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0',
            'Referer': 'https://www.google.com/',
            'Content-type': 'application/json',
            'Recaptcha': reCaptchaV3(ANCHOR_URL)
        }
        data = {
            'username': self.user,
            'password': self.password
        }
        r = self.post(url=self.login_url, json=data)
        jwt = r.json()['message']['token']['jwttoken']
        self.headers = {'Authorization': jwt}

    def bc_post(self, url: str, **kwargs) -> any:
        '''
        Modification to post method to handle disconnection from the server.
        See post propertys.
        '''
        r = self.post(url=url, **kwargs)
        if r.status_code == 403:
            self.auth_bc()
            r = self.post(url=url, **kwargs)
        return r.json()


class AlarmsCount():
    '''
    Router Alarms Count from Birght City API.
    '''

    def __init__(self, session: BrightCitySession):
        self.session = session
        self.url = os.environ.get('BC_URL') + 'bc_ui_app/api/base/get/alarms-count'
        self.records: list[dict] = None

    def export(self):
        '''
        Export records of alarms
        '''
        payload = {
            'bp_solr_search': '''{"customerId":4,"filter":{},"systemId":1}''',
            'user': 'LucasD',
            'IP': 'undefined'
        }
        self.records = self.session.bc_post(url=self.url, files=payload)['message'][0]['alarmDetails']
        return self.records


class AlarmsDevice():
    '''
    Router Alarms Device
    '''

    def __init__(self, session: BrightCitySession):
        self.session = session
        self.url = os.environ.get('BC_URL') + 'ams/alarms/device/'
        self.records: list[dict] = None

    def export(self, id_lcu: int):
        '''
        Export a list of alarms from a LCU.
        '''
        parameters_dto = {
            "filter": {"startRow": 0, "count": 40},
            "sorting": {
                "sortFirst": {"field": "dateOpen", "sort": "desc"}
            }
        }
        payload = {
            'parameters': (None, json.dumps(parameters_dto)),
            'user': (None, 'LucasD'),
            'IP': (None, 'undefined'),
            'systemId': (None, 'undefined')
        }
        self.records = self.session.bc_post(url=self.url + str(id_lcu), files=payload, timeout=120)
        return self.records


class DeviceHistory():
    '''
    Router device/history from Bright City API.
    '''

    def __init__(self, session: BrightCitySession):
        self.session = session
        self.url = os.environ.get('BC_URL') + 'bc_ui_app/api/base/device/history'
        self.records: list[dict] = None

    def export(self, measurements: list[str], lcus_id: list[int], data_inicial: datetime, data_final: datetime) -> list[dict]:
        '''
        Export a list of measurements from a list of lcus_ids.
        '''
        # datetime must be in UTC +00:00.
        data_inicial = data_inicial.strftime('%Y-%m-%dT%H:%M:%SZ')
        data_final = data_final.strftime('%Y-%m-%dT%H:%M:%SZ')
        payload = {
                "bpoint": lcus_id,
                "measurement": measurements,
                "startTime": data_inicial,
                "endTime": data_final,
                "bpointTagName": "sn",
                "systemId": 1,
                "port1Measurement": [],
                "port2Measurement": []
        }
        self.records = self.session.bc_post(url=self.url, json=payload, timeout=120)
        return self.records


class PointsSearch():
    '''
    Router points/search from Bright City API.
    '''

    def __init__(self, session: BrightCitySession):
        self.session = session
        self.url = os.environ.get('BC_URL') + 'bc_ui_app/api/base/get/bright-points/search'
        self.records: list[dict] = None

    def get_lcu_count(self) -> int:
        '''
        Returns the number of lcus from the system.
        '''
        payload = {
        'bp_solr_search': f'{{"customerId":{self.session.costumer_id},"rows":2,"start":0,"sortBy":{{"id":"asc"}},"systemId":1}}',
        'user': 'LucasD',
        'IP': 'undefined'
        }
        r = self.session.bc_post(url=self.url, files=payload)
        return int(r['message'][0]['deviceCount'])

    def export(self, bc_filter: str = '') -> list[dict]:
        '''
        Returns records of all lcus from brigth city
        '''
        payload = {
        'bp_solr_search': f'{{"customerId":{self.session.costumer_id},"rows":{self.get_lcu_count()},"start":0,"sortBy":{{"id":"asc"}},"systemId":1{bc_filter}}}',
        'user': 'LucasD',
        'IP': 'undefined'
        }
        r = self.session.bc_post(url=self.url, files=payload)
        self.records = r['message'][0]['devices']
        return self.records
