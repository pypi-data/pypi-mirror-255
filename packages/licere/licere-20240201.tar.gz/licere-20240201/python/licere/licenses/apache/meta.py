from licere.api import *

def licenses():
    base = License(
        name="Apache",
        template="apache.md.jinja",
        requires={
            "year",
            "copyright",
        },
        data=data(
            terms=True,
            short=True,
            appendix=True,
        )
    )
    return [
        base(
            name="Apache (Full)",
            aliases=["apache-full"], 
            data=data(
                appendix=False,
                terms=True,
                short=True,
            )
        ),
        
        base(
            name="Apache (Full with Appendix)",
            aliases=["apache-full-appendix"],
            data=data(
                terms=True,
                appendix=True,
                short=True,
            )
        ),
        base(
            name="Apache (Short)",
            aliases=["apache-short"],
            data=data(
                short=True,
                terms=False,
                appendix=False,
            )
        ),
    ]

 
