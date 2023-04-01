import asyncio
import re
import os
import tempfile
import traceback
from pathlib import Path

import aioipfs
import aiofiles

import shutil
import markdown
import pkg_resources

from yattag import Doc
from yattag import indent

from aether_purrsist.models import Boards
from aether_purrsist.models import Posts
from aether_purrsist.models import PublicKeys
from aether_purrsist.models import Threads


aethcssp = Path(pkg_resources.resource_filename('aether_purrsist',
                                                'aether.css'))
cssp = Path(pkg_resources.resource_filename('aether_purrsist',
                                            'awsm_theme_big-stone.css'))


def mkd(path: Path):
    path.mkdir(parents=True, exist_ok=True)


async def boards_selection(boards_list: list):
    for board in await Boards.all().order_by('Name'):
        for regex, item in boards_list.items():
            if re.search(regex, board.Name):
                yield board


async def write_doc(doc: Doc, path: Path) -> bool:
    try:
        async with aiofiles.open(str(path), 'w+t') as fd:
            await fd.write(indent(doc.getvalue()))

        return True
    except Exception:
        traceback.print_exc()
        return False


async def pubkey(fingerprint: str) -> PublicKeys:
    """
    Return the PublicKeys instance for a given fingerprint.
    This allows us to get the name of a user by fingerprint.
    """
    return await PublicKeys.filter(
        Fingerprint=fingerprint
    ).first()


pidx = 0


def pcssc():
    global pidx

    pidx += 1

    if divmod(pidx, 2)[1] == 0:
        return 'aether-post-cold'
    else:
        return 'aether-post-warm'


async def thread_posts_output(doc: Doc,
                              board: Boards,
                              thread: Threads, posts):
    tag = doc.tag
    text = doc.text

    for idx, post in enumerate(posts):
        owner = await pubkey(post.Owner)

        # Replies to this post
        replies = await Posts.filter(
            Board=board.Fingerprint,
            Thread=thread.Fingerprint,
            Parent=post.Fingerprint
        )

        with tag('div',
                 klass='aether-post ' + pcssc()):
            with tag('p'):
                with tag('h3'):
                    if owner:
                        text(f'@{owner.Name}')
                    else:
                        text('Unknown user')

                with tag('h4'):
                    # Not sure LocalArrival is the right ts to use
                    text(post.LocalArrival.strftime('%d-%m-%Y %I:%M %p'))

            with tag('p'):
                doc.asis(markdown.markdown(post.Body))

            if len(replies) > 0:
                await thread_posts_output(doc, board, thread, replies)


async def purrsist_thread(board: Boards,
                          thread: Threads,
                          threadp: Path) -> bool:
    """
    Purrsist a given thread with all its posts
    """
    indexp = threadp.joinpath('index.html')

    posts = await Posts.filter(
        Board=board.Fingerprint,
        Thread=thread.Fingerprint,
        Parent=thread.Fingerprint
    )

    doc, tag, text = Doc().tagtext()
    doc.asis('<!DOCTYPE html>')

    towner = await pubkey(thread.Owner)

    with tag('html'):
        with tag('head'):
            doc.stag('meta', charset='UTF-8')
            doc.stag('link',
                     rel='stylesheet',
                     href='../../style.css')
            doc.stag('link',
                     rel='stylesheet',
                     href='../../aether.css')
        with tag('p'):
            with tag('h1'):
                text(thread.Name)

            if thread.Link:
                with tag('a', href=thread.Link):
                    text(thread.Link)

            with tag('h4'):
                text(thread.LocalArrival.strftime('%d-%m-%Y %I:%M %p'))

        with tag('body'):
            with tag('div',
                     klass='aether-thread-body'):

                with tag('p'):
                    doc.asis(markdown.markdown(thread.Body))

                if towner:
                    with tag('h3'):
                        text(f'@{towner.Name}')

            with tag('div'):
                await thread_posts_output(doc, board, thread, posts)

    return await write_doc(doc, indexp)


async def board_threads_index(board: Boards,
                              boardp: Path,
                              threads) -> bool:
    """
    Threads index for a community
    """
    indexp = boardp.joinpath('index.html')

    doc, tag, text = Doc().tagtext()
    doc.asis('<!DOCTYPE html>')

    owner = await pubkey(board.Owner)

    with tag('html'):
        with tag('head'):
            doc.stag('meta', charset='UTF-8')
            doc.stag('link',
                     rel='stylesheet',
                     href='../style.css')

        with tag('div'):
            with tag('h1'):
                text(f'Aether community archive for: {board.Name}')

            if owner:
                with tag('h2', style='margin: 5px'):
                    text(f'Created by: @{owner.Name}')

            with tag('ul'):
                for thread in threads:
                    with tag('li'):
                        with tag('a', href=thread.Fingerprint):
                            text(thread.Name)

    return await write_doc(doc, indexp)


async def boards_index(indexp: Path, boards):
    doc, tag, text = Doc().tagtext()
    doc.asis('<!DOCTYPE html>')

    with tag('html'):
        with tag('head'):
            doc.stag('meta', charset='UTF-8')
            doc.stag('link',
                     rel='stylesheet',
                     href='style.css')

        with tag('h1'):
            text('Aether archive: communities list')

        with tag('div'):
            with tag('ul'):
                for board in boards:
                    with tag('li'):
                        with tag('a', href=board.Fingerprint):
                            text(board.Name)

    return await write_doc(doc, indexp)


async def purrsist(cfg: dict) -> bool:
    ipfscfg = cfg['ipfs']

    client = aioipfs.AsyncIPFS(
        maddr=ipfscfg.get('maddr', '/dns4/localhost/tcp/5001')
    )

    try:
        keys = await client.key.list()
        kid, kn = None, ipfscfg.get('ipns_key', 'aether')
    except aioipfs.APIError:
        raise

    for k in keys['Keys']:
        if k['Name'] == kn:
            kid = k['Id']

    if not kid:
        resp = await client.key.gen(kn)
        assert resp

        kid = resp['Id']

    purr_ipfsp = f'/ipns/{kid}'

    topd = Path(tempfile.mkdtemp(prefix='aetherp'))
    dstd = topd.joinpath(kid)

    boardsp = dstd.joinpath('boards')

    try:
        await client.get(purr_ipfsp, dstdir=str(topd))
        assert dstd.is_dir()
    except AssertionError:
        if dstd.is_file():
            os.unlink(dstd)
    except (Exception, aioipfs.APIError):
        mkd(dstd)

    mkd(boardsp)

    shutil.copy(cssp, boardsp.joinpath('style.css'))

    acss = boardsp.joinpath('aether.css')
    if acss.is_file():
        acss.unlink()

    shutil.copy(aethcssp, acss)

    boards = [b async for b in boards_selection(cfg['boards'])]
    vboards = []

    for board in boards:
        boardp = boardsp.joinpath(board.Fingerprint)
        mkd(boardp)

        thrs = await Threads.filter(Board=board.Fingerprint).order_by(
            '-LocalArrival')

        if len(thrs) == 0:
            continue

        for thread in thrs:
            threadp = boardp.joinpath(thread.Fingerprint)

            mkd(threadp)

            await purrsist_thread(board, thread, threadp)

        await board_threads_index(board, boardp, thrs)

        vboards.append(board)

    await boards_index(boardsp.joinpath('index.html'), vboards)

    entries = [entry async for entry in client.add(str(boardsp),
                                                   cid_version=1,
                                                   recursive=True)]

    try:
        pr_cfg = ipfscfg['pinremote']
        entry = entries[-1]
        cid = entry['Hash']

        result = await client.name.publish(cid, key=kid)
        assert result

        if pr_cfg['enabled']:
            await client.pin.remote.rm(
                pr_cfg['service'],
                name=pr_cfg['pin_name']
            )

            await asyncio.sleep(1)

            await client.pin.remote.add(
                pr_cfg['service'],
                cid,
                name=pr_cfg['pin_name']
            )

            print(f'https://{cid}.ipfs.dweb.link')

        await client.close()
    except Exception as err:
        raise err
    else:
        print(cid)

    shutil.rmtree(topd)

    return True
