from common.priorities import AFTER_ALL_TARGET_MAX_METERS_PRIORITY
from focs._effects import (
    CurrentTurn,
    EffectsGroup,
    IsSource,
    LocalCandidate,
    MinOf,
    Planet,
    SetMaxSupply,
    SetSupply,
    Target,
    Value,
)

STANDARD_SUPPLY_GROWTH = EffectsGroup(  # increase 1 per turn, up to max
    scope=IsSource,
    activation=Planet()
    & (LocalCandidate.LastTurnConquered < CurrentTurn)
    & (LocalCandidate.LastTurnAttackedByShip < CurrentTurn),
    priority=AFTER_ALL_TARGET_MAX_METERS_PRIORITY,
    effects=SetSupply(value=MinOf(float, Value(Target.MaxSupply), Value + 1)),
)

BAD_SUPPLY = [
    EffectsGroup(
        description="BAD_SUPPLY_DESC",
        scope=IsSource,
        activation=Planet(),
        accountinglabel="BAD_SUPPLY_LABEL",
        effects=SetMaxSupply(value=Value + 0),
    ),
    STANDARD_SUPPLY_GROWTH,
]


AVERAGE_SUPPLY = [
    EffectsGroup(
        scope=IsSource,
        activation=Planet(),
        accountinglabel="AVERAGE_SUPPLY_LABEL",
        effects=SetMaxSupply(value=Value + 1),
    ),
    STANDARD_SUPPLY_GROWTH,
]

GREAT_SUPPLY = [
    EffectsGroup(
        description="GREAT_SUPPLY_DESC",
        scope=IsSource,
        activation=Planet(),
        accountinglabel="GREAT_SUPPLY_LABEL",
        effects=SetMaxSupply(value=Value + 2),
    ),
    STANDARD_SUPPLY_GROWTH,
]
