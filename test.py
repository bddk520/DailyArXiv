import urllib
import feedparser

def test_arxiv_query(query: str, max_results: int = 10, link: str = "AND"):
    """
    测试 arXiv API 查询是否能得到有效结果
    :param query: 要查询的字符串
    :param max_results: 每次查询最大返回的论文数量
    :param link: 连接逻辑，"OR" 或 "AND"
    """
    # 确保 link 只能是 "OR" 或 "AND"
    assert link in ["OR", "AND"], "link should be 'OR' or 'AND'"

    # 构造查询 URL
    query = urllib.parse.quote(query.strip())  # 确保没有多余空格，进行URL编码
    url = f"http://export.arxiv.org/api/query?search_query=ti:{query}+OR+abs:{query}&max_results={max_results}&sortBy=lastUpdatedDate"
    
    # 发起请求
    response = urllib.request.urlopen(url).read().decode('utf-8')

    # 解析返回的 XML 数据
    feed = feedparser.parse(response)

    # 检查返回的条目数量
    if len(feed.entries) == 0:
        print("No results found for your query!")
    else:
        print(f"Found {len(feed.entries)} papers for query: {query}")
        # 打印前几个结果
        for entry in feed.entries[:5]:  # 仅打印前5个条目
            print(f"Title: {entry.title}")
            print(f"Link: {entry.link}")
            print(f"Date: {entry.updated}")
            print(f"Abstract: {entry.summary}")
            print("=" * 50)

# 测试查询字符串
query = "LLM AND attack"  # 替换为您想要测试的查询字符串
test_arxiv_query(query)
