import asyncio
import json

import aiofiles
import aiohttp

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
]

SEMAPHORE = asyncio.Semaphore(5)
LOCK = asyncio.Lock()


async def fetch_url(url, session, file):
    async with SEMAPHORE:
        res = {"url": url}
        try:
            async with session.get(url, timeout=30) as response:
                res["status_code"] = response.status

        except asyncio.TimeoutError:
            res["status_code"] = 408
            res["error"] = "Request timeout"

        except aiohttp.ClientConnectionError:
            res["status_code"] = 0
            res["error"] = "Connection error"

        except Exception as e:
            res["status_code"] = 500
            res["error"] = str(e)

        async with LOCK:
            await file.write(json.dumps(res) + "\n")


async def fetch_urls(urls: list[str], file_path: str):
    async with (
        aiohttp.ClientSession() as session,
        aiofiles.open(file_path, "w") as file,
    ):
        tasks = [fetch_url(url, session, file) for url in urls]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(fetch_urls(urls, "./results.jsonl"))
