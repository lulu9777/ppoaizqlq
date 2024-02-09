from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
import logging

# 配置 logging
logging.basicConfig(filename='./log.txt', level=logging.INFO, format='%(asctime)s %(message)s')

print("已启动篮球data_fetch.py")

def fetch_data():
    options = Options()
    options.add_argument("--headless")

    driver = None  # 初始赋值

    for i in range(3):  # 尝试3次
        try:
            driver = webdriver.Firefox(options=options)
            driver.get("https://lq3.titan007.com/nba.htm")

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

    current_row = {}
    for i, row in enumerate(rows):
        if i in [0, 0]:  # 这个判断有点问题，两个0是重复的
            continue

        league_type = row.find("span", {"class": "leaguesname"}).get_text().strip() if row.find("span", {"class": "leaguesname"}) else ""
        match_time = row.find("td", {"class": "s-time2 right-line"}).get_text().strip() if row.find("td", {"class": "s-time2 right-line"}) else ""
        match_duration = row.find("span", {"id": lambda x: x and x.startswith("zt_")}).get_text().strip() if row.find("span", {"id": lambda x: x and x.startswith("zt_")}) else ""
        team1 = row.find("a", {"id": lambda x: x and x.startswith("team1_")}).get_text().strip() if row.find("a", {"id": lambda x: x and x.startswith("team1_")}) else ""
        score = row.find("td", {"id": lambda x: x and x.startswith("qzf_")}).get_text().strip().replace('全:', '') if row.find("td", {"id": lambda x: x and x.startswith("qzf_")}) else ""
        team2 = row.find("a", {"id": lambda x: x and x.startswith("team2_")}).get_text().strip() if row.find("a", {"id": lambda x: x and x.startswith("team2_")}) else ""
        half_score = row.find("td", {"id": lambda x: x and x.startswith("bzf_")}).get_text().strip().replace('半:', '') if row.find("td", {"id": lambda x: x and x.startswith("bzf_")}) else ""

        if league_type:
            current_row["league_type"] = league_type
        if match_time:
            current_row["match_time"] = match_time
        if match_duration:
            current_row["match_duration"] = match_duration
        if team1:
            current_row["team1"] = team1
        if score:
            current_row["score"] = score
        if team2:
            current_row["team2"] = team2
        if half_score:
            current_row["half_score"] = half_score

        if len(current_row.keys()) == 7:
            new_row_df = pd.DataFrame([current_row], dtype=str)
            data = pd.concat([data, new_row_df], ignore_index=True)
            current_row = {}

    try:
        # 先将数据写入到临时文件
        data.to_csv("./temp.csv", index=False, encoding="utf-8-sig")
        
        # 读取临时文件的数据
        temp_data = pd.read_csv("./temp.csv")

        # 删除"half_score"列无值的行
        temp_data = temp_data[temp_data['half_score'].notna()]

        # 将清洗后的数据写入到最终的CSV文件
        temp_data.to_csv("./transformed_data.csv", index=False, encoding="utf-8-sig")

        logging.info("数据获取和清洗完成，已保存到CSV文件。")
    except Exception as e:
        logging.error(f"在处理数据时出现错误: {e}")

fetch_data()
