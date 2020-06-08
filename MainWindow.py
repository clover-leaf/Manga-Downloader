from os import listdir
from os.path import isfile, join
from lxml import html
from requests import session

def getListUpdate(content):
	mangaItemList = []
	tree = html.fromstring(content)
	ls = tree.xpath("(//*[@class='lstCategory']/tr)")
	idList = [x.attrib["data-id"] for x in ls]
	for Id in idList:
		ls = tree.xpath("(//tr[@data-id=%s]/td/a)"%Id)
		title = ls[0].text
		ls = tree.xpath("(//tr[@data-id=%s]/td)"%Id)
		chapters = ls[2].text	
		uploader = ls[3].text
		views    = ls[4].text
		item = {
			"id"      : Id,
			"title"   : title,
			"chapters": chapters,
			"uploader": uploader,
			"views"   : views
			}
		mangaItemList.append(item)
	return mangaItemList

s = session()

data = {"username": "ILikeManga",
	    "password": "thanghay"}

head = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}

r = s.post("http://id.blogtruyen.com/dang-nhap", data=data, headers=head)
print(r.content)
# resp = s.get("https://blogtruyen.com/admin/truyen-da-dang")
# resp = s.get("https://blogtruyen.com/admin/truyen-tham-gia-update")

# mypath = "C:/Users/THANG/Pictures/Rough/95 - Ngẫu nhiên thôi"
# onlyfiles = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]

# files = {}
# for f in onlyfiles:
# 	files[f[-6:-2]] = open(f, "rb")
# print(files)
# s.post("https://blogtruyen.com/admin/them-moi-chuong/9484?isCaption=False", files=files, headers=head)
# for i in getListUpdate(resp.content):
# 	print(i)

	


