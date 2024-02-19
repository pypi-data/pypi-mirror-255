import re

from iwashi.helper import HTTP_REGEX, session
from iwashi.visitor import Context, SiteVisitor


class Googl(SiteVisitor):
    NAME = "Googl"
    URL_REGEX: re.Pattern = re.compile(
        HTTP_REGEX + r"goo\.gl/(?P<id>\w+)", re.IGNORECASE
    )

    async def normalize(self, url: str) -> str:
        match = self.URL_REGEX.match(url)
        if match is None:
            return url
        return f'https://{match.group("id")}'

    async def visit(self, url, context: Context, id: str):
        res = await session.get(
            f"https://goo.gl/{id}",
        )
        context.create_result("Googl", url=url, score=1.0)
        context.visit(res.url)
