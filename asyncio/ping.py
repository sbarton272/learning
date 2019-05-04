import aiohttp
import asyncio
import random

url = 'http://google.com'

async def get(url, num):
  await asyncio.sleep(random.uniform(0, 1))
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
      return resp.status, num

loop = asyncio.get_event_loop()
tasks = [get(url, i) for i in range(10)]
statuses = loop.run_until_complete(asyncio.gather(*tasks))
print(statuses)
