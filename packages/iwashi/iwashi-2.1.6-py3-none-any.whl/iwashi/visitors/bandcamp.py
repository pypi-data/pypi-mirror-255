from __future__ import annotations

import json
import re
from typing import List, TypedDict, Union

import bs4

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor

DATA_REGEX = r"preloadLink\s?=\s(?P<json>{[^;]+)"


class Bandcamp(SiteVisitor):
    NAME = "Bandcamp"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"(?P<id>[\w-]+\.)?bandcamp\.com/(?P<slug>[\w-]+)?", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        return (
            f'https://{match.group("id") or ""}bandcamp.com/{match.group("slug") or ""}'
        )

    async def visit(
        self, url, context: Context, id: str | None = None, slug: str | None = None
    ) -> None:
        res = await session.get(url)
        soup = bs4.BeautifulSoup(await res.text(), "html.parser")
        script = soup.select_one("script[type='application/ld+json']")
        if script is None:
            raise Exception("No script found")

        data: Root = json.loads(script.text)
        context.create_result(
            site_name="Bandcamp",
            url=url,
            name=data["name"],
            description=data.get("description"),
            profile_picture=data["image"],
        )

        for link in data["publisher"]["mainEntityOfPage"]:
            if link["@type"] != "WebPage":
                continue
            context.visit(link["url"])


AdditionalpropertyItem = TypedDict(
    "additionalProperty_item", {"@type": "str", "name": "str", "value": "int"}
)
AdditionalpropertyItem0 = TypedDict(
    "additionalProperty_item", {"@type": "str", "name": "str", "value": "str"}
)


class Pricespecification(TypedDict):
    minPrice: float


Offers = TypedDict(
    "offers",
    {
        "@type": "str",
        "url": "str",
        "priceCurrency": "str",
        "price": "float",
        "priceSpecification": "Pricespecification",
        "availability": "str",
    },
)
AlbumreleaseItem = TypedDict(
    "albumRelease_item",
    {
        "@type": "List[str]",
        "@id": "str",
        "name": "str",
        "additionalProperty": "List[Union[AdditionalpropertyItem, AdditionalpropertyItem0]]",
        "description": "str",
        "offers": "Offers",
        "musicReleaseFormat": "str",
        "image": "List[str]",
    },
)
AdditionalpropertyItem1 = TypedDict(
    "additionalProperty_item", {"@type": "str", "name": "str", "value": "bool"}
)
AdditionalpropertyItem2 = TypedDict(
    "additionalProperty_item", {"@type": "str", "name": "str", "value": "float"}
)
Offers0 = TypedDict(
    "offers",
    {
        "@type": "str",
        "url": "str",
        "priceCurrency": "str",
        "price": "float",
        "priceSpecification": "Pricespecification",
        "availability": "str",
        "additionalProperty": "List[Union[AdditionalpropertyItem, AdditionalpropertyItem2]]",
    },
)
AlbumreleaseItem0 = TypedDict(
    "albumRelease_item",
    {
        "@type": "List[str]",
        "@id": "str",
        "name": "str",
        "additionalProperty": "List[Union[AdditionalpropertyItem, AdditionalpropertyItem1, AdditionalpropertyItem0]]",
        "offers": "Offers0",
        "musicReleaseFormat": "str",
        "image": "List[str]",
    },
)
Inalbum = TypedDict(
    "inAlbum",
    {
        "@type": "str",
        "name": "str",
        "albumRelease": "List[Union[AlbumreleaseItem0, AlbumreleaseItem]]",
        "albumReleaseType": "str",
        "numTracks": "int",
    },
)
Byartist = TypedDict("byArtist", {"@type": "str", "name": "str", "@id": "str"})
MainentityofpageItem = TypedDict(
    "mainEntityOfPage_item", {"@type": "str", "url": "str", "name": "str"}
)
SubjectofItem = TypedDict(
    "subjectOf_item",
    {
        "@type": "str",
        "url": "str",
        "name": "str",
        "additionalProperty": "List[AdditionalpropertyItem0]",
    },
)
Foundinglocation = TypedDict("foundingLocation", {"@type": "str", "name": "str"})
Publisher = TypedDict(
    "publisher",
    {
        "@type": "str",
        "@id": "str",
        "name": "str",
        "additionalProperty": "List[Union[AdditionalpropertyItem, AdditionalpropertyItem1]]",
        "image": "str",
        "genre": "str",
        "description": "str",
        "mainEntityOfPage": "List[MainentityofpageItem]",
        "subjectOf": "List[SubjectofItem]",
        "foundingLocation": "Foundinglocation",
    },
)
Author = TypedDict(
    "author",
    {
        "@type": "str",
        "url": "str",
        "image": "str",
        "additionalProperty": "List[AdditionalpropertyItem]",
        "name": "str",
    },
)
CommentItem = TypedDict(
    "comment_item", {"@type": "str", "author": "Author", "text": "List[str]"}
)
Root = TypedDict(
    "Root",
    {
        "@type": "str",
        "@id": "str",
        "additionalProperty": "List[Union[AdditionalpropertyItem, AdditionalpropertyItem0]]",
        "name": "str",
        "description": "str",
        "duration": "str",
        "dateModified": "str",
        "datePublished": "str",
        "inAlbum": "Inalbum",
        "byArtist": "Byartist",
        "publisher": "Publisher",
        "copyrightNotice": "str",
        "comment": "List[CommentItem]",
        "keywords": "List[str]",
        "image": "str",
        "sponsor": "List[Author]",
        "mainEntityOfPage": "str",
        "@context": "str",
    },
)
