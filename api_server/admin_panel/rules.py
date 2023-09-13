from typing import List

from fastapi import APIRouter, Query

from api_server.models import RuleResponse
from api_server.rule import Rule
from .auth import check_authentication

router = APIRouter()


@router.get("", response_model=List[RuleResponse])
async def get_rules(token: str = Query(...)):
    await check_authentication(token)
    # Get all the subclasses of the Rule base class
    rule_classes = Rule.__subclasses__()
    rules = []

    for rule_class in rule_classes:
        rules.append({
            "name": rule_class.name,
            "description": rule_class.description
        })
    return rules
