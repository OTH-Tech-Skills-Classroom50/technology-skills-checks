import random
import string

import check50


@check50.check()
def exists():
    """📁\tDie Datei hello.py existiert"""
    check50.exists("hello.py")


@check50.check(exists)
def hello_output():
    """👋\tAusgabe eines zufälligen Namens"""
    name = "".join(random.choices(string.ascii_letters, k=10))
    check50.run("python3 hello.py").stdin(name, prompt=False).stdout(f"Hallo {name}", regex=False).exit()
