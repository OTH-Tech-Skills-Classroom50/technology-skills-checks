import json

import check50


def write_phonebook(data):
    with open("phonebook.txt", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def read_phonebook():
    with open("phonebook.txt", encoding="utf-8") as f:
        return json.load(f)


@check50.check()
def exists():
    """📂\tDatei phonebook.txt existiert"""
    check50.exists("phonebook.py")
    check50.exists("phonebook.txt")


@check50.check(exists)
def add_overwrites_existing_entry():
    """✏️\tBestehende Einträge werden überschrieben"""
    write_phonebook({"Alice": "0151 1111"})
    check50.run("python3 phonebook.py") \
        .stdin("a", prompt=False) \
        .stdin("Alice", prompt=False) \
        .stdin("0151 2222", prompt=False) \
        .stdin("q", prompt=False) \
        .exit()
    data = read_phonebook()
    if data.get("Alice") != "0151 2222":
        raise check50.Failure(f'expected Alice to be "0151 2222", not {data.get("Alice")!r}')


@check50.check(exists)
def menu_flow_add():
    """✏️\tHinzufügen über Menü funktioniert"""
    write_phonebook({})
    check50.run("python3 phonebook.py") \
        .stdin("a", prompt=False) \
        .stdin("Clara", prompt=False) \
        .stdin("0151 9999", prompt=False) \
        .stdin("q", prompt=False) \
        .exit()
    data = read_phonebook()
    if data.get("Clara") != "0151 9999":
        raise check50.Failure(f'expected Clara to be "0151 9999", not {data.get("Clara")!r}')


@check50.check(exists)
def menu_flow_search_mobile():
    """📱\tSuche nach Kontakt mit Mobilnummer zeigt Handy-Emoji"""
    write_phonebook({"Clara": "0151 1234"})
    check50.run("python3 phonebook.py") \
        .stdin("s", prompt=False) \
        .stdin("Clara", prompt=False) \
        .stdin("q", prompt=False) \
        .stdout("📱\t0151 1234", regex=False) \
        .exit()


@check50.check(exists)
def menu_flow_search_landline():
    """☎️\tSuche nach Kontakt mit Festnetznummer zeigt Festnetz-Emoji"""
    write_phonebook({"Don": "0941 4321"})
    check50.run("python3 phonebook.py") \
        .stdin("s", prompt=False) \
        .stdin("Don", prompt=False) \
        .stdin("q", prompt=False) \
        .stdout("️\t0941 4321", regex=False) \
        .exit()


@check50.check(exists)
def menu_flow_quit():
    """🖐\tBeenden über Menü funktioniert"""
    check50.run("python3 phonebook.py") \
        .stdin("q", prompt=False) \
        .stdout("🖐\tTschüss!", regex=False) \
        .exit()


@check50.check(exists)
def search_not_found_prints_cross():
    """❌\tSuche nach nicht vorhandenem Kontakt zeigt Kreuz-Emoji"""
    write_phonebook({})
    check50.run("python3 phonebook.py") \
        .stdin("s", prompt=False) \
        .stdin("NOT IN PHONEBOOK - 127127192 xskdghkusdhkusdhuk", prompt=False) \
        .stdin("q", prompt=False) \
        .stdout("❌\tKontakt nicht gefunden.", regex=False) \
        .exit()
