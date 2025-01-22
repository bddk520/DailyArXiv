import sys
import time
import pytz
from datetime import datetime

from utils import get_daily_papers_by_keyword_with_retries, generate_table, back_up_files,\
    restore_files, remove_backups, get_daily_date


beijing_timezone = pytz.timezone('Asia/Shanghai')

# NOTE: arXiv API seems to sometimes return an unexpected empty list.

# get current beijing time date in the format of "2021-08-01"
current_date = datetime.now(beijing_timezone).strftime("%Y-%m-%d")
# get last update date from README.md
with open("README.md", "r") as f:
    while True:
        line = f.readline()
        if "Last update:" in line: break
    last_update_date = line.split(": ")[1].strip()
    # if last_update_date == current_date:
        # sys.exit("Already updated today!")

keywords = [["LLM", "attack"]]  # 每组关键词以子列表形式表示，使用 AND 逻辑
max_result = 100  # 每组关键词的最大返回论文数量
issues_result = 15  # Issue 中包含的最大论文数量
column_names = ["Title", "Link", "Abstract", "Date", "Comment"]

back_up_files()  # 备份 README.md 和 ISSUE_TEMPLATE.md

# 初始化 README.md 文件
f_rm = open("README.md", "w")
f_rm.write("# Daily Papers\n")
f_rm.write("The project automatically fetches the latest papers from arXiv based on keywords.\n\nThe subheadings in the README file represent the search keywords.\n\nOnly the most recent articles for each keyword are retained, up to a maximum of 100 papers.\n\nYou can click the 'Watch' button to receive daily email notifications.\n\nLast update: {0}\n\n".format(current_date))

# 初始化 ISSUE_TEMPLATE.md 文件
f_is = open(".github/ISSUE_TEMPLATE.md", "w")
f_is.write("---\n")
f_is.write("title: Latest {0} Papers - {1}\n".format(issues_result, get_daily_date()))
f_is.write("labels: documentation\n")
f_is.write("---\n")
f_is.write("**Please check the [Github](https://github.com/zezhishao/MTS_Daily_ArXiv) page for a better reading experience and more papers.**\n\n")

for keyword_group in keywords:
    keyword_display = " AND ".join(keyword_group)  # 显示用的关键词组合
    f_rm.write("## {0}\n".format(keyword_display))
    f_is.write("## {0}\n".format(keyword_display))
    
    # 构造 AND 逻辑的查询字符串
    query = " AND ".join(f"({kw})" for kw in keyword_group)
    
    papers = get_daily_papers_by_keyword_with_retries(query, column_names, max_result, link="AND")
    if papers is None:  # 如果获取失败
        print("Failed to get papers!")
        f_rm.close()
        f_is.close()
        restore_files()
        sys.exit("Failed to get papers!")
    
    # 生成表格内容
    rm_table = generate_table(papers)
    is_table = generate_table(papers[:issues_result], ignore_keys=["Abstract"])
    
    # 写入到 README.md 和 ISSUE_TEMPLATE.md
    f_rm.write(rm_table)
    f_rm.write("\n\n")
    f_is.write(is_table)
    f_is.write("\n\n")
    time.sleep(5)  # 避免触发 arXiv API 的速率限制

f_rm.close()
f_is.close()
remove_backups()  # 删除备份文件
