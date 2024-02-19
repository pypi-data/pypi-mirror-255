#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author  : zhengdongqi
@Email   : nickdecodes@163.com
@Usage   :
@FileName: test.py
@DateTime: 2024/1/28 20:13
@SoftWare: 
"""

from lottokit.daletou import Daletou
from collections import Counter
from itertools import combinations
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import Iterable, List, Tuple, Any, Optional, Union, Set, Dict
import re


class Test(Daletou):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)

    def get_history_num_count(self):
        history_data = self.read_csv_data_from_file(self.history_record_path, app_log=self.app_log)
        all_count = len(list(history_data[:-1]))
        print(all_count)
        num_front_count = Counter()
        num_back_count = Counter()

        for comb in history_data[-11:-1]:
            num_front_count.update(self.calculate_front(comb))
            num_back_count.update(self.calculate_back(comb))

        return num_front_count, num_back_count

    def get_all_number_frequency(self, start=1, end=35, size=5):
        # 生成1到35之间取5个数的所有组合
        all_combinations = list(combinations(range(start, end + 1), size))

        # 将所有组合展开为一个列表
        all_numbers = [number for combination in all_combinations for number in combination]

        # 统计每个数字的频率
        number_frequency = Counter(all_numbers)

        # 计算每个数字的百分比
        total_count = len(all_numbers)
        number_percentage = {number: (count / total_count) * 100 for number, count in number_frequency.items()}

        print(number_percentage)
        return number_frequency


    def run(self):
        num_front_count, num_back_count = self.get_history_num_count()
        print(num_front_count.most_common())
        print(num_back_count.most_common())
        self.get_all_number_frequency(start=1, end=35, size=5)
        self.get_all_number_frequency(start=1, end=12, size=2)


class SpiderUtil:
    """
    Mostly crawling data
    """
    url = 'https://www.lottery.gov.cn/kj/kjlb.html?dlt'

    def __init__(self, **kwargs):
        """
        Initialize the SpiderUtil object with a URL.

        :param kwargs: A dictionary of keyword arguments where:
            - 'url': str is the URL to fetch the data from. If not provided, it defaults to an empty string.
        """
        self.url = kwargs.get('url', '') or self.url

    def spider_chrome_driver(self) -> webdriver.Chrome:
        """
        Initialize a Chrome WebDriver with headless option and navigate to the URL.

        :return: An instance of Chrome WebDriver.
        """
        # Import browser configuration
        options = webdriver.ChromeOptions()
        # Set headless mode
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        return driver

    def spider_recent_data(self) -> List[List[str]]:
        """
        Fetch the recent data from the web page.

        :return: A list of lists containing recent data entries.
        """
        driver = self.spider_chrome_driver()
        time.sleep(1)  # Allow time for the page to load
        frame = driver.find_element(By.XPATH, '//iframe[@id="iFrame1"]')
        driver.switch_to.frame(frame)
        content = driver.find_element(By.XPATH, '//tbody[@id="historyData"]')
        recent_data = [x.split(' ')[:9] for x in content.text.split('\n')]
        return recent_data

    def spider_full_data(self) -> List[List[str]]:
        """
        Load the full set of data from the source.

        :return: A list of lists containing all data entries.
        """
        # The implementation should be provided by the subclass.
        driver = self.spider_chrome_driver()
        time.sleep(1)  # Allow time for the page to load
        frame = driver.find_element(By.XPATH, '//iframe[@id="iFrame1"]')
        driver.switch_to.frame(frame)
        matches = re.findall(r'goNextPage\((\d+)\)', driver.page_source)
        page_index = [int(match) for match in matches]
        print(max(page_index))
        for index in range(max(page_index)):
            # next_button = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.CLASS_NAME, "下一页"))
            # )

            # 等待数据加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//tbody[@id="historyData"]'))
            )

            # 提取数据
            content = driver.find_element(By.XPATH, '//tbody[@id="historyData"]')
            recent_data = [x.split()[:9] for x in content.text.split('\n') if len(x.split()) >= 9]
            recent_data = sorted(recent_data, key=lambda x: int(x[0]))
            print(recent_data[-3:])

            # 切回主文档

            # 等待下一页元素加载
            try:
                # 尝试找到位置为13的元素
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/ul/li[position()=13]"))
                )
            except:
                # 如果找不到位置为13的元素，则找位置为8的元素
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/ul/li[position()=8]"))
                )

            # 点击下一页
            next_button.click()
            time.sleep(3)

        # 关闭浏览器
        driver.quit()
        # frame = driver.find_element(By.XPATH, '//iframe[@id="iFrame1"]')
        # driver.switch_to.frame(frame)
        # # last_frame_count = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/ul/li[14]')
        # next_frame = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/ul/li[13]')
        # next_frame.click()
        # time.sleep(2)
        # handle = driver.window_handles
        # print(driver.page_source)
        # print(handle)

        return []


if __name__ == '__main__':
    # t = Test()
    # t.run()
    s = SpiderUtil()
    s.spider_full_data()

