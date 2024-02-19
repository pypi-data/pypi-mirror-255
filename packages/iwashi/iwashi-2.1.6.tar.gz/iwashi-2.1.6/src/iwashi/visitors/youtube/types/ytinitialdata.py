from typing import List, NotRequired, TypedDict


class thumbnail(TypedDict):
    url: str
    width: int
    height: int


class thumbnails(TypedDict):
    thumbnails: List[thumbnail]


class urlEndpoint(TypedDict):
    url: str


class webCommandMetadata(TypedDict):
    sendPost: bool
    apiUrl: str


class commandMetadata(TypedDict):
    webCommandMetadata: webCommandMetadata
    sendPost: bool
    apiUrl: str


class continuationCommand(TypedDict):
    token: str
    request: str


class continuationEndpoint(TypedDict):
    commandMetadata: commandMetadata
    continuationCommand: continuationCommand


class continuationItemRenderer(TypedDict):
    continuationEndpoint: continuationEndpoint


class itemSectionRenderer_content(TypedDict):
    continuationItemRenderer: continuationItemRenderer


class itemSectionRenderer(TypedDict):
    contents: List[itemSectionRenderer_content]


class sectionListRenderer_contents(TypedDict):
    itemSectionRenderer: itemSectionRenderer


class sectionListRenderer(TypedDict):
    contents: List[sectionListRenderer_contents]


class content(TypedDict):
    sectionListRenderer: sectionListRenderer


class engagementPanelSectionListRenderer(TypedDict):
    content: content


class engagementPanel(TypedDict):
    engagementPanelSectionListRenderer: engagementPanelSectionListRenderer


class showEngagementPanelEndpoint(TypedDict):
    engagementPanel: engagementPanel


class innertubeCommand(TypedDict):
    urlEndpoint: urlEndpoint
    showEngagementPanelEndpoint: showEngagementPanelEndpoint


class onTap(TypedDict):
    innertubeCommand: innertubeCommand


class _commandRuns(TypedDict):
    onTap: onTap


class firstLink(TypedDict):
    content: str
    commandRuns: List[_commandRuns]


class more(TypedDict):
    content: str
    commandRuns: List[_commandRuns]


class channelHeaderLinksViewModel(TypedDict):
    firstLink: NotRequired[firstLink]
    more: NotRequired[more]


class headerLinks(TypedDict):
    channelHeaderLinksViewModel: channelHeaderLinksViewModel


class runs_item(TypedDict):
    text: str


class runs(TypedDict):
    runs: List[runs_item]


class c4TabbedHeaderRenderer(TypedDict):
    channelId: str
    title: str
    avatar: thumbnails
    banner: thumbnails
    headerLinks: NotRequired[headerLinks]
    trackingParams: str
    channelHandleText: runs
    style: str


class header(TypedDict):
    c4TabbedHeaderRenderer: c4TabbedHeaderRenderer


class channelMetadataRenderer(TypedDict):
    title: str
    description: str
    rssUrl: str
    externalId: str
    keywords: str
    ownerUrls: List[str]
    avatar: thumbnails
    channelUrl: str
    isFamilySafe: bool
    vanityChannelUrl: str


class metadata(TypedDict):
    channelMetadataRenderer: channelMetadataRenderer


class link(TypedDict):
    hrefUrl: str


class linkAlternates(TypedDict):
    linkAlternates: List[link]


class microformatDataRenderer(TypedDict):
    urlCanonical: str
    title: str
    description: str
    thumbnail: thumbnails
    siteName: str
    appName: str
    urlApplinksWeb: str
    schemaDotOrgType: str
    noindex: bool
    unlisted: bool
    familySafe: bool
    linkAlternates: linkAlternates


class microformat(TypedDict):
    microformatDataRenderer: microformatDataRenderer


class ytinitialdata(TypedDict):
    header: header
    metadata: metadata
    microformat: microformat
