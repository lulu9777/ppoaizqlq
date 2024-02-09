from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
from filelock import FileLock
import re
import logging

# 配置 logging
logging.basicConfig(filename='./log.txt', level=logging.INFO, format='%(asctime)s %(message)s')

def contains_unwanted_words(row):
    unwanted_words = ['取消', '待定', '推迟', '腰斩']
    return any(word in str(value) for value in row for word in unwanted_words)

def fetch_data():
    options = Options()
    options.add_argument("--headless")

    driver = None  # 初始赋值

    for i in range(3):  # 尝试3次
        try:
            driver = webdriver.Firefox(options=options)
            driver.get("https://live.titan007.com/oldIndexall.aspx")

            time.sleep(20)

            page_source = driver.page_source
            break  # 如果成功获取网页内容，就跳出循环
        except Exception as e:
            logging.error(f"在获取网页内容时出现错误，这是第{i+1}次尝试: {e}")
            if i < 2:  # 如果不是最后一次尝试，就继续循环
                continue
            else:  # 如果是最后一次尝试，就返回
                return
        finally:
            if driver is not None:  # 只在 driver 不为 None 时调用 quit
                driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')
    rows = soup.find_all('tr')

    data = pd.DataFrame(columns=["league_type", "match_time", "match_duration", "team1", "score", "team2", "half_score"], dtype=str)

    for i, row in enumerate(rows):
        if i in [0, 1]:
            continue

        league_type = row.find("span").get_text().strip() if row.find("span") else ""
        match_time = row.find("td", {"id": lambda x: x and x.startswith("mt_")}).get_text().strip() if row.find("td", {"id": lambda x: x and x.startswith("mt_")}) else ""
        match_duration = row.find("td", {"class": "td_status"}).get_text().strip() if row.find("td", {"class": "td_status"}) else ""
        team1 = row.find("a", {"id": lambda x: x and x.startswith("team1_")}).get_text().strip() if row.find("a", {"id": lambda x: x and x.startswith("team1_")}) else ""
        score = row.find("td", {"class": ["td_score", "td_scoreR"]}).get_text().strip() if row.find("td", {"class": ["td_score", "td_scoreR"]}) else ""
        team2 = row.find("a", {"id": lambda x: x and x.startswith("team2_")}).get_text().strip() if row.find("a", {"id": lambda x: x and x.startswith("team2_")}) else ""
        half_score = row.find("td", {"class": "td_halfR"}).get_text().strip() if row.find("td", {"class": "td_halfR"}) else ""

        if league_type == "" and match_time == "" and match_duration == "" and team1 == "" and score == "" and team2 == "" and half_score == "":
            continue

        new_row = {"league_type": league_type.replace("-", "vs"), "match_time": match_time.replace("-", "vs"), "match_duration": match_duration.replace("-", "vs"), "team1": team1.replace("-", "vs"), "score": score.replace("-", "vs"), "team2": team2.replace("-", "vs"), "half_score": half_score.replace("-", "vs")}
        new_row_df = pd.DataFrame([new_row], dtype=str)
        data = pd.concat([data, new_row_df], ignore_index=True)

    # 清洗数据：删除 'score' 列或 'half_score' 列中包含空内容的行
    data = data[(data['score'] != '') & (data['half_score'] != '')]
    
    # 删除包含 '取消', '待定', '推迟', '腰斩' 的行
    data = data[~data.apply(contains_unwanted_words, axis=1)]

    lock = FileLock("./filtered_data.lock")
    with lock:
        data.to_csv("./filtered_data.csv", index=False, encoding="utf-8-sig")
    
    # 转换数据
    transform_data()

def transform_data():
    try:
        # 读取原始的 CSV 文件
        lock = FileLock("./filtered_data.lock")
        with lock:
            data = pd.read_csv("./filtered_data.csv")

        # 将 'score' 和 'half_score' 列分割为两个新的列
        data[['team1_score', 'team2_score']] = data['score'].str.split(r'vs|-', expand=True, regex=True)
        data[['team1_half_score', 'team2_half_score']] = data['half_score'].str.split(r'vs|-', expand=True, regex=True)

        # 删除原始的 'score' 和 'half_score' 列
        data = data.drop(columns=['score', 'half_score'])

        # 将新的 DataFrame 保存为 CSV 文件
        data.to_csv("./transformed_data.csv", index=False, encoding="utf-8-sig")
        
        logging.info("数据转换完成，已保存到新的CSV文件。")
    except Exception as e:
        logging.error(f"在转换数据时出现错误: {e}")
