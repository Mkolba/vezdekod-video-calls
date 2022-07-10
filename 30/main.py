# -*- coding: utf-8 -*-
from utils import Logger
from vk import VkApi
import asyncio
import argparse

logger = Logger('Notifier')


def notify(status, title, group):
    if status == 'upcoming':
        logger.ok(f'В сообществе «{group}» была запланирована трансляция «{title}»')
    elif status == 'waiting':
        logger.ok(f'В сообществе «{group}» начинается трансляция «{title}». Ждём ведущего!')
    elif status == 'started':
        logger.ok(f'В сообществе «{group}» началась трансляция «{title}»')
    elif status == 'finished':
        logger.ok(f'В сообществе «{group}» завершилась трансляция «{title}»')
    elif status == 'failed':
        logger.ok(f'В сообществе «{group}» не состоялась трансляция «{title}»')


async def main(token, group_id):
    vk = VkApi(token=token).get_api()

    group_title = (await vk.groups.getById(group_ids=abs(group_id)))[0]['name']
    logger.ok(f'Начинаю следить за трансляциями в сообществе «{group_title}»')
    lives = {}

    while True:
        data = await vk.video.get(owner_id=group_id, count=100)

        for item in data['items']:
            if item.get('live_status', 0):
                status = item['live_status']
                if item['id'] in lives:
                    old_status = lives[item['id']]

                    if old_status != status:
                        lives[item['id']] = item['live_status']
                        notify(item['live_status'], item['title'], group_title)

                elif status not in ['failed', 'finished']:
                    lives.update({item['id']: item['live_status']})
                    notify(item['live_status'], item['title'], group_title)

        await asyncio.sleep(60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', dest='token', type=str, help='VK User Token', required=True)
    parser.add_argument('--group_id', dest='group_id', type=int, help='group id', required=True)
    args = parser.parse_args()

    group_id = -args.group_id if args.group_id > 0 else args.group_id

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.token, group_id))