import check50


@check50.check()
def exists():
    """blocks.py exists"""
    check50.exists("blocks.py")


@check50.check(exists)
def rejects_negative():
    """rejects a negative size"""
    check50.run("python3 blocks.py").stdin("-1", prompt=False).stdin("1", prompt=False).stdout("#", regex=False)


@check50.check(exists)
def rejects_zero():
    """rejects a size of 0"""
    check50.run("python3 blocks.py").stdin("0", prompt=False).stdin("1", prompt=False).stdout("#", regex=False)


@check50.check(exists)
def rejects_nine():
    """rejects a size of 9"""
    check50.run("python3 blocks.py").stdin("9", prompt=False).stdin("1", prompt=False).stdout("#", regex=False)


@check50.check(exists)
def size_one():
    """generates a correct wall for size 1"""
    check50.run("python3 blocks.py").stdin("1", prompt=False).stdout("#", regex=False)


@check50.check(exists)
def size_two():
    """generates a correct wall for size 2"""
    check50.run("python3 blocks.py").stdin("2", prompt=False).stdout("#*\n*#", regex=False)


@check50.check(exists)
def size_eight():
    """generates a correct wall for size 8"""
    check50.run("python3 blocks.py").stdin("8", prompt=False).stdout(
        "#*#*#*#*\n*#*#*#*#\n#*#*#*#*\n*#*#*#*#\n#*#*#*#*\n*#*#*#*#\n#*#*#*#*\n*#*#*#*#",
        regex=False,
    )
