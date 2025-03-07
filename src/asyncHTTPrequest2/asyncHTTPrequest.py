import asyncio
import json

import aiofiles
import aiohttp


async def fetch_url(
    url: str,
    session: aiohttp.ClientSession,
    out_file,
    lock: asyncio.Lock,
    semaphore: asyncio.Semaphore,
):
    async with semaphore:
        result = {"url": url}
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    result["content"] = data
                else:
                    result["status_code"] = response.status
                    result["error"] = f"HTTP {response.status}"

        except asyncio.TimeoutError:
            result["status_code"] = 408
            result["error"] = "Request timeout"

        except aiohttp.ClientConnectionError:
            result["status_code"] = 0
            result["error"] = "Connection error"

        except Exception as e:
            result["status_code"] = 500
            result["error"] = str(e)

        async with lock:
            await out_file.write(json.dumps(result) + "\n")


async def fetch_urls(urls_file: str, result_file: str = "result.jsonl"):
    semaphore = asyncio.Semaphore(5)
    lock = asyncio.Lock()

    async with (
        aiohttp.ClientSession() as session,
        aiofiles.open(result_file, "a") as out_file,
        aiofiles.open(urls_file, "r") as in_file,
    ):
        tasks = []
        async for line in in_file:
            url = line.strip()
            if not url:
                continue

            tasks.append(fetch_url(url, session, out_file, lock, semaphore))

            if len(tasks) >= 20:
                await asyncio.gather(*tasks, return_exceptions=True)
                tasks.clear()

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(fetch_urls("urls.txt"))
