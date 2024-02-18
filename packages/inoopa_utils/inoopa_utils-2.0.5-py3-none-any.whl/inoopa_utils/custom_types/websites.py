from dataclasses import dataclass


@dataclass
class PageInfo:
    url: str
    content: str | None = None

@dataclass
class CompanyWebsiteContent:
    url: str
    # MongoDB id initialized when the company is created in the DB
    _id: str | None = None
    home: PageInfo| None = None
    about: PageInfo | None = None
    contact: PageInfo | None =  None
