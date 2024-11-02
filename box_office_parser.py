######################################################################
# task 1：数据采集。
######################################################################
# 备注：http://58921.com/boxoffice/wangpiao网站已于2019.11.14日起停止更新，
# 在此采用2019.11.14日的网页爬取其昨日票房信息。
import requests
today = requests.get('http://58921.com/boxoffice/wangpiao/20191114')
today.encoding = 'UTF-8'

# 使用BeautifulSoup处理网页文本内容。
from bs4 import BeautifulSoup
soup = BeautifulSoup(today.text, "html.parser")

# 网页文本中爬取昨日票房链接。
yesterday_link = soup.find('a', attrs={'title':'昨日票房'})['href']

# 进入昨日票房信息网页，获取网页内容。
yesterday = requests.get('http://58921.com' + yesterday_link)
yesterday.encoding = 'UTF-8'

# 使用BeautifulSoup处理网页文本内容。
soup = BeautifulSoup(yesterday.text, "html.parser")

# 爬取网页上显示的当日日期。
table_title = soup.find('div', attrs={'class':'box_office_type_view'}).\
find('h2').text
year = table_title[:4]
month = table_title[5:7]
day = table_title[8:10]
date = year + '-' + month + '-' + day

# 获取当日网票票房统计表格。
table = soup.find('table', attrs={'class':'center_table'})

# 从表格中获取所有的行项目信息。
rows = table.find_all(lambda tag: tag.name=='tr')

# 获取表头信息，存放在head中。
head = []
h = rows[0].find_all('th')
for i in range(len(h)):
    head.append(h[i].text)

# 获取表格数据信息，以行为单位存放在data中。
data = []  
for row in rows[1:]:  
    a = row.find_all('td')
    title = a[0].text
    gross = a[1].text
    today = a[2].find('img')['src']
    effective = a[3].find('img')['src']
    canceled = a[4].text
    man_time = a[5].text
    occupancy_rate = a[6].find('img')['src']
    action = 'http://58921.com' + a[7].find('a')['href']
    data.append((title, gross, today, effective, \
        canceled, man_time, occupancy_rate, action))

# 以昨日日期作为文件名，将表格数据存入 20XX-XX-XX.csv 文件。
import pandas as pd
df = pd.DataFrame(data, columns=head)
df.to_csv(date +'.csv', index=False, encoding='UTF-8')


######################################################################
# task 2: 数据处理与分析。
######################################################################
# 使用 Python 的 pandas 读取 20XX-XX-XX.csv 文件。
movies = pd.read_csv(date +'.csv')

# 将当前文件名读取的日期作为新的一列增加到最左边。
cols = movies.columns.tolist()
cols.insert(0, '日期')
movies = movies.reindex(columns=cols)
movies['日期'] = date

# 去掉总票房为空的数据记录，如果有其他数据列为空也可去掉。
movies = movies.dropna()

# 处理不规整数据（万、亿）。
for i in range(len(movies.index)):
    gross = movies.loc[i, '总票房(元)']
    if gross[-1] == '万':
        movies.loc[i, '总票房(元)'] = movies.loc[i, '总票房(元)'].\
        replace(gross, str(float(gross[:-1]) * 10000))
    elif gross[-1] == '亿':
        movies.loc[i, '总票房(元)'] = movies.loc[i, '总票房(元)'].\
        replace(gross, str(float(gross[:-1]) * 100000000))
pd.to_numeric(movies['总票房(元)'])

# 按购票“人次”从高到低输出到 movies.csv 文件中去。
movies = movies.sort_values('人次', ascending=False)
movies.to_csv('movies.csv', index=False, encoding='UTF-8')


######################################################################
# task 3: 数据可视化。
######################################################################
import matplotlib as mlp
import matplotlib.pyplot as plt

# 调整字体库，以防乱码。
mlp.rc("font",family='Heiti TC')

# 导入数据。
raw = pd.read_csv('movies.csv', index_col='电影')

# 按要求准备总票房最高的五部电影、废场最少的五部电影、观看人次最高的五部电影数据。
df1 = raw.sort_values('总票房(元)', ascending=False).iloc[:5]
df2 = raw.sort_values('废场').iloc[:5]
df3 = raw.sort_values('人次', ascending=False).iloc[:5]

# 设置总图格式。
fig = plt.figure(figsize=(20, 8))

# 绘制子图1:总票房最高的五部电影。
ax1 = fig.add_subplot(1, 3, 1)
plt.plot(df1.index, df1['总票房(元)'], marker='o')
ax1.set(title = "总票房最高的五部电影", ylabel = "总票房(元)")
ax1.set_xticks(ax1.get_xticks()) # 消除bug：“UserWarning: \
# # FixedFormatter should only be used together with FixedLocator”
ax1.set_xticklabels(df1.index, rotation=20, fontsize=10)
ax1.get_yaxis().get_major_formatter().set_scientific(False)

# 绘制子图2:废场最少的五部电影。
ax2 = fig.add_subplot(1, 3, 2)
plt.plot(df2.index, df2['废场'], marker='o')
ax2.set(title = "废场最少的五部电影", ylabel = "废场数")
ax2.set_xticks(ax2.get_xticks()) # 消除bug：“UserWarning: \
# # FixedFormatter should only be used together with FixedLocator”
ax2.set_xticklabels(df2.index, rotation=20, fontsize=10)
# # 纵坐标单位设置为整数。
from matplotlib.ticker import MaxNLocator
ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

# 绘制子图3:观看人次最高的五部电影。
ax3 = fig.add_subplot(1, 3, 3)
plt.plot(df3.index, df3['人次'], marker='o')
ax3.set(title = "观看人次最高的五部电影", ylabel = "人次")
ax3.set_xticks(ax3.get_xticks()) # 消除bug：“UserWarning: \
# # FixedFormatter should only be used together with FixedLocator”
ax3.set_xticklabels(df3.index, rotation=20, fontsize=10)

# 输出保存折线图。
fig.tight_layout()
plt.savefig('J3-1_plot')