from common.base_prod import TROOPS_PER_POP
from common.priorities import (
    AFTER_ALL_TARGET_MAX_METERS_PRIORITY,
    TARGET_AFTER_2ND_SCALING_PRIORITY,
    TARGET_EARLY_BEFORE_SCALING_PRIORITY,
    TARGET_SCALING_PRIORITY,
)
from focs._effects import (
    Abs,
    Adequate,
    Capital,
    CurrentTurn,
    DesignHasPart,
    EffectsGroup,
    EmpireStockpile,
    Focus,
    GalaxyMaxAIAggression,
    Happiness,
    HasEmpireStockpile,
    HasSpecies,
    Homeworld,
    Hostile,
    Influence,
    IsHuman,
    IsSource,
    LocalCandidate,
    MaxOf,
    MinOf,
    NamedReal,
    NamedRealLookup,
    OwnedBy,
    PartCapacity,
    Planet,
    Poor,
    SetCapacity,
    SetMaxTroops,
    SetRebelTroops,
    SetTargetHappiness,
    SetTargetInfluence,
    SetTroops,
    Ship,
    Source,
    StatisticCount,
    Target,
    Unowned,
    Value,
)

UNSTABLE_REBEL_TROOPS = [
    EffectsGroup(
        scope=IsSource,
        activation=~Unowned & ~Happiness(low=0),
        accountinglabel="INSTABILITY_REBELLION",
        priority=TARGET_EARLY_BEFORE_SCALING_PRIORITY,
        # more negative stability and more population generates more rebels each turn
        # TODO: scale with some species trait?
        effects=SetRebelTroops(value=Value + Abs(float, Target.Happiness) * (Target.Population / 5.0) ** 0.5),
    ),
    EffectsGroup(
        scope=IsSource,
        activation=Planet() & ~Unowned & ~HasEmpireStockpile(empire=Source.Owner, resource=Influence, low=0) & ~Capital
        # TODO: some species trait?
        ,
        accountinglabel="PARTISANS_REBELLION",
        priority=TARGET_EARLY_BEFORE_SCALING_PRIORITY,
        effects=SetTargetHappiness(
            value=Value - 0.5 * Abs(float, EmpireStockpile(empire=Source.Owner, resource=Influence)) ** 0.5
        ),
    ),
    EffectsGroup(
        scope=IsSource,
        activation=Planet() & ~Unowned & ~HasEmpireStockpile(empire=Source.Owner, resource=Influence, low=0) & ~Capital,
        accountinglabel="INFLUENCE_DEBT_DECAY",
        priority=TARGET_EARLY_BEFORE_SCALING_PRIORITY,
        effects=SetTargetInfluence(
            value=Value
            + 0.5
            * Abs(float, EmpireStockpile(empire=Source.Owner, resource=Influence)) ** 0.5
            / MaxOf(float, 1.0, StatisticCount(float, condition=Planet() & HasSpecies() & OwnedBy(empire=Source.Owner)))
        ),
    ),
    EffectsGroup(
        scope=IsSource,
        activation=Planet(environment=[Adequate]),
        accountinglabel="DEPENDENCE_ON_IMPERIAL_SUPPORT_DUE_TO_ENVIRONMENT",
        priority=TARGET_SCALING_PRIORITY,
        effects=SetRebelTroops(value=MaxOf(float, 0.0, Abs(float, Value / 1.5))),
    ),
    EffectsGroup(
        scope=IsSource,
        activation=Planet(environment=[Poor]),
        accountinglabel="DEPENDENCE_ON_IMPERIAL_SUPPORT_DUE_TO_ENVIRONMENT",
        priority=TARGET_SCALING_PRIORITY,
        effects=SetRebelTroops(value=MaxOf(float, 0.0, Abs(float, Value / 2.0))),
    ),
    EffectsGroup(
        scope=IsSource,
        activation=Planet(environment=[Hostile]),
        accountinglabel="DEPENDENCE_ON_IMPERIAL_SUPPORT_DUE_TO_ENVIRONMENT",
        priority=TARGET_SCALING_PRIORITY,
        effects=SetRebelTroops(value=MaxOf(float, 0.0, Abs(float, Value / 4.0))),
    ),
]

BASIC_DEFENSE_TROOPS = [
    EffectsGroup(
        scope=IsSource,
        activation=Homeworld() & ~Unowned,
        stackinggroup="HOMEWORLD_TROOPS_STACK",
        priority=TARGET_EARLY_BEFORE_SCALING_PRIORITY,
        effects=SetMaxTroops(value=Value + 4),
        # accountinglabel="HOMEWORLD_LABEL",
    ),
    EffectsGroup(
        scope=IsSource,
        activation=Planet() & ~Unowned,
        accountinglabel="IMPERIAL_GARRISON_LABEL",
        priority=TARGET_EARLY_BEFORE_SCALING_PRIORITY,
        effects=SetMaxTroops(value=Value + NamedRealLookup(name="IMPERIAL_GARRISON_MAX_TROOPS_FLAT")),
    ),
    EffectsGroup(
        scope=IsSource,
        activation=Planet() & Unowned,
        stackinggroup="BASIC_TROOPS_STACK",
        accountinglabel="INDEPENDENT_TROOP_LABEL",
        priority=TARGET_EARLY_BEFORE_SCALING_PRIORITY,
        effects=SetMaxTroops(value=Value + 10),
    ),
    EffectsGroup(
        scope=IsSource,
        activation=Planet(),
        stackinggroup="POPULATION_TROOPS_STACK",
        accountinglabel="DEF_ROOT_DEFENSE",
        priority=TARGET_EARLY_BEFORE_SCALING_PRIORITY,
        effects=SetMaxTroops(
            value=Value
            + Target.Population * NamedReal(name="BASIC_DEFENSE_TROOPS_MAX_TROOPS_PERPOP", value=1.0 * TROOPS_PER_POP)
        ),
    ),
    EffectsGroup(  # gives human bonuses when AI Aggression set to Beginner
        scope=IsSource,
        activation=IsHuman & (GalaxyMaxAIAggression == 0) & Planet(),  # human player, not human species
        accountinglabel="DIFFICULTY",
        effects=SetMaxTroops(value=MaxOf(float, 6, Value * 2)),
    ),
    EffectsGroup(  # base troops regeneration
        scope=IsSource,
        activation=Planet()
        & (LocalCandidate.LastTurnConquered < CurrentTurn)
        & (LocalCandidate.LastTurnAttackedByShip < CurrentTurn),
        priority=AFTER_ALL_TARGET_MAX_METERS_PRIORITY,
        effects=SetTroops(
            value=MinOf(
                float, Value(Target.MaxTroops), Value + NamedReal(name="BASIC_DEFENSE_TROOPS_TROOPREGEN_FLAT", value=1)
            )
        ),
    ),
]

PROTECTION_FOCUS_TROOPS = [
    EffectsGroup(  # double max troops
        scope=IsSource,
        activation=Planet() & Focus(type=["FOCUS_PROTECTION"]),
        stackinggroup="FOCUS_PROTECTION_TROOPS_STACK",
        priority=TARGET_AFTER_2ND_SCALING_PRIORITY,
        effects=SetMaxTroops(value=MaxOf(float, Value, Value * 2)),
        # accountinglabel="FOCUS_PROTECTION_LABEL",
    ),
    EffectsGroup(  # increase troop growth rate
        scope=IsSource,
        activation=Planet()
        & Focus(type=["FOCUS_PROTECTION"])
        & (LocalCandidate.LastTurnConquered < CurrentTurn)
        & (LocalCandidate.LastTurnAttackedByShip < CurrentTurn),
        accountinglabel="FOCUS_PROTECTION_LABEL",
        priority=AFTER_ALL_TARGET_MAX_METERS_PRIORITY,
        effects=SetTroops(
            value=MinOf(
                float, Value(Target.MaxTroops), Value + MaxOf(float, Target.MaxTroops, Target.Population) ** 0.5
            )
        ),
    ),
]

NO_OFFENSE_TROOPS = [
    EffectsGroup(
        description="NO_OFFENSE_TROOPS_DESC",
        scope=IsSource,
        activation=Ship & (DesignHasPart(name="GT_TROOP_POD") | DesignHasPart(name="GT_TROOP_POD_2")),
        stackinggroup="NO_OFFENSIVE_TROOPS_STACK",
        accountinglabel="NO_OFFENSIVE_TROOPS_LABEL",
        effects=[
            SetCapacity(partname="GT_TROOP_POD", value=Value * 0),  # float is not yet supported
            SetCapacity(partname="GT_TROOP_POD_2", value=Value * 0),  # float is not yet supported
        ],
    )
]


BAD_DEFENSE_TROOPS = [
    *BASIC_DEFENSE_TROOPS,
    EffectsGroup(
        description="BAD_DEFENSE_TROOPS_DESC",
        scope=IsSource,
        activation=Planet(),
        effects=SetMaxTroops(value=Value * 0.5),
        # accountinglabel="BAD_TROOPS_LABEL",
    ),
    *UNSTABLE_REBEL_TROOPS,
    *PROTECTION_FOCUS_TROOPS,
]

AVERAGE_DEFENSE_TROOPS = [
    *BASIC_DEFENSE_TROOPS,
    *UNSTABLE_REBEL_TROOPS,
    *PROTECTION_FOCUS_TROOPS,
]

GREAT_DEFENSE_TROOPS = [
    *BASIC_DEFENSE_TROOPS,
    EffectsGroup(
        description="GREAT_DEFENSE_TROOPS_DESC",
        scope=IsSource,
        activation=Planet(),
        effects=SetMaxTroops(value=Value * 2),
    ),
    *UNSTABLE_REBEL_TROOPS,
    *PROTECTION_FOCUS_TROOPS,
]


BAD_OFFENSE_TROOPS = [
    EffectsGroup(
        description="BAD_OFFENSE_TROOPS_DESC",
        scope=IsSource,
        activation=Ship & (DesignHasPart(name="GT_TROOP_POD") | DesignHasPart(name="GT_TROOP_POD_2")),
        stackinggroup="BAD_OFFENSIVE_TROOPS_STACK",
        accountinglabel="BAD_OFFENSIVE_TROOPS_LABEL",
        effects=[
            SetCapacity(partname="GT_TROOP_POD", value=PartCapacity(name="GT_TROOP_POD") * 0.5),
            SetCapacity(partname="GT_TROOP_POD_2", value=PartCapacity(name="GT_TROOP_POD_2") * 0.5),
        ],
    )
]

GOOD_DEFENSE_TROOPS = [
    *BASIC_DEFENSE_TROOPS,
    EffectsGroup(
        description="GOOD_DEFENSE_TROOPS_DESC",
        scope=IsSource,
        activation=Planet(),
        effects=SetMaxTroops(value=Value * 1.5),
        accountinglabel="GOOD_TROOPS_LABEL",
    ),
    *UNSTABLE_REBEL_TROOPS,
    *PROTECTION_FOCUS_TROOPS,
]
