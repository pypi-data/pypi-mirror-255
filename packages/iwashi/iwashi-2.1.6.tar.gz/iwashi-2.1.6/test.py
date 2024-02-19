import asyncio

import iwashi


async def main():
    result = await iwashi.visit("https://www.youtube.com/@hololive")
    if result:
        iwashi.helper.print_result(result)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
