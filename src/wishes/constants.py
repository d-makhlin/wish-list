from enum import unique

from common.enums import StrEnum


@unique
class WishItemStatus(StrEnum):
    OPEN = 'OPEN'
    BOOKED_TO_GIFT = 'BOOKED_TO_GIFT'
    GIFTED = 'GIFTED'
    OUTDATED = 'OUTDATED'
