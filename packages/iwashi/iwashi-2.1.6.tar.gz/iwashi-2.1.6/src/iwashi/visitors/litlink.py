from __future__ import annotations

import json
import re
from typing import Dict, List, TypedDict, Union

import bs4
from loguru import logger

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor


class LitLink(SiteVisitor):
    NAME = "LitLink"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"lit\.link/(?P<id>\w+)", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        return f'https://lit.link/{match.group("id")}'

    async def visit(self, url, context: Context, id: str):
        res = await session.get(
            f"https://lit.link/{id}",
        )
        soup = bs4.BeautifulSoup(await res.text(), "html.parser")
        data_element = soup.find(attrs={"id": "__NEXT_DATA__"})
        if data_element is None:
            logger.warning(f"[LitLink] Could not find data element for {url}")
            return
        data: Root = json.loads(data_element.get_text())
        profile = data["props"]["pageProps"]["profile"]

        context.create_result(
            "LitLink",
            url=url,
            name=profile["name"],
            score=1.0,
            description=profile["profileText"],
            profile_picture=profile["pictureUrl"],
        )

        for link in profile["snsIconLinks"]:
            if "url" not in link:
                continue
            context.visit(link["url"])


class SnsiconlinksItem(TypedDict):
    id: str
    type: str
    url: str
    userId: str
    creatorId: str


class Textlink(TypedDict):
    id: str
    title: None
    description: str
    publicationStartAt: None
    publicationEndAt: None
    userId: str
    creatorId: str


class ProfilelinksItem(TypedDict):
    profileLinkType: str
    buttonLink: None
    textLink: Textlink
    imageLink: None
    movieLink: None
    musicLink: None
    shopLink: None
    marginBlock: None


class Buttonlink(TypedDict):
    id: str
    iconUrl: str
    title: str
    description: None
    url: str
    urlType: str
    publicationStartAt: None
    publicationEndAt: None
    userId: str
    creatorId: str


class ProfilelinksItem0(TypedDict):
    profileLinkType: str
    buttonLink: Buttonlink
    textLink: None
    imageLink: None
    movieLink: None
    musicLink: None
    shopLink: None
    marginBlock: None


class Textlink0(TypedDict):
    id: str
    title: str
    description: str
    publicationStartAt: None
    publicationEndAt: None
    userId: str
    creatorId: str


class ProfilelinksItem1(TypedDict):
    profileLinkType: str
    buttonLink: None
    textLink: Textlink0
    imageLink: None
    movieLink: None
    musicLink: None
    shopLink: None
    marginBlock: None


class ProfileimagesItem(TypedDict):
    id: str
    iconUrl: None
    imageUrl: str
    title: None
    description: None
    url: str
    urlType: str
    imageLinkId: str


class Imagelink(TypedDict):
    id: str
    type: str
    profileImages: List[ProfileimagesItem]
    publicationStartAt: None
    publicationEndAt: None
    userId: str
    creatorId: str


class ProfilelinksItem2(TypedDict):
    profileLinkType: str
    buttonLink: None
    textLink: None
    imageLink: Imagelink
    movieLink: None
    musicLink: None
    shopLink: None
    marginBlock: None


class ProfileimagesItem0(TypedDict):
    id: str
    iconUrl: None
    imageUrl: str
    title: None
    description: None
    url: None
    urlType: str
    imageLinkId: str


class Imagelink0(TypedDict):
    id: str
    type: str
    profileImages: List[ProfileimagesItem0]
    publicationStartAt: None
    publicationEndAt: None
    userId: str
    creatorId: str


class ProfilelinksItem3(TypedDict):
    profileLinkType: str
    buttonLink: None
    textLink: None
    imageLink: Imagelink0
    movieLink: None
    musicLink: None
    shopLink: None
    marginBlock: None


class Creatordetaillayout(TypedDict):
    id: str
    fontFamily: str
    fontColor: str
    fontSize: str
    textAlign: str
    backgroundImageUrl: str
    backgroundColor: str
    backgroundGradation: str
    backgroundOverlayColor: str
    linkShape: str
    linkColor: str
    template: str
    userId: str
    creatorId: str


class Profile(TypedDict):
    uid: str
    userId: str
    creatorId: str
    name: str
    catchphrase: str
    sex: str
    birthday: str
    profileText: None
    urlPath: str
    pictureUrl: str
    pictureType: str
    snsIconLinks: List[SnsiconlinksItem]
    profileLinks: List[
        Union[
            ProfilelinksItem1,
            ProfilelinksItem0,
            ProfilelinksItem,
            ProfilelinksItem2,
            ProfilelinksItem3,
        ]
    ]
    creatorDetailLayout: Creatordetaillayout
    creatorSnsActivityCategories: List


class Account(TypedDict):
    email: str
    url: str
    emailUpdateResponse: None
    isLoading: bool
    lineConnected: bool
    emailConnected: bool
    urlUpdateResponse: None
    urlUpdateError: None


class Creatordetailedit(TypedDict):
    error: None
    isEdit: bool
    editingProfile: None
    isLoading: bool
    imageUpLoading: bool
    showSavedToast: bool
    toastText: str
    selectedIndexOnImageOrSnsModal: int
    showIconQrCode: bool
    hasSavedProfile: bool


class Genrecategory(TypedDict):
    isLoading: bool
    selectedMoreThanOne: bool
    selectedSnsActivityCategoryIds: List
    selectedSnsActivityGenreIds: List
    apiError: None


class Profile0(TypedDict):
    isLoggedIn: bool
    showCopiedMessage: bool
    showIconQrCode: bool
    profile: None
    isSendViewTypeAccessLog: bool


class Linelogin(TypedDict):
    isLoading: bool
    apiError: None
    lineLoginResponse: None
    hasInit: bool
    isError: bool


class Login(TypedDict):
    apiError: None
    loginResponse: None
    isLoading: bool
    loginErrorMessageId: None


class Modal(TypedDict):
    modalComponent: None
    modalOpened: bool
    masterModalId: str
    modalMaxWidth: int
    isFullSizeInMobile: bool
    onCloseModal: None


class Linemessaging(TypedDict):
    lineMessaging: None
    isLoading: bool


class Passwordreminder(TypedDict):
    passwordReminderResponse: None
    isLoading: bool
    isCompletedSendEmail: bool
    hasErrorResponse: bool


class Signup(TypedDict):
    isSignUpSuccess: bool
    signUpByLineResponse: None
    signUpEmailResponse: None
    isLoading: bool
    registeredAlready: bool
    defaultEmail: str
    hasErrorSignupResponse: bool


class Firebaseauth(TypedDict):
    firebaseUser: None
    isAuthLoading: bool
    isResendEmailVerificationSucceeded: None


class Signupdetail(TypedDict):
    isInstagramConnected: bool
    isTwitterConnected: bool
    isLoading: bool
    isVerifiedUrl: None


class Linesignup(TypedDict):
    apiError: bool
    lineSignUpResponse: None
    isLoading: bool
    signUpApiResponse: None


class DatasetsItem(TypedDict):
    label: str
    backgroundColor: str
    borderColor: str
    fill: bool
    tension: float
    data: List


class Usergraphaccesslog(TypedDict):
    labels: List
    datasets: List[DatasetsItem]


class Analytics(TypedDict):
    displayPeriod: str
    urlSortType: str
    topSortType: str
    isUrlSortAscendant: bool
    isTopSortAscendant: bool
    isReferralSortAscendant: bool
    isDeviceSortAscendant: bool
    pvCounts: int
    clickCounts: int
    accessTopTableSortType: str
    userTodayAccessLog: None
    userOneWeekAccessLog: None
    userOneMonthAccessLog: None
    userThreeMonthsAccessLog: None
    userSixMonthsAccessLog: None
    userOneYearAccessLog: None
    userAllAccessLog: None
    userGraphAccessLog: Usergraphaccesslog
    userUrlAccessLogs: List
    userTopAccessLogs: List
    userReferralAccessLogs: List
    userDeviceAccessLogs: List
    isAnalyticsStateLoading: bool
    urlAddedAreaHeight: int
    topAddedAreaHeight: int
    referralAddedAreaHeight: int
    isShowingMoreOnUrl: bool
    isShowingMoreOnTop: bool
    isShowingMoreOnReferral: bool
    isAnalyticsApiError: bool
    isShowingToast: bool
    apiError: None


class Notificationlist(TypedDict):
    isLoading: bool
    selectedNotificationId: None


class Creatordetailedittutorial(TypedDict):
    editingCreatorPreference: None
    tutorialCount: int
    isTutorialButtonEditDone: bool
    isTutorialLinkDraggerDone: bool
    isTutorialLinkEditDone: bool


class Accountdelete(TypedDict):
    isLoading: bool


class Profileimagenftmodal(TypedDict):
    isLoading: bool
    error: None


class Signupgenre(TypedDict):
    isSucceeded: None
    isLoading: bool
    selectedMoreThanOne: bool
    selectedSnsActivityCategoryIds: List
    selectedSnsActivityGenreIds: List


class Maintenance(TypedDict):
    isLoading: bool
    litlinkError: None
    isFirestoreMaintenanceMode: bool
    isApiMaintenanceMode: bool


class Authentication(TypedDict):
    userId: str
    accessToken: str
    apiError: None


class Urlalertmodal(TypedDict):
    alertUrlType: None
    alertMovieType: None
    alertMusicType: None
    alertShopType: None


class Profilesnsmodal(TypedDict):
    error: None
    editingSnsIconLinkDetails: List
    modalSnsType: None
    snsModalDefaultUrl: str
    updatingSnsIconLinkId: None


class Creator(TypedDict):
    creators: Dict
    currentCreatorId: None


class Creatordetaillayout0(TypedDict):
    creatorDetailLayouts: Dict


class Creatorsnsactivitycategory(TypedDict):
    creatorSnsActivityCategories: Dict


class Snsiconlink(TypedDict):
    snsIconLinks: Dict


class User(TypedDict):
    users: Dict


class Buttonlink0(TypedDict):
    buttonLinks: Dict


class Textlink1(TypedDict):
    textLinks: Dict


class Imagelink1(TypedDict):
    imageLinks: Dict


class Movielink(TypedDict):
    movieLinks: Dict


class Musiclink(TypedDict):
    musicLinks: Dict


class Shoplink(TypedDict):
    shopLinks: Dict


class Marginblock(TypedDict):
    marginBlocks: Dict


class Creatordetaileditlinks(TypedDict):
    isLoading: bool
    error: None
    editingProfileLinks: List
    isActiveUrlPastingOnText: bool
    profileLinkWidth: int
    profileLinkErrors: List
    multipleImageLinkIndex: int
    fourImageLinkIndex: int


class Fontcolor(TypedDict):
    r: int
    g: int
    b: int
    a: int


class Creatordetaileditprofile(TypedDict):
    isLoading: bool
    error: None
    editingCreatorDetailLayout: None
    selectedBackgroundCategory: str
    fontColor: Fontcolor
    backgroundColor: Fontcolor
    backgroundGradationStartColor: Fontcolor
    backgroundGradationEndColor: Fontcolor
    backgroundGradationColorPaletteIndex: int
    linkColor: Fontcolor
    backgroundImageUrlForOverlay: str


class Creatordetaileditgenre(TypedDict):
    error: None
    isLoading: bool
    selectedSnsActivityGenreId: None


class Snsactivitylist(TypedDict):
    error: None
    isLoading: bool


class Creatorpreference(TypedDict):
    creatorPreferences: Dict


class Notification(TypedDict):
    notifications: Dict


class Notificationrelationship(TypedDict):
    notificationRelationships: Dict
    totalNotificationUnreadCount: int


class Initialstate(TypedDict):
    account: Account
    creatorDetailEdit: Creatordetailedit
    genreCategory: Genrecategory
    profile: Profile0
    lineLogin: Linelogin
    login: Login
    modal: Modal
    lineMessaging: Linemessaging
    passwordReminder: Passwordreminder
    signUp: Signup
    firebaseAuth: Firebaseauth
    signupDetail: Signupdetail
    lineSignup: Linesignup
    analytics: Analytics
    notificationList: Notificationlist
    creatorDetailEditTutorial: Creatordetailedittutorial
    accountDelete: Accountdelete
    profileImageNFTModal: Profileimagenftmodal
    signupGenre: Signupgenre
    maintenance: Maintenance
    authentication: Authentication
    urlAlertModal: Urlalertmodal
    profileSnsModal: Profilesnsmodal
    creator: Creator
    creatorDetailLayout: Creatordetaillayout0
    creatorSnsActivityCategory: Creatorsnsactivitycategory
    snsIconLink: Snsiconlink
    user: User
    buttonLink: Buttonlink0
    textLink: Textlink1
    imageLink: Imagelink1
    movieLink: Movielink
    musicLink: Musiclink
    shopLink: Shoplink
    marginBlock: Marginblock
    creatorDetailEditLinks: Creatordetaileditlinks
    selectBackgroundImageModal: Profileimagenftmodal
    creatorDetailEditProfile: Creatordetaileditprofile
    creatorDetailEditGenre: Creatordetaileditgenre
    snsActivityList: Snsactivitylist
    creatorPreference: Creatorpreference
    editingMarginBlock: Profileimagenftmodal
    notification: Notification
    notificationRelationship: Notificationrelationship


class Pageprops(TypedDict):
    profile: Profile
    ogpImageUrl: str
    errorCode: str
    initialState: Initialstate


class Props(TypedDict):
    pageProps: Pageprops
    __N_SSP: bool


class Query(TypedDict):
    creatorUrl: str


class Root(TypedDict):
    props: Props
    page: str
    query: Query
    buildId: str
    isFallback: bool
    gssp: bool
    locale: str
    locales: List[str]
    defaultLocale: str
    scriptLoader: List
