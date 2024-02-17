from licere.api import License, data

def licenses():
    base = License(
        name="Polyform Base",
        template="polyform.md.jinja",    
        data=data(
            version="1.0.0"
        )
    )
    return [
        base(
            name="PolyForm Non Commercial License",
            
            aliases=["polyform-noncommercial"],
            data=data(
                type={"noncommercial"},
                type_name="noncommercial",
            )
        ),
        base(
            name="PolyForm Strict License",
            aliases=["polyform-strict"],
            data=data(
                type={"strict"},
                type_name="strict",
            )
        ),
        base(
            name="PolyForm Perimeter License",
            aliases=["polyform-perimeter"],
            data=data(
                type={"perimeter"},
                type_name="perimeter",
            )
        ),
        base(
            name="PolyForm Shield License",
            aliases=["polyform-shield"],
            data=data(
                type={"shield"},
                type_name="shield",
            )
        ),
        base(
            name="PolyForm Free Trial License",
            aliases=["polyform-free-trial"],
            data=data(
                type={"free-trial"},
                type_name="free-trial",
            )
        ),
    ]

 
