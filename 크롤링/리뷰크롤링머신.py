import requests
import math
from time import sleep
import numpy as np
import pandas as pd
import time
import re
# 허용되지 않는 문자를 제거하는 함수
def remove_illegal_chars(text):
    pattern = r'[\x00-\x1F\x7F]'
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

##### 선별리스트 파일 ####
read_file = '한식_해산물리스트(최종).xlsx'
df = pd.read_excel(read_file)

for i in range(0,len(df.index)) :
  review_data = pd.DataFrame(data=[], columns=['별점', '생성일', '작성자', '방문횟수', '리뷰'])
  total_item_no = None

  # ## 식당 id 여기서 입력!
  restaurant_id = df.iloc[i]['storeCode']
  # 저장할 엑셀 파일 이름!
  save_file = f"{df.iloc[i]['업체명']}.xlsx"

  now_loop_count = 0
  total_loop_count = 10000
  total_item = 0
  headers = {
    # 찾고자 하는 식당 주소 입력
    'referer': f'https://pcmap.place.naver.com/restaurant/{restaurant_id}/home?entry=bmp&from=map&fromPanelNum=2',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
  }
  # 쿠키 입력 : 이거 없으면 네이버에서 차단함
  cookie= {'NNB':'KS66LPP2VIKGM'}

  time.sleep(1)  # 요청 사이에 1초 대기

  while True:
    if total_loop_count <= now_loop_count:
      break
    data = dict(
      operationName="getVisitorReviews",
      # 쿼리 입력
      query="query getVisitorReviews($input: VisitorReviewsInput) {\n  visitorReviews(input: $input) {\n    items {\n      id\n      rating\n      author {\n        id\n        nickname\n        from\n        imageUrl\n        borderImageUrl\n        objectId\n        url\n        review {\n          totalCount\n          imageCount\n          avgRating\n          __typename\n        }\n        theme {\n          totalCount\n          __typename\n        }\n        isFollowing\n        followerCount\n        followRequested\n        __typename\n      }\n      body\n      thumbnail\n      media {\n        type\n        thumbnail\n        thumbnailRatio\n        class\n        videoId\n        videoOriginSource\n        trailerUrl\n        __typename\n      }\n      tags\n      status\n      visitCount\n      viewCount\n      visited\n      created\n      reply {\n        editUrl\n        body\n        editedBy\n        created\n        date\n        replyTitle\n        isReported\n        isSuspended\n        __typename\n      }\n      originType\n      item {\n        name\n        code\n        options\n        __typename\n      }\n      language\n      highlightOffsets\n      apolloCacheId\n      translatedText\n      businessName\n      showBookingItemName\n      bookingItemName\n      votedKeywords {\n        code\n        iconUrl\n        iconCode\n        displayName\n        __typename\n      }\n      userIdno\n      loginIdno\n      receiptInfoUrl\n      reactionStat {\n        id\n        typeCount {\n          name\n          count\n          __typename\n        }\n        totalCount\n        __typename\n      }\n      hasViewerReacted {\n        id\n        reacted\n        __typename\n      }\n      nickname\n      showPaymentInfo\n      visitKeywords {\n        category\n        keywords\n        __typename\n      }\n      __typename\n    }\n    starDistribution {\n      score\n      count\n      __typename\n    }\n    hideProductSelectBox\n    total\n    showRecommendationSort\n    itemReviewStats {\n      score\n      count\n      itemId\n      starDistribution {\n        score\n        count\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
      variables=dict(
        id=f"{restaurant_id}",  # 입력
        input={
          "bookingBusinessId": "null",  # 입력
          "businessId": f"{restaurant_id}",  # 입력
          "businessType": "restaurant",  # 입력
          # "cidList": ["220036", "220037", "220075", "220769", "221553"],  # 입력
          "display": 20,  # 한번에 몇개의 정보를 불러올지 설정
          "getAuthorInfo": True,
          "includeContent": True,
          "includeReceiptPhotos": True,
          "isPhotoUsed": False,
          "item": "0",
          "page": now_loop_count + 1
        }
      )
    )
    resp = requests.post('https://pcmap-api.place.naver.com/graphql',
                         headers=headers,
                         json=data,
                         cookies=cookie
                         )
    data = resp.json()

    total_item = data['data']['visitorReviews']['total']
    if total_item_no is None and total_item:
      # 첫 시작 & 요청 제대로
      total_item_no = total_item
      total_loop_count = math.ceil(total_item_no / 20)  # 위의 display 숫자랑 동일하게 설정
      now_loop_count += 1

      print("첫시작 응답 잘 옴")
      print("total개수;", total_item_no)

    elif total_item_no is None and not total_item:
      # 요청 제대로 안 옴 & 첫 시작
      print(" 요청 제대로 안 옴 & 첫 시작  => 기다림")
      continue


    elif not total_item and not total_item_no:
      # 첫 시작 X & 응답 안줌 => 기다림
      sleep(3)
      print("첫 시작 X & 응답 안줌 => 기다림")
      continue

    elif total_item_no and total_item:
      # 첫 시작 X  & 응답도 잘 옴
      now_loop_count += 1
      sleep(1)
      print("응답 잘 옴 ")
    else:
      print("첫 시작 X & 응답 안줌")
      print("total item: ", total_item, "\n total_item_no:", total_item_no)
      sleep(3)
      continue

    items = data['data']['visitorReviews']['items']
    print("{}페이지 items개수 {}".format(now_loop_count, len(items)))




    # 데이터 프레임 저장
    for item in items:
      tmp = []
      # 별점
      tmp.append(str(item['rating']))
      # 생성일
      tmp.append(str(item['created']))
      # 작성자
      author = item['author']['nickname']
      tmp.append(author)
      # 방문횟수
      visitCount = item['visitCount']
      tmp.append(visitCount)
      # 리뷰내용
      # 리뷰내용 (허용되지 않는 문자 제거)
      review_body = remove_illegal_chars(item['body'])
      tmp.append(review_body)

      tmp = pd.DataFrame(data=[tmp], columns=['별점', '생성일', '작성자', '방문횟수', '리뷰',])
      review_data = pd.concat([review_data, tmp])

  #파일 이름 수정!
  review_data.to_excel(save_file, index=False)