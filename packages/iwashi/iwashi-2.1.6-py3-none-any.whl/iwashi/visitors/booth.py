import re

import bs4

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor


class Booth(SiteVisitor):
    NAME = "Booth"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"(?P<id>[\w-]+)\.booth\.pm", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        return f'https://{match.group("id")}.booth.pm'

    async def visit(self, url, context: Context, id: str):
        res = await session.get(f"https://{id}.booth.pm")
        soup = bs4.BeautifulSoup(await res.text(), "html.parser")
        name_element: bs4.Tag = soup.find(
            attrs={"class": "home-link-container__nickname"}
        )  # type: ignore
        name = name_element is not None and name_element.find("a") or None
        desc_element: bs4.Tag = soup.find(attrs={"class": "description"})  # type: ignore
        description = (
            desc_element is not None
            and desc_element.find(attrs={"v-html": "formattedDescription"})
            or None
        )
        avater_element: bs4.Tag = soup.find(attrs={"class": "avatar-image"})  # type: ignore

        context.create_result(
            "Booth",
            url=url,
            name=name.text if name is not None else None,
            score=1.0,
            description=description.text if description is not None else None,
            profile_picture=avater_element.attrs["style"].split("url(")[1].split(")")[0]
            if avater_element is not None
            else None,
        )

        for link in desc_element.find_all(attrs={"class": "shop-contacts__link"}):
            link: bs4.Tag = link.find("a")  # type: ignore
            if link.has_attr("href"):
                context.visit(link.attrs["href"])
