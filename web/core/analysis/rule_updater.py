from .phrase_identifier import Phrase
from web.core.models.entities import EntitySet, Entity
from web.core.models.rules import (
    CommonPropertiesRule,
    ParentalRule,
    NoSecondaryEntitySetException,
    SmallEntitySetException,
    NoCommonPropertiesException,
    WrongApproximationsException
)


def update_rules(phrases: list[Phrase], node_cache: dict[str, Entity]):

    for phrase in phrases:

        if phrase.node_type != EntitySet:
            continue

        try:
            ParentalRule.create_or_update(phrase, node_cache)
        except NoSecondaryEntitySetException:
            pass
        except WrongApproximationsException:
            pass

        try:
            CommonPropertiesRule.create_or_update(phrase)
        except SmallEntitySetException:
            pass
        except NoCommonPropertiesException:
            pass
