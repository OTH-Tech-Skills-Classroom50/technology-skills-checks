import check50


@check50.check()
def exists():
    """📁\tDie Datei blocks.py existiert"""
    check50.exists("blocks.py")


@check50.check(exists)
def rejects_negative():
    """🙅\tProgramm akzeptiert keine negativen Werte"""
    check50.run("python3 blocks.py").stdin("-1", prompt=False).stdin("1", prompt=False).stdout("#", regex=False)


@check50.check(exists)
def rejects_zero():
    """🙅\tProgramm akzeptiert den Wert 0 nicht"""
    check50.run("python3 blocks.py").stdin("0", prompt=False).stdin("1", prompt=False).stdout("#", regex=False)


@check50.check(exists)
def rejects_nine():
    """🙅\tProgramm akzeptiert den Wert 9 nicht"""
    check50.run("python3 blocks.py").stdin("9", prompt=False).stdin("1", prompt=False).stdout("#", regex=False)


@check50.check(exists)
def size_one():
    """🧱\tMauer für den Wert 1 korrekt ausgegeben"""
    check50.run("python3 blocks.py").stdin("1", prompt=False).stdout("#", regex=False)


@check50.check(exists)
def size_two():
    """🧱\tMauer für den Wert 2 korrekt ausgegeben"""
    check50.run("python3 blocks.py").stdin("2", prompt=False).stdout("#*\n*#", regex=False)


@check50.check(exists)
def size_eight():
    """🧱\tMauer für den Wert 8 korrekt ausgegeben"""
    check50.run("python3 blocks.py").stdin("8", prompt=False).stdout(
        "#*#*#*#*\n*#*#*#*#\n#*#*#*#*\n*#*#*#*#\n#*#*#*#*\n*#*#*#*#\n#*#*#*#*\n*#*#*#*#",
        regex=False,
    )
