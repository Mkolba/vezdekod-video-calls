# -*- coding: utf-8 -*-
from utils import Logger
from vk import VkApi
import asyncio
import argparse
import regex
from tqdm import tqdm

logger = Logger('Notifier')


async def main(token, group_id, patterns, count=10):
    patterns = {item: 0 for item in patterns}
    vk = VkApi(token=token).get_api()

    group_title = (await vk.groups.getById(group_ids=abs(group_id)))[0]['name']
    logger.ok(f'Начинаю подсчёт комментариев в сообществе «{group_title}»')

    data = await vk.video.get(owner_id=group_id, count=count)
    for item in tqdm(data['items']):
        if item['comments'] > 0:
            comments = await vk.video.getComments(owner_id=group_id, video_id=item['id'], count=100, sort='desc')
            offset = 0
            while offset < comments['count']:
                for comment in comments['items']:
                    for pattern in patterns:
                        if regex.findall(pattern, comment.get('text', '')):
                            patterns[pattern] += 1

                offset += 100
                if offset < comments['count']:
                    comments = await vk.video.getComments(owner_id=group_id, video_id=item['id'], count=100, sort='desc', offset=offset)

    print('Подсчет завершён:\n')

    for pattern, result in patterns.items():
        print(pattern.pattern + ':', result)

    await vk._vk.session.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', dest='token', type=str, help='VK User Token', required=True)
    parser.add_argument('--group_id', dest='group_id', type=int, help='group id', required=True)
    parser.add_argument('--count', dest='count', type=int, help='videos count')
    parser.add_argument('--patterns', dest='patterns', metavar='Pattern', type=str, nargs='+', help='patterns to search (RegExp allowed)', required=True)
    args = parser.parse_args()

    group_id = -args.group_id if args.group_id > 0 else args.group_id

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.token, group_id, [regex.compile(item) for item in args.patterns], args.count or 10))
