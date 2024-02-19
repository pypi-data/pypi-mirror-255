from rich import markup
from rich.console import RenderableType
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static
from typing_extensions import override

from tooi.data.events import Event
from tooi.context import get_context
from tooi.entities import MediaAttachment, Status
from tooi.utils.datetime import format_datetime
from tooi.widgets.account import AccountHeader
from tooi.widgets.event_detail import EventDetail
from tooi.widgets.image import HalfblockImage
from tooi.widgets.link import Link
from tooi.widgets.markdown import Markdown
from tooi.widgets.poll import Poll


class StatusDetail(EventDetail):
    _revealed: set[str] = set()

    DEFAULT_CSS = """

    StatusDetail {
        .status_content {
            margin-top: 1;
        }

        .spoiler_text {
            margin-top: 1;
        }

        .sensitive {
            height: auto;
        }

        StatusSensitiveNotice { display: none; }

        &.hide_sensitive {
            .sensitive { display: none; }
            StatusSensitiveNotice { display: block; }
            StatusSensitiveOpenedNotice { display: none; }
        }
    }
    """

    def __init__(self, event: Event):
        super().__init__(event)
        assert event.status is not None
        self.context = get_context()
        self.status = event.status
        self.sensitive = self.status.original.sensitive
        self.set_class(self.sensitive and not self.revealed, "hide_sensitive")

    def reveal(self):
        if self.status.original.id in self._revealed:
            self._revealed.discard(self.status.id)
        else:
            self._revealed.add(self.status.id)

        self.set_class(self.sensitive and not self.revealed, "hide_sensitive")

    @property
    def revealed(self) -> bool:
        return (
            self.context.config.options.always_show_sensitive or
            self.status.original.id in self._revealed
        )

    def compose(self) -> ComposeResult:
        status = self.status.original

        if self.status.reblog:
            yield StatusHeader(f"boosted by {self.status.account.acct}")

        yield AccountHeader(status.account)

        if status.spoiler_text:
            yield Static(status.spoiler_text, markup=False, classes="spoiler_text")

        if status.sensitive:
            yield StatusSensitiveNotice()
            yield StatusSensitiveOpenedNotice()

        # Content which should be hidden if status is sensitive and not revealed
        with Vertical(classes="sensitive"):
            yield Markdown(status.content_md, classes="status_content")

            if status.poll:
                yield Poll(status.poll)

            if status.card:
                yield StatusCard(status)

            for attachment in status.original.media_attachments:
                yield StatusMediaAttachment(attachment)

        yield StatusMeta(status)

    @override
    def on_event_updated(self):
        """Called when the status has updated. Currently only updates the StatusMeta."""
        assert self.event and self.event.status
        self.query_one(StatusMeta).update_status(self.event.status)


class StatusHeader(Static):
    DEFAULT_CSS = """
    StatusHeader {
        color: gray;
        border-bottom: ascii gray;
    }
    """

    def __init__(self, renderable: RenderableType = ""):
        super().__init__(renderable, markup=False)


class StatusCard(Widget):
    DEFAULT_CSS = """
    StatusCard {
        border: round white;
        padding: 0 1;
        height: auto;
        margin-top: 1;
    }

    .title {
        text-style: bold;
    }
    """

    def __init__(self, status: Status):
        self.status = status
        super().__init__()

    def compose(self):
        card = self.status.original.card

        if not card:
            return

        yield Link(card.url, card.title, classes="title")

        if card.author_name:
            yield Static(f"by {card.author_name}", markup=False)

        if card.description:
            yield Static("")
            yield Static(card.description, markup=False)

        yield Static("")
        yield Link(card.url)


class StatusMediaAttachment(Widget):
    DEFAULT_CSS = """
    StatusMediaAttachment {
        border-top: ascii gray;
        height: auto;
    }

    .title {
        text-style: bold;
    }

    .media_attachment_image {
        margin-top: 1;
    }
    """

    attachment: MediaAttachment

    def __init__(self, attachment: MediaAttachment):
        self.attachment = attachment
        super().__init__()

    def compose(self):
        yield Static(f"Media attachment ({self.attachment.type})", markup=False, classes="title")
        if self.attachment.description:
            yield Static(self.attachment.description, markup=False)
        yield Link(self.attachment.url)

        if self.attachment.type == "image":
            yield HalfblockImage(
                self.attachment.preview_url,
                width=50,
                height=40,
                blurhash=self.attachment.blurhash,
                aspect_ratio=self.attachment.aspect_ratio,
                classes="media_attachment_image",
            )


class StatusMeta(Static):
    DEFAULT_CSS = """
    StatusMeta {
        color: gray;
        border-top: ascii gray;
    }
    """

    def __init__(self, status: Status):
        self.status = status
        self.ctx = get_context()
        super().__init__()

    def visibility_string(self, status: Status):
        vis = f"{status.visibility.capitalize()}"
        if status.local_only:
            vis += " (local only)"
        return vis

    def format_timestamp(self):
        relative = get_context().config.options.relative_timestamps
        created_ts = format_datetime(self.status.created_at, relative=relative)

        if self.status.edited_at:
            edited_ts = format_datetime(self.status.edited_at, relative=relative)
            return f"{created_ts} (edited {edited_ts} ago)"

        return created_ts

    def render(self):
        status = self.status.original
        reblogged = self.status.reblogged
        favourited = self.status.favourited

        parts = [
            f"[bold]{markup.escape(self.format_timestamp())}[/]",
            highlight(f"{status.reblogs_count} boosts", "yellow", reblogged),
            highlight(f"{status.favourites_count} favourites", "yellow", favourited),
            f"{status.replies_count} replies",
            markup.escape(self.visibility_string(status)),
        ]

        if status.application:
            parts.append(status.application.name)

        return " · ".join(parts)

    def update_status(self, status: Status):
        self.status = status
        self.refresh()


# TODO: this is not stylable via css so should probably be replaced by a widget
def highlight(text: str, color: str, cond: bool | None = True):
    return f"[{color}]{text}[/]" if cond else text


class StatusSensitiveNotice(Static):
    DEFAULT_CSS = """
    StatusSensitiveNotice {
        margin-top: 1;
        padding-left: 1;
        color: red;
        border: round red;
    }
    """

    def __init__(self):
        super().__init__("Marked as sensitive. Press S to view.")


class StatusSensitiveOpenedNotice(Static):
    DEFAULT_CSS = """
    StatusSensitiveOpenedNotice {
        margin-top: 1;
        padding-left: 1;
        color: gray;
        border: round gray;
    }
    """

    def __init__(self):
        super().__init__("Marked as sensitive. Press S to hide.")
