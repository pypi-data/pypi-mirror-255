import inspect

import json

from datetime import datetime, timezone

import uuid

from typing import Sequence, Tuple, Any, Callable
from cloudevents.pydantic import CloudEvent

import os
from google.cloud import pubsub_v1

from krules_companion_client import __version__
from krules_companion_client.commands import _validate_filter


class _JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if inspect.isfunction(obj):
            return obj.__name__
        elif isinstance(obj, object):
            return str(type(obj))
        return json.JSONEncoder.default(self, obj)


def _callback(publish_future, exception_handler=None):
    try:
        publish_future.result(timeout=0)
    except Exception as ex:
        if exception_handler is not None:
            exception_handler(ex)
        else:
            raise


class PubsubClient(object):

    def __init__(self, topic_path: str = None, subscription: str = None, client: pubsub_v1.PublisherClient = None):

        if client is None:
            self.client = pubsub_v1.PublisherClient()
        else:
            self.client = client

        if topic_path is None:
            self.topic_path = os.environ.get('COMPANION_INGESTION_TOPIC')

        else:
            self.topic_path = topic_path

        if subscription is None:
            self.subscription = os.environ.get('COMPANION_SUBSCRIPTION')
        else:
            raise ValueError("Subscription is required, check the COMPANION_SUBSCRIPTION environment variable")

        if "CE_SOURCE" in os.environ:
            self.source = os.environ.get('CE_SOURCE')
        else:
            self.source = f"CompanionClient/{__version__}"

    def publish(self, group: str = None, entity: str = None, filters: Sequence[Tuple[str, str, Any]] = (),
                properties: dict = None,
                exception_handler: Callable = None, **properties_kwargs) -> None:

        if filters is None:
            filters = []
        has_filters = len(filters) > 0

        if group is None:
            raise ValueError("group cannot be None")
        if entity is None and not has_filters:
            raise ValueError("one of entity or filters must be provided")

        if has_filters and len(filters) > 1:
            raise ValueError("currently, only a single filter is supported")

        if properties is None:
            properties = {}
        properties.update(properties_kwargs)

        event_type: str | None = None
        subject: str | None = None
        payload: dict = {}

        _id = str(uuid.uuid4())
        if has_filters:
            event_type = "io.krules.streams.group.v1.data"
            subject = f'group|{self.subscription}|{group}'
            filter = _validate_filter(filters[0])
            payload = {
                "data": properties,
                "entities_filter": filter,
            }
        else:
            event_type = "io.krules.streams.entity.v1.data"
            subject = f'entity|{self.subscription}|{group}|{entity}'
            payload = {
                "data": properties,
            }

        ext_props = {}
        ext_props['originid'] = _id  # TODO: #869394akv
        ext_props["subscription"] = self.subscription
        ext_props["group"] = group

        event = CloudEvent(
            id=_id,
            type=event_type,
            source=self.source,
            subject=subject,
            data=payload,
            time=datetime.now(timezone.utc),
            datacontenttype="application/json",
            # dataschema=dataschema,
        )

        event_obj = event.model_dump(exclude_unset=True, exclude_none=True)
        event_obj["data"] = json.dumps(event_obj["data"], cls=_JSONEncoder).encode()
        event_obj["time"] = event_obj["time"].isoformat()

        future = self.client.publish(self.topic_path, **event_obj, **ext_props, contentType="text/json")
        future.add_done_callback(lambda _future: _callback(_future, exception_handler))
