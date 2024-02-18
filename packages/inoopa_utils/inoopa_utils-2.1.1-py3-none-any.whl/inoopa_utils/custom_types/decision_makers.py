from dataclasses import dataclass
from datetime import datetime
from bson import ObjectId


@dataclass
class DecisionMaker:
    # Foreign key to the `company` collection
    company_id: str
    firstname: str
    lastname: str
    source: str
    # The raw string from the source, will cleaned and classified into `function_string`
    raw_function_string: str
    function_string: str
    last_seen: datetime
    _id: ObjectId | None = None
    email: str | None = None
    email_score: int | None = None
    phone: str | None = None
    phone_score: int | None = None
    language: str | None = None
    function_code: int | None = None
    linkedin_url: str | None = None
    cluster: str | None = None
    cluster_score: float | None = None
    cluster_best_match: str | None = None

