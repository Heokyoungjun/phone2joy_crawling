from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import os
from urllib.parse import quote_plus

# 웹사이트 설정
baseUrl = 'https://phone2joy.com'

# 대구분
item1 = ["GALAXY", "APPLE", "Z플립 케이스"]
# 중구분
item2 = [["노트시리즈", "S시리즈", "A시리즈", "J시리즈-ETC"], "아이폰", ""]
# 소구분
item3 = [["갤럭시노트", "갤럭시S", "갤럭시A", "갤럭시"], "", ""]
# 출력데이타
csvData = []
# 에러메세지파일
errorFile = "ErrorMsg.txt"
# 다운로드완료 상품 목록 리스트파일
itemsList = "ItemsList.txt"

# 다운로드 유무 확인
def downloadCheck(itemName):

    file = ""
    rstFlag = False

    if os.path.isfile(itemsList):
        # 파일에 추가
        file = open(itemsList, 'r')
    else:
        file = open(itemsList, 'w')
        file.write("상품명" + "\n")
        file.close()
        file = open(itemsList, 'r')

    readItems = file.read()
    if 0 < readItems.find(itemName):
        rstFlag = True
    else:
        file.close()
        file = open(itemsList, 'a')
        file.write(itemName+"\n")

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

        if idx != len(data)-1:
            file.write(",")
        idx += 1

    file.write("\n")
    file.close()

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

# 디렉토리 생성 메소드
def createFolder(dir):
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
    except OSError:
        makeErrorTxt("ERROR: Creating directory." + dir)

# 메인 페이지 읽기
def getUrl():

    # 웹사이트 오픈
    html = urlopen(baseUrl)
    # 메인 페이지 파씽
    soup = bs(html, "html.parser")

    # 대구분 링크 읽기
    alink1 = soup.select('.d1')

    return alink1

# 하위 페이지 읽기
def getUrl2(inputData):
    # 링크정보 읽기
    url = inputData.find("a")["href"]

    # 한글url 치환
    url = quote_plus(baseUrl + url)
    url = url.replace("%2F","/")
    url = url.replace("%3A", ":")

    # url open
    html = urlopen(url)

    # 페이지 파싱
    soup = bs(html, "html.parser")
    alink = soup.select('.dm2')

    # 파싱데이터 반환
    return alink

# 소분류 페이지 읽기
def getUrl3(inputData, saveDir, data1, data2, data3):
    # 링크정보 읽기
    url = inputData.find("a")["href"]

    # 한글url 치환
    url = quote_plus(baseUrl + url)
    url = url.replace("%2F","/")
    url = url.replace("%3A", ":")

    # url open
    html = urlopen(url)

    # 페이지 파싱
    soup = bs(html, "html.parser")

    # 마지막페이지 구하기
    lastPage = soup.select('.last')
    txtTmp = lastPage[0]["href"]
    txtPnt = txtTmp.find("=")
    lastPageCnt = txtTmp[txtPnt+1:]

    # 헤더 데이타 쓰기
    csvData = ["대분류","중분류","소분류","상품명","판매가","소비자가","기종","색상","디자인","섬네일","상세이미지","링크"]
    if data3 != " ":
        makeCsv(saveDir + "/" + data3 + ".csv", csvData)
    elif data3 == " " and data2 != " ":
        makeCsv(saveDir  + "/" + data2 + ".csv", csvData)
    elif data3 == " " and data2 == " " and data1 != " ":
        makeCsv(saveDir  + "/" + data1 + ".csv", csvData)

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

            resultFlag = downloadCheck(alt)
            if resultFlag:
                continue

            print(alt)

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

            # src = tagImg['src']
            # 한글url 치환
            url1 = quote_plus(baseUrl + link)
            url1 = url1.replace("%2F","/")
            url1 = url1.replace("%3A", ":")

            # url open
            html2 = urlopen(url1)

            # 페이지 파싱
            soup2 = bs(html2, "html.parser")

            # 판매가
            price = soup2.select('#span_product_price_text')
            csvData.append(price[0].get_text().replace(",",""))

            # 소비자가
            consumer = soup2.select('#span_product_price_custom')
            csvData.append(consumer[0].get_text().replace(",",""))

            # 기종 색상 디자인
            consumer = soup2.select('.xans-product-option')
            kiFlg = 0
            clrFlg = 0
            dgnFlg = 0
            for z in consumer:
                thtmp = z.find_all('th')
                # 기종 값 추출
                if kiFlg == 0 and thtmp[0].get_text() in "기종":
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
                if clrFlg == 0 and thtmp[0].get_text() in "색상":
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
                if dgnFlg == 0 and thtmp[0].get_text() in "디자인":
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
            imgFileName = imgSrc[idx+1:]

            # 한글url 치환
            url2 = quote_plus(imgSrc)
            url2 = url2.replace("%2F","/")
            url2 = url2.replace("%3A", ":")
            url2 = url2.replace("+", "%20")

            try:
                # 상세 메인이미지 다운로드 및 썸네일
                with urlopen(url2) as f:
                    with open(saveDir + "/" + alt + "-main-" + imgFileName,'wb') as h: # w - write b - binary
                        imgFile = f.read()
                        h.write(imgFile)
            except ValueError:
                url2 = "https:" + url2
                # 상세 메인이미지 다운로드 및 썸네일
                with urlopen(url2) as f:
                    with open(saveDir + "/" + alt + "-main-" + imgFileName,'wb') as h: # w - write b - binary
                        img = f.read()
                        h.write(img)
            except Exception as e:
                makeErrorTxt("에러 상품 : " + alt)
                makeErrorTxt("알수 없는 에러 발생: " + e)

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
                        url3 = url3.replace("%2F","/")
                        url3 = url3.replace("%3A", ":")
                        url3 = url3.replace("+", "%20")
                        url3 = "https://phone2joy.com" + imgSrc + "/" + url3

                        try:
                        # 상세 메인이미지 다운로드 및 썸네일
                            with urlopen(url3) as f:
                                with open(saveDir + "/" + alt + "-detail-" + imgFileName2,'wb') as h: # w - write b - binary
                                    imgFile = f.read()
                                    h.write(imgFile)
                        except:
                            makeErrorTxt("문제 페이지 = " + data1 + " , " + data2 + " , " + data3 + " , " + str(pageidx) + "페이지" + " , 상품명 : " + alt)
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

            # csv 파일 쓰기
            if data3 != " ":
                makeCsv(saveDir + "/" + data3 + ".csv", csvData)
            elif data3 == " " and data2 != " ":
                makeCsv(saveDir  + "/" + data2 + ".csv", csvData)
            elif data3 == " " and data2 == " " and data1 != " ":
                makeCsv(saveDir  + "/" + data1 + ".csv", csvData)

# 데이터 크롤링 메소드
def urlcwraling():

    # 대구분 아이템 카운트
    items_count1 = 0
    # 중구분 이이템 카운트
    items_count2 = 0

    # 메인 페이지 읽기
    alink1 = getUrl();

    for i in alink1:

        # 초기화
        items_count2 = 0

        # 대구분 체크
        if item1[items_count1] == i.get_text():

            # 중분류 페이지 읽기
            alink2 = getUrl2(i)

            # 중분류 데이터 체크 존재할 경우
            if item2[items_count1] != "":
                for j in alink2:
                    # 중분류 페이지 읽기
                    alink3 = getUrl2(j)

                    # 소분류 데이터 체크 존재할 경우
                    if item3[items_count1] != "":
                        # 갤럭시
                        for k in alink3:
                            # 디렉토리 만들기
                            dir3 = k.find('a').get_text()[:-2]
                            dir3 = dir3.replace("/", "-").strip()
                            makeDir = item1[items_count1] + "/" + item2[items_count1][items_count2] + "/" + dir3
                            createFolder(makeDir)

                            # 소분류 페이지 읽기
                            getUrl3(k, makeDir, item1[items_count1], item2[items_count1][items_count2], dir3)
                    else:
                        # 아이폰
                        for k in alink3:
                            dir3 = k.find('a').get_text()[:-2]
                            dir3 = dir3.replace("/", "-").strip()
                            makeDir = item1[items_count1] + "/" + "/" + dir3
                            createFolder(makeDir)

                            # 소분류 페이지 읽기
                            getUrl3(k, makeDir, item1[items_count1], dir3, " ")
                        break

                    items_count2 += 1

            else:
                # Z플립
                makeDir = item1[items_count1]
                createFolder(makeDir)

                # 소분류 페이지 읽기
                getUrl3(i, makeDir, item1[items_count1], " ", " ")

            items_count1 += 1

        # 대구분 종료 체크
        if items_count1 == 3:
            break

# 데이터 크롤링
urlcwraling()

print("완료했습니다")
