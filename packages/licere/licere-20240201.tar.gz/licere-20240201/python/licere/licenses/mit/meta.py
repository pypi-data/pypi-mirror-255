from licere.api import *

def licenses():
    return [
        License(
            name="MIT",
            requires=["year", "copyright"],
            template="mit.txt.jinja",
            aliases=["mit"],
        ),
    ]