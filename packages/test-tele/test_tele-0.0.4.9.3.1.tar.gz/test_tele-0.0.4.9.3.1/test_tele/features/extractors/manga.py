import os
import logging
import aiohttp
import requests

from PIL import Image
from bs4 import BeautifulSoup

from test_tele.features.extractors.utils import  *
# from test_tele.features.extractors.telegraph import generate_new_telepage, images_in_folder

OFFSET = 40

session = requests.Session()
session.cookies.update({'nsfw': '2', 'imgser': '1'})


async def get_manga_list(query: str, pid: int = 0, lang: str = 'en'):
    url = 'https://mangapark.net/search'
    query_example = "detective conan +mystery +police -gore"
    optional = {}

    query = query.strip().lower().replace(".md", "").lstrip()
    genre_lists = {'include': [], 'exclude': []}

    keywords = query.split()
    for key in keywords:
        if key.startswith("+"):
            genre_lists['include'].append(key.replace("+", ""))
            query = query.replace(key, "")
        if key.startswith("-"):
            genre_lists['exclude'].append(key.replace("-", ""))
            query = query.replace(key, "")
        if key.startswith("lang:"):
            lang = key.split(":")[-1]
            query = query.replace(key, "")

    genres = f"{(',').join(genre_lists['include'])}"
    if genre_lists['exclude']:
        genres += f"|{(',').join(genre_lists['exclude'])}"

    word = query.strip()
    if word:
        word_params = {'word': word}
        optional = word_params

    if genres:
        genre_param = {"genres": genres}
        optional.update(genre_param)

    params = {"lang": lang, "sortby": "field_score", "ig_genres": "1", "page": pid + 1}
    if optional:
        optional.update(params)
        params = optional

    response = session.get(url, params=params)
    if response.status_code == 200:
        return await set_info_dict(response)
    else:
        return None


async def set_info_dict(response) -> list[dict]:
    """Set dict based on website"""
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('div', {'q:key': 'q4_9'})

    manga_list = []
    for div in divs:
        title = div.find('h3').text
        thumbnail = div.find('img')['src']
        link = div.find('h3').find('a')['href'].replace("/title", "")

        try:
            author = div.find('div', {'q:key': "6N_0"}).text
        except:
            author = "Unknown"

        span_rating = div.find('span', {'q:key': "XH_1"})
        if span_rating:
            rating = span_rating.find('span').text

        div_genres = div.find('div', {'q:key': 'HB_9'})
        if div_genres:
            spans = div_genres.find_all('span', {'class': 'whitespace-nowrap'})
            genres = [f'`{span.text}`' for span in spans]

        manga = {
            "title": title,
            "thumbnail": thumbnail,
            "manga_url": link,
            "author": author,
            "rating": "N/A" if not span_rating else rating,
            "genres": " " if not div_genres else (", ").join(genres),
        }
        manga_list.append(manga)

    return manga_list


async def get_chapter_list(link: str, pid: int = 0, offset=OFFSET):
    url = f"https://mangapark.net/title{link}"
    example_url = "https://mangapark.net/title/357309-en-mother-son-island-survival-new"

    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text.split(" - ")[0]
        divs = soup.find_all('div', {"q:key": "8t_8"})
        chapters = []
        for div in divs[pid: pid + offset]:
            chapter = div.find('a').text
            link = div.find('a')['href'].replace("/title", "")

            # Tambahkan judul dan link chapter ke dalam daftar
            chapters.append({
                'title': title,
                'chapter': chapter,
                'link_chapter': link
            })
        return chapters
    else:
        return None


async def get_chapter_images(link: str, pid: int = 0, offset=OFFSET):
    url = f"https://mangapark.net/title{link}"
    example_url = "https://mangapark.net/title/10851-en-detective-conan/6954662-vol-96-ch-1091"

    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data_json = soup.find('script', {"type": "qwik/json"}).text
        data = json.loads(data_json)

        prev_ch = soup.find('a', {"q:key": "0B_8"})['href'].replace("/title", "")
        next_ch = soup.find('a', {"q:key": "0B_9"})['href'].replace("/title", "")

        data_objs = data['objs']
        chapters = []
        n = 0
        for i, obj in enumerate(data_objs):
            if isinstance(obj, str):
                if obj.startswith("https://xfs"):
                    if n >= pid + 2:
                        chapter_dict = {
                            "prev_ch": prev_ch,
                            "next_ch": next_ch,
                            "images": obj
                        }
                        chapters.append(chapter_dict)
                    n += 1
                    if n >= offset + 2:
                        break
        return chapters
    else:
        return None


async def get_manga_file(query: str):
    if 'cover' in query:
        query = query.split("cover")[-1]
        query = query.strip()
        return query


# async def crop_manwha_images():
    
#     image = Image.open("test/1.png")

#     # Get the current width and height of the image
#     width, height = image.size

#     # Calculate the new height of each piece
#     new_height = int(width * 2)

#     # Create a list to store the pieces
#     pieces = []

#     # Iterate over the image and crop each piece
#     for i in range(0, height, new_height):
#         piece = image.crop((0, i, width, i + new_height))
#         pieces.append(piece)

#     # Save each piece to a file
#     for i, piece in enumerate(pieces):
#         piece.save("output{}.jpg".format(str(i).zfill(2)))


# async def download_media(session, elemen):
#     nama_file =  elemen['id'] + "_" + elemen['index'] +'.jpg'
#     folder = f"temps/{elemen['id']}"
#     if not os.path.exists(folder):
#         os.makedirs(folder)
    
#     path_file = os.path.join(folder, nama_file)
#     async with session.get(elemen['img_url']) as response:
#         if response.status == 200:
#             with open(path_file, 'wb') as f:
#                 f.write(await response.read())
#         else:
#             logging.warning(f'Failed to download file {nama_file}')


# async def generate_telegraph(id):
#     url = f"https://www.tsumino.com/entry/{id}"
#     gallery_dl_result = await gallery_dl(url, offset=10000, filter='--range')
#     lists = await set_info_dict(gallery_dl_result)
    
#     # Bagian download gambar secara paralel
#     async with aiohttp.ClientSession() as session:
#         tasks = [download_media(session, element) for element in lists]
#         await asyncio.gather(*tasks)
#     # Bagian upload ke telegraph
#     link_telepage = await generate_new_telepage(
#         f'temps/{lists[-1]["id"]}',
#         lists[-1]['id'] + '-' + lists[-1]['title'],
#         lists[-1]['artist']
#     )
    
#     return link_telepage