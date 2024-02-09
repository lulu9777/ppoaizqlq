import os
import logging
from fetch_and_transform import fetch_data

# 配置 logging
logging.basicConfig(filename='./log.txt', level=logging.INFO, format='%(asctime)s %(message)s')

def clear_large_files():
    directories = ["/root/qqqq", "/root/qqqq/qqqq2222", "/root/qqqq/ppollll", "/root/qqqq/ppollll/pppppp333"]
    for dir_path in directories:
        for filename in os.listdir(dir_path):
            if filename.endswith(".txt") or filename.endswith(".log"):
                file_path = os.path.join(dir_path, filename)
                if os.path.getsize(file_path) > 5 * 1024 * 1024:  # 文件大小大于5MB
                    os.remove(file_path)
                    logging.info(f"已删除文件: {file_path}")

if __name__ == "__main__":
    fetch_data()
    logging.info("开始清理文件...")
    clear_large_files()
