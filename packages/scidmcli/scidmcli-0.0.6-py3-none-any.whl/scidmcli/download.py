import re
from urllib.parse import unquote
from tqdm import tqdm
import aiohttp
import asyncio
from scidmcli.util import isNone, isFile


def get_file_from_content_disposition(content_disposition):
    _, params = content_disposition.split(';')
    for param in params.split(';'):
        name, value = param.strip().split('=')
        if name == 'filename':
            return unquote(value).strip('"')
        
    return 'unknown'

async def fetch_with_progress(url, header, path, chunk_size=1024):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=header, timeout=None) as resp:
            total = int(resp.headers.get('Content-Length', 0))
            if total == 0 and resp.headers.get('Content-Range'):
                match = re.match(r'bytes \d+-\d+/(\d+)', resp.headers['Content-Range'])
                if match:
                    total = int(match.group(1))

            count = 1
            if resp.headers.get('Content-Disposition'):
                filename = get_file_from_content_disposition(resp.headers['Content-Disposition'])
                if len(filename.rsplit('.', 1)) > 1:
                    name, ext = filename.rsplit('.', 1)
                    file_path = f'{path.rstrip("/")}/{name}.{ext}'
                    while not isNone(file_path) and isFile(file_path):
                        file_path = f'{path.rstrip("/")}/{name}({count}).{ext}'
                        count += 1
                else:
                    file_path = f'{path.rstrip("/")}/{filename}'
                    while not isNone(file_path) and isFile(file_path):
                        file_path = f'{path.rstrip("/")}/{filename}({count})'
                        count += 1
            else:
                file_path = f'{path.rstrip("/")}/unknown'
                while not isNone(file_path) and isFile(file_path):
                    file_path = f'{path.rstrip("/")}/unknown({count})'
                    count += 1

            with open(file_path, 'wb') as file, tqdm(
                desc=file_path,
                total=total,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                while True:
                    chunk = await resp.content.read(chunk_size)
                    if not chunk:
                        break
                    size = file.write(chunk)
                    bar.update(size)

async def download_file(resp, header, path):
    tasks = []
    for resource in resp.get('resources'):
        tasks.append(fetch_with_progress(resource["url"], header, path))

    await asyncio.gather(*tasks)
