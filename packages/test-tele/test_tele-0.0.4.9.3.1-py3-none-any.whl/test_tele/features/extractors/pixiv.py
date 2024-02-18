import logging

from pixivpy3 import *
from test_tele.config_bot import BOT_CONFIG
from test_tele.features.extractors.utils import *


PIXIV_MODE = ['no_ai', 'nsfw', 'safe']


async def get_pixiv_list(query: str, offset: int, mode: dict = {}):
    api = AppPixivAPI()
    api.auth(refresh_token=BOT_CONFIG.apis.pixiv_refresh_token)

    if query != '':
        input = query.split()
        for val in input:
            if val.isdigit():
                return await set_dict_detail(api.illust_detail(int(val)), mode, offset=offset)
            if 'id:' in val:
                user_id = val.split("id:")[-1]
                return await set_dict_search(api.user_illusts(int(user_id), offset=offset), mode)
    else:
        # Default = sangonomiya kokomi
        query = '珊瑚宮心海'

    return await set_dict_search(api.search_illust(query, offset=offset), mode)


async def set_dict_search(pixiv_json, mode: dict) -> dict:
    illusts = pixiv_json.get("illusts", None)
    media_posts = []

    if illusts:
        for illust in illusts:
            if illust["meta_pages"]:
                img_ori = illust["meta_pages"][0]["image_urls"]["original"]
            else:
                img_ori = illust['meta_single_page']['original_image_url']
                
            images = {
                "img_thumb": illust["image_urls"]["medium"],
                "img_sample": illust["image_urls"]["medium"],
                "img_original": img_ori
            }
            media_post = {
                'id': str(illust["id"]),
                'title': illust["title"],
                'user_id': str(illust["user"]["id"]),
                'user_name': illust["user"]["name"],
                'tags': '' if 'no_tag' in mode else await get_pixiv_tags(illust["tags"]),
                'img_urls': images
            }
            media_posts.append(media_post)
    return media_posts


async def set_dict_detail(pixiv_json, mode: dict, offset: int = None) -> dict:
    illusts = pixiv_json.get("illust", None)
    media_posts = []

    if illusts:
        if 'meta_pages' in illusts and illusts['meta_pages']:
            for illust in illusts['meta_pages']:
                images = {
                    "img_thumb": illust["image_urls"]["medium"],
                    "img_sample": illust["image_urls"]["medium"],
                    "img_original": illust["image_urls"]["original"]
                }
                media_post = {
                    'id': str(illusts["id"]),
                    'title': illusts["title"],
                    'user_id': str(illusts["user"]["id"]),
                    'user_name': illusts["user"]["name"],
                    'tags': '' if 'no_tag' in mode else await get_pixiv_tags(illusts["tags"]),
                    'img_urls': images
                }
                media_posts.append(media_post)
        else:
            images = {
                "img_thumb": illusts["image_urls"]["medium"],
                "img_sample": illusts["image_urls"]["medium"],
                "img_original": illusts["meta_single_page"]["original_image_url"]
            }
            media_post = {
                'id': str(illusts["id"]),
                'title': illusts["title"],
                'user_id': str(illusts["user"]["id"]),
                'user_name': illusts["user"]["name"],
                'tags': '' if 'no_tag' in mode else await get_pixiv_tags(illusts["tags"]),
                'img_urls': images
            }
            media_posts.append(media_post)

        if len(media_posts) > 50:
            media_posts = media_posts[:50]
        if offset:
            media_posts = media_posts[offset:offset + 30]

    return media_posts


async def get_pixiv_tags(tags):
    all_tags = []
    for tag in tags:
        if not tag.translated_name:
            re_tag = f"`{tag.name}`"
        else:
            re_tag = f"`{tag.name}`(`{tag.translated_name}`)"
        all_tags.append(re_tag)
    final_tag = (", ").join(all_tags)
    return final_tag


async def get_pixiv_file(url):
    return f"https://i.pximg.net/img-original/img/{url}"

