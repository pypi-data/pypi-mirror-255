import os
import sys

package = ""
for i in sys.argv:
    if not i == sys.argv[0]:
        package += i

mirrors = [
    ["https://pypi.tuna.tsinghua.edu.cn/simple/", "清华大学"],
    ["https://mirrors.aliyun.com/pypi/simple/", "阿里云"],
    ["https://mirrors.163.com/pypi/simple/", "网易"],
    ["https://pypi.douban.com/simple/", "豆瓣"],
    ["https://mirror.baidu.com/pypi/simple/", "百度云"],
    ["https://pypi.mirrors.ustc.edu.cn/simple/", "中国科技大学"],
    ["https://mirrors.huaweicloud.com/repository/pypi/simple/", "华为云"],
    ["https://mirrors.cloud.tencent.com/pypi/simple/", "腾讯云"],
    ["https://pypi.org/simple/", "默认"],
    ["https://test.pypi.org/simple/", "测试"]
]

def install(package: str):
    os.system("echo off")
    for mirror in mirrors:
        print(f"正在从源\"{mirror[1]}：{mirror[0]}\"下载包\"{package}\"……")
        os.system(f"pip install -i {mirror[0]} {package}")
        print("结束。")

if __name__ == "__main__":
    print("""========================================
HDLRTool\\pip_install
----------------------------------------
版权所有 © 寒冬利刃(handongliren(hdlr))
Copyright © 寒冬利刃(handongliren(hdlr))
========================================""")
    if not package == "":
        install(package)
    os.system("pause")