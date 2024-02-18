# -*- coding: utf-8 -*-

import os
from urllib import request
from selenium import webdriver
from dramkit.const import HEADERS


def url2file(url: str,
             fpath: str,
             force: bool = False,
             ) -> None:
    '''下载文件'''
    if force or (not os.path.exists(fpath)):
        try:
            request.urlretrieve(url, fpath)
        except:
            # https://blog.csdn.net/wtl1992/article/details/129254986
            opener = request.build_opener()
            opener.addheaders = [(k, v) for k, v in HEADERS.items()]
            request.install_opener(opener)             
            request.urlretrieve(url, fpath)


def url2mhtml(url: str,
              mhtml_path: str,
              force: bool = False,
              ) -> None:
    '''
    | 下载给定url网页保存为mhtml文件
    | 注：须安装Chrome浏览器，
    |    然后下载对应版本的chromedriver解压后复制到anaconda3的Scripts文件夹下
    |    最后pip install selenium   
    
    References
    ----------
    - https://blog.csdn.net/weixin_38392612/article/details/125500278
    - https://chromedriver.chromium.org/downloads/version-selection
    - https://chromedriver.chromium.org/downloads
    - https://chromedriver.storage.googleapis.com/index.html
    - https://registry.npmmirror.com/binary.html?path=chromedriver/
    '''
    
    if not force and os.path.exists(mhtml_path):
        return
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
     
    driver = webdriver.Chrome(options=chrome_options)    
    driver.get(url)
    # 调用chrome开发者工具# 调用chrome开发者工具
    resp = driver.execute_cdp_cmd('Page.captureSnapshot', {})
    
    with open(mhtml_path, 'w', newline='') as fp:
        html = resp.get('data')
        if html:
            fp.write(html)
    
    driver.quit()





