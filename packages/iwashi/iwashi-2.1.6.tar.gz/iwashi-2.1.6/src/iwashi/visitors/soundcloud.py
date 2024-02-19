import json
import re
from typing import List, TypedDict

from loguru import logger

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor


class Soundcloud(SiteVisitor):
    NAME = "Soundcloud"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"soundcloud\.com/(?P<id>[-\w]+)", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        return f'https://soundcloud.com/{match.group("id")}'

    async def visit(self, url, context: Context, id: str):
        url = f"https://soundcloud.com/{id}"
        res = await session.get(
            url,
        )
        info_json = re.search(
            r"window\.__sc_hydration ?= ?(?P<info>.+);", await res.text()
        )
        if info_json is None:
            logger.warning(f"[Soundcloud] Could not find info for {url}")
            return
        info_list: Root = json.loads(info_json.group("info"))
        for info in info_list:
            if info["hydratable"] == "user":
                break
        else:
            logger.warning(f"[Soundcloud] Could not find user info for {url}")
            return

        context.create_result(
            "Soundcloud",
            url=url,
            name=info["data"]["username"],
            score=1.0,
            description=info["data"]["description"],
            profile_picture=info["data"]["avatar_url"],
        )

        client_id_res = await session.get(
            "https://a-v2.sndcdn.com/assets/0-bf97f26a.js",
        )
        match = re.search(
            r"client_id: ?\"(?P<client_id>\w{32})\"", await client_id_res.text()
        )
        if match is None:
            logger.warning(f"[Soundcloud] Could not find client_id for {url}")
            return
        client_id = match.group("client_id")

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ja,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "Authorization": "OAuth 2-294132-999490816-Mf51UTFjQ256LP",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Origin": "https://soundcloud.com",
            "Pragma": "no-cache",
            "Referer": "https://soundcloud.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "sec-ch-ua": '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        params = {
            "client_id": client_id,
            "app_version": "1697797929",
            "app_locale": "en",
        }

        profile_res = await session.get(
            f'https://api-v2.soundcloud.com/users/{info["data"]["urn"]}/web-profiles',
            params=params,
            headers=headers,
        )
        profile: List[ProfileItem] = await profile_res.json()
        for item in profile:
            context.visit(item["url"])


class ProfileItem(TypedDict):
    url: str
    network: str
    title: str


class Product(TypedDict):
    id: str


class CreatorSubscriptionsItem0(TypedDict):
    product: Product


class VisualsItem0(TypedDict):
    urn: str
    entry_time: int
    visual_url: str


class Visuals(TypedDict):
    urn: str
    enabled: bool
    visuals: List[VisualsItem0]
    tracking: None


class Badges(TypedDict):
    pro: bool
    pro_unlimited: bool
    verified: bool


class Data4(TypedDict):
    avatar_url: str
    city: str
    comments_count: int
    country_code: str
    created_at: str
    creator_subscriptions: List[CreatorSubscriptionsItem0]
    creator_subscription: CreatorSubscriptionsItem0
    description: str
    followers_count: int
    followings_count: int
    first_name: str
    full_name: str
    groups_count: int
    id: int
    kind: str
    last_modified: str
    last_name: str
    likes_count: int
    playlist_likes_count: int
    permalink: str
    permalink_url: str
    playlist_count: int
    reposts_count: None
    track_count: int
    uri: str
    urn: str
    username: str
    verified: bool
    visuals: Visuals
    badges: Badges
    station_urn: str
    station_permalink: str
    url: str


class RootItem0(TypedDict):
    hydratable: str
    data: Data4


Root = List[RootItem0]
