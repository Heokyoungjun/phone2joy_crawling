from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import os
from urllib.parse import quote_plus

# 검색 대분류(순서) 왼쪽부터 1 ~
item = [4, 5, 6, 7, 8, 10]
# 대분류 상품명
items1 = []
# 대분류 링크
link1 = []
# 중분류 소분류 상품명
items2 = []
# 류중분류 소분류 링크
link2 = []
# 웹사이트 설정
baseUrl = 'https://phone2joy.com'
# 출력데이타
csvData = []
# 에러메세지파일
errorFile = "ErrorMsg.txt"
# 다운로드완료 상품 목록 리스트파일
itemsList = "ImageDownLoadItemsList.txt"

# 슬래쉬 -> 스페이스 변환
def slashChange(str):
    str = str.replace("/", " ")
    return str

# error내용 출력
def makeErrorTxt(msg):
    file = ""

    if os.path.isfile(errorFile):
        # 파일에 추가
        file = open(errorFile, 'a')
    else:
        # 파일 작성
        file = open(errorFile, 'w')

    # 데이타 출력
    file.write(msg)
    file.write("\n")
    file.close()

# 다룬로드체크파일 작성
def downloadFileWrite(itemName):
    if os.path.isfile(itemsList):
        # 파일에 추가
        file = open(itemsList, 'a')
    else:
        # 파일 작성
        file = open(itemsList, 'w')

    # 파일에 추가
    file.write(itemName + "\n")
    file.close()

# 다운로드 유무 확인(다운로드O:False, 다운로드X:True)
def downloadCheck(url, itemName):
    rstFlag = True

    if os.path.isfile(url):
        pass
    else:
        # 파일 작성
        file = open(itemsList, 'w')
        file.write("")
        file.close()
        return rstFlag

    file = open(url, 'r')

    readItems = file.read()
    if 0 <= readItems.find(itemName):
        rstFlag = False

    file.close()

    return rstFlag

# csv파일 작성
def makeCsv(fileName, data):
    file = ""

    if os.path.isfile(fileName):
        # 파일에 추가
        file = open(fileName, 'a')
    else:
        # 파일 작성
        file = open(fileName, 'w')

    # 데이타 출력
    idx = 0
    for i in data:
        cnt = 0
        file.write(i)

        if idx != len(data) - 1:
            file.write(",")
        idx += 1

    file.write("\n")
    file.close()

# 디렉토리 생성 메소드
def createFolder(dir):
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
    except OSError:
        makeErrorTxt("ERROR: Creating directory." + dir)

# 소분류 페이지 읽기
def getUrl(saveDir, siteUrl, data1, data2, data3):

    # 한글url 치환
    url = quote_plus(baseUrl + siteUrl)
    url = url.replace("%2F", "/")
    url = url.replace("%3A", ":")

    # url open
    html = urlopen(url)

    # 페이지 파싱
    soup = bs(html, "html.parser")

    # 마지막페이지 구하기
    lastPage = soup.select('.last')
    txtTmp = lastPage[0]["href"]
    txtPnt = txtTmp.find("=")
    lastPageCnt = txtTmp[txtPnt + 1:]

    # 헤더 데이타 쓰기
    csvData = ["대분류", "중분류", "소분류", "상품명", "판매가", "소비자가", "기종", "색상", "디자인", "섬네일", "상세이미지", "링크"]
    if data3 != " ":
        if os.path.isfile(saveDir + "/" + data3 + ".csv"):
            pass
        else:
            makeCsv(saveDir + "/" + data3 + ".csv", csvData)

    elif data3 == " " and data2 != " ":
        if os.path.isfile(saveDir + "/" + data2 + ".csv"):
            pass
        else:
            makeCsv(saveDir + "/" + data2 + ".csv", csvData)
    elif data3 == " " and data2 == " " and data1 != " ":
        if os.path.isfile(saveDir + "/" + data1 + ".csv"):
            pass
        else:
            makeCsv(saveDir + "/" + data1 + ".csv", csvData)

    # 마지막 페이지가 없을 경우
    if lastPageCnt == "#none":
        lastPageCnt = 1

    # 첫페이지부터 마지막페이지까지
    for pageidx in range(1, int(lastPageCnt) + 1):

        print("현재 페이지 = " + data1 + " , " + data2 + " , " + data3 + " , " + str(pageidx) + "페이지 출력중")

        # 각페이지 url
        urltmp = url + "?page=" + str(pageidx)

        # url open
        html = urlopen(urltmp)

        # 페이지 파싱
        soup = bs(html, "html.parser")

        # 각페이지 읽어드리기
        pageData = soup.select('.thumbnail')
        for i in pageData:
            link = i.find('a')['href']
            tagImg = i.find_all('img')[5]
            alt = tagImg['alt']

            # 각CSV파일 다운로드 체크
            eachOtherFileFlag = False
            if data3 != " ":
                eachOtherFileFlag = downloadCheck(saveDir + "/" + data3 + ".csv", alt)
            elif data3 == " " and data2 != " ":
                eachOtherFileFlag = downloadCheck(saveDir + "/" + data2 + ".csv", alt)
            elif data3 == " " and data2 == " " and data1 != " ":
                eachOtherFileFlag = downloadCheck(saveDir + "/" + data1 + ".csv", alt)

            imgFileDownLoadFlag = downloadCheck(itemsList, alt)
            print("상품명 : " + alt + " , eachOtherFileFlag : " + str(eachOtherFileFlag) + " , imgFileDownLoadFlag : ",
                  imgFileDownLoadFlag)

            if eachOtherFileFlag or imgFileDownLoadFlag:
                # CSVdata초기화
                csvData = []

                # 대분류 임시저장
                csvData.append(data1)
                # 중분류 임시저장
                csvData.append(data2)
                # 소분류 임시저장
                csvData.append(data3)
                # 상품명
                csvData.append(alt)

                # 한글url 치환
                url1 = quote_plus(baseUrl + link)
                url1 = url1.replace("%2F", "/")
                url1 = url1.replace("%3A", ":")

                print(url1)
                # url open
                html2 = urlopen(url1)

                # 페이지 파싱
                soup2 = bs(html2, "html.parser")

                # 판매가
                price = soup2.select('#span_product_price_text')
                csvData.append(price[0].get_text().replace(",", ""))

                # 소비자가
                consumer = soup2.select('#span_product_price_custom')
                csvData.append(consumer[0].get_text().replace(",", ""))

                # 기종 색상 디자인
                consumer = soup2.select('.xans-product-option')
                kiFlg = 0
                clrFlg = 0
                dgnFlg = 0
                for z in consumer:
                    thtmp = z.find_all('th')
                    # 기종 값 추출
                    if 0 != len(thtmp) and kiFlg == 0 and thtmp[0].get_text() in "기종":
                        designTmp = "["
                        design = soup2.select('#product_option_id1')
                        designOption = design[0].find_all('option')
                        for designText in designOption:
                            if designText['value'] != "*" and designText['value'] != "**":
                                designTmp = designTmp + designText.get_text() + ":"

                        designTmp = designTmp[:-1] + "]"
                        csvData.append(designTmp)
                        kiFlg = 1

                # 기종 값 공백
                if kiFlg == 0:
                    csvData.append(" ")

                for z in consumer:
                    thtmp = z.find_all('th')
                    # 색상 값 추출
                    if 0 != len(thtmp) and clrFlg == 0 and thtmp[0].get_text() in "색상":
                        designTmp = "["
                        designOption = soup2.find_all(disabled="disabled")
                        for designText in designOption:
                            if designText['value'] != "*" and designText['value'] != "**":
                                designTmp = designTmp + designText.get_text() + ":"

                        designTmp = designTmp[:-1] + "]"
                        csvData.append(designTmp)
                        clrFlg = 1

                # 색상 값 공백
                if clrFlg == 0:
                    csvData.append(" ")

                for z in consumer:
                    thtmp = z.find_all('th')
                    # 디자인 값 추출
                    if 0 != len(thtmp) and dgnFlg == 0 and thtmp[0].get_text() in "디자인":
                        designTmp = "["
                        design = soup2.select('#product_option_id1')
                        designOption = design[0].find_all('option')
                        for designText in designOption:
                            if designText['value'] != "*" and designText['value'] != "**":
                                designTmp = designTmp + designText.get_text() + ":"

                        designTmp = designTmp[:-1] + "]"
                        csvData.append(designTmp)
                        dgnFlg = 1

                # 디자인 값 공백
                if dgnFlg == 0:
                    csvData.append(" ")

                # 상세 메인이미지 주소
                img = soup2.select('.BigImage')
                imgSrc = img[0]["src"]

                # 상세 메인이미지 파일명 갖고오기
                idx = imgSrc.rfind("/")
                imgFileName = imgSrc[idx + 1:]

                # 한글url 치환
                url2 = quote_plus(imgSrc)
                url2 = url2.replace("%2F", "/")
                url2 = url2.replace("%3A", ":")
                url2 = url2.replace("+", "%20")

                # 다운로드 유무 체크
                if imgFileDownLoadFlag:
                    try:
                        # 상세 메인이미지 다운로드 및 썸네일
                        with urlopen(url2) as f:
                            with open(saveDir + "/" + alt + "-main-" + imgFileName, 'wb') as h:  # w - write b - binary
                                imgFile = f.read()
                                h.write(imgFile)
                    except ValueError:
                        try:
                            print("url2 : " + url2)
                            # 상세 메인이미지 다운로드 및 썸네일
                            with urlopen("https:" + url2) as f:
                                with open(saveDir + "/" + alt + "-main-" + imgFileName, 'wb') as h:  # w - write b - binary
                                    img = f.read()
                                    h.write(img)
                        except:
                            makeErrorTxt("ValueError 에러 상품 : " + alt)

                    except Exception as e:
                        makeErrorTxt("Exception 에러 상품 : " + alt)

                # 상세 내용 이미지 주소
                img2 = soup2.select('.cont')

                # 상세 내용 이미지 주소tmp
                img2Tmp = "["

                for j in img2:
                    src2 = j.find_all('img')

                    for k in src2:
                        src3 = k['ec-data-src']
                        imgFileName2 = ""

                        if "event" not in src3 and "shop_guide" not in src3 and "title" not in src3:

                            # 상세 메인이미지 파일명 갖고오기
                            idx2 = src3.rfind("/")
                            imgFileName2 = src3[idx2 + 1:]

                            imgSrc = src3[:idx2]

                            # 한글url 치환
                            url3 = quote_plus(imgFileName2)
                            url3 = url3.replace("%2F", "/")
                            url3 = url3.replace("%3A", ":")
                            url3 = url3.replace("+", "%20")
                            url3 = "https://phone2joy.com" + imgSrc + "/" + url3

                            # 다운로드 유무 체크
                            if imgFileDownLoadFlag:
                                try:
                                    # 상세 메인이미지 다운로드 및 썸네일
                                    with urlopen(url3) as f:
                                        with open(saveDir + "/" + alt + "-detail-" + imgFileName2,
                                                  'wb') as h:  # w - write b - binary
                                            imgFile = f.read()
                                            h.write(imgFile)
                                except Exception as e:
                                    makeErrorTxt("문제 페이지 = " + data1 + " , " + data2 + " , " + data3 + " , " + str(
                                        pageidx) + "페이지" + " , 상품명 : " + alt)
                                    makeErrorTxt("ERROR not Found : " + url3)

                            # 상세 내용 이미지 주소tmp
                            img2Tmp = img2Tmp + alt + "-detail-" + imgFileName2 + ":"

                # 섬네일
                csvData.append(alt + "-main-" + imgFileName)

                # 상세 이미지
                img2Tmp = img2Tmp[:-1] + "]"
                csvData.append(img2Tmp)

                # 해당링크
                csvData.append(baseUrl + link)

                # 다운로드 유무 체크
                if eachOtherFileFlag:
                    # csv 파일 쓰기
                    if data3 != " ":
                        makeCsv(saveDir + "/" + data3 + ".csv", csvData)
                    elif data3 == " " and data2 != " ":
                        makeCsv(saveDir + "/" + data2 + ".csv", csvData)
                    elif data3 == " " and data2 == " " and data1 != " ":
                        makeCsv(saveDir + "/" + data1 + ".csv", csvData)

                if imgFileDownLoadFlag:
                    # 다운로드완료한 상품명 작성
                    downloadFileWrite(alt)


# 데이터 크롤링 메소드
def urlcwraling():
    # 웹사이트 오픈
    html = urlopen(baseUrl)
    # 메인 페이지 파씽
    soup = bs(html, "html.parser")

    # 대구분 링크 읽기
    alink1 = soup.find_all('ul', {'class': 'nav d1-wrap'})

    # 대분류 및 중분류 링크 저장
    for i in alink1:
        for j in i.find_all('li'):
            items1.append(j.get_text())
            link1.append(j.find('a')['href'])

    # 대분류 수 만큼 루프
    for i in item:

        # 대분류명
        itemTop = items1[i-1]

        url1 = baseUrl + link1[i-1]

        # 한글url 치환
        url1 = quote_plus(url1)
        url1 = url1.replace("%2F", "/")
        url1 = url1.replace("%3A", ":")

        # url open
        html1 = urlopen(url1)

        # 메인 페이지 파씽
        soup1 = bs(html1, "html.parser")

        alink2 = soup1.find_all('ul', {'class': 'menuCategory'})
        alink3 = alink2[0].find_all('li', {'class':'xans-element-'})

        if 0 == len(alink3):
            # 대구분만 있을경우

            # 디렉토리 작성
            makeDir = slashChange(itemTop)
            createFolder(makeDir)

            # 페이지 읽기
            getUrl(makeDir, link1[i-1], itemTop, " ", " ")

        else:
            # 중분류가 있을경우
            for k in range(0,len(alink3)):
                alink4 = alink3[k].find_all('a')

                # 중분류 소분류 링크 저장
                items2 = []
                link2 = []
                for j in alink4:
                    items2.append(j.get_text()[:-2])
                    link2.append(j['href'])

                if 1 == len(items2):
                    # 중분류만 있을경우

                    # 디렉토리 작성
                    makeDir = slashChange(itemTop) + "/" + slashChange(items2[0])
                    createFolder(makeDir)

                    # 페이지 읽기
                    getUrl(makeDir, link2[0], itemTop, items2[0], " ")
                else:
                    # 소분류가 있을경우

                    # 디렉토리 작성
                    for ind in range(1, len(items2)):
                        makeDir = slashChange(itemTop) + "/" + slashChange(items2[0]) + "/" + slashChange(items2[ind])
                        createFolder(makeDir)

                        # 페이지 읽기
                        getUrl(makeDir, link2[ind], itemTop, items2[0], items2[ind])

# 데이터 크롤링
urlcwraling()

print("완료했습니다")

