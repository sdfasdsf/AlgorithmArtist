import json
import requests
from dotenv import dotenv_values
import time

config = dotenv_values(".env")
moviedata_token = config.get('MOVIEDATA_TOKEN')

moviedata_url = "https://api.themoviedb.org/3/trending/movie/day?language=ko-KR"
headers = {"Authorization": f"Bearer {moviedata_token}"} # Bearer 토큰 방식으로 API 키 전달

# moviedata_url = "https://api.themoviedb.org/3"
# search_movie_endpoint = f"{moviedata_url}/search/movie"

# 모든 데이터를 저장할 리스트
all_movies = []
# 외부 API 호출 함수
def get_movies(page):
    try:
        # 요청 매개변수 설정
        params = {"page": page, "language": "ko-KR"}
        # API 요청
        response = requests.get(moviedata_url, headers=headers, params=params)
        # 응답 상태 확인
        if response.status_code == 200:
            return response.json()
        else:
            print(f"페이지 {page} 요청 실패: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"페이지 {page}에서 요청 중 오류 발생: {e}")
        return None
        
for i in range(1,51):
    movies_data = get_movies(i)
    if movies_data and "results" in movies_data:
        all_movies.extend(movies_data["results"])  # "results" 데이터를 리스트에 추가
    else:
        print(f"페이지 {i} 데이터 없음 또는 오류 발생.")
    
    # API 요청 간 딜레이 추가 (0.2초)
    time.sleep(0.2)
if all_movies:
    with open('response.json', 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=4)
    print(f"총 {len(all_movies)}개의 인기영화 데이터를 저장했습니다.")
else:
    print("수집된 데이터가 없습니다.")

moviedata_url = "https://api.themoviedb.org/3/movie/now_playing"
headers = {"Authorization": f"Bearer {moviedata_token}"} # Bearer 토큰 방식으로 API 키 전달

for i in range(1,51):
    movies_data = get_movies(i)
    if movies_data and "results" in movies_data:
        all_movies.extend(movies_data["results"])  # "results" 데이터를 리스트에 추가
    else:
        print(f"페이지 {i} 데이터 없음 또는 오류 발생.")
    
    # API 요청 간 딜레이 추가 (0.2초)
    time.sleep(0.2)
if all_movies:
    with open('response.json', 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=4)
    print(f"총 {len(all_movies)}개의 상영 중인 영화 데이터를 저장했습니다.")
else:
    print("수집된 데이터가 없습니다.")


url = "https://api.themoviedb.org/3/movie/upcoming"
headers = {
    "Authorization": f"Bearer {moviedata_token}"  # Bearer Token 방식 인증
}

for i in range(1,51):
    movies_data = get_movies(i)
    if movies_data and "results" in movies_data:
        all_movies.extend(movies_data["results"])  # "results" 데이터를 리스트에 추가
    else:
        print(f"페이지 {i} 데이터 없음 또는 오류 발생.")
    
    # API 요청 간 딜레이 추가 (0.2초)
    time.sleep(0.2)
if all_movies:
    with open('response.json', 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=4)
    print(f"총 {len(all_movies)}개의 개봉 예정인 영화 데이터를 저장했습니다.")
else:
    print("수집된 데이터가 없습니다.")


url = "https://api.themoviedb.org/3/movie/upcoming"
headers = {
    "Authorization": f"Bearer {moviedata_token}"  # Bearer Token 방식 인증
}