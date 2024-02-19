import json
import re
from typing import List, Optional, TypedDict, Union

import bs4

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor


class Linktree(SiteVisitor):
    NAME = "Linktree"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"linktr\.ee/(?P<id>\w+)", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        return f'https://linktr.ee/{match.group("id")}'

    async def visit(self, url, context: Context, id: str):
        res = await session.get(
            f"https://linktr.ee/{id}",
        )
        if res.status != 200:
            return None
        soup = bs4.BeautifulSoup(await res.text(), "html.parser")
        data_element = soup.find(attrs={"id": "__NEXT_DATA__"})
        assert data_element
        data: Root = json.loads(data_element.get_text())
        info = data["props"]["pageProps"]
        context.create_result(
            "Linktree",
            url=url,
            score=1.0,
            description=info["description"],
            profile_picture=info["profilePictureUrl"],
        )
        links = info["links"]
        for link in links:
            if not link["url"]:
                continue
            context.visit(link["url"])


class Owner(TypedDict):
    id: int
    isEmailVerified: bool


class Modifiers(TypedDict):
    animation: None
    isForwarding: bool
    isForwardingActive: bool
    thumbnailUrl: None
    amazonAffiliate: None


class Gate(TypedDict):
    activeOrder: List
    age: None
    passcode: None
    nft: None
    payment: None


class Rules(TypedDict):
    gate: Gate


class Context1(TypedDict):
    layoutOption: str


class Context2(TypedDict):
    channelId: str
    subscribe: None
    embedOption: str


class LinksItem0(TypedDict):
    id: int
    type: str
    title: str
    position: int
    url: str
    shouldRouteToProfile: bool
    modifiers: Modifiers
    context: Union[Context, Context1, Context2]
    rules: Rules


class Background(TypedDict):
    color: str
    style: str
    type: str


class BackgroundStyle(TypedDict):
    color: str


class ButtonStyle(TypedDict):
    type: str
    backgroundStyle: BackgroundStyle
    shadowStyle: BackgroundStyle
    textStyle: BackgroundStyle


class Typeface(TypedDict):
    color: str
    family: str


class Theme(TypedDict):
    key: str
    luminance: str
    background: Background
    buttonStyle: ButtonStyle
    socialStyle: BackgroundStyle
    typeface: Typeface


class ThemeV2(TypedDict):
    key: str
    luminance: str
    background: Background
    buttonStyle: ButtonStyle
    typeface: Typeface


class Account(TypedDict):
    id: int
    uuid: str
    username: str
    tier: str
    isActive: bool
    profilePictureUrl: str
    pageTitle: str
    googleAnalyticsId: None
    facebookPixelId: None
    tiktokPixelId: None
    donationsActive: bool
    causeBanner: None
    contentWarning: None
    description: str
    isLogoVisible: bool
    socialLinksPosition: str
    useFooterSignup: bool
    useSignupLink: bool
    createdAt: int
    updatedAt: int
    expandableLinkCaret: bool
    verticals: List[Optional[str]]
    customAvatar: str
    customAvatarAttributes: None
    backgroundImageAttributes: None
    showRepeatVisitorSignupCta: bool
    profileBadges: None
    isVenmoEnabled: bool
    isSquareWalletEnabled: bool
    isCookieBannerEnabled: bool
    isInitialsProfileEnabled: bool
    isWhatsappNotificationsEnabled: bool
    isShareLinksEnabled: bool
    isOnlyfansSEOEnabled: bool
    linkTypesForSEO: None
    manualTitleTag: None
    profileDirectoryUrl: None
    enableDynamicProfilePageMetadata: bool
    linkPlatforms: List[str]
    activeGates: List
    isAmazonAffiliateEnabled: bool
    profileLinkContentDisplayType: str
    complementaryThemeProperties: bool
    timezone: str
    affiliateTokens: List
    owner: Owner
    pageMeta: None
    integrations: List
    links: List[LinksItem0]
    socialLinks: List
    theme: Theme
    themeV2: ThemeV2


class SeoSchemaClassifications(TypedDict):
    typeClassification: None


class LinksItem01(TypedDict):
    id: str
    title: str
    context: Union[Context, Context2]
    animation: None
    thumbnail: None
    url: str
    amazonAffiliate: None
    type: str
    rules: Rules
    position: int
    locked: None


class ChildLinksItem0(TypedDict):
    id: str
    title: str
    context: Context2
    animation: None
    thumbnail: None
    url: str
    amazonAffiliate: None
    type: str
    rules: Rules
    position: int
    locked: None
    autoOpenOnActive: bool
    isContentMatchingType: bool


class LinksItem1(TypedDict):
    id: str
    title: str
    context: Context1
    animation: None
    thumbnail: None
    url: str
    amazonAffiliate: None
    type: str
    rules: Rules
    position: int
    locked: None
    childLinks: Union[List[ChildLinksItem0], List[ChildLinksItem0]]


class Environment(TypedDict):
    LINK_TYPES_ASSETS_ENDPOINT: str
    STRIPE_PAYMENTS_API_ENDPOINT: str
    STRIPE_PUBLISHABLE_KEY: str
    PAYPAL_PAYMENTS_API_ENDPOINT: str
    PAYPAL_PAYMENTS_CLIENT_ID: str
    SHOPIFY_INTEGRATIONS_API_ENDPOINT: str
    META_IMAGE_URL: str
    RECAPTCHA_SITE_KEY: str
    RECAPTCHA_SITE_KEY_INVISIBLE: str
    GRAPHQL_API_ENDPOINT: str
    PROFILES_API_HOST: str


class Auth0Config(TypedDict):
    clientID: str
    domain: str
    redirectUri: str
    responseType: str
    responseMode: str
    audience: str


class PageProps(TypedDict):
    account: Account
    theme: ThemeV2
    isProfileVerified: bool
    hasConsentedToView: bool
    username: str
    pageTitle: str
    description: str
    socialLinks: List
    integrations: List
    seoSchemaClassifications: SeoSchemaClassifications
    metaTitle: str
    metaDescription: str
    profilePictureUrl: str
    links: List[Union[LinksItem01, LinksItem1]]
    leapLink: None
    isOwner: bool
    isLogoVisible: bool
    mobileDetected: bool
    userAgent: str
    stage: str
    environment: Environment
    contentGating: str
    videoStructuredData: List
    hasSensitiveContent: bool
    auth0Config: Auth0Config
    followerNotificationsEnabled: bool
    followerCapabilities: None


class Props(TypedDict):
    pageProps: PageProps
    __N_SSP: bool


class Query(TypedDict):
    profile: str


class RuntimeConfig(TypedDict):
    INGRESS_API_ENDPOINT: str
    PAYMENTS_API_ENDPOINT: str
    ANALYTICS_SCRIPT_URL: str
    LINK_TYPES_ASSETS_ENDPOINT: str
    STAGE: str
    SERVICE: str
    WEB_VITALS: str
    DD_SAMPLE_RATE: str
    DD_CLIENT_TOKEN: str
    STRIPE_PAYMENTS_API_ENDPOINT: str
    STRIPE_PUBLISHABLE_KEY: str
    PAYPAL_PAYMENTS_API_ENDPOINT: str
    PAYPAL_PAYMENTS_CLIENT_ID: str
    SHOPIFY_INTEGRATIONS_API_ENDPOINT: str
    RECAPTCHA_SITE_KEY: str
    RECAPTCHA_SITE_KEY_INVISIBLE: str
    BASE_URL: str
    BASE_PROFILE_URL: str


class Root(TypedDict):
    props: Props
    page: str
    query: Query
    buildId: str
    assetPrefix: str
    runtimeConfig: RuntimeConfig
    isFallback: bool
    gssp: bool
    customServer: bool
    locale: str
    locales: List[str]
    defaultLocale: str
    scriptLoader: List
