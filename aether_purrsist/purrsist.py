import asyncio
import re
import os
import tempfile
import traceback
from pathlib import Path
from datetime import datetime
from datetime import timezone
from typing import Union
from typing import List

import aioipfs
import aiofiles
import ipfshttpclient
from yarl import URL

import shutil
import markdown
import pkg_resources

from yattag import Doc
from yattag import indent

from feedgen.feed import FeedGenerator

from .models import Boards
from .models import Posts
from .models import PublicKeys
from .models import Threads
from .models import Votes
from .md import is_markdown


aethcssp = Path(pkg_resources.resource_filename('aether_purrsist',
                                                'aether.css'))
cssp = Path(pkg_resources.resource_filename('aether_purrsist',
                                            'awsm_theme_big-stone.css'))


def mkd(path: Path):
    path.mkdir(parents=True, exist_ok=True)


async def boards_selection(boards_list: list):
    fps = []

    for board in await Boards.all().order_by('Name'):
        for regex, bcfg in boards_list.items():
            bcfg_fp = bcfg.get('fingerprint')

            if board.Fingerprint in fps:
                continue

            if bcfg_fp and board.Fingerprint == bcfg_fp:
                fps.append(bcfg_fp)
                yield board, bcfg

                continue
            elif re.search(rf'^{regex}$', board.Name) and not bcfg_fp:
                fps.append(board.Fingerprint)
                yield board, bcfg


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
gendate = datetime.now().strftime('%d-%m-%Y %I:%M %p')


def pcssc():
    global pidx

    pidx += 1
    mod = divmod(pidx, 3)[1]

    if mod == 0:
        return 'aether-post-cold'
    elif mod == 1:
        return 'aether-post-gray'
    else:
        return 'aether-post-dark'


def footer(doc: Doc):
    tag = doc.tag
    text = doc.text

    doc.stag('div', klass='clear')

    with tag('div', klass='purrsist-footer'):
        with tag('p'):
            text('Generated by ')

            with tag('a', href='https://gitlab.com/galacteek/aether-purrsist'):
                text('aether-purrsist')

            text(f' ({gendate})')


def show_usernick(doc: Doc, owner) -> None:
    with doc.tag('h3', klass='aether-nickname'):
        if owner:
            doc.text(f'@{owner.Name}')
        else:
            doc.text('Unknown user')


def show_date(doc: Doc, obj: Union[Threads, Boards, Posts]) -> None:
    with doc.tag('h4'):
        doc.text(obj.LocalArrival.strftime('%d-%m-%Y %I:%M %p'))


def votes_score(votes: List[Votes]) -> int:
    """
    Compute the score for a post given a list of votes
    """

    score: int = 0

    for vote in votes:
        # Not sure what other values of TypeClass exist
        if vote.TypeClass != 1:
            continue

        if vote.Type == 1:
            score += 1
        elif vote.Type == 2:
            score -= 1

    return score


def show_score(doc: Doc, votes: List[Votes]) -> None:
    score = votes_score(votes)

    if score != 0:
        with doc.tag('span',
                     klass='arrow-up' if score > 0 else 'arrow-down'):
            with doc.tag('span', style='padding-left: 24px'):
                doc.text(score)


def show_post_infos(doc: Doc, owner, obj: Union[Threads, Posts],
                    votes: List[Votes] = []) -> None:
    with doc.tag('p', klass='aether-post-infos'):
        with doc.tag('div', style='float: left'):
            show_usernick(doc, owner)

        with doc.tag('div', style='float: right'):
            show_date(doc, obj)
            show_score(doc, votes)

        doc.stag('div', klass='clear')


def show_body(doc: Doc, obj: Union[Threads, Posts]) -> None:
    """
    This function outputs the body of a post or thread.
    It uses the markdown module if it detects markdown content.
    """
    if is_markdown(obj.Body):
        with doc.tag('p'):
            doc.asis(markdown.markdown(
                obj.Body,
                extensions=[
                    'attr_list',
                    'fenced_code'
                ]
            ))
    else:
        with doc.tag('pre'):
            doc.text(obj.Body)


async def thread_posts_output(doc: Doc,
                              board: Boards,
                              thread: Threads, posts):
    tag = doc.tag

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
            show_post_infos(
                doc, owner, post,
                votes=await Votes.filter(
                    Board=board.Fingerprint,
                    Thread=thread.Fingerprint,
                    Target=post.Fingerprint
                )
            )

            show_body(doc, post)

            if len(replies) > 0:
                await thread_posts_output(doc, board, thread, replies)


async def purrsist_thread(board: Boards,
                          thread: Threads,
                          threadp: Path,
                          votes: List[Votes] = []) -> bool:
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

            with tag('title'):
                text(thread.Name)

        with tag('p'):
            with tag('div', klass='thread-name'):
                with tag('a', href='.', klass='thread-name'):
                    text(thread.Name)

            if thread.Link:
                url = URL(thread.Link)
                ext = os.path.splitext(url.name)[1]

                if ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                    with tag('a', href=thread.Link):
                        with tag('img', src=thread.Link):
                            text(thread.Link)
                elif ext in ['.mp4', '.webm', '.avi']:
                    with tag('video', src=thread.Link,
                             controls=''):
                        pass
                else:
                    with tag('a', href=thread.Link):
                        text(thread.Link)

            with tag('h4'):
                text(thread.LocalArrival.strftime('%d-%m-%Y %I:%M %p'))

        with tag('body'):
            with tag('div',
                     klass='aether-thread-body'):
                show_post_infos(doc, towner, thread,
                                votes=votes)

                show_body(doc, thread)

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
            doc.stag('link',
                     rel='stylesheet',
                     href='../aether.css')
            with tag('title'):
                text(f'Aether archive: {board.Name}')

        with tag('body'):
            with tag('div'):
                with tag('h1'):
                    text(f'Aether archive: {board.Name}')

                if owner:
                    with tag('h2', style='margin: 5px'):
                        text(f'Created by: @{owner.Name}')

                with tag('ul'):
                    for thread in threads:
                        votes = await Votes.filter(
                            Board=board.Fingerprint,
                            Thread=thread.Fingerprint,
                            Target=thread.Fingerprint
                        )

                        with tag('li'):
                            with tag('a', href=thread.Fingerprint):
                                text(thread.Name)

                            show_score(doc, votes)

            footer(doc)

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
            with tag('title'):
                text(f'Aether archive: {gendate}')

        with tag('body'):
            with tag('h1'):
                text('Aether archive')

            with tag('div'):
                with tag('ul'):
                    for board in boards:
                        with tag('li'):
                            with tag('a', href=board.Fingerprint):
                                text(board.Name)

            footer(doc)

    return await write_doc(doc, indexp)


async def purrsist(args, cfg: dict) -> bool:
    now = datetime.now(timezone.utc)
    nowd = now.strftime('%d-%m-%Y')

    fg = FeedGenerator()
    fg.id('https://gitlab.com/galacteek/aether-purrsist')
    fg.language('en')
    fg.title(f'Aether mirror feed ({nowd})')
    fg.description('Generated by aether-purrsist')
    fg.lastBuildDate(now)
    fg.pubDate(now)
    fg.link(href='.')

    ipfscfg = cfg['ipfs']
    feedscfg = cfg.get('feeds', {
        'atom_generate': True,
        'rss_generate': False
    })

    client = aioipfs.AsyncIPFS(
        maddr=ipfscfg.get('maddr', '/dns4/localhost/tcp/5001')
    )
    ipclient = ipfshttpclient.Client(
        ipfscfg.get('maddr', '/dns4/localhost/tcp/5001')
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
    atomfeedp = boardsp.joinpath('atom.xml')
    rssfeedp = boardsp.joinpath('rss.xml')

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

    for board, board_cfg in boards:
        thr_processed = 0
        max_threads = board_cfg.get('max_threads', 0)
        thread_filter = board_cfg.get('threads_ignore_byname', [])
        fingerprint = board_cfg.get('fingerprint',
                                    board.Fingerprint)

        boardp = boardsp.joinpath(board.Fingerprint)

        mkd(boardp)

        thrs = await Threads.filter(Board=fingerprint).order_by(
            '-LocalArrival')

        if len(thrs) == 0:
            continue

        if args.verbose > 0:
            print(f'Processing board: {board.Name} ({fingerprint})')

        for thread in thrs:
            if any(re.compile(reg).search(thread.Name)
                   for reg in thread_filter):
                continue

            threadp = boardp.joinpath(thread.Fingerprint)

            if args.verbose > 1:
                print(f'Processing thread: {thread.Name}')

            mkd(threadp)

            await purrsist_thread(
                board, thread, threadp,
                votes=await Votes.filter(
                    Board=board.Fingerprint,
                    Thread=thread.Fingerprint,
                    Target=thread.Fingerprint
                )
            )

            thr_processed += 1

            # Add an entry in the feed for this thread
            fe = fg.add_entry()
            fe.id(
                f'aether://board/{board.Fingerprint}'
                f'/thread/{thread.Fingerprint}'
            )
            fe.title(f'{board.Name}: {thread.Name}')
            fe.link(href=f'/{board.Fingerprint}/{thread.Fingerprint}')
            fe.published(thread.LocalArrival)

            # Set the entry's content
            safeb = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', thread.Body)
            if is_markdown(safeb):
                fe.content(content=markdown.markdown(safeb))
            else:
                fe.content(content=safeb)

            if thread.Link:
                fe.source(url=thread.Link)

            if max_threads > 0 and thr_processed >= max_threads:
                break

        await board_threads_index(board, boardp, thrs)

        vboards.append(board)

    await boards_index(boardsp.joinpath('index.html'), vboards)

    # Generate the atom/rss feeds
    if feedscfg['atom_generate']:
        fg.atom_file(str(atomfeedp))

    if feedscfg['rss_generate']:
        fg.rss_file(str(rssfeedp))

    # the async add call is messed up so use the ipfshttpclient here
    entries = ipclient.add(str(boardsp), cid_version=1, recursive=True)

    try:
        pr_cfg = ipfscfg['pinremote']
        entry = entries[-1]
        cid = entry['Hash']

        result = await client.name.publish(cid, key=kid)
        assert result

        if pr_cfg['enabled']:
            try:
                await client.pin.remote.rm(
                    pr_cfg['service'],
                    name=pr_cfg['pin_name'],
                    force=True
                )
            except aioipfs.APIError as e:
                print(f'Failed to unpin from rps: {e.message}')

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
