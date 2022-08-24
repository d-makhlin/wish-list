import json
import os
from enum import unique
from typing import Any, Dict, List
from uuid import UUID
from kafka import KafkaProducer

from common.enums import StrEnum

@unique
class KafkaTopic(StrEnum):
    GENERAL = 'GENERAL'


@unique
class NotificationType(StrEnum):
    USER_FRIENDSHIP_UPDATED = 'USER_FRIENDSHIP_UPDATED'
    WISH_ITEM_UPDATED = 'WISH_ITEM_UPDATED'
    WISH_LIST_UPDATED = 'WISH_LIST_UPDATED'


class NotificationService:
    host = os.environ.get('KAFKA_HOST', 'localhost')
    producer = KafkaProducer(
        bootstrap_servers=[f'{host}:9092'], 
        value_serializer=lambda x: json.dumps(x).encode('utf-8'))

    NotificationTypeTopicMap = {
        NotificationType.USER_FRIENDSHIP_UPDATED: KafkaTopic.GENERAL,
        NotificationType.WISH_ITEM_UPDATED: KafkaTopic.GENERAL,
        NotificationType.WISH_LIST_UPDATED: KafkaTopic.GENERAL,
    }

    @classmethod
    def notify(cls, users_ids: List[UUID], notification_type: NotificationType, payload: Dict[Any, Any] = {}) -> None:
        for user_id in users_ids:
            message = {'client_id': str(user_id), 'type': notification_type, 'payload': payload}
            cls._notify(cls.NotificationTypeTopicMap[notification_type], message)

    @classmethod
    def _notify(cls, topic: KafkaTopic, message: Dict[Any, Any]) -> None:
        cls.producer.send(topic, message)