import json
import requests
from dotenv import dotenv_values
import time
from apscheduler.schedulers.background import BackgroundScheduler

def data_receive():
    config = dotenv_values(".env")
    moviedata_token = config.get('MOVIEDATA_TOKEN')

    # API URL 및 카테고리 설정
    categories = {
        "popular": "https://api.themoviedb.org/3/movie/popular?language=ko-KR&region=KR",
        "now_playing": "https://api.themoviedb.org/3/movie/now_playing?language=ko-KR&region=KR",
        "upcoming": "https://api.themoviedb.org/3/movie/upcoming?language=ko-KR&region=KR",
    }

    headers = {
        "Authorization": f"Bearer {moviedata_token}"  # Bearer 토큰 방식 인증
    }

    # 모든 데이터를 저장할 리스트
    all_movies = []

    # API 호출 함수
    def get_movies(url, page):
        try:
            # 요청 매개변수 설정
            params = {"page": page}
            # API 요청
            response = requests.get(url, headers=headers, params=params)
            # 응답 상태 확인
            if response.status_code == 200:
                return response.json()
            else:
                print(f"페이지 {page} 요청 실패: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"페이지 {page}에서 요청 중 오류 발생: {e}")
            return None

    # 영화 데이터 수집
    def collect_movies(category_name, url):
        print(f"{category_name} 카테고리 영화 데이터를 수집 중입니다...")
        for i in range(1, 51):  # 최대 50페이지까지 수집
            movies_data = get_movies(url, i)
            if movies_data and "results" in movies_data:
                all_movies.extend(movies_data["results"])  # "results" 데이터를 리스트에 추가
            else:
                print(f"페이지 {i} 데이터 없음 또는 오류 발생.")

            # API 요청 간 딜레이 추가 (0.2초)
            time.sleep(0.2)

    # 각 카테고리의 데이터를 수집
    for category, url in categories.items():
        collect_movies(category, url)

    # 중복 제거 및 데이터 저장
    def save_unique_movies():
        if all_movies:
            with open('response.json', 'w', encoding='utf-8') as f:
                json.dump(all_movies, f, ensure_ascii=False, indent=4)
            print(f"총 {len(all_movies)}개의 영화 데이터를 저장했습니다.")

            # 중복 제거 (title 기준)
            unique_titles = {item['title']: item for item in all_movies}.values()

            with open('response.json', 'w', encoding='utf-8') as f:
                json.dump(list(unique_titles), f, ensure_ascii=False, indent=4)

            print(f"중복 제거 후 {len(unique_titles)}개의 영화 데이터를 저장했습니다.")
        else:
            print("수집된 데이터가 없습니다.")

    save_unique_movies()

def start_receive():
    scheduler = BackgroundScheduler()
    scheduler.add_job(data_receive, 'interval', days=7)
    scheduler.start()
    print("데이터 수집 중")
