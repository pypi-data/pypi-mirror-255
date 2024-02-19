from test_tele.features.extractors.utils import *


async def set_info_dict(gallery_dl_result, mode: dict) -> list[dict]:
    """Set dict based on website"""
    my_dict = {}
    lists: list = []
    
    if gallery_dl_result:
        for elemen in gallery_dl_result:
            if elemen[0] == 3:
                my_dict = {
                    'img_url': elemen[1],
                    'thumbnail': elemen[2]['sample_url'],
                    'id': str(elemen[2]['id']),
                    'width': int(elemen[2]['width']),
                    'height': int(elemen[2]['height']),
                    'filename': str(elemen[2]['filename']),
                    'tags': '' if 'no_tag' in mode else await get_tags(elemen[2]['tags'].strip().split()),
                    'extension': elemen[2]['extension'],
                }
                lists.append(my_dict)
    return lists


async def get_nude_list(query: str, pid:int, mode: dict = {}) -> str:
    base_url = "https://realbooru.com/index.php?page=post&s=list&tags="
    
    # Default = asian -bbc pussy
    query = "asian+-bbc+pussy" if query == "" else query.replace(" ", '+')

    gallery_dl_result = await gallery_dl(f"{base_url}{query}", pid)
    lists = await set_info_dict(gallery_dl_result, mode)
    return lists


async def get_nude_file(callb_query:str):
    modified_string = "{}/{}/{}".format(callb_query[:2], callb_query[2:4], callb_query)
    return f"https://realbooru.com//images/{modified_string}"

