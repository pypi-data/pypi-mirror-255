import re

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor


class Bitly(SiteVisitor):
    NAME = "Bitly"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"bit\.ly/(?P<id>\w+)", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        return f'https://bit.ly/{match.group("id")}'

    async def visit(self, url, context: Context, id: str):
        res = await session.get(
            f"https://bit.ly/{id}",
        )
        context.create_result("Bitly", url=url, score=1.0)
        context.visit(res.url)
