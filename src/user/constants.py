from enum import unique

from common.enums import StrEnum


@unique
class UserStatus(StrEnum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


@unique
class UserFriendshipState(StrEnum):
    REQUESTED = 'REQUESTED'
    ACCEPTED = 'ACCEPTED'
    BLOCKED = 'BLOCKED'
    REJECTED = 'REJECTED'
