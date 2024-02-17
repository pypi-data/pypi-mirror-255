from pydantic import BaseModel, computed_field
from schwifty import BIC, exceptions


class BicResponse(BaseModel):
    bic: str
    is_valid: bool
    exists: bool
    message: str = ""
    parsed: BIC | str = ""

    @computed_field
    def details(self) -> dict:
        if self.parsed:
            return {
                "type": self.parsed.type,
                "bank_code": self.parsed.bank_code,
                "bank_names": self.parsed.bank_names,
                "bank_short_names": self.parsed.bank_short_names,
                "branch_code": self.parsed.branch_code,
                "country": dict(self.parsed.country),
                "domestic_bank_codes": self.parsed.domestic_bank_codes,
                "formatted": self.parsed.formatted,
                "location_code": self.parsed.location_code,
            }
        return {}


def validate_bic(*, bic: str, enforce_swift_compliance: bool = True) -> dict:
    try:
        _bic = BIC(
            bic, allow_invalid=False, enforce_swift_compliance=enforce_swift_compliance
        )
    except exceptions.SchwiftyException as e:
        response = BicResponse(bic=bic, is_valid=False, exists=False, message=str(e))
    else:
        response = BicResponse(
            bic=_bic.compact, is_valid=True, exists=_bic.exists, parsed=_bic
        )
    return response.model_dump(exclude={"parsed": True})
