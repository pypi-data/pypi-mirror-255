"""Stream type classes for tap-pushbullet."""

from __future__ import annotations

from typing import Any, TypeVar

from singer_sdk import typing as th

from tap_pushbullet.client import PushbulletStream

__all__ = ["Chats", "Devices", "Pushes", "Subscriptions"]

W = TypeVar("W", bound=th.JSONTypeHelper)


class Property(th.Property):
    """Property type class for tap-pushbullet."""

    def __init__(
        self,
        *args: Any,
        example: Any | None = None,  # noqa: ANN401
        **kwargs: Any,
    ) -> None:
        """Initialize Property object.

        Args:
            *args: Positional arguments passed to super().
            example: Example value in the JSON Schema.
            **kwargs: Additional keyword arguments passed to super().
        """
        examples = kwargs.pop("examples", None)
        kwargs["examples"] = examples or ([example] if example else None)
        super().__init__(*args, **kwargs)


IDEN_FIELD = Property(
    "iden",
    th.StringType,
    description="Unique identifier for this object",
    example="ujpah72o0sjAoRtnM0jc",
)

CREATED_FIELD = Property(
    "created",
    th.NumberType,
    description=(
        "Creation time in floating point seconds "
        "([unix timestamp](https://en.wikipedia.org/wiki/Unix_time))"
    ),
    example="1381092887.398433",
)

MODIFIED_FIELD = Property(
    "modified",
    th.NumberType,
    description=(
        "Last modified time in floating point seconds "
        "([unix timestamp](https://en.wikipedia.org/wiki/Unix_time))"
    ),
    example="1441054560.741007",
)

ACTIVE_FIELD = Property(
    "active",
    th.BooleanType,
    description="`false` if the item has been deleted",
    example=False,
)


class EmailField(Property):
    """Email address field."""

    DESCRIPTION = "Email address of the person"

    def __init__(
        self,
        name: str,
        *,
        required: bool = False,
        default: str | None = None,
    ) -> None:
        """Initialize an EmailField.

        Args:
            name: Name of the field.
            required: Whether the field is required.
            default: Default value of the field.
        """
        super().__init__(
            name,
            th.StringType,
            required=required,
            default=default,
            description=self.DESCRIPTION,
            example="carmack@idsoftware.com",
        )


class NormalizedEmailField(EmailField):
    """Normalized email address field."""

    DESCRIPTION = "Canonical email address of the person"


class Chats(PushbulletStream):
    """Chats stream."""

    name = "chats"
    path = "/v2/chats"
    replication_key = "modified"
    records_jsonpath = f"$.{name}[*]"

    schema = th.PropertiesList(
        IDEN_FIELD,
        ACTIVE_FIELD,
        CREATED_FIELD,
        MODIFIED_FIELD,
        Property(
            "muted",
            th.BooleanType,
            description="If `true`, notifications from this chat will not be shown",
        ),
        Property(
            "with",
            th.ObjectType(
                EmailField("email"),
                NormalizedEmailField("email_normalized"),
                Property(
                    "iden",
                    th.StringType,
                    description="If this is a user, the iden of that user",
                    example="ujlMns72k",
                ),
                Property(
                    "image_url",
                    th.StringType,
                    description="Image to display for the person",
                    example="https://dl.pushbulletusercontent.com/abc/john.jpg",
                ),
                Property(
                    "type",
                    th.StringType,
                    description='`"email"` or `"user"`',
                    example="user",
                    allowed_values=["email", "user"],
                ),
                Property(
                    "name",
                    th.StringType,
                    description="Name of the person",
                    example="John Carmack",
                ),
            ),
            description="The user or email that the chat is with",
        ),
    ).to_dict()


class Devices(PushbulletStream):
    """Devices stream."""

    name = "devices"
    path = "/v2/devices"
    replication_key = "modified"
    records_jsonpath = f"$.{name}[*]"

    schema = th.PropertiesList(
        IDEN_FIELD,
        ACTIVE_FIELD,
        CREATED_FIELD,
        MODIFIED_FIELD,
        Property(
            "icon",
            th.StringType,
            description=(
                "Icon to use for this device, can be an arbitrary string. "
                'Commonly used values are: "desktop", "browser", "website", '
                '"laptop", "tablet", "phone", "watch", "system"'
            ),
            examples=["ios"],
        ),
        Property(
            "nickname",
            th.StringType,
            description="Name to use when displaying the device",
            example="Elon Musk's iPhone",
        ),
        Property(
            "generated_nickname",
            th.BooleanType,
            description=(
                "`true` if the nickname was automatically generated from the "
                "`manufacturer` and `model` fields (only used for some android phones)"
            ),
        ),
        Property(
            "manufacturer",
            th.StringType,
            description="Manufacturer of the device",
            example="Apple",
        ),
        Property(
            "model",
            th.StringType,
            description="Model of the device",
            example="iPhone 5s (GSM(",
        ),
        Property(
            "app_version",
            th.IntegerType,
            description="Version of the Pushbullet application installed on the device",
            example=8623,
        ),
        Property(
            "fingerprint",
            th.StringType,
            description=(
                "String fingerprint for the device, used by apps to avoid duplicate "
                "devices. Value is platform-specific."
            ),
            example="nLN19IRNzS5xidPF+X8mKGNRpQo2X6XBgyO30FL6OiQ=",
        ),
        Property(
            "key_fingerprint",
            th.StringType,
            description=(
                "Fingerprint for the device's end-to-end encryption key, used to "
                "determine which devices the current device (based on its own key "
                "fingerprint) will be able to talk to."
            ),
            example="5ae6ec7e1fe681861b0cc85c53accc13bf94c11db7461a2808903f7469bfda56",
        ),
        Property(
            "push_token",
            th.StringType,
            description=(
                "Platform-specific push token. If you are making your own device, "
                "leave this blank and you can listen for events on the "
                "[Realtime Event Stream]"
                "(https://docs.pushbullet.com/#realtime-event-stream)."
            ),
            example="production:f73be0ee7877c8c7fa69b1468cde764f",
        ),
        Property(
            "has_sms",
            th.BooleanType,
            description=(
                "`true` if the devices has SMS capability, currently only true for "
                '`type="android"` devices'
            ),
            example=True,
        ),
    ).to_dict()


class Pushes(PushbulletStream):
    """Pushes stream."""

    name = "pushes"
    path = "/v2/pushes"
    replication_key = "modified"
    records_jsonpath = f"$.{name}[*]"

    schema = th.PropertiesList(
        IDEN_FIELD,
        ACTIVE_FIELD,
        CREATED_FIELD,
        MODIFIED_FIELD,
        Property(
            "type",
            th.StringType,
            description='Type of the push, one of `"note"`, `"file"`, `"link"`.',
            example="note",
            allowed_values=["note", "file", "link"],
        ),
        Property(
            "dismissed",
            th.BooleanType,
            description="Whether the push has been dismissed",
        ),
        Property(
            "guid",
            th.StringType,
            description=(
                "Unique identifier set by the client, used to identify a push in case "
                "you receive it from `/v2/everything` before the call to `/v2/pushes` "
                "has completed. This should be a unique value. Pushes with `guid` set "
                "are mostly idempotent, meaning that sending another push with the "
                "same guid is unlikely to create another push (it will return the "
                "previously created push)."
            ),
            example="993aaa48567d91068e96c75a74644159",
        ),
        Property(
            "direction",
            th.StringType,
            description=(
                'Direction the push was sent in, can be `"self"`, `"outgoing"`, or '
                '`"incoming"`'
            ),
            example="self",
            allowed_values=["self", "outgoing", "incoming"],
        ),
        Property(
            "sender_iden",
            th.StringType,
            description="The push's sender's ID",
        ),
        EmailField("sender_email"),
        NormalizedEmailField("sender_email_normalized"),
        Property(
            "sender_name",
            th.StringType,
            description="Name of the sender",
            example="Elon Musk",
        ),
        Property(
            "receiver_iden",
            th.StringType,
            description="The push's receiver's ID",
        ),
        EmailField("receiver_email"),
        NormalizedEmailField("receiver_email_normalized"),
        Property(
            "target_device_iden",
            th.StringType,
            description=(
                "Device iden of the target device, if sending to a single device"
            ),
            example="ujpah72o0sjAoRtnM0jc",
        ),
        Property(
            "source_device_iden",
            th.StringType,
            description=(
                "Device iden of the sending device. Optionally set by the sender when "
                "creating a push"
            ),
            example="ujpah72o0sjAoRtnM0jc",
        ),
        Property(
            "client_iden",
            th.StringType,
            description=(
                "If the push was created by a client, set to the iden of that client."
            ),
            example="ujpah72o0sjAoRtnM0jc",
        ),
        Property(
            "channel_iden",
            th.StringType,
            description=(
                "If the push was created by a channel, set to the iden of that channel"
            ),
            example="ujpah72o0sjAoRtnM0jc",
        ),
        Property(
            "awake_app_guids",
            th.ArrayType(th.StringType),
            description=(
                "List of `guids` (client side identifiers, not the `guid` field on "
                "pushes) for awake apps at the time the push was sent. If the length "
                "of this list is > 0, `dismissed` will be set to `true` and the awake "
                "app(s) must decide what to do with the notification"
            ),
            example=["web-2d8cdf2a2b9b", "web-cdb2313c74e"],
        ),
        Property(
            "title",
            th.StringType,
            description="Title of the push, used for all types of pushes",
            example="Space Travel Ideas",
        ),
        Property(
            "body",
            th.StringType,
            description="Body of the push, used for all types of pushes",
            example="Space Elevator, Mars Hyperloop, Space Model S (Model Space?)",
        ),
        Property(
            "url",
            th.StringType,
            description='URL field, used for `type="link"` pushes',
            example="https://www.teslamotors.com/",
        ),
        Property(
            "file_name",
            th.StringType,
            description='File name, used for `type="file"` pushes',
            example="john.jpg",
        ),
        Property(
            "file_type",
            th.StringType,
            description='File mime type, used for `type="file"` pushes',
            example="image/jpeg",
        ),
        Property(
            "file_url",
            th.StringType,
            description='File download url, used for `type="file"` pushes',
            example="https://dl.pushbulletusercontent.com/abc/john.jpg",
        ),
        Property(
            "image_url",
            th.StringType,
            description=(
                'URL to an image to use for this push, present on `type="file"` pushes '
                "if file_type matches image/*"
            ),
            example="https://lh3.googleusercontent.com/abc",
        ),
        Property(
            "image_width",
            th.IntegerType,
            description="Width of image in pixels, only present if `image_url` is set",
            example=322,
        ),
        Property(
            "image_height",
            th.IntegerType,
            description="Height of image in pixels, only present if `image_url` is set",
            example=484,
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: Stream context.
            next_page_token: Token for the next page, if any.

        Returns:
            A mapping of URL parameter names to values.
        """
        params = super().get_url_params(context, next_page_token)
        params["active"] = "true"
        return params


class Subscriptions(PushbulletStream):
    """Subscriptions stream."""

    name = "subscriptions"
    path = "/v2/subscriptions"
    replication_key = "modified"
    records_jsonpath = f"$.{name}[*]"

    schema = th.PropertiesList(
        IDEN_FIELD,
        ACTIVE_FIELD,
        CREATED_FIELD,
        MODIFIED_FIELD,
        Property(
            "muted",
            th.BooleanType,
            description=(
                "If `true`, notifications from this subscription will not be shown"
            ),
        ),
        Property(
            "channel",
            th.ObjectType(
                Property(
                    "iden",
                    th.StringType,
                    description="Unique identifier for the channel",
                    example="ujpah72o0sjAoRtnM0jc",
                ),
                Property(
                    "tag",
                    th.StringType,
                    description="Unique tag for this channel",
                    example="elonmusknews",
                ),
                Property(
                    "name",
                    th.StringType,
                    description="Name of the channel",
                    example="Elon Musk News",
                ),
                Property(
                    "description",
                    th.StringType,
                    description="Description of the channel",
                    example="News about Elon Musk",
                ),
                Property(
                    "image_url",
                    th.StringType,
                    description="Image for the channel",
                    example="https://dl.pushbulletusercontent.com/abc/musk.jpg",
                ),
                Property(
                    "website_url",
                    th.StringType,
                    description="Link to a website for the channel",
                    example="https://twitter.com/elonmusk",
                ),
            ),
            description="Information about the channel that is being subscribed to",
        ),
    ).to_dict()
