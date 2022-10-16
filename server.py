import argparse
import asyncio
import functools
import logging
import os

import aiofiles
from aiohttp import web
from environs import Env


def create_input_args_parser():
    description = ('Asynchronous download service.')
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        '--debug_mode',
        help='Turn on debug mode',
        action="store_true",
    )

    parser.add_argument(
        '--response_delay',
        metavar='{response delay}',
        help='Set response delay in seconds, 0 by default',
        type=int,
    )

    parser.add_argument(
        '--folder_path',
        metavar='{folder path}',
        help='Path to photos folder, test_photos by default',
    )

    return parser


async def archive(request, response_delay, folder_path):
    response = web.StreamResponse()
    archive_hash = request.match_info.get('archive_hash', 'Anonymous')
    source_path = os.path.join(folder_path, archive_hash)
    if not os.path.exists(source_path):
        raise web.HTTPNotFound(text='The archive does not exist')

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
        cwd=source_path
    )
    bytes_portion = 102400
    try:
        while True:
            logging.debug('Sending archive chunk ...')
            portion = await process.stdout.read(bytes_portion)
            await response.write(portion)
            if process.stdout.at_eof():
                break
            await asyncio.sleep(response_delay)
    except (asyncio.CancelledError, IndexError, SystemExit) as fail:
        if isinstance(fail, asyncio.CancelledError):
            logging.debug('Download was interrupted')
        process.kill()
        await process.communicate()
        response.force_close()
        raise

    return response

# pylint: disable=unused-argument


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    env = Env()
    env.read_env()
    input_args_parser = create_input_args_parser()
    input_args = input_args_parser.parse_args()
    debug_mode = input_args.debug_mode or env.bool('DEBUG_MODE', False)
    if input_args.response_delay:
        response_delay = input_args.response_delay
    else:
        response_delay = env.int('RESPONSE_DELAY', 0)

    if input_args.folder_path:
        folder_path = input_args.folder_path
    else:
        folder_path = env('FOLDER_PATH', 'test_photos')

    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s [%(asctime)s]  %(message)s'
        )
    app = web.Application()
    archive_handler = functools.partial(
        archive,
        response_delay=response_delay,
        folder_path=folder_path
    )
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive_handler),
    ])
    web.run_app(app)
