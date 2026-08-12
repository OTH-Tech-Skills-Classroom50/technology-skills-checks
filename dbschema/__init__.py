import sqlite3
from sqlite3 import IntegrityError

import check50


@check50.check()
def exists():
    """📁\tDie Datei konzertTicketShop.db existiert"""
    check50.exists("konzertTicketShop.db")


@check50.check(exists)
def tables_exist():
    """🗂️\tTabellen kunden, konzerte und buchungen existieren"""
    conn = sqlite3.connect("konzertTicketShop.db")
    for table in ("kunden", "konzerte", "buchungen"):
        rs = conn.execute("SELECT count(*) FROM sqlite_master WHERE name=?;", (table,))
        if rs.fetchone()[0] != 1:
            raise check50.Failure(f"Die Tabelle '{table}' existiert nicht")
    conn.close()


@check50.check(tables_exist)
def kunden_datatypes():
    """🧩\tDatentypen der Spalten für Tabelle kunden sind korrekt"""
    conn = sqlite3.connect("konzertTicketShop.db")
    for entry in conn.execute("pragma table_info(kunden);"):
        name, dtype = entry[1].lower(), entry[2].lower()
        if name in ("kundennr", "kundennummer"):
            if dtype != "int":
                raise check50.Failure("Datentyp von kundennr in Tabelle 'kunden' ist nicht INT")
        elif name == "email":
            if not dtype.startswith("varchar"):
                raise check50.Failure("Datentyp von eMail in Tabelle 'kunden' ist nicht VARCHAR")
        elif name == "name":
            if not dtype.startswith("varchar"):
                raise check50.Failure("Datentyp von name in Tabelle 'kunden' ist nicht VARCHAR")
        else:
            raise check50.Failure(
                "Die Tabelle 'kunden' enthält eine Spalte, die nicht in der Aufgabenstellung vorkommt. "
                "Bitte benutze nur die Spalten kundennr, eMail und name"
            )
    conn.close()


@check50.check(tables_exist)
def konzerte_datatypes():
    """🧩\tDatentypen der Spalten für Tabelle konzerte sind korrekt"""
    conn = sqlite3.connect("konzertTicketShop.db")
    for entry in conn.execute("pragma table_info(konzerte);"):
        name, dtype = entry[1].lower(), entry[2].lower()
        if name in ("konzertnr", "konzertnummer"):
            if dtype != "int":
                raise check50.Failure("Datentyp von konzertnr in Tabelle 'konzerte' ist nicht INT")
        elif name == "band":
            if not dtype.startswith("varchar"):
                raise check50.Failure("Datentyp von band in Tabelle 'konzerte' ist nicht VARCHAR")
        elif name == "termin":
            if dtype != "timestamp":
                raise check50.Failure("Datentyp von termin in Tabelle 'konzerte' ist nicht TIMESTAMP")
        elif name == "ort":
            if not dtype.startswith("varchar"):
                raise check50.Failure("Datentyp von ort in Tabelle 'konzerte' ist nicht VARCHAR")
        else:
            raise check50.Failure(
                "Die Tabelle 'konzerte' enthält eine Spalte, die nicht in der Aufgabenstellung vorkommt. "
                "Bitte benutze nur die Spalten konzertnr, band, termin und ort"
            )
    conn.close()


@check50.check(tables_exist)
def buchungen_datatypes():
    """🧩\tDatentypen der Spalten für Tabelle buchungen sind korrekt"""
    conn = sqlite3.connect("konzertTicketShop.db")
    for entry in conn.execute("pragma table_info(buchungen);"):
        name, dtype = entry[1].lower(), entry[2].lower()
        if name in ("buchungsnr", "buchungsnummer"):
            if dtype != "int":
                raise check50.Failure("Datentyp von buchungsnr in Tabelle 'buchungen' ist nicht INTEGER")
        elif name in ("kundennr", "kundennummer"):
            if dtype != "int":
                raise check50.Failure("Datentyp von kundennr in Tabelle 'buchungen' ist nicht INTEGER")
        elif name in ("konzertnr", "konzertnummer"):
            if dtype != "int":
                raise check50.Failure("Datentyp von konzertnr in Tabelle 'buchungen' ist nicht INTEGER")
        elif name == "buchungszeitpunkt":
            if dtype != "timestamp":
                raise check50.Failure("Datentyp von buchungszeitpunkt in Tabelle 'buchungen' ist nicht TIMESTAMP")
        elif name == "anzahltickets":
            if dtype != "int":
                raise check50.Failure("Datentyp von anzahlTickets in Tabelle 'buchungen' ist nicht INTEGER")
        else:
            raise check50.Failure(
                "Die Tabelle 'buchungen' enthält eine Spalte, die nicht in der Aufgabenstellung vorkommt. "
                "Bitte benutze nur die Spalten buchungsnr, kundennr, konzertnr, buchungszeitpunkt und anzahlTickets"
            )
    conn.close()


@check50.check(tables_exist)
def primary_keys():
    """🔑\tKorrekte Primärschlüssel verwendet"""
    conn = sqlite3.connect("konzertTicketShop.db")
    conn.execute("begin")
    try:
        conn.execute("DELETE FROM kunden;")
        conn.execute("DELETE FROM konzerte;")
        conn.execute("DELETE FROM buchungen;")

        try:
            conn.execute("INSERT INTO kunden VALUES(1, 'Tester1@test.de', 'Tester1');")
            conn.execute("INSERT INTO kunden VALUES(1, 'Tester2@test.de', 'Tester2');")
        except IntegrityError:
            pass
        else:
            raise check50.Failure("Primary key in kunden is not unique")

        try:
            conn.execute("INSERT INTO konzerte VALUES(1, 'Rammstein', '2019-01-01 20:00:00', 'Regensburg');")
            conn.execute("INSERT INTO konzerte VALUES(1, 'Metallica', '2020-01-02 20:00:00', 'München');")
        except IntegrityError:
            pass
        else:
            raise check50.Failure("Primary key in konzerte is not unique")

        try:
            conn.execute("INSERT INTO buchungen VALUES(1, 1, 1, '2018-01-01 19:00:00', 2);")
            conn.execute("INSERT INTO buchungen VALUES(1, 1, 1, '2018-01-01 19:00:00', 2);")
        except IntegrityError:
            pass
        else:
            raise check50.Failure("Primary key in buchungen is not unique")
    finally:
        conn.execute("rollback")
        conn.close()


@check50.check(tables_exist)
def references():
    """🗝️\tFremdschlüssel korrekt definiert"""
    conn = sqlite3.connect("konzertTicketShop.db")
    rs = conn.execute("pragma foreign_key_list('buchungen');")
    count = 0
    for entry in rs:
        count += 1
        table = entry[2].lower()
        if table == "konzerte":
            if entry[3].lower() not in ("konzertnr", "konzertnummer") or entry[4].lower() not in ("konzertnr", "konzertnummer"):
                raise check50.Failure(
                    "Fremdschlüssel in Tabelle Buchungen verweist nicht korrekt auf Spalte konzertnr in Tabelle Konzerte"
                )
        elif table == "kunden":
            if entry[3].lower() not in ("kundennr", "kundennummer") or entry[4].lower() not in ("kundennr", "kundennummer"):
                raise check50.Failure(
                    "Fremdschlüssel in Tabelle Buchungen verweist nicht korrekt auf Spalte kundennr in Tabelle Kunden"
                )
        else:
            raise check50.Failure(
                "Die Tabelle 'buchungen' enthält eine Fremdschlüsselbeziehung, die nicht in der Aufgabenstellung "
                "vorkommt. Bitte benutze nur die Fremdschlüsselbeziehungen zu den Id's der Tabelle Kunden und Tabelle Konzerte"
            )
    conn.close()
    if count != 2:
        raise check50.Failure("Falsche constraint Anzahl. Die Tabelle 'buchungen' muss genau zwei constraints haben")


@check50.check(tables_exist)
def inserted_data():
    """💾\tDaten wurden korrekt in die Tabellen hinzugefügt"""
    conn = sqlite3.connect("konzertTicketShop.db")
    rs = conn.execute("SELECT count(*) FROM kunden;")
    if rs.fetchone()[0] < 2:
        raise check50.Failure("Fügen Sie mindestens 2 Kunden in die Tabelle 'kunden' ein")

    rs = conn.execute("SELECT count(*) FROM konzerte;")
    if rs.fetchone()[0] < 2:
        raise check50.Failure("Fügen Sie mindestens 2 Konzerte in die Tabelle 'konzerte' ein")

    rs = conn.execute("SELECT count(*) FROM buchungen;")
    if rs.fetchone()[0] < 2:
        raise check50.Failure("Fügen Sie mindestens 2 Buchungen in die Tabelle 'buchungen' ein")

    rs = conn.execute("SELECT count(*) FROM konzerte where ort = 'Regensburg';")
    if rs.fetchone()[0] < 1:
        raise check50.Failure("Fügen Sie mindestens 1 Konzert in Regensburg in die Tabelle 'konzerte' ein")
    conn.close()
