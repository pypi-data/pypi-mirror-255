import pendulum
from typing import Literal
from datetime import datetime
from dataclasses import dataclass


@dataclass(slots=True)
class ParsedAddress:
    street: str | None = None
    number: str | None = None
    city: str | None = None
    postal_code: str | None = None


@dataclass(slots=True)
class NaceCode:
    number: str
    description: str
    is_correted: bool = False
    correction_ranking: int | None = None


@dataclass(slots=True)
class Address:
    source: str
    last_update: datetime | None # From source
    last_seen: datetime   # When we last saw it while scraping
    street: str | None = None
    number: str | None = None
    city: str | None = None
    postal_code: str | None = None
    additionnal_address_info: str | None = None
    string_address: str | None = None


@dataclass(slots=True)
class Email:
    email: str
    source: str
    last_seen: datetime
    score: int | None = None


@dataclass(slots=True)
class Phone:
    phone: str
    source: str
    last_seen: datetime
    score: int | None = None


@dataclass(slots=True)
class Website:
    source: str
    website: str
    last_seen: datetime
    score: int | None = None


@dataclass(slots=True)
class BoardMember:
    is_company: bool
    function: str
    name: str
    start_date: datetime
    linked_company_number: str | None = None


@dataclass(slots=True)
class SocialNetwork:
    last_seen: datetime
    name: str
    url: str
    source: str | None = None
    score: int | None = None


@dataclass(slots=True)
class Establishment:
    establishment_number: str
    last_seen: datetime
    status: str | None = None
    start_date: datetime | None = None
    country: Literal["BE"] = "BE"
    name: str | None = None
    name_fr: str | None = None
    name_nl: str | None = None
    name_de: str | None = None
    name_last_update: datetime | None = None
    social_networks: list[SocialNetwork] | None = None
    address: Address | None = None
    best_email: Email | None = None
    emails: list[Email] | None = None
    best_phone: Phone | None = None
    phones: list[Phone] | None = None
    best_website: Website | None = None
    websites: list[Website] | None = None
    end_date: str | None = None
    nace_codes: list[NaceCode] | None = None
    is_nace_codes_corrected: bool = False


@dataclass(slots=True)
class Company:
    # A combination of country ISO code and country_company_id in format: BE_1234567890
    _id: str
    # VAT number in Belgium for ex, SIRET in France,...
    company_number: str
    country: Literal["BE", "FR", "NL"] = "BE"
    legal_situation: str | None = None
    status: str | None = None
    start_date: datetime | None = None
    entity_type: str | None = None
    legal_form: str | None = None
    legal_form_last_update: str | None = None
    address: Address | None = None
    best_email: Email | None = None
    emails: list[Email] | None = None
    best_phone: Phone | None = None
    phones: list[Phone] | None = None
    best_website: Website | None = None
    websites: list[Website] | None = None
    last_website_finding_date: datetime | None = None
    last_bce_update: datetime | None = None
    name: str | None = None
    name_fr: str | None = None
    name_nl: str | None = None
    name_de: str | None = None
    name_last_update: str | None = None
    social_networks: list[SocialNetwork] | None = None
    number_of_establishments: int | None = None
    establishments: list[Establishment] | None = None
    end_date: datetime | None = None
    legal_situation_last_update: str | None = None
    board_members: list[BoardMember] | None = None
    nace_codes: list[NaceCode] | None = None
    is_nace_codes_corrected: bool | None = False
    employee_category_code: int | None = None
    employee_category_formatted: str | None = None


def convert_dict_to_company(company_dict: dict) -> Company:
    """Convert a dict to a Company object."""
    company_dict = _parse_datetime_fields(company_dict)
    # Handle nested establishments
    establishments = []
    if company_dict.get('establishments'):
        for establishment in company_dict.get('establishments', []):
            establishment = _parse_datetime_fields(establishment)
            establishments.append(Establishment(
                establishment_number=establishment['establishment_number'],
                last_seen=establishment['last_seen'],
                status=establishment.get('status'),
                start_date=establishment.get('start_date'),
                country=establishment.get('country', 'BE'),
                name=establishment.get('name'),
                name_fr=establishment.get('name_fr'),
                name_nl=establishment.get('name_nl'),
                name_de=establishment.get('name_de'),
                name_last_update=establishment.get('name_last_update'),
                social_networks=[SocialNetwork(**sn) for sn in establishment.get('social_networks', []) or []],
                address=Address(**establishment.get('addresses', {})),
                best_email=establishment.get('best_email'),
                emails=[Email(**email) for email in establishment.get('emails', []) or []],
                best_phone=establishment.get('best_phone'),
                phones=[Phone(**phone) for phone in establishment.get('phones', []) or []],
                best_website=establishment.get('best_website'),
                websites=[Website(**website) for website in establishment.get('websites', []) or []],
                end_date=establishment.get('end_date'),
                nace_codes=[NaceCode(**nc) for nc in establishment.get('nace_codes', []) or []],
                is_nace_codes_corrected=establishment.get('is_nace_codes_corrected', False)
            ))

    # Create the Company instance
    return Company(
        _id=company_dict['_id'],
        company_number=company_dict['company_number'],
        country=company_dict.get('country', 'BE'),
        status=company_dict.get('status'),
        start_date=company_dict.get('start_date'),
        entity_type=company_dict.get('entity_type'),
        legal_form=company_dict.get('legal_form'),
        legal_form_last_update=company_dict.get('legal_form_last_update'),
        legal_situation=company_dict.get('legal_situation'),
        legal_situation_last_update=company_dict.get('legal_situation_last_update'),
        address=Address(**company_dict.get('addresses', {})),
        best_email=company_dict.get('best_email'),
        emails=[Email(**email) for email in company_dict.get('emails', []) or []],
        best_phone=company_dict.get('best_phone'),
        phones=[Phone(**phone) for phone in company_dict.get('phones', []) or []],
        best_website=company_dict.get('best_website'),
        websites=[Website(**website)for website in company_dict.get('websites', []) or []],
        last_website_finding_date=company_dict.get('best_website'),
        name=company_dict.get('name'),
        name_fr=company_dict.get('name_fr'),
        name_nl=company_dict.get('name_nl'),
        name_de=company_dict.get('name_de'),
        name_last_update=company_dict.get('name_last_update'),
        number_of_establishments=company_dict.get('number_of_establishments'),
        establishments=establishments,
        nace_codes=[NaceCode(**nc) for nc in company_dict.get('nace_codes', []) or []],
        is_nace_codes_corrected=company_dict.get('is_nace_codes_corrected', False),
        employee_category_code=company_dict.get('employee_category_code'),
        employee_category_formatted=company_dict.get('employee_category_formatted'),
        board_members=[BoardMember(**bm) for bm in company_dict.get('board_members', []) or []],
        end_date=company_dict.get('end_date'),
        social_networks=[SocialNetwork(**sn) for sn in company_dict.get('social_networks', []) or []],
    )


def _parse_datetime_fields(entity: dict) -> dict:
    """
    Parse datetime fields to ensure they are in the right format.
    
    Sometime we have to loose the timedate format for json serialization purpose. This fixes it.
    """
    field_nested_items_with_last_seen = ["addresses", "websites", "emails", "phones", "social_networks"]
    for field in field_nested_items_with_last_seen:
        entity_item_list = entity.get(field)
        if not entity_item_list:
            continue
        for i, item in enumerate(entity_item_list):
            if isinstance(item["last_seen"], str):
                entity[field][i]["last_seen"] = pendulum.parse(item["last_seen"], strict=False)
            if isinstance(item.get("last_update"), str):
                entity[field][i]["last_update"] = pendulum.parse(item["last_update"], strict=False)
    
    fields_datetime = ["start_date", "last_website_finding_date", "end_date", "name_last_update", "last_seen"]
    for field in fields_datetime:
        if isinstance(entity.get(field), str):
            entity[field] = pendulum.parse(entity[field], strict=False)
    return entity
