from copy import deepcopy
from typing import Any, List

from glom import assign, glom
from requests.utils import _parse_content_type_header  # type: ignore


def obfuscate_claim_value(value: Any) -> str:
    """
    Obfuscates the value of a claim, so it can be logged safely

    If a dict of claims is supplied, all of the values will be obfuscated
    """
    if isinstance(value, dict):
        for k, v in value.items():
            value[k] = obfuscate_claim_value(v)
        return value
    else:
        value = str(value)
        threshold = int(len(value) * 0.75)
        return "".join([x if i > threshold else "*" for i, x in enumerate(value)])


def obfuscate_claims(claims: dict, claims_to_obfuscate: List[str]) -> dict:
    copied_claims = deepcopy(claims)
    for claim_name in claims_to_obfuscate:
        # NOTE: this does not support claim names that have dots in them
        claim_value = glom(copied_claims, claim_name)
        assign(copied_claims, claim_name, obfuscate_claim_value(claim_value))
    return copied_claims


def extract_content_type(ct_header: str) -> str:
    """
    Get the content type + parameters from content type header.

    This is internal API since we use a requests internal utility, which may be
    removed/modified at any time. However, this is a deliberate choices since I trust
    requests to have a correct implementation more than coming up with one myself.
    """
    content_type, _ = _parse_content_type_header(ct_header)
    # discard the params, we only want the content type itself
    return content_type
