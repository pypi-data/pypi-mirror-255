from __future__ import annotations

from typing import List, TypedDict


class Title(TypedDict):
    content: str


class Channelexternallinkviewmodel(TypedDict):
    title: Title
    link: Title


class LinksItem(TypedDict):
    channelExternalLinkViewModel: Channelexternallinkviewmodel


class Aboutchannelviewmodel(TypedDict):
    description: str
    links: List[LinksItem]


class Metadata(TypedDict):
    aboutChannelViewModel: Aboutchannelviewmodel


class Aboutchannelrenderer(TypedDict):
    metadata: Metadata


class ContinuationitemsItem(TypedDict):
    aboutChannelRenderer: Aboutchannelrenderer


class Appendcontinuationitemsaction(TypedDict):
    continuationItems: List[ContinuationitemsItem]


class OnresponsereceivedendpointsItem(TypedDict):
    appendContinuationItemsAction: Appendcontinuationitemsaction


class AboutRes(TypedDict):
    onResponseReceivedEndpoints: List[OnresponsereceivedendpointsItem]
