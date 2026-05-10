# asyncio import gareko
# Yo asynchronous programming garna use huncha
# Multiple tasks lai same time ma manage garna help garcha
import asyncio

# aiohttp import gareko
# Yo async HTTP requests garna use huncha
# requests library जस्तै हो, तर async/concurrent API calls ko lagi
import aiohttp

# time module import gareko
# Program kati time lagyo measure garna use huncha
import time


# URLs ko list banako
# Each URL le response dina 2 seconds delay garcha
urls = [
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/2",
]


# async function banako
# Yo single URL fetch garna use huncha
# async means यो function pause/resume huna sakcha without blocking whole program
async def fetch(session, url):

    # session.get(url) le async GET request send garcha
    # async with le response resource safely open/close garcha
    async with session.get(url) as response:

        # Response JSON data wait garera read gareko
        # await means "yo काम complete नभएसम्म wait गर,
        # tara अरू async tasks चल्न देऊ"
        data = await response.json()

        # Response status code return gareko
        # Example: 200 means success
        return response.status


# Main async function
# Program ko main async logic यहीं हुन्छ
async def main():

    # Start time record gareko
    start = time.time()

    # aiohttp ClientSession create gareko
    # एउटै session reuse गर्दा multiple requests efficient हुन्छ
    async with aiohttp.ClientSession() as session:

        # Tasks store garna empty list banako
        tasks = []

        # urls list ko each URL ko lagi task prepare gareko
        for url in urls:

            # fetch(session, url) coroutine create garera tasks list ma add gareko
            # Note: यहाँ अझै request execute भएको छैन
            tasks.append(fetch(session, url))

        # asyncio.gather le सबै tasks lai concurrently run garcha
        # Meaning: 5 ota API calls almost same time ma start huncha
        results = await asyncio.gather(*tasks)

    # End time record gareko
    end = time.time()

    # सबै requests ko status codes print gareko
    print("Status codes:", results)

    # Total execution time print gareko
    print("Total time:", end - start)


# Async program start gareko
# asyncio.run() le main() coroutine execute garcha
asyncio.run(main())