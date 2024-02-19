import json
import re
from typing import List, TypedDict

import bs4
from loguru import logger

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor


class Nicovideo(SiteVisitor):
    NAME = "Nicovideo"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"(sp\.)?nicovideo\.jp/(?P<path>user|mylist)/(?P<id>\d+)",
        re.IGNORECASE,
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        if match.group("path") == "mylist":
            res = await session.get(
                f'https://www.nicovideo.jp/mylist/{match.group("id")}'
            )
            return await self.normalize(str(res.url))
        return f'nicovideo.jp/user/{match.group("id")}'

    async def visit(self, url, context: Context, path: str, id: str):
        url = f"https://www.nicovideo.jp/user/{id}"
        res = await session.get(
            f"https://www.nicovideo.jp/user/{id}",
        )
        soup = bs4.BeautifulSoup(await res.text(), "html.parser")
        element: bs4.Tag = soup.find(attrs={"id": "js-initial-userpage-data"})  # type: ignore
        if element is None:
            logger.warning(f"[Nicovideo] {id} not found")
            return None

        info: Root = json.loads(element.attrs["data-initial-data"])
        user = info["state"]["userDetails"]["userDetails"]["user"]
        context.create_result(
            "Nicovideo",
            url=url,
            score=1.0,
            name=user["nickname"],
            description=user["description"],
            profile_picture=user["icons"]["large"],
        )

        for link in user["sns"]:
            context.visit(link["url"])


class UserLevel(TypedDict):
    currentLevel: int
    nextLevelThresholdExperience: int
    nextLevelExperience: int
    currentLevelExperience: int


class SnsItem0(TypedDict):
    type: str
    label: str
    iconUrl: str
    screenName: str
    url: str


class CoverImage(TypedDict):
    ogpUrl: str
    pcUrl: str
    smartphoneUrl: str


class Icons(TypedDict):
    small: str
    large: str


class User(TypedDict):
    description: str
    decoratedDescriptionHtml: str
    strippedDescription: str
    isPremium: bool
    registeredVersion: str
    followeeCount: int
    followerCount: int
    userLevel: UserLevel
    userChannel: None
    isNicorepoReadable: bool
    sns: List[SnsItem0]
    coverImage: CoverImage
    id: int
    nickname: str
    icons: Icons


class FollowStatus(TypedDict):
    isFollowing: bool


class UserDetails1(TypedDict):
    type: str
    user: User
    followStatus: FollowStatus


class UserDetails(TypedDict):
    userDetails: UserDetails1


class State(TypedDict):
    userDetails: UserDetails


class Root(TypedDict):
    state: State
    nvapi: List
