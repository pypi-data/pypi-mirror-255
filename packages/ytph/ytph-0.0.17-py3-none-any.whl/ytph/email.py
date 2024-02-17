import httpx as hx
from email_validator import EmailNotValidError
from email_validator import validate_email as _validate_email

from .utils.cache import TimeBoundedLRU
from .utils.email import FREE_DOMAINS

DISPOSABLE_EMAIL_URL = (
    "https://disposable.github.io/disposable-email-domains/domains.json"
)
FREE_EMAIL_URL = "https://f.hubspotusercontent40.net/hubfs/2832391/Marketing/Lead-Capture/free-domains-2.csv"


def _get_disposable_emails() -> list:
    try:
        emails = hx.get(url=DISPOSABLE_EMAIL_URL).raise_for_status().json()
    except (hx.HTTPError, hx.InvalidURL):
        emails = []
    return emails


get_disposable_emails = TimeBoundedLRU(
    func=_get_disposable_emails, maxsize=128, maxage=60 * 60 * 1
)


def _get_free_emails() -> list:
    try:
        _emails = hx.get(url=FREE_EMAIL_URL).raise_for_status()
    except (hx.HTTPError, hx.InvalidURL):
        emails = [*FREE_DOMAINS]
    else:
        disposable_emails_set = set(get_disposable_emails())
        hubspot_emails_set = set(_emails.text.splitlines())
        emails = [*list(hubspot_emails_set - disposable_emails_set), *FREE_DOMAINS]
    return emails


get_free_emails = TimeBoundedLRU(func=_get_free_emails, maxsize=128, maxage=60 * 60 * 1)


def validate_email(email: str) -> bool:
    try:
        _ = _validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return False
    return True
