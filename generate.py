# -*- coding: utf-8 -*-

import xlrd
from jinja2 import Template

okrag_wojewodztwo = {1: "dolnośląskie", 2: "dolnośląskie", 3: "dolnośląskie", 4: "dolnośląskie", 5: "kujawsko-pomorskie", 6: "kujawsko-pomorskie",
                     7: "kujawsko-pomorskie",
                     8: "lubelskie", 9: "lubelskie", 10: "lubelskie", 11: "lubelskie", 12: "lubelskie", 13: "lubuskie", 14: "lubuskie", 15: "łódzkie",
                     16: "łódzkie",
                     17: "łódzkie", 18: "łódzkie", 19: "łódzkie", 20: "małopolskie", 21: "małopolskie", 22: "małopolskie", 23: "małopolskie", 24: "małopolskie",
                     25: "małopolskie", 26: "małopolskie", 27: "małopolskie", 28: "mazowieckie", 29: "mazowieckie", 30: "mazowieckie", 31: "mazowieckie",
                     32: "mazowieckie", 33: "mazowieckie", 34: "mazowieckie", 35: "mazowieckie", 36: "mazowieckie", 37: "opolskie", 38: "opolskie",
                     39: "podkarpackie",
                     40: "podkarpackie", 41: "podkarpackie", 42: "podkarpackie", 43: "podlaskie", 44: "podlaskie", 45: "podlaskie", 46: "pomorskie",
                     47: "pomorskie",
                     48: "pomorskie", 49: "śląskie", 50: "śląskie", 51: "śląskie", 52: "śląskie", 53: "śląskie", 54: "śląskie", 55: "świętokrzyskie",
                     56: "świętokrzyskie",
                     57: "warmińsko-mazurskie", 58: "warmińsko-mazurskie", 59: "warmińsko-mazurskie", 60: "wielkopolskie", 61: "wielkopolskie",
                     62: "wielkopolskie",
                     63: "wielkopolskie", 64: "wielkopolskie", 65: "zachodniopomorskie", 66: "zachodniopomorskie", 67: "zachodniopomorskie",
                     68: "zachodniopomorskie"}

kandydaci = []

glosow_wojewodztwo = {}

wynik_kraj = []
wynik_wojewodztwo = {}
wynik_okregi = {}
wynik_gminy = {}
wynik_obwody = {}

wojewodztwa_okregi = {}
okregi_gminy = {}
gminy_obwody = {}


def init_data():
    for _, woj in okrag_wojewodztwo.items():
        wynik_wojewodztwo[woj] = {}

    kbook = xlrd.open_workbook('data/gm-kraj.xls')
    ksh = kbook.sheet_by_index(0)

    # znajdz kandydatów w pierwszym wierszu pliku z danymi
    for k in ksh.row(0)[10:]:
        k = str(k).replace("text:", "").replace("'", "")
        kandydaci.append(k)
        wynik_kraj.append(0)

    # dodaj kandydatow do kazdego wojewodztwa
    for w in wynik_wojewodztwo:
        wynik_wojewodztwo[w] = [0] * len(kandydaci)

    # dodaj kandydatów do kazdego okregu
    for x in range(1, 69):
        wynik_okregi[x] = [0] * len(kandydaci)


def generate_page(file_name, title, votes_data, links, links_prefix, is_main=False):
    render_data = {'title': title, 'country_mode': is_main, 'gmina_mode': False}

    all_votes = 0
    for votes in votes_data:
        all_votes += votes

    render_data['people'] = []
    candidate = 0
    for votes in votes_data:
        render_data['people'].append({'name': kandydaci[candidate], 'votes': votes, 'percentage': (votes / all_votes) * 100})
        candidate += 1
    render_data['people'] = sorted(render_data['people'], key=lambda item: item['votes'], reverse=True)
    for person in range(0, len(render_data['people'])):
        render_data['people'][person]['index'] = person + 1

    render_pages = []
    for name, _ in links.items():
        if isinstance(name, str):
            render_pages.append({'link': str(links_prefix) + name.lower() + ".html", 'name': name})
        else:
            render_pages.append({'link': str(links_prefix) + str(name) + ".html", 'name': name})
    render_pages = sorted(render_pages, key=lambda page: page['name'])
    render_data['pages'] = render_pages

    f = open('template/index.tmp')
    template_content = f.read()
    f.close()

    t = Template(template_content)
    output = t.render(render_data)

    print("Generating HTML - " + str(file_name))
    f = open(file_name, mode='w')
    f.write(output)
    f.close()


def generate_page_gmina(file_name, title, gmina_data, obwod_data):
    render_data = {'title': title, 'country_mode': False, 'gmina_mode': True}

    all_votes = 0
    for votes in gmina_data:
        all_votes += votes

    render_data['people'] = []
    candidate = 0
    for votes in gmina_data:
        render_data['people'].append({'name': kandydaci[candidate], 'votes': votes, 'percentage': (votes / all_votes) * 100})
        candidate += 1
    render_data['people'] = sorted(render_data['people'], key=lambda item: item['votes'], reverse=True)
    for person in range(0, len(render_data['people'])):
        render_data['people'][person]['index'] = person + 1

    render_data['kandydaci'] = kandydaci
    render_data['obwody'] = obwod_data

    f = open('template/index.tmp')
    template_content = f.read()
    f.close()

    t = Template(template_content)
    output = t.render(render_data)

    print("Generating HTML - " + str(file_name))
    f = open(file_name, mode='w')
    f.write(output)
    f.close()


def read_file(filename):
    results_start_index = 12

    book = xlrd.open_workbook(filename)
    sh = book.sheet_by_index(0)

    for x in range(1, sh.nrows):
        row = sh.row(x)

        okr_id = int(row[0].value)
        gmina_id = row[2].value
        obwod_id = int(row[4].value)
        obwod_nazwa = row[6].value

        # kraj
        i = 0
        for k in row[results_start_index:]:
            wynik_kraj[i] += int(k.value)
            i += 1

        # wojewodztwo
        i = 0
        for k in row[results_start_index:]:
            wynik_wojewodztwo[okrag_wojewodztwo[okr_id]][i] += int(k.value)
            i += 1
        if okrag_wojewodztwo[okr_id] not in wojewodztwa_okregi:
            wojewodztwa_okregi[okrag_wojewodztwo[okr_id]] = {}
        wojewodztwa_okregi[okrag_wojewodztwo[okr_id]][okr_id] = True

        # okregi
        i = 0
        for k in row[results_start_index:]:
            wynik_okregi[okr_id][i] += int(k.value)
            i += 1
        if okr_id not in okregi_gminy:
            okregi_gminy[okr_id] = {}
        okregi_gminy[okr_id][gmina_id] = True

        # gminy
        i = 0
        if gmina_id not in wynik_gminy:
            wynik_gminy[gmina_id] = [0] * len(kandydaci)
        for k in row[results_start_index:]:
            wynik_gminy[gmina_id][i] += int(k.value)
            i += 1
        if gmina_id not in gminy_obwody:
            gminy_obwody[gmina_id] = {}
        gminy_obwody[gmina_id][obwod_id] = True

        # obwody
        if gmina_id not in wynik_obwody:
            wynik_obwody[gmina_id] = []
        w = []
        for k in row[results_start_index:]:
            w.append(int(k.value))
        wynik_obwody[gmina_id].append({"indeks": obwod_id, "wyniki": w, "nazwa": obwod_nazwa})


def generate_js(filename, votes_data):
    render_data = {}
    votes = []
    for w, v in votes_data.items():
        votes.append({'name': w, 'votes': v})

    render_data['provinces'] = votes

    f = open('template/loader.tmp')
    template_content = f.read()
    f.close()

    t = Template(template_content)
    output = t.render(render_data)

    f = open(filename, mode='w')
    f.write(output)
    f.close()


def read_data():
    for i in range(1, 69):
        n = ""
        if i < 10:
            n = "0" + str(i)
        else:
            n = str(i)
        read_file("data/obwod/obw" + n + ".xls")


def render():
    # Głosów w województwie
    for wojewodztwo, wyniki in wynik_wojewodztwo.items():
        glosow_wojewodztwo[wojewodztwo] = 0
        for w in wyniki:
            glosow_wojewodztwo[wojewodztwo] += w

    generate_js('out/js/maps.js', glosow_wojewodztwo)

    # Kraj
    generate_page('out/index.html', 'Wybory prezydenta 2000', wynik_kraj, {}, "", is_main=True)

    # Wojewodztwa
    for w, data in wynik_wojewodztwo.items():
        generate_page('out/' + w.lower() + '.html', "Województwo - " + w, data, wojewodztwa_okregi[w], "okrag-")

    # Okregi
    for o, data in wynik_okregi.items():
        generate_page('out/' + 'okrag-' + str(o) + '.html', "Okrąg - " + str(o), data, okregi_gminy[o], "gmina-")

    # Gminy
    for g, data in wynik_gminy.items():
        generate_page_gmina('out/' + 'gmina-' + g.lower() + '.html', "Gmina - " + g, data, wynik_obwody[g])


init_data()
read_data()
render()
