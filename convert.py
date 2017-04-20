""" Module for class Results """

import os
import xlrd
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zadanie2.settings")
django.setup()
from elections.models import *

DATA_DIR = '../zadanie1/data/'

CIRCUIT_ROW_DEF = [
    'nr_okregu',
    'kod_gminy',
    'gmina',
    'powiat',
    'nr_obwodu',
    'typ_obwodu',
    'adres',
    'uprawnieni',
    'wydane_karty',
    'glosy_oddane',
    'glosy_niewazne',
    'glosy_wazne',
    'grabowski',
    'ikonowicz',
    'kalinowski',
    'korwin',
    'krzaklewski',
    'kwasniewski',
    'lepper',
    'lopuszanski',
    'olechowski',
    'pawlowski',
    'walesa',
    'wilecki'
]

CANDIDATES = {
    'grabowski': 'Dariusz Grabowski',
    'ikonowicz': 'Piotr Ikonowicz',
    'kalinowski': 'Jarosław Kalinowski',
    'korwin': 'Janusz Korwin-Mikke',
    'krzaklewski': 'Marian Krzaklewski',
    'kwasniewski': 'Aleksander Kwaśniewski',
    'lepper': 'Andrzej Lepper',
    'lopuszanski': 'Jan Łopuszański',
    'olechowski': 'Andrzej Olechowski',
    'pawlowski': 'Bogdan Pawłowski',
    'walesa': 'Lech Wałęsa',
    'wilecki': 'Tadeusz Wilecki'
}

VOIVODESHIP_NAME = {
    'DS': 'dolnośląskie',
    'KP': 'kujawsko-pomorskie',
    'LB': 'lubuskie',
    'LU': 'lubelskie',
    'LD': 'łódzkie',
    'MA': 'małopolskie',
    'MZ': 'mazowieckie',
    'OP': 'opolskie',
    'PD': 'podlaskie',
    'PK': 'podkarpackie',
    'PM': 'pomorskie',
    'SL': 'śląskie',
    'SK': 'świętokrzyskie',
    'WN': 'warmińsko-mazurskie',
    'WP': 'wielkopolskie',
    'ZP': 'zachodniopomorskie',
}

PRECINCT_VOIVODESHIP = {
    1: 'DS',
    2: 'DS',
    3: 'DS',
    4: 'DS',
    5: 'KP',
    6: 'KP',
    7: 'KP',
    8: 'LU',
    9: 'LU',
    10: 'LU',
    11: 'LU',
    12: 'LU',
    13: 'LB',
    14: 'LB',
    15: 'LD',
    16: 'LD',
    17: 'LD',
    18: 'LD',
    19: 'LD',
    20: 'MA',
    21: 'MA',
    22: 'MA',
    23: 'MA',
    24: 'MA',
    25: 'MA',
    26: 'MA',
    27: 'MA',
    28: 'MZ',
    29: 'MZ',
    30: 'MZ',
    31: 'MZ',
    32: 'MZ',
    33: 'MZ',
    34: 'MZ',
    35: 'MZ',
    36: 'MZ',
    37: 'OP',
    38: 'OP',
    39: 'PK',
    40: 'PK',
    41: 'PK',
    42: 'PK',
    43: 'PD',
    44: 'PD',
    45: 'PD',
    46: 'PM',
    47: 'PM',
    48: 'PM',
    49: 'SL',
    50: 'SL',
    51: 'SL',
    52: 'SL',
    53: 'SL',
    54: 'SL',
    55: 'SK',
    56: 'SK',
    57: 'WN',
    58: 'WN',
    59: 'WN',
    60: 'WP',
    61: 'WP',
    62: 'WP',
    63: 'WP',
    64: 'WP',
    65: 'ZP',
    66: 'ZP',
    67: 'ZP',
    68: 'ZP'
}

OKR_NAME = {
    1: 'Wrocław',
    2: 'Jelenia Góra',
    3: 'Legnica',
    4: 'Wałbrzych',
    5: 'Bydgoszcz',
    6: 'Toruń',
    7: 'Włocławek',
    8: 'Lublin',
    9: 'Biała Podlaska',
    10: 'Chełm',
    11: 'Puławy',
    12: 'Zamość',
    13: 'Zielona Góra',
    14: 'Gorzów Wielkopolski',
    15: 'Łódź',
    16: 'Łódź',
    17: 'Piotrków Trybunalski',
    18: 'Sieradz',
    19: 'Skierniewice',
    20: 'Kraków',
    21: 'Kraków',
    22: 'Kraków',
    23: 'Chrzanów',
    24: 'Myślenice',
    25: 'Nowy Sącz',
    26: 'Nowy Targ',
    27: 'Tarnów',
    28: 'Warszawa',
    29: 'Warszawa',
    30: 'Ciechanów',
    31: 'Legionowo',
    32: 'Ostrołęka',
    33: 'Piaseczno',
    34: 'Płock',
    35: 'Radom',
    36: 'Siedlce',
    37: 'Opole',
    38: 'Opole',
    39: 'Rzeszów',
    40: 'Krosno',
    41: 'Przemyśl',
    42: 'Tarnobrzeg',
    43: 'Białystok',
    44: 'Łomża',
    45: 'Suwałki',
    46: 'Gdańsk',
    47: 'Gdańsk',
    48: 'Słupsk',
    49: 'Katowice',
    50: 'Bielsko-Biała',
    51: 'Bytom',
    52: 'Częstochowa',
    53: 'Gliwice',
    54: 'Sosnowiec',
    55: 'Kielce',
    56: 'Kielce',
    57: 'Olsztyn',
    58: 'Elbląg',
    59: 'Ełk',
    60: 'Poznań',
    61: 'Kalisz',
    62: 'Konin',
    63: 'Leszno',
    64: 'Piła',
    65: 'Szczecin',
    66: 'Koszalin',
    67: 'Stargard Szczeciński',
    68: 'Szczecinek'
}


def get_field_mapping():
    """ Convert field names to ids in row"""

    if not hasattr(get_field_mapping, 'fields'):
        fields = {}
        for i, item in enumerate(CIRCUIT_ROW_DEF):
            fields[item] = i

        get_field_mapping.fields = fields

    return get_field_mapping.fields


def parse_obw_row(row):
    """ Parse xlrd row into dictionary  """
    mapping = get_field_mapping()
    result = {}

    for field in CIRCUIT_ROW_DEF:
        item = row[mapping[field]]

        if isinstance(item.value, str):
            result[field] = item.value
        else:
            result[field] = int(item.value)

    return result


class Results:
    """ Class handling result computation """

    def __init__(self):
        # Build dict with candidates
        self.candidates = {}

        for c, name in CANDIDATES.items():
            first, last = name.split(" ")
            self.candidates[c] = Candidate.objects.get(first_name=first, last_name=last)

        print(self.candidates)

    def load_obw_files(self):
        """ Read all obw files in data folder """

        obw_path = os.path.join(os.path.curdir, DATA_DIR, 'obwod')
        for file in os.listdir(obw_path):
            print("Reading from %s" % file)
            self.read_obw_file(os.path.join(obw_path, file))

    def read_obw_file(self, path):
        """ Read file with given filename """
        book = xlrd.open_workbook(path)

        sheet = book.sheet_by_index(0)
        for row_num in range(1, sheet.nrows):
            row = sheet.row(row_num)
            results = parse_obw_row(row)
            self.add_obw_results(results)

    def add_obw_results(self, results):
        borough, created = Borough.objects.get_or_create(
            name=results['gmina'],
            code=results['kod_gminy']
        )

        if created:
            precinct = Precinct.objects.get(id=results['nr_okregu'])
            precinct.boroughs.add(borough)
            precinct.save()

        circuit = Circuit(
            address=results['adres'],
            cards=results['wydane_karty'],
            valid_cards=results['glosy_wazne'],
            borough=borough,
        )
        circuit.save()

        for c in CANDIDATES:
            w = CandidateResult(
                candidate=self.candidates[c],
                circuit=circuit,
                votes=results[c]
            )
            w.save()


# Populate Voivodeship table
def insert_voivodeship():
    for code, name in VOIVODESHIP_NAME.items():
        w = Voivodeship(name=name, code=code.lower())
        w.save()


def insert_candidate():
    for _, name in CANDIDATES.items():
        first, last = name.split(" ")
        k = Candidate(first_name=first, last_name=last)
        k.save()


def insert_precinct():
    for i, name in OKR_NAME.items():
        voivodeship_code = PRECINCT_VOIVODESHIP[i].lower()
        voivodeship = Voivodeship.objects.get(code=voivodeship_code)
        precinct = Precinct(name=name, number=i, voivodeship=voivodeship)
        precinct.save()


def insert_obw():
    r = Results()
    r.load_obw_files()


def insert_all():
    insert_voivodeship()
    insert_candidate()
    insert_precinct()
    insert_obw()


insert_all()
