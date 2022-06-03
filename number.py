import os
import re
import sys
import threading
import time
from typing import Set
import urllib.parse
import urllib.request
from pathlib import Path

from multiprocessing import Pool


def open_url(url, headers=None):
    try_c = 0
    while try_c < 3:
        try:
            if headers == None:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.30"
                }
                req = urllib.request.Request(url, headers=headers)

                page = urllib.request.urlopen(req)
                html = page.read().decode("utf-8")
                try_c = 3
        except:
            try_c = try_c + 1
            print("重试\n")

    return html


def get_url(url, visited: Set[str]):
    if url in visited:
        return []

    print(url, visited)

    urllist = []
    try_c = 0
    while try_c < 3:
        try:
            html = open_url(url)
            other_htmls = re.findall("/girl/\d+/album/\d+\.html", html)
            for other in other_htmls:
                other_url = "https://fnvshen.com" + other
                visited.add(other_url)
                urllist += get_url(other_url, visited)
            urllist += re.findall("<a class='igalleryli_link' href='/g/([^/]+?)/'", html)
            try_c = 3
            return urllist
        except:
            try_c = try_c + 1
            print("重试\n")
    raise ValueError


def dl_img(each, headers):
    print(each + "\n")
    filename = each.split("/")[-1]
    req = urllib.request.Request(each, headers=headers)
    try_c = 0
    while try_c < 3:
        try:
            page = urllib.request.urlopen(req, timeout=5)
            html = page.read()  # .decode('utf-8')
            with open(filename, "wb") as f:
                f.write(html)
                f.close()
            try_c = 3
        except:
            try_c = try_c + 1
            print("重试\n")


def get_img(html, headers):
    p = r"<img src='([^']+?)'"
    imglist = re.findall(p, html)
    t = []
    for each in imglist:
        a = threading.Thread(target=dl_img, args=(each, headers))
        a.start()
        t.append(a)
    for a in t:
        a.join()


def main(name_search):
    m_name_search = str(name_search)

    girl1 = m_name_search
    o_url = "https://www.fnvshen.com/girl/" + girl1 + "/album/"
    urllist = get_url(o_url + "1.html", set())

    a_cont = 0
    exist_dir_search = os.path.isdir(m_name_search)
    if not exist_dir_search:
        os.mkdir(m_name_search)
    pwd = Path(os.getcwd())
    os.chdir(pwd / m_name_search)
    download_time = 999
    download_time_counter = 1  # 下载的专辑数计数
    for url in urllist:
        thread_c0 = threading.active_count()
        url = "https://www.fnvshen.com/g/" + url + "/"
        print(url)
        html_new_dir = open_url(url)
        new_dir_name = re.findall("<title>(.+?)</title>", html_new_dir)[0]
        dir_exist = os.path.isdir(new_dir_name)
        if dir_exist:
            continue
        os.mkdir(pwd / m_name_search / new_dir_name)
        os.chdir(pwd / m_name_search / new_dir_name)
        new_href = "10"
        for i in range(1, 100):
            url_new = url + str(i) + ".html"
            a = open_url(url_new)
            if i <= 1:
                # new_href = re.findall(">([^<]+?)</a><a class='a1'[^>]+?>下一页</a>",a)[0]
                a_cont += 1  # 表示示正在下专辑序数
            if i != int(new_href):  # 当前不是最后一页就找最后一页
                new_href = re.findall(">([^<]+?)</a><a class='a1'[^>]+?>下一页</a>", a)[0]
            headers = {
                "Referer": url_new,
                "User-Agent": "Mozilla/5.0 (Window\
s NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, \
like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53\
.3103.400 QQBrowser/9.6.11372.400",
            }
            get_img(a, headers)
            print(i)
            print(new_href)

            print(a_cont)
            if i > 1:
                if i == int(new_href):
                    break

            # time.sleep(0.1)
            time.sleep(0.2)
        thread_c1 = threading.active_count()
        while thread_c1 - thread_c0 != 0:
            time.sleep(1)
            thread_c1 = threading.active_count()
            print("当前线程数---初始线程数：" + str(thread_c1) + "---" + str(thread_c0))
        os.chdir(pwd / m_name_search)
        if download_time_counter >= download_time:
            break
        download_time_counter += 1
        time.sleep(0.2)
    os.chdir(pwd)


if __name__ == "__main__":
    ids = map(int, sys.argv[1:])

    Pool(len(ids)).map(main, map(str, ids))
