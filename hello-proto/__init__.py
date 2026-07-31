import check50


@check50.check()
def exists():
    """hello.py exists"""
    check50.exists("hello.py")


@check50.check(exists)
def hello_emma():
    """responds to name Emma"""
    check50.run("python3 hello.py").stdin("Emma").stdout("Hallo Emma").exit()


@check50.check(exists)
def hello_rodrigo():
    """responds to name Rodrigo"""
    check50.run("python3 hello.py").stdin("Rodrigo").stdout("Hallo Rodrigo").exit()
