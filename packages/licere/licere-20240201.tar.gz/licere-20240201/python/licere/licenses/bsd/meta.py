from licere.api import *

def licenses():
    return [
        License(
            name="3-Clause BSD License",
            requires=["year", "copyright"],
            template="bsd-3.txt.jinja",
            aliases=["3-clause-bsd", "bsd-3-clause", "new-bsd", "modified-bsd"],
        ),
        License(
            name="2-Clause BSD License",
            requires=["year", "copyright"],
            template="bsd-2.txt.jinja",
            aliases=["simplified-bsd", "freebsd"],
        )
    ]