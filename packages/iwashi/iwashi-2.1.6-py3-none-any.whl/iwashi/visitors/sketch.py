from __future__ import annotations

import json
import re
from typing import Dict, List, TypedDict

import bs4
from loguru import logger

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor


class Sketch(SiteVisitor):
    NAME = "Sketch"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"sketch\.pixiv\.net/@(?P<id>\w+)", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        return f'https://sketch.pixiv.net/@{match.group("id")}'

    async def visit(self, url, context: Context, id: str):
        res = await session.get(
            f"https://sketch.pixiv.net/@{id}",
        )
        soup = bs4.BeautifulSoup(await res.text(), "html.parser")
        # __NEXT_DATA__
        element: bs4.Tag = soup.find(attrs={"id": "__NEXT_DATA__"})  # type: ignore
        if element is None:
            logger.warning(f"__NEXT_DATA__ not found: {id}")
        next_data = json.loads(element.text)
        data: Root = json.loads(next_data["props"]["pageProps"]["initialState"])
        lives = tuple(data["live"]["lives"].values())
        if len(lives) == 0:
            return
        live = lives[0]
        users = data["users"]["users"]
        user_id = live["owner"]["user_id"]
        user = users[user_id]
        context.create_result(
            "Pixiv Sketch",
            url=url,
            name=user["name"],
            score=1.0,
            description=user["description"],
            profile_picture=user["icon"]["photo"]["original"]["url"],
        )

        context.visit(f'https://pixiv.net/users/{user["pixiv_user_id"]}')


class DescriptionFragmentsItem(TypedDict):
    type: str
    body: str
    normalized_body: str


class Sq800(TypedDict):
    url: str


class Thumbnail(TypedDict):
    sq800: Sq800
    w160: Sq800
    w400: Sq800
    w1280: Sq800
    original: Sq800


class Owner(TypedDict):
    user_id: str
    channel_id: str
    thumbnail: Thumbnail
    hls_movie: str
    is_enabled_mic_input: bool


class LiveInfo(TypedDict):
    finished_at: None
    description_fragments: List[DescriptionFragmentsItem]
    is_r15: bool
    is_closed: bool
    mode: str
    server: str
    is_r18: bool
    publicity: str
    is_adult: bool
    performers: List
    chat_count: int
    created_at: str
    member_count: int
    is_enabled_chat: bool
    name: str
    thumbnail: Thumbnail
    total_audience_count: int
    owner: Owner
    audience_count: int
    is_broadcasting: bool
    heart_count: int
    channel_id: str
    deleted: bool
    source: str
    id: str
    description: str
    is_single: bool
    performer_count: int
    is_enabled_mic_input: bool
    is_enabled_gifting: bool


class Options(TypedDict):
    filterBy: None
    orderBy: str


class Livelist(TypedDict):
    ids: List
    ended: bool
    fetching: bool
    options: Options


class Live(TypedDict):
    lives: Dict[str, LiveInfo]
    liveAdStages: Dict
    liveAvailability: bool
    liveClosedAvailability: bool
    liveLogs: Dict
    liveCaptions: Dict
    liveChatErrorMessage: None
    liveArchiveLink: Dict
    liveGiftings: Dict
    liveGiftingSummaries: Dict
    liveGiftingRecommends: Dict
    liveGiftingRecommendsPaging: Dict
    liveGiftingHistories: Dict
    liveSummaryUrl: None
    liveList: Livelist
    unpresentedBlacklistedLiveChats: List


class Color(TypedDict):
    hex: str
    r: int
    g: int
    b: int


class Pxsq60(TypedDict):
    width: int
    height: int
    url: str
    url2x: str


class Photo(TypedDict):
    pxsq60: Pxsq60
    pxw540: Pxsq60
    pxsq180: Pxsq60
    pxsq120: Pxsq60
    sq180: Pxsq60
    original: Pxsq60
    sq120: Pxsq60
    w240: Pxsq60
    sq60: Pxsq60
    w540: Pxsq60
    pxw240: Pxsq60


class Icon(TypedDict):
    id: int
    type: str
    color: Color
    photo: Photo


class Self(TypedDict):
    method: str
    href: str


class _Links(TypedDict):
    self: Self


class Stats(TypedDict):
    follower_count: int
    following_count: int
    heart_count: int
    resnap_count: int
    public_post_count: int


class UserInfo(TypedDict):
    description_fragments: List
    name: str
    followed: bool
    following: bool
    blocking: bool
    icon: Icon
    unique_name: str
    post_ids: List
    _links: _Links
    id: str
    pixiv_user_id: str
    description: str
    stats: Stats


Usercolors = TypedDict(
    "userColors",
    {"15241365": "str", "17391869": "str", "30087679": "str", "50150007": "str"},
)


class Users0(TypedDict):
    users: Dict[str, UserInfo]
    userWalls: Dict
    userLinks: Dict
    userColors: Usercolors
    usersRecommended: List
    usersBlockedWall: List
    usersBlockedWallLink: Dict


class Params(TypedDict):
    id: str


class Navigation(TypedDict):
    name: str
    params: Params
    search: Dict


class Status(TypedDict):
    code: str
    message: None


class Route(TypedDict):
    historyState: None
    isNavigating: bool
    navigation: Navigation
    status: Status


class Root(TypedDict):
    live: Live
    users: Users0
    route: Route
