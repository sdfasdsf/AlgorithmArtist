
# 🎥Cinema Web & Chatbot : TMOVING🎥
-----
## 목차

1.  [프로젝트 개요](#1-프로젝트-개요)
2.  [팀원 구성](#2-팀원-구성)
3.  [프로젝트 일정](#3-프로젝트-일정)
4.  [기능 소개](#4-기능-소개)
5.  [기술적 의사결정 및 주요기능 소개](#5-기술적-의사결정-및-주요기능-소개)
6.  [트러블 슈팅](#6-트러블-슈팅)
7.  [사용 기술](#7-사용-기술)
8.  [성과 및 회고](#8-성과-및-회고)
-----
## **1. 프로젝트 개요** 

현대인들은 방대한 영화 정보 속에서 자신에게 맞는 영화를 찾기 위해 많은 시간을 소비하거나, 원하는 정보를 얻기 위해 여러 플랫폼을 헤매는 경우가 많습니다. 이러한 불편함을 해소하고자, 최신 영화와 인기 있는 영화에 대한 정보를 손쉽게 제공하는 챗봇을 기획하게 되었습니다.

-----

## **2. 팀원 구성** 

| 역할| 이름 | 주요 업무 |
| --- | --- | --- |
| 리더 | 인정배 | 백엔드 구현(accounts), 프론트엔드 구현(accounts), 서비스 배포 |
| 부리더 | 한상민 | 백엔드 구현(articles, AI 및 전체적인 부분 다듬기), 프론트엔드 구현(articles, AI 및 전체적인 부분 다듬기) |
| 서기 | 오승진 | 프론트엔드 구현(UI 기본 틀 구현), 문서 작성 |


-----

## **3. 프로젝트 일정**

| 날짜 | 업무 |
| --- | --- |
| 12.30 ~ 01.03 | 프로젝트 기획 |
| 01.06 ~ 01.10 | 백엔드 구현(accounts, articles) |
| 01.13 ~ 01.21 | 백엔드 구현(AI) |
| 01.22 ~ 01.30 | 프론트엔드 구현 및 배포|
| 01.31 | 발표 |

-----
## **4. 기능 소개**

- 메인 홈페이지에서 최근 영화 목록, 인기 영화 목록 보기 기능
- 메인 홈페이지에서 영화 포스터 클릭 시 영화 상세 정보 조회 기능
- 회원 가입, 로그인 페이지에서 회원 가입 기능, 로그인 기능
- 유저 프로필 페이지, 프로필 수정 기능
- 프로필 수정 페이지에서 유저 프로필 사진 변경 기능, 비밀번호 변경 기능, 닉네임 변경 기능
- 게시글 목록, 게시글 수정 페이지, 게시글 상세 조회 기능
- 영화 리뷰 페이지에서 리뷰 조회 기능


-----
## **5. 기술적 의사결정** 

<details>
<summary><strong>🖥️ 프론트엔드</strong></summary>


#### Django Template

가져온 데이터를 기반으로 동적으로 HTML 콘텐츠를 생성할 수 있고 API와 웹 페이지를 동시에 제공할 수 있어, 동일한 뷰에서 RESTful API 응답과 HTML 페이지를 모두 처리할 수 있다는 장점이 있어 선택했습니다.

#### css

다양한 디자인을 적용하여 사용자 경험을 향상시킬 수 있도록 웹 페이지를 스타일링 하기 위해 선택했습니다.

#### JavaScript

API에서 가져온 리뷰 목록을 웹 페이지에 표시를 하는 등 서버로부터 데이터를 비동기적으로 가져와 HTML 요소에 동적으로 표시하기 위해 선택했습니다.





</details>

<details>
<summary><strong>📀 백엔드</strong></summary>


#### Django-rest-framework

직관적인 API 설계와 다양한 인증/권한 관리 기능을 제공하고 RESTful API를 쉽게 구축할 수 있어 선택했습니다.

#### rest_framework_simplejwt

토큰 기반 인증으로, 세션 관리 없이도 사용자 인증을 간편하게 처리할 수 있어 로그인하여 로그인한 사용자만 동작이 가능하게 하기 위해 선택했습니다.

#### rest_framework_simplejwt.token_blacklist

보안성을 높이고, 사용자 로그아웃 후에도 안전하게 인증을 관리할 수 있다는 장점이 있어  JWT 토큰의 블랙리스트 기능을 사용하여 로그아웃 시 토큰을 무효화하기 위해 선택했습니다.

</details>

<details>
<summary><strong>🔑API</strong></summary>


#### TMDB

해외 영화 및 국내 영화 모두 줄거리와 평점 등도 함께 제공하여 선택하였습니다.

#### OpenAI

가져온 정보를 가지고 최신 영화 및 인기 영화를 추천해주기 위해 선택하였습니다.
</details>

-----
## **6. 트러블 슈팅**

<details>
<summary><strong>프로필 오류</strong></summary>

### 문제
1. AssertionError: The field 'phone_number' was declared on serializer UserProfileSerializer, but has not been included in the 'fields' option.

### 해결 방법
1. 이 오류를 해결하기 위해 `UserProfileSerializer`의 `fields` 옵션에 `phone_number` 필드를 추가하였습니다.
</details>

<details>
<summary><strong>댓글 좋아요 오류</strong></summary>



### 문제
- TypeError: CommentLike.post() got an unexpected keyword argument 'article_pk'
  
  
### 해결 방법
1. 이 오류를 해결하기 위해 `Comment` 객체를 가져오는 코드에서 `article_pk` 변수를 추가하였습니다. 

변경된 코드는 다음과 같습니다:

```python
comment = Comment.objects.get(id=comment_pk, article_id=article_pk)
```

</details>

<details>
<summary><strong>로그아웃 오류</strong></summary>

### 문제
- rest_framework.request.WrappedAttributeError: 'IsAuthenticated' object has no attribute 'authenticate'

### 해결 방법
이 오류를 해결하기 위해 다음 두 가지를 적용하였습니다:

1. `@authentication_classes([JWTAuthentication])`를 사용하여 JWT 인증을 명시적으로 설정하였습니다.
2. `BLACKLIST_AFTER_ROTATION` 설정을 `True`로 변경하여 토큰 회전 후 블랙리스트에 추가하도록 하였습니다.

</details>

<details>
<summary><strong>게시글 좋아요 오류</strong></summary>

### 문제
- rest_framework.request.WrappedAttributeError: 'IsAuthenticated' object has no attribute 'authenticate'

### 해결 방법
1. 이 오류는 `fields` 옵션에 `Favorite_articles` 필드가 포함되지 않았기 때문에 발생하는 문제입니다. 이를 해결하기 위해 `UserProfileSerializer`의 `fields` 옵션에 `Favorite_articles` 필드를 추가하였습니다.

</details>

-----

## **7\. 사용 기술** 

🖥️ 프론트엔드

- CSS
- JavaScript
- HTML
- Django 템플릿

📀 백엔드

- Python
- Django
- Django-rest-framework
- rest_framework_simplejwt
- rest_framework_simplejwt.token_blacklist

⚙️ 버전관리
- Git

💬 협업도구
- GitHub
- Slack
- Notion

📡 배포
- CloudType
-----
## **8\. 성과 및 회고** 

-   잘된 점
    -   외부 API를 사용하여 영화 정보를 가져오고 박스오피스 순위 및 정보를 얻을 수 있어 좋음
    -   AI 챗봇한테 영화를 추천 받을 수 있어 편리함을 느낄 수 있음
    -   리뷰를 작성하여 해당 영화의 평가가 어떤지 확인 할 수 있음
-   아쉬운 점
    -   RAG 챗봇을 구현했지만 할루시네이션 때문에 응답이 아쉬운 부분이 있음
    -   정보 제공이 다양하지 않아 아쉬운 부분이 있음
-    향후 계획
    -   한국어만 아닌, 다국어 지원 기능 구현
    -   원하는 정보의 영화도 찾을 수 있도록 기능 구현
    -   리뷰 작성한 것도 챗봇이 학습하여 더욱 성능이 좋아지도록 구현
    -   챗봇의 답변에 관련해서 텍스트를 음성으로 입ㆍ출력기능 구현
