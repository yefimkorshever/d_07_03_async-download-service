import asyncio

import os

import aiofiles
from aiohttp import web


INTERVAL_SECS = 1


async def archive(request):
    response = web.StreamResponse()
    archive_hash = request.match_info.get('archive_hash', 'Anonymous')
    folder_path = os.path.join('test_photos', archive_hash)

    response.headers['Content-Type'] = 'text/html'
    content_disposition = 'attachment; filename="archive.zip"'
    response.headers['Content-Disposition'] = content_disposition

    await response.prepare(request)

    process = await asyncio.create_subprocess_exec(
        'zip',
        '-',
        '.',
        '-r',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=folder_path
    )
    bytes_portion = 102400

    while True:
        portion = await process.stdout.read(bytes_portion)

        await response.write(portion)
        if process.stdout.at_eof():
            break

    return response

# pylint: disable=unused-argument


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
