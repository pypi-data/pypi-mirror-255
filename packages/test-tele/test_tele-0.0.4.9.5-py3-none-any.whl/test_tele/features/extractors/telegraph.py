import re
import os
import shutil
import asyncio
import logging
import aiohttp

from PIL import Image
from typing import Union
from telegraph.aio import Telegraph
from test_tele.config_bot import BOT_CONFIG, write_bot_config


QUALITY = 30


async def check_access_token():
    access_token = BOT_CONFIG.telegraph.access_token
    if access_token:
        return access_token
    
    response = await Telegraph().create_account(short_name=BOT_CONFIG.telegraph.short_name)
    access_token = response['access_token']

    BOT_CONFIG.telegraph.access_token = access_token
    BOT_CONFIG.telegraph.auth_url = response['auth_url']

    write_bot_config(BOT_CONFIG)

    return access_token


telegraph = Telegraph(asyncio.run(check_access_token()))


async def generate_new_telepage(images: Union[str, list], title: str, author_name: str):
    content = []
    if isinstance(images, str):
        folder_name = images
        images = await images_in_folder(images)
        
    compressed_image_path = await compress_image(images)

    async with aiohttp.ClientSession() as session:
        upload_tasks = [upload_image(session, image) for image in compressed_image_path]
        uploaded_results = await asyncio.gather(*upload_tasks)

    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

    uploaded_results = sorted(uploaded_results, key=lambda x: natural_sort_key(os.path.basename(x[0])))

    for image, response in uploaded_results:
        os.remove(image)  # Remove the compressed image
        if response and 'src' in response[0]:
            path = response[0]['src']
            content.append({'tag': 'img', 'attrs': {'src': path}})
        else:
            logging.error(f"Failed to upload image: {image}")

    page = await telegraph.create_page(
        title=title + BOT_CONFIG.telegraph.prefix,
        content=content, 
        html_content=f"<p>{BOT_CONFIG.telegraph.description}</p>",
        author_name=author_name, 
        author_url=BOT_CONFIG.bot_name.replace("@", 'https://t.me/'),
        return_content=True
    )

    if os.path.exists(folder_name) and os.path.isdir(folder_name):
        shutil.rmtree(folder_name)

    return page['url']


async def compress_image(images):
    lists_compressed_image = []
    for image in images:
        with open(image, 'rb') as f:
            img = Image.open(f)
            
            # Convert to RGB mode
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            compressed_image_path = os.path.splitext(image)[0] + '_compressed.jpg'
            img.save(compressed_image_path, format='JPEG', quality=QUALITY)
            lists_compressed_image.append(compressed_image_path)
        
    return lists_compressed_image


async def upload_image(session, image_path):
    url = 'https://telegra.ph/upload'
    data = aiohttp.FormData()
    data.add_field('file', open(image_path, 'rb'), filename=os.path.basename(image_path))
    
    async with session.post(url, data=data) as response:
        return image_path, await response.json()


async def images_in_folder(folder_path):
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        images = []

        for filename in os.listdir(folder_path):
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in image_extensions:
                images.append(os.path.join(folder_path, filename))
        return images


async def cari_konten(text):
    posts = []
    page_list = await telegraph.get_page_list()
    for post in page_list["pages"]:
        if re.findall(text, post["title"] + post["description"]):
            posts.append(post)
    
    return posts

