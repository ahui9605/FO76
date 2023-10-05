import asyncio
import json
import requests
import re
from bs4 import BeautifulSoup
from bilibili_api import user
from datetime import datetime
from PIL import Image
import io


URL = "https://www.falloutbuilds.com/fo76/nuke-codes/"
USER_ID = user.User(11144166)  # 卖片哥b站账号id
PREFIX = "阿帕拉契亚周报"
KEYWORD_DATA = {
    "赛季活动及挑战": ("font-size-20", 0),
    "米诺瓦金条游商": ("font-size-16", 1),
}


def open_version_json():
    with open("config.json", "r", encoding="utf-8") as f:
        data = json.load(f)

        current_version_data = data.get("current_version", {})
        current_id = current_version_data.get("id", None)
        current_nuke_codes = current_version_data.get(
            "nuke_password_last_updated", None
        )

    return current_id, current_nuke_codes


def update_json(file_path, new_id, new_title, new_nuke_password_last_updated):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 获取当前日期并格式化为MM/DD/YYYY
    current_date = datetime.now().strftime("%m/%d/%Y")

    # 检查 "current_version" 是否存在并是否为一个字典
    if "current_version" not in data or not isinstance(data["current_version"], dict):
        data["current_version"] = {}

    data["current_version"]["last_refreshed"] = current_date
    data["current_version"]["id"] = new_id
    data["current_version"]["title"] = new_title
    data["current_version"][
        "nuke_password_last_updated"
    ] = new_nuke_password_last_updated

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def download_image(img_url, file_name):
    file_path = f"imgs/{file_name}"

    response = requests.get(img_url)
    if response.status_code == 200:
        # BytesIO来处理二进制数据
        img_data = io.BytesIO(response.content)
        img = Image.open(img_data)

        # jpg转PNG格式并保存
        file_path_png = file_path.replace(".jpg", ".png")
        img.save(file_path_png, "PNG")

        print(f"Image saved as {file_path_png}")
    else:
        print(f"Failed to retrieve image from {img_url}")


# def write_nuke_codes_to_file():
#     url = "https://www.falloutbuilds.com/fo76/nuke-codes/"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
#     }
#     filename = "txt/核弹密码.txt"

#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")
#         div_element = soup.find("div", class_="card card-terminal mb-3 p-2")

#         if div_element:
#             with open(filename, "w", encoding="utf-8") as file:
#                 strong_elements = div_element.find_all("strong")
#                 if strong_elements and len(strong_elements) == 2:
#                     valid_from = strong_elements[0].get_text(strip=True)
#                     valid_to = strong_elements[1].get_text(strip=True)
#                     file.write(f"有效时间: {valid_from} - {valid_to}\n")

#                 small_elements = div_element.find_all("small")
#                 for small_element in small_elements:
#                     code_label = small_element.get_text(strip=True)
#                     code = small_element.find_next_sibling(string=True).strip()
#                     file.write(f"{code_label}: {code}\n")
#             print("最新核弹密码已获取")
#         else:
#             print("Div element not found.")
#     else:
#         print(f"Failed to retrieve the content. Status code: {response.status_code}")
#         print("网络连接可能不稳定")


# 英语日期转换成数字日期并存入version.json以供后期更新
def convert_date_to_numeric(date_str):
    # 使用datetime来解析日期字符串
    date_obj = datetime.strptime(date_str, "%B %d, %Y")
    # 格式化日期为数字形式
    numeric_date = date_obj.strftime("%m%d%Y")
    return numeric_date


def write_nuke_codes_to_file(current_nuke_codes):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    filename = "txt/核弹密码.txt"

    password_updated = False
    updated_nuke_codes = 0

    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()  # 检查是否有HTTP错误

        soup = BeautifulSoup(response.text, "html.parser")
        div_element = soup.find("div", class_="card card-terminal mb-3 p-2")

        if div_element:
            with open(filename, "w", encoding="utf-8") as file:
                strong_elements = div_element.find_all("strong")
                if strong_elements and len(strong_elements) == 2:
                    valid_from = strong_elements[0].get_text(strip=True)
                    valid_to = strong_elements[1].get_text(strip=True)

                    numeric_valid_from = convert_date_to_numeric(valid_from)
                    numeric_valid_to = convert_date_to_numeric(valid_to)

                    file.write(f"有效时间: {valid_from} - {valid_to}\n")
                    updated_nuke_codes = numeric_valid_from + numeric_valid_to
                    # print((f"核弹密码上次更新时间: {numeric_valid_from}{numeric_valid_to}\n"))

                    if updated_nuke_codes != current_nuke_codes:
                        small_elements = div_element.find_all("small")

                        for small_element in small_elements:
                            code_label = small_element.get_text(strip=True)
                            code = small_element.find_next_sibling(string=True).strip()
                            file.write(f"{code_label}: {code}\n")
                            password_updated = True
        else:
            print("Div element not found.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the content: {str(e)}")
        print("网络连接可能不稳定")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    if password_updated:
        print("最新核弹密码已获取")
        return updated_nuke_codes
    else:
        print("目前已经是最新核弹密码")


async def main():
    articles = await USER_ID.get_articles(order=user.ArticleOrder.PUBDATE, pn=1)

    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)


def run():
    asyncio.run(main())

    with open("articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    current_id, current_nuke_codes = open_version_json()

    articles = data.get("articles", [])
    article_list = []

    for article in articles:
        title = article.get("title", "")
        if title.startswith(PREFIX):
            id_ = article.get("id")
            article_url_template = f"https://www.bilibili.com/read/cv{id_}/"
            article_list.append(
                {"ID": id_, "Title": title, "URL": article_url_template}
            )

    article_url = article_list[0]["URL"]

    if current_id == article_list[0]["ID"]:
        print("当前是最新内容，无需再次刷新")
    else:
        print("正在更新中...")

        webpage_content = requests.get(article_url).text
        with open("webpage_content.html", "w", encoding="utf-8") as html_file:
            html_file.write(webpage_content)

        
        soup = BeautifulSoup(webpage_content, "html.parser")
        div = soup.find("div", class_="article-container__content")

        if div:
            for keyword, (class_suffix, img_index) in KEYWORD_DATA.items():
                for tag in div.find_all(True, class_=re.compile(f"{class_suffix}$")):
                    if keyword in tag.get_text():
                        img_tags = tag.find_all_next("img", limit=img_index + 1)
                        if len(img_tags) >= img_index + 1:
                            img_link = img_tags[img_index].get("data-src") or img_tags[img_index].get("src")
                            if img_link:
                                img_link = "https:" + img_link
                                file_name = keyword + ".png"
                                download_image(img_link, file_name)
                                print(f"{keyword}: {img_link}")
                                break
                            else:
                                print(f"{keyword}: Image link not found")
                                break
                        else:
                            print(f"{keyword}: 未找到足够数量的<img>标签")
                            break
        else:
            print("未找到指定的<div>标签")

    updated_nuke_codes_date = write_nuke_codes_to_file(current_nuke_codes)

    new_id = article_list[0]["ID"]
    new_title = article_list[0]["Title"]

    update_json("config.json", new_id, new_title, int(updated_nuke_codes_date))
    print("json文件已更新")
