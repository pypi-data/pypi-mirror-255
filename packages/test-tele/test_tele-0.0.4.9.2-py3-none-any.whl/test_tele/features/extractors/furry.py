from test_tele.features.extractors.utils import *

# e621 & e6ai ===================================================================

FURRY_MODE = ['-ai']


async def set_info_dict(gallery_dl_result, mode: dict = {}) -> list[dict]:
    """Set dict based on website"""
    my_dict = {}
    lists: list = []
    
    for elemen in gallery_dl_result:
        if elemen[0] == 3:
            my_dict = {
                'img_url': elemen[1],
                'id_file': str(elemen[2]['file']['md5']),
                'id': str(elemen[2]['id']),
                'extension': elemen[2]['extension'],
                'category': elemen[2]['category'],
                'width': elemen[2]['file']['width'],
                'height': elemen[2]['file']['height'],
                'artist': await get_tags(elemen[2]['tags']['artist']) if 'artist' in elemen[2]['tags'] else "AI",
                'thumbnail': elemen[2]['preview']['url'],
                'tags': '' if 'no_tag' in mode else await get_tags(elemen[2]['tags']['general'], 40),
            }
            lists.append(my_dict)
    return lists


async def get_furry_list(query: str, pid:int, mode: dict = {}) -> str:
    base_url = "https://e621.net/posts?tags="
    if "-ai" in mode:
        base_url = base_url.replace("e621.net", "e6ai.net")
    
    # Default = my little pony
    query = "my_little_pony+-penis" if query == "" else query.replace(" ", '+')

    gallery_dl_result = await gallery_dl(f"{base_url}{query}", pid)
    lists = await set_info_dict(gallery_dl_result, mode)
    return lists


async def get_fur_file(callb_query:str):
    website, file_name = callb_query.split(",")
    modified_string = "{}/{}/{}".format(file_name[:2], file_name[2:4], file_name)
    return f"https://static1.{website}.net/data/{modified_string}"

