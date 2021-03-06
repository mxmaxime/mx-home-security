from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import Optional, Sequence, Type

from django.db.models import Model
import alarm.business.alarm as alarm
from devices.models import Device
from mqtt_services.models import MqttServicesConnectionStatusLogs
import mqtt_services.tasks as mqtt_tasks
from utils.mqtt import MQTT, MqttMessage
from utils.mqtt.mqtt_data import MqttTopicSubscriptionBoolean
from utils.mqtt.mqtt_service import ServiceDescriptor


SERVICE_STATUS_TOPIC_MATCHER = r"^[\w]+/(?P<service>[\w]+)/(?P<device_id>[\w]+)"

@dataclass
class ServiceStatusTopic:
    service: str
    device_id: str


def service_status_topic(topic: str) -> ServiceStatusTopic:
   match = re.match(SERVICE_STATUS_TOPIC_MATCHER, topic)
   if match:
       return ServiceStatusTopic(**match.groupdict())

   raise ValueError(f'topic {topic} can not be decoded for service status. Wrong format, should be like `connected/[service]/[device_id]`.')


class OnConnectedHandler(ABC):
    """Abstract class to implement and perform actions when mqtt service connect/disconnect.
    """
    def __init__(self, *_args, **_kwargs) -> None:
        pass

    @abstractmethod
    def on_connect(self, service_name: str, device_id: str) -> None:
        pass

    @abstractmethod
    def on_disconnect(self, service_name: str, device_id: str) -> None:
        pass


class OnConnectedVerifyStatusHandler:
    """
    Performs a test (for every connect/disconnect call) if the corresponding `running` field
    is set to the received `status` for the given pk device (device retrieve thanks to the `device_id`).
    If not, it creates a task which will handle this failure.
    Thanks to this, the system can monitor if a mqtt connection is "right": connected or disconnected when it should be,
    relying on the database to know the source of truth.
    For example, in the database the alarm status is on and the system receives a mqtt message that indicates a disconnect
    from the alarm.
    """

    def __init__(self, status_model: Type[Model], on_connect=True, on_disconnect=True):
        self._status_model = status_model
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect

    def _is_status_exist(self, service_name: str, device_id: str, status: bool) -> None:
        if not alarm.is_status_exists(self._status_model, device_id, status):
            kwargs = {
                'device_id': device_id,
                'received_status': status,
                'service_name': service_name,
            }

            mqtt_tasks.mqtt_status_does_not_match_database.apply_async(kwargs=kwargs)

    def on_connect(self, service_name: str, device_id: str) -> None:
        if self._on_connect:
            self._is_status_exist(service_name, device_id, True)

    def on_disconnect(self, service_name, device_id: str) -> None:
        if self._on_disconnect:
            self._is_status_exist(service_name, device_id, False)


class OnConnectedHandlerLog(OnConnectedHandler):
    """Handler that logs events to the database.
    """

    def on_connect(self, service_name: str, device_id: str) -> None:
        MqttServicesConnectionStatusLogs.objects.create(device_id=device_id, status=True, service_name=service_name)

    def on_disconnect(self, service_name: str, device_id: str) -> None:
        MqttServicesConnectionStatusLogs.objects.create(device_id=device_id, status=False, service_name=service_name)


class OnStatus:
    """
    Class to call the appropriate method on the handler
    depending on the mqtt payload with the extracted device_id from the mqtt topic.
    This helps to keep all mqtt services implementation the same.
    """

    def __init__(self, handler: OnConnectedHandler):
        self._handler = handler

    def on_connected(self, message: MqttMessage) -> None:
        topic = service_status_topic(message.topic)
        service_name = topic.service
        device_id = topic.device_id

        if not Device.objects.filter(device_id=device_id).exists():
            return None

        if message.payload is True:
            self._handler.on_connect(service_name, device_id)
        else:
            self._handler.on_disconnect(service_name, device_id)


def bind_on_connected(service_name: str, handler_instance: OnConnectedHandler) -> MqttTopicSubscriptionBoolean:
    on_status = OnStatus(handler_instance)

    return MqttTopicSubscriptionBoolean(f'connected/{service_name}/+', on_status.on_connected)


def on_connected_services(mqtt: MQTT, services: Sequence[ServiceDescriptor]) -> None:
    subscriptions = [bind_on_connected(service.name, service.on_connect(mqtt)) for service in services if service.on_connect is not None]
    mqtt.add_subscribe(subscriptions) 

