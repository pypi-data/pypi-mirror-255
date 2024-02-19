from __future__ import annotations

import re
from typing import Dict, List, TypedDict, Union

import bs4

from iwashi.helper import BASE_HEADERS, HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor


class Mirrativ(SiteVisitor):
    NAME = "Mirrative"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"mirrativ.com/user/(?P<id>[\d]+)", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        return f'https://mirrativ.com/user/{match.group("id")}'

    async def fetch_scrf_token(self) -> str | None:
        res = await session.get(
            "https://www.mirrativ.com/",
        )
        soup = bs4.BeautifulSoup(await res.text(), "html.parser")
        element = soup.select_one('meta[name="csrf-token"]')
        if element is None:
            raise RuntimeError("Could not find csrf-token")
        return element.attrs.get("content")

    async def visit(self, url, context: Context, id: str):
        url = f"https://www.mirrativ.com/api/user/profile?user_id={id}"

        headers = BASE_HEADERS | {
            "accept": "application/json",
            "x-csrf-token": self.fetch_scrf_token(),
        }

        res = await session.get(
            "https://www.mirrativ.com/api/user/profile",
            params={
                "user_id": id,
            },
            headers=headers,
        )
        info: Root = await res.json()
        context.create_result(
            "Mirrativ",
            url=url,
            name=info["name"],
            score=1.0,
            description=info["description"],
            profile_picture=info["profile_image_url"],
        )

        for link in info["links"]:
            context.visit(link["url"])


class PreviewViewersItem(TypedDict):
    profile_frame_image_url: str
    badge_image_url: str
    profile_image_url: str
    yell_rank: int
    user_id: str


class SeasonYell(TypedDict):
    is_display_target: bool
    preview_viewers: List[PreviewViewersItem]
    total_viewer_count: int


class BadgesItem(TypedDict):
    image_url: str
    small_image_url: str


class LinksItem(TypedDict):
    url: str


class MutualFollowees(TypedDict):
    text: str
    image_urls: List


class Onlive(TypedDict):
    live_id: str


class Status(TypedDict):
    msg: str
    ok: int
    error: str
    captcha_url: str
    error_code: int
    message: str


class RibbonsItem(TypedDict):
    is_continuous_ribbon: int
    label_remaining_period: None
    image_url: str
    ribbon_id: int
    is_label: int


class RibbonsItem0(TypedDict):
    is_continuous_ribbon: int
    image_url: str
    is_label: int


class LabelRemainingPeriod(TypedDict):
    remain_seconds: int
    text: str
    is_highlight: int


class RibbonsItem1(TypedDict):
    is_continuous_ribbon: int
    label_remaining_period: LabelRemainingPeriod
    image_url: str
    ribbon_id: int
    is_label: int


class SeasonRating(TypedDict):
    class_name: str
    icon_url: str


class Root(TypedDict):
    avatar_body_image_url: str
    ambassador_image_url: str
    current_continuous_record: str
    registered_at: str
    custom_thanks_message: str
    profile_image_url: str
    season_yell: SeasonYell
    badges: List[BadgesItem]
    continuous_type: int
    is_visible_birthday: bool
    follower_num: str
    next_continuous_streamer_badge_url: str
    anniversary: Dict
    my_app_num: int
    links: List[LinksItem]
    mutual_followees: MutualFollowees
    grade_id: int
    twitter_screen_name: str
    birthday_to: int
    name: str
    description: str
    birthday_editable_date: str
    is_birthday: int
    properties: List
    total_viewer_num: int
    profile_frame_image_url: str
    live_announcement: None
    is_blocking: int
    is_blocked: int
    user_id: str
    paypal_username: str
    next_continuous_streamer_text: str
    onlive: Onlive
    share_url: str
    is_able_continuous_stream_holiday: int
    status: Status
    ribbons: List[Union[RibbonsItem, RibbonsItem0, RibbonsItem1]]
    birthday_from: int
    tutorial_mission: None
    is_birthday_editable: int
    avatar_background_image_url: str
    is_new: int
    following_num: str
    is_cheerleader: int
    catalog_label_image_url: str
    kakao_name: str
    is_follower: int
    has_started_first_live: int
    max_continuous_record: str
    season_rating: SeasonRating
    birthday: str
    user_level: Dict
    remaining_days_for_continuous_streamer: int
    continuous_achieved_text: str
    chat_enabled: int
    is_continuous_streamer: int
    is_following: int
    live_request_num: str
