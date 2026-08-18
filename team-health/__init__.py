import check50

# TODO: placeholder checks -- replace once the real assignment content is
# decided. For now, this just confirms the pipeline (starter -> check ->
# submit -> autograder) works end to end.


@check50.check()
def exists():
    """📄\tteam-health.md existiert"""
    check50.exists("team-health.md")


@check50.check(exists)
def not_empty():
    """✏️\tteam-health.md wurde bearbeitet"""
    content = open("team-health.md", encoding="utf-8").read().strip()
    if not content:
        raise check50.Failure("team-health.md is empty")
