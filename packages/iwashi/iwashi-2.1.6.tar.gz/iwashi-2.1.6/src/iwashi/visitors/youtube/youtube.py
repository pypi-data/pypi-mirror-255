import json
import re
from pathlib import Path
from typing import Tuple
from urllib import parse

import bs4

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor

from .types import thumbnails, ytinitialdata
from .types.about import AboutRes


class Youtube(SiteVisitor):
    NAME = "Youtube"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"((m|gaming)\.)?(youtube\.com|youtu\.be)", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str | None:
        uri = parse.urlparse(url)
        if uri.hostname == "youtu.be":
            return await self._channel_by_video(uri.path[1:])
        type = next(filter(None, uri.path.split("/")))
        if type.startswith("@"):
            return f"https://www.youtube.com/{type}"
        if type == "playlist":
            return None
        if type == "watch":
            return await self._channel_by_video(parse.parse_qs(uri.query)["v"][0])
        if type in ("channel", "user", "c"):
            return await self._channel_by_url(url)
        return url

    async def _channel_by_video(self, video_id: str) -> str | None:
        res = await session.get(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        )
        if res.status == 404:
            return None
        data = await res.json()
        return data["author_url"]

    async def _channel_by_url(self, url: str) -> str | None:
        res = await session.get(url)
        if res.status == 404:
            return None
        soup = bs4.BeautifulSoup(await res.text(), "html.parser")
        data = self.extract_initial_data(soup)
        return data["metadata"]["channelMetadataRenderer"]["vanityChannelUrl"]

    def parse_thumbnail(self, thumbnails: thumbnails) -> str:
        size = 0
        url: str | None = None
        for thumbnail in thumbnails["thumbnails"]:
            if thumbnail["width"] > size:
                size = thumbnail["width"]
                url = thumbnail["url"]
        if url is None:
            raise RuntimeError("Thumbnail not found")
        return url

    def parse_token(
        self, data: ytinitialdata
    ) -> Tuple[str | None, Tuple[str, str] | None]:
        # TODO: 地獄
        first_link = None
        c4TabbedHeaderRenderer = data["header"]["c4TabbedHeaderRenderer"]
        if "headerLinks" not in c4TabbedHeaderRenderer:
            return (first_link, None)
        channelHeaderLinksViewModel = c4TabbedHeaderRenderer["headerLinks"][
            "channelHeaderLinksViewModel"
        ]
        if "firstLink" in channelHeaderLinksViewModel:
            first_link = channelHeaderLinksViewModel["firstLink"]["commandRuns"][0][
                "onTap"
            ]["innertubeCommand"]["urlEndpoint"]["url"]
        if "more" not in channelHeaderLinksViewModel:
            return (first_link, None)
        runs = channelHeaderLinksViewModel["more"]["commandRuns"]
        command = runs[0]["onTap"]["innertubeCommand"]
        if "showEngagementPanelEndpoint" not in command:
            raise RuntimeError("token not found")
        contents1 = command["showEngagementPanelEndpoint"]["engagementPanel"][
            "engagementPanelSectionListRenderer"
        ]["content"]["sectionListRenderer"]["contents"]
        contents2 = contents1[0]["itemSectionRenderer"]["contents"]
        endpoint = contents2[0]["continuationItemRenderer"]["continuationEndpoint"]
        api_url = endpoint["commandMetadata"]["webCommandMetadata"]["apiUrl"]
        token = endpoint["continuationCommand"]["token"]
        return (first_link, (api_url, token))

    def parse_redirect(self, url: str) -> str:
        uri = parse.urlparse(url)
        if uri.hostname != "www.youtube.com":
            return url
        if uri.path == "/redirect":
            return parse.parse_qs(uri.query)["q"][0]
        return url

    async def visit(self, url: str, context: Context):
        res = await session.get(url)
        if res.status // 100 != 2:
            raise RuntimeError(f"HTTP Error: {res.status}")
        soup = bs4.BeautifulSoup(await res.text(), "html.parser")
        data = self.extract_initial_data(soup)
        vanity_id = data["metadata"]["channelMetadataRenderer"]["vanityChannelUrl"]
        name = data["metadata"]["channelMetadataRenderer"]["title"]
        description = data["metadata"]["channelMetadataRenderer"]["description"]
        profile_picture = self.parse_thumbnail(
            data["metadata"]["channelMetadataRenderer"]["avatar"]
        )
        context.create_result(
            site_name="Youtube",
            url=f"https://www.youtube.com/@{vanity_id.split('@')[1]}",
            name=name,
            description=description,
            profile_picture=profile_picture,
        )

        first_link, api = self.parse_token(data)
        if first_link is not None:
            context.visit(self.parse_redirect(first_link))
        if api is None:
            return
        api_url, token = api
        about_res = await session.post(
            f"https://www.youtube.com{api_url}",
            data=json.dumps(
                {
                    "context": {
                        "client": {
                            "userAgent": session.headers["User-Agent"],
                            "clientName": "WEB",
                            "clientVersion": "2.20231219.04.00",
                        }
                    },
                    "continuation": token,
                }
            ),
        )
        about_data: AboutRes = await about_res.json()
        links = about_data["onResponseReceivedEndpoints"][0][
            "appendContinuationItemsAction"
        ]["continuationItems"][0]["aboutChannelRenderer"]["metadata"][
            "aboutChannelViewModel"
        ]["links"]
        for link in links:
            link_url = link["channelExternalLinkViewModel"]["link"]["content"]
            context.visit(self.parse_redirect(link_url))

    def extract_initial_data(self, soup: bs4.BeautifulSoup) -> ytinitialdata:
        for script in soup.select("script"):
            if script.string is None:
                continue
            match = re.search(r"ytInitialData\s*=\s*({.*?});", script.string)
            if match is not None:
                data: ytinitialdata = json.loads(match.group(1))
                break
        else:
            raise RuntimeError("ytInitialData not found")
        return data
