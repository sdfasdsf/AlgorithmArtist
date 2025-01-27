# import json
# import requests
# from dotenv import dotenv_values
# import time



# config = dotenv_values(".env")
# moviedata_token = config.get('MOVIEDATA_TOKEN')

# # API URL 및 카테고리 설정
# categories = {
#     "popular": "https://api.themoviedb.org/3/movie/popular?language=ko-KR&region=KR",
#     "now_playing": "https://api.themoviedb.org/3/movie/now_playing?language=ko-KR&region=KR",
#     "upcoming": "https://api.themoviedb.org/3/movie/upcoming?language=ko-KR&region=KR",
# }

# headers = {
#     "Authorization": f"Bearer {moviedata_token}"  # Bearer 토큰 방식 인증
# }

# # 모든 데이터를 저장할 리스트
# all_movies = []

# # API 호출 함수
# def get_movies(url, page):
#     try:
#         # 요청 매개변수 설정
#         params = {"page": page}
#         # API 요청
#         response = requests.get(url, headers=headers, params=params)
#         # 응답 상태 확인
#         if response.status_code == 200:
#             return response.json()
#         else:
#             print(f"페이지 {page} 요청 실패: {response.status_code}")
#             return None
#     except requests.exceptions.RequestException as e:
#         print(f"페이지 {page}에서 요청 중 오류 발생: {e}")
#         return None

# # 영화 데이터 수집
# def collect_movies(category_name, url):
#     print(f"{category_name} 카테고리 영화 데이터를 수집 중입니다...")
#     for i in range(1, 51):  # 최대 50페이지까지 수집
#         movies_data = get_movies(url, i)
#         if movies_data and "results" in movies_data:
#             all_movies.extend(movies_data["results"])  # "results" 데이터를 리스트에 추가
#         else:
#             print(f"페이지 {i} 데이터 없음 또는 오류 발생.")

#         # API 요청 간 딜레이 추가 (0.2초)
#         time.sleep(0.2)

# # 각 카테고리의 데이터를 수집
# for category, url in categories.items():
#     collect_movies(category, url)

# # 중복 제거 및 데이터 저장
# def save_unique_movies():
#     if all_movies:
#         with open('response.json', 'w', encoding='utf-8') as f:
#             json.dump(all_movies, f, ensure_ascii=False, indent=4)
#         print(f"총 {len(all_movies)}개의 영화 데이터를 저장했습니다.")

#         # 중복 제거 (title 기준)
#         unique_titles = {item['title']: item for item in all_movies}.values()

#         with open('response.json', 'w', encoding='utf-8') as f:
#             json.dump(list(unique_titles), f, ensure_ascii=False, indent=4)

#         print(f"중복 제거 후 {len(unique_titles)}개의 영화 데이터를 저장했습니다.")
#     else:
#         print("수집된 데이터가 없습니다.")

# save_unique_movies()

# import requests
# import json
# from datetime import datetime

# # API 키와 기본 URL 설정
# API_KEY = '528be68f87cd17fbb63cd610049e189b'
# BASE_URL = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json'

# # 모든 데이터를 저장할 리스트
# all_movies = []

# # 현재 연도 가져오기
# year = datetime.now().year

# # JSON 파일에서 기존 데이터를 불러오기
# try:
#     with open('movies.json', 'r', encoding='utf-8') as json_file:
#         existing_movies = json.load(json_file)
#         print(f"기존 데이터 {len(existing_movies)}개를 불러왔습니다.")
# except (FileNotFoundError, json.JSONDecodeError):
#     existing_movies = []
#     print("기존 데이터가 없거나 JSON 파일이 손상되었습니다. 새로운 파일을 생성합니다.")

# # 기존 데이터를 dict로 변환 (movieCd 기준)
# existing_movie_dict = {movie['movieCd']: movie for movie in existing_movies}

# # 새로운 데이터 수집
# for i in range(1, 20):
#     # 요청 파라미터 설정
#     params = {
#         'key': API_KEY,
#         'openStartDt': '2000',
#         'openEndDt': str(year),
#         'curPage': i,
#         'itemPerPage': 100,
#     }

#     # API 요청
#     response = requests.get(BASE_URL, params=params)

#     # 응답 확인
#     if response.status_code == 200:
#         data = response.json()
#         movie_list = data.get('movieListResult', {}).get('movieList', [])
#         all_movies.extend(movie_list)
#         print(f"페이지 {i} 데이터 수집 완료 ({len(movie_list)}개 영화)")
#     else:
#         print(f"페이지 {i} 요청 실패: {response.status_code}, {response.text}")

# # 새로운 데이터 dict로 변환 (movieCd 기준)
# new_movie_dict = {movie['movieCd']: movie for movie in all_movies}

# # 기존 데이터와 새로운 데이터를 병합
# existing_movie_dict.update(new_movie_dict)

# # 최종 데이터 리스트로 변환
# final_movie_list = list(existing_movie_dict.values())

# # JSON 파일 저장
# with open('movies.json', 'w', encoding='utf-8') as json_file:
#     json.dump(final_movie_list, json_file, ensure_ascii=False, indent=4)
# print(f"총 {len(final_movie_list)}개의 영화 데이터가 'movies.json' 파일에 저장되었습니다.")

# import requests
# import json
# import requests
# from dotenv import dotenv_values
# import time
# from AIanswer import load_movies_from_file


# config = dotenv_values(".env")
# moviedata_token = config.get('MOVIEDATA_TOKEN')

# movie = load_movies_from_file("movies.json")
# print(len(movie))
# print(movie[2]["movieNmEn"])
# search_query = movie[2]["movieNmEn"]
# url = f"https://api.themoviedb.org/3/search/movie?include_adult=false&language=ko-KR&page=1&query={search_query}"

# headers = {
#     "Authorization": f"Bearer {moviedata_token}"  # Bearer 토큰 방식 인증
# }


# response = requests.get(url, headers=headers)

# if response.status_code == 200:
#     data = response.json()  # JSON 형식으로 응답 파싱
#     results = data.get("results", [])  # 결과 목록 가져오기

#     if results:  # 결과가 존재하면
#         top_result = results[0]  # 첫 번째 결과 가져오기
#         print(json.dumps(top_result, ensure_ascii=False, indent=4))  # 첫 번째 결과를 보기 좋게 출력
#     else:
#         print("검색 결과가 없습니다.")
# else:
#     print(f"API 요청 실패: {response.status_code}, {response.text}")


# import requests
# import json
# from AIanswer import load_movies_from_file
# import time

# # API 정보
# API_KEY = '528be68f87cd17fbb63cd610049e189b'  # 자신의 API 키 입력
# BASE_URL = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json'

# movies = load_movies_from_file("movies.json")

# all_movies = []

# for movie in movies:
    
#     movieCd = movie.get("movieCd")
#     # 요청 파라미터
#     params = {
#         'key': API_KEY,       # API 키
#         'movieCd': movieCd # 영화 코드
#     }

#     # API 호출
#     response = requests.get(BASE_URL, params=params)

#     # 응답 처리
#     if response.status_code == 200:
#         try:
#             data = response.json()  # JSON 응답 파싱

#             # 영화 상세 정보 추출
#             movie_info = data.get("movieInfoResult", {}).get("movieInfo", {})
#             if movie_info:
#                 print("\n[영화 상세 정보]")
#                 print(json.dumps(movie_info, ensure_ascii=False, indent=4))
#             else:
#                 print("영화 상세 정보를 찾을 수 없습니다.")
#             all_movies.append(movie_info)
#             time.sleep(0.5)
#         except json.JSONDecodeError as e:
#             print(f"JSON 디코딩 오류: {e}")
            

#     else:
#         print(f"API 요청 실패: {response.status_code}")
#         print(response.text)

# if all_movies:
#     with open('movie2.json', 'w', encoding='utf-8') as f:
#         json.dump(all_movies, f, ensure_ascii=False, indent=4)
#     print(f"총 {len(all_movies)}개의 영화 데이터를 저장했습니다.")

#     # 중복 제거 (title 기준)
#     unique_titles = {item['movieCd']: item for item in all_movies}.values()

#     with open('movie2.json', 'w', encoding='utf-8') as f:
#         json.dump(list(unique_titles), f, ensure_ascii=False, indent=4)

#     print(f"중복 제거 후 {len(unique_titles)}개의 영화 데이터를 저장했습니다.")
# else:
#     print("수집된 데이터가 없습니다.")


import requests

# 조회할 영화 ID
movie_id = 27205  # Inception의 ID

# 요청 URL
url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=ko-KR"

# 요청 헤더
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwNTlhZmFlZTVmNTBmMTQxNzk2NTcyMjVkMTYzNGI1MCIsIm5iZiI6MTczNjkwMTc3Ny4wOTEsInN1YiI6IjY3ODcwNDkxYmQ3OTNjMDM1NDRmMTVhZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.x_BLnc_T-WkxuE_3ECOtbzxNH6OVjz7kXR1eNB2vS3w"
}

# API 요청
response = requests.get(url, headers=headers)

# 결과 출력
if response.status_code == 200:
    movie_data = response.json()  # JSON 응답을 파이썬 딕셔너리로 변환
    print(movie_data)
    print(f"제목: {movie_data['title']}")
    print(f"개봉일: {movie_data['release_date']}")
    print(f"평점: {movie_data['vote_average']}")
    print(f"개요: {movie_data['overview']}")
else:
    print(f"에러 발생: {response.status_code}")
    print(response.text)