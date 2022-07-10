# -*- coding: utf-8 -*-
import os
import cv2
from PIL import Image, ImageDraw, ImageFont
from vk import VkApi
from utils import resolve_cover, incline_views
import asyncio
from pathlib import Path
import argparse
import shutil

path = str(Path.home()) + '\\images-vezdekod-IT-Square' if ' ' in str(os.path.curdir) else '.\\images'


async def get_covers(token, group_id, count=6):
    vk = VkApi(token).get_api()
    data = await vk.video.get(owner_id=group_id, count=100)

    videos = []
    for item in data['items']:
        videos.append({
            'title': item['title'],
            'views': item['views'],
            'cover': resolve_cover(item['image'])
        })

    videos.sort(key=lambda x: x['views'], reverse=True)

    if not os.path.exists(path):
        os.makedirs(path)

    tasks = [asyncio.create_task(fetch_photo(n, item['cover'], vk._vk.session)) for n, item in enumerate(videos[:count], start=1)]
    await asyncio.gather(*tasks)
    await vk._vk.session.close()

    process_images(videos[:count])


async def fetch_photo(index, url, session):
    async with session.get(url) as resp:
        with open(f'{path}\\{index}.jpg', 'wb') as f:
            f.write(await resp.read())


def process_images(items):
    font = ImageFont.truetype('./VKSansDisplay-Medium.ttf', 40, encoding='UTF-8')
    views_font = ImageFont.truetype('./VKSansDisplay-Medium.ttf', 26, encoding='UTF-8')
    for index, item in enumerate(items, start=1):
        img = Image.open(f'{path}\\{index}.jpg')
        width, height = img.size

        if width * height != 1280 * 720:
            img = img.resize((1280, 720), Image.Resampling.LANCZOS)

        img.save(f'{path}\\{index}.png')

        img = Image.open(f'{path}\\{index}.png')
        img = img.convert('RGBA')

        width, height = img.size
        gradient = Image.new('L', (1, height), color=0xFF)
        for y in range(1, height):
            gradient.putpixel((0, height - y), int(0.8 * 255 * (1 - 1. * float(y) / height)))
        alpha = gradient.resize(img.size)
        black_im = Image.new('RGBA', (width, height), color=0)  # i.e. black
        black_im.putalpha(alpha)
        gradient_im = Image.alpha_composite(img, black_im)

        draw = ImageDraw.Draw(gradient_im)

        title = item['title']
        width = font.getlength(item['title'])
        while width > 1200:
            title = title[:-1]
            width = font.getlength(title + '...')

        draw.text((40, 580), title if title == item['title'] else title + '...', (255, 255, 255), font=font)
        draw.text((40, 630), f'{item["views"]} {incline_views(item["views"])}', (255, 255, 255), font=views_font)

        gradient_im.save(f'{path}\\{index}.png')

    generate_video()


def generate_video():
    video_name = 'output.mp4'

    images = [img for img in os.listdir(path)
              if img.endswith("png")]

    frame = cv2.imread(f'{os.path.join(path, images[0])}')

    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 0.2, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(path, image)))

    cv2.destroyAllWindows()
    video.release()

    shutil.rmtree(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', dest='token', type=str, help='VK User Token', required=True)
    parser.add_argument('--group_id', dest='group_id', type=int, help='group id', required=True)
    parser.add_argument('--count', dest='count', type=int, help='count of videos to display (max 100)', default=6)
    args = parser.parse_args()

    group_id = -args.group_id if args.group_id > 0 else args.group_id

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_covers(args.token, group_id, args.count))