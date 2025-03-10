import asyncio
import json

import aiofiles
import aiohttp


async def fetch_url(
    queue: asyncio.Queue,
    session: aiohttp.ClientSession,
    out_file,
    lock: asyncio.Lock,
):
    while True:
        url = await queue.get()
        if url is None:
            break

        result = {"url": url}
        try:
            async with session.get(url, timeout=60) as response:
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

        queue.task_done()


async def fetch_urls(urls_file: str, result_file: str = "result.jsonl"):
    queue = asyncio.Queue()
    lock = asyncio.Lock()

    async with (
        aiohttp.ClientSession() as session,
        aiofiles.open(result_file, "a") as out_file,
        aiofiles.open(urls_file, "r") as in_file,
    ):
        async for line in in_file:
            url = line.strip()
            if not url:
                continue
            await queue.put(url)

        workers = [asyncio.create_task(fetch_url(queue, session, out_file, lock)) for _ in range(5)]

        await queue.join()

        for _ in range(5):
            await queue.put(None)

        await asyncio.gather(*workers)


if __name__ == "__main__":
    asyncio.run(fetch_urls("urls.txt"))
