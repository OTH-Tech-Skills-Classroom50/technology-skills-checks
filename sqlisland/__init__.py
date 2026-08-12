import urllib3
import requests

import check50

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@check50.check()
def exists():
    """📁\tDie Datei sqlIsland.txt existiert"""
    check50.exists("sqlIsland.txt")


@check50.check(exists)
def id_sqlIsland_valid():
    """🏝️\tKorrekte Zertifikats-ID übermittelt."""
    with open("sqlIsland.txt") as f:
        lines = f.readlines()

    if len(lines) != 1:
        raise check50.Failure(
            "Tragen Sie bitte nur Ihre SqlIsland-Zertifikats Id in die Erste Zeile der Datei ein"
        )

    url = "https://sql-island.informatik.uni-kl.de/cert.php?check&id=" + lines[0].strip()
    response = requests.get(url, verify=False)
    if response.text != "valid":
        raise check50.Failure("Die Id ist ungültig")
