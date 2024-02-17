from pydantic import BaseModel, computed_field
from schwifty import IBAN, exceptions


class IbanResponse(BaseModel):
    iban: str
    is_valid: bool
    message: str = ""
    parsed: IBAN | str = ""

    @computed_field
    def account(self) -> dict:
        if self.parsed:
            return {
                "bban": self.parsed.bban.__str__(),
                "checksum_digits": self.parsed.checksum_digits,
                "account_code": self.parsed.account_code,
                "account_type": self.parsed.account_type,
                "in_sepa_zone": self.parsed.in_sepa_zone,
                "national_checksum_digits": self.parsed.national_checksum_digits,
                "formatted": self.parsed.formatted,
            }
        return {}

    @computed_field
    def bank(self) -> dict:
        if self.parsed:
            _bank = getattr(self.parsed, "bank", {})
            return _bank if _bank is not None else {}
        return {}

    @computed_field
    def country(self) -> dict:
        if self.parsed:
            _country = getattr(self.parsed, "country", {})
            return dict(_country) if _country is not None else {}
        return {}

    @computed_field
    def specification(self) -> dict:
        if self.parsed:
            _specification = getattr(self.parsed, "spec", {})
            if _specification is None:
                return {}
            return _specification
        return {}


def validate_iban(iban: str) -> dict:
    try:
        _iban = IBAN(iban, allow_invalid=False, validate_bban=True)
    except exceptions.SchwiftyException as e:
        response = IbanResponse(iban=iban, is_valid=False, message=str(e))
    else:
        response = IbanResponse(iban=_iban.compact, is_valid=True, parsed=_iban)
    return response.model_dump(exclude={"parsed": True, "specification": "regex"})
