from typing import List

from django.db.models import QuerySet, Q
from common.notification_service import NotificationService, NotificationType

from user.constants import UserFriendshipState
from user.models import User
from user.models.userfriendship import UserFriendship


class UserFriendshipService:
    @classmethod
    def create_user_friendship(cls, sender, receiver: User) -> UserFriendship:
        existing = UserFriendship.objects.filter(
            Q(sender_id=sender.id, receiver_id=receiver.id) | Q(receiver_id=sender.id, sender_id=receiver.id)).first()
        if not existing:
            return UserFriendship.objects.create(sender=sender, receiver=receiver)

        if existing.state in (UserFriendshipState.REQUESTED, UserFriendshipState.ACCEPTED):
            return existing
        if existing.state == UserFriendshipState.REJECTED:
            if existing.sender_id == receiver.id:
                existing.sender = sender
                existing.receiver = receiver
            existing.state = UserFriendshipState.REQUESTED
            existing.save()
            NotificationService().notify([sender.id, receiver.id], NotificationType.USER_FRIENDSHIP_UPDATED)
            return existing
        # ToDo raise error if already blocked

    @staticmethod
    def get_user_friendships_by_state(user_id: str, state: UserFriendshipState) -> QuerySet[UserFriendship]:
        if state in (UserFriendshipState.REQUESTED, UserFriendshipState.BLOCKED):
            return UserFriendship.objects.filter(sender_id=user_id, state=state)
        return UserFriendship.objects.filter(state=state).filter(Q(sender_id=user_id) | Q(receiver_id=user_id))

    @classmethod
    def accept_friendship_request(cls, user_friendship: UserFriendship) -> UserFriendship:
        user_friendship.state = UserFriendshipState.ACCEPTED
        user_friendship.save()
        NotificationService().notify([user_friendship.sender_id, user_friendship.receiver_id], NotificationType.USER_FRIENDSHIP_UPDATED)
        return user_friendship

    @classmethod
    def reject_friendship_request(cls, user_friendship: UserFriendship) -> UserFriendship:
        user_friendship.state = UserFriendshipState.REJECTED
        user_friendship.save()
        NotificationService().notify([user_friendship.receiver_id], NotificationType.USER_FRIENDSHIP_UPDATED)
        return user_friendship

    @staticmethod
    def is_in_friendship(user_1_id, user_2_id: str) -> bool:
        return (
            UserFriendship.objects.filter(state=UserFriendshipState.ACCEPTED)
            .filter(Q(sender_id=user_1_id, receiver_id=user_2_id) | Q(sender_id=user_2_id, receiver_id=user_1_id))
            .exists()
        )

    @classmethod
    def notify_friends(cls, user_id: str, notification_type: NotificationType) -> None:
        friendships = cls.get_user_friendships_by_state(user_id, UserFriendshipState.ACCEPTED).values('sender_id', 'receiver_id')
        NotificationService().notify(
            [f['sender_id'] if f['sender_id'] != user_id else f['receiver_id'] for f in friendships], notification_type)
