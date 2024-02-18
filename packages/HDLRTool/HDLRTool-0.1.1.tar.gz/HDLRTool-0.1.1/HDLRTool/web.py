import requests
import time
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"
}


def get(url):
    torrent = requests.get(url, headers=headers)
    return torrent.text


def download(url, path=os.getcwd(), filename=True):
    if filename:
        filename = os.path.basename(url)
    leng = 1
    while leng == 1:
        torrent = requests.get(url, headers=headers)
        leng = len(list(torrent.iter_content(1024)))  # 下载区块数
        if leng == 1:  # 如果是1 就是空文件 重新下载
            # print(filename, '下载失败,重新下载')
            time.sleep(1)
        else:
            pass
            # print(path, '下载完成')
    with open(path + filename, 'wb') as f:
        # noinspection PyUnboundLocalVariable
        for chunk in torrent.iter_content(1024):  # 防止文件过大，以1024为单位一段段写入
            f.write(chunk)
