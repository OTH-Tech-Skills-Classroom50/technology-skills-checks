import requests

import check50


@check50.check()
def exists():
    """📁\tDie Datei monsterPark.txt existiert"""
    check50.exists("monsterPark.txt")


@check50.check(exists)
def id_monsterPark_valid():
    """👹\tKorrekte Zertifikats-ID übermittelt."""
    with open("monsterPark.txt") as f:
        lines = f.readlines()

    if len(lines) != 1:
        raise check50.Failure(
            "Tragen Sie bitte nur Ihre Monster-Zertifikats Id in die Erste Zeile der Datei ein"
        )

    url = "https://www.monst-er.de/cert.php?check&id=" + lines[0].strip()
    r = requests.get(url)
    if r.status_code != 200:
        raise check50.Failure("Die Id ist ungültig")
