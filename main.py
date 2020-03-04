# encoding: utf-8

import requests
from lxml import etree
import xlwt


base_domain = 'http://dytt8.net'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
}
urls = []
detail_urls = []
names = ["封面图片链接",
         "年代",
         "产地",
         "类别",
         "豆瓣评分",
         "片长",
         "导演",
         "主演",
         "简介",
         "ftp下载链接",
         "magnet下载链接"]


# 获取到第num页所有的url
def page(num):
    i = 1
    while i <= num:
        urls.append("https://dytt8.net/html/gndy/dyzz/list_23_%d.html" % i)
        i += 1


# 获取页面中进入详细页的url
def get_detail_urls():
    for url in urls:
        response = requests.get(url, headers=headers)
        # response.text/response.content
        # request库，默认会使用自己猜测的编码方式将抓取下来的网页进行编码，然后储存到text属性上去
        # 在电影天堂的网页中，因为编码方式，requests库猜错了。所以就会产生乱码
        text = response.content.decode('gbk', errors='ignore')  # 右键网页源代码可以找到"charset=gb2312"，表明网页用gbk进行了编码
        html = etree.HTML(text)  # 将text转换成可以解析的html代码，etree的结构，Element tree
        detail_url = html.xpath(
            "//table[@class='tbspan']//a/@href")  # 获取每个页面电影的简介网址，@class='tbspan'是table的属性,@href表示取href的值
        for false_detail_url in detail_url:
            true_detail_url = base_domain + false_detail_url
            detail_urls.append(true_detail_url)


# 获取某个电影详细信息
def detail_page():
    response = requests.get(detail_url, headers=headers)
    text = response.content.decode('gbk', errors='ignore')
    html = etree.HTML(text)
    title = html.xpath('//title/text()')[0]
    real_title = "《" + title.split("《", 2)[1].split("》")[0] + "》"
    cover = html.xpath('//div[@id="Zoom"]//img/@src')[0]  # /@src表示取scr的值
    # 将电影名称写入excel
    worksheet.write(row + 1, 0, real_title)
    # 防止后面解码错误跳过导致少爬取某部电影
    print(real_title)
    try:
        movie = []
        title_cover = {"封面图片链接": cover}
        movie.append(title_cover)
        content = html.xpath('//div[@id="Zoom"]//p/text()')

        for i in content:
            if i.startswith("◎年　　代"):
                year = i.replace("◎年　　代", "").strip()  # strip()去除前后空格
                dict_year = {"年代": year}
                movie.append(dict_year)
            elif i.startswith("◎产　　地"):
                country = i.replace("◎产　　地", "").strip()
                dict_country = {"产地": country}
                movie.append(dict_country)
            elif i.startswith("◎类　　别"):
                category = i.replace("◎类　　别", "").strip()
                dict_category = {"类别": category}
                movie.append(dict_category)
            elif i.startswith("◎豆瓣评分"):
                douban_rating = i.replace("◎豆瓣评分", "").strip()
                dict_douban_rating = {"豆瓣评分": douban_rating}
                movie.append(dict_douban_rating)
            elif i.startswith("◎片　　长"):
                duration = i.replace("◎片　　长", "").strip()
                dict_duration = {"片长": duration}
                movie.append(dict_duration)
            elif i.startswith("◎导　　演"):
                director = i.replace("◎导　　演", "").strip()
                dict_director = {"导演": director}
                movie.append(dict_director)

        for x in content:
            actor = []
            if x.startswith("◎主　　演"):
                x_rectify = x.replace("◎主　　演", "").strip()
                actor.append(x_rectify)
                num = content.index(x)
                while 1:
                    num += 1
                    y = content[num]
                    if y.startswith("◎标　　签"):
                        break
                    else:
                        y_rectify = y.strip()
                        actor.append(y_rectify)
                actor_dict = {"主演": actor}
                movie.append(actor_dict)
            if x.startswith("◎简　　介"):
                num = content.index(x)
                profile = content[num + 1].strip()
                dict_profile = {"简介": profile}
                movie.append(dict_profile)

        ftp_download = html.xpath('//td[@bgcolor="#fdfddf"]//a/@href')[0]
        magnet_download = html.xpath('//p//a/@href')[0]
        ftp_download_dict = {"ftp下载链接": ftp_download}
        movie.append(ftp_download_dict)
        magnet_download_dict = {"magnet下载链接": magnet_download}
        movie.append(magnet_download_dict)
        print(movie)
        print("=" * 100)
        # 将movie写入excel
        b = 1
        for name in names:
            worksheet.write(row + 1, b, movie[b - 1][name])
            b += 1
    except:
        print("这部电影需手动爬取")
        print("=" * 100)


if __name__ == '__main__':
    page(2)
    get_detail_urls()
    # 新建excel
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet("sheet1")
    worksheet.write(0, 0, "电影名称")
    a = 1
    for name in names:
        worksheet.write(0, a, name)
        a += 1
    for detail_url in detail_urls:
        row = detail_urls.index(detail_url)
        detail_page()
    workbook.save("爬虫结果.xls")
