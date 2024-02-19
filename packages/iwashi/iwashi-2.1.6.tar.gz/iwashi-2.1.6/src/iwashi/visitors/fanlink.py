from __future__ import annotations

import json
import re
from typing import List, TypedDict, Union

import bs4

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor

DATA_REGEX = r"preloadLink\s?=\s(?P<json>{[^;]+)"


class Fanlink(SiteVisitor):
    NAME = "Fanlink"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"(?P<id>[\w-]+\.)?fanlink\.to/(?P<slug>[\w-]+)", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        id = match.group("id")
        if id is None:
            return f'https://fanlink.to/{match.group("slug")}'
        return f'https://{id}fanlink.to/{match.group("slug")}'

    async def visit(
        self, url, context: Context, id: str | None = None, slug: str | None = None
    ) -> None:
        res = await session.get(url)
        soup = bs4.BeautifulSoup(await res.text(), "html.parser")
        for script in soup.find_all("script"):
            if not script.string:
                continue
            match = re.search(DATA_REGEX, script.string)
            if match is None:
                continue
            data = json.loads(match.group("json"))
            break
        else:
            raise Exception("No script found")

        context.create_result(
            site_name="Fanlink",
            url=url,
            name=data["title"],
            description=data["description"],
            profile_picture=data["image_url"],
        )

        for link in data["social_settings"]:
            context.visit(link["url"])


class ScheduleItem(TypedDict):
    type: str
    start_date: str


class PixelsItem(TypedDict):
    platform: str


class ServicesItem(TypedDict):
    id: int
    url: str
    type: str
    active: bool
    track_id: str
    service_name: str
    match_confidence: int
    clickthrough_count: int


class ServicesItem0(TypedDict):
    id: int
    url: str
    isrc: str
    type: str
    active: bool
    track_id: str
    preview_url: str
    service_name: str
    match_confidence: int
    clickthrough_count: int


class ServicesItem1(TypedDict):
    id: int
    url: str
    type: str
    active: bool
    track_id: str
    preview_url: str
    service_name: str
    match_confidence: int
    clickthrough_count: int


class ServicesItem2(TypedDict):
    id: int
    active: bool
    rescan: bool
    service_name: str
    match_confidence: None
    clickthrough_count: int


class ServicesItem3(TypedDict):
    id: int
    url: str
    active: bool
    track_id: str
    preview_url: str
    service_name: str
    match_confidence: int
    clickthrough_count: int


class ServicesItem4(TypedDict):
    id: int
    active: bool
    service_name: str
    attachment_id: int
    clickthrough_count: int


class SocialSettingsItem(TypedDict):
    url: str
    color: str
    active: bool
    platform: str


class Root(TypedDict):
    click_count: int
    past_events: None
    schedule: List[ScheduleItem]
    id: int
    active_job_id: None
    author: str
    call_to_action: str
    button_color: str
    bg_color: None
    clickthrough_count: int
    emails_sent: None
    custom_domain: None
    date: None
    description: None
    display_content: None
    location: None
    price: None
    image_url: str
    bg_url: None
    is_hidden: bool
    is_active: bool
    message_settings: None
    isrc: None
    upc: None
    metadata_description: str
    metadata_image_url: str
    metadata_title: str
    meta_tags: List
    preview_url: str
    autoplay_preview: bool
    rsvp_attachment_id: None
    mock_insights: bool
    sort_services_by_clickthroughs: bool
    affiliate_codes: None
    pixels: List[PixelsItem]
    rules: List
    services: List[
        Union[
            ServicesItem0,
            ServicesItem3,
            ServicesItem,
            ServicesItem1,
            ServicesItem4,
            ServicesItem2,
        ]
    ]
    shortened_path: str
    show_socials: bool
    skip_landing_page: bool
    social_settings: List[SocialSettingsItem]
    subdomain: str
    target_type: str
    target_url: str
    title: str
    header: str
    use_saved_service: bool
    user_id: int
    createdAt: str
    updatedAt: str
    rsvp_attachment: None
