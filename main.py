import sys
import time
import pytz
from datetime import datetime

from utils import get_daily_papers_by_keyword_with_retries, generate_table, back_up_files,\
    restore_files, remove_backups, get_daily_date

beijing_timezone = pytz.timezone('Asia/Shanghai')

current_date = datetime.now(beijing_timezone).strftime("%Y-%m-%d")

# 修改关键词结构为双层列表
keywords = [
    ["LLM", "attack"],      # 第一组：
    ["LLM","Backdoor Attack"],    # 第二组：
    ["large language model", "attack"],  # 第三组：
    ["large language model", "Backdoor Attack"]  # 第四组：
]

max_result = 10
issues_result = 15
column_names = ["Title", "Link", "Abstract", "Date", "Comment"]

back_up_files()

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
    # 构造显示用字符串
    keyword_display = " AND ".join(keyword_group)
    
    # 构造API查询字符串（保持AND逻辑）
    query = " AND ".join(f"({kw})" for kw in keyword_group)

    f_rm.write(f"## {keyword_display}\n")
    f_is.write(f"## {keyword_display}\n")
    
    papers = get_daily_papers_by_keyword_with_retries(query, column_names, max_result, link="OR")
    
    if papers is None:
        print("Failed to get papers!")
        f_rm.close()
        f_is.close()
        restore_files()
        sys.exit("Failed to get papers!")

    # 生成表格内容
    rm_table = generate_table(papers)
    is_table = generate_table(papers[:issues_result], ignore_keys=["Abstract"])
    
    f_rm.write(rm_table)
    f_rm.write("\n\n")
    f_is.write(is_table)
    f_is.write("\n\n")
    
    time.sleep(5)  # 保持API请求间隔

f_rm.close()
f_is.close()
remove_backups()