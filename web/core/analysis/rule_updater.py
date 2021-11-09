from .phrase_identifier import Phrase
from web.core.models.entities import EntitySet, Entity
from web.core.models.rules import (
    CommonPropertiesRule,
    ParentalRule,
    NoSecondaryEntitySetException,
    SmallEntitySetException,
    NoCommonPropertiesException,
)


def update_rules(phrases: list[Phrase], node_cache: dict[str, Entity]):

    for phrase in phrases:

        if phrase.node_type != EntitySet:
            continue

        try:
            CommonPropertiesRule.create_or_update(phrase)
            ParentalRule.create_or_update(phrase, node_cache)
        except NoSecondaryEntitySetException:
            pass
        except SmallEntitySetException:
            pass
        except NoCommonPropertiesException:
            pass
