# DisasterKok 테스트 & 개선 이력

> 고도화 전 베이스라인 확보, 버그 수정 이력, 기능 테스트 방법을 기록한 문서.

---

## 목차

1. [로컬 환경 실행](#1-로컬-환경-실행)
2. [기능 테스트 (API)](#2-기능-테스트-api)
3. [부하 테스트](#3-부하-테스트)
4. [버그 수정 이력](#4-버그-수정-이력)
5. [코드 개선 대기 목록](#5-코드-개선-대기-목록)

---

## 1. 로컬 환경 실행

### 1.1 사전 준비

```bash
# .env 파일 생성 (sample_env 참고)
cp sample_env .env
# 필요한 값 채우기: SECRET_KEY, DB 설정 등

# Docker Desktop 실행 확인
docker info
```

### 1.2 서버 시작

```bash
# 빌드 + 백그라운드 실행
docker-compose up -d --build

# DB 마이그레이션
docker-compose exec gunicorn python manage.py migrate

# 로그 확인
docker-compose logs -f gunicorn
docker-compose logs -f daphne
```

### 1.3 테스트 데이터 생성

```bash
# 테스트 유저 2명 생성
docker-compose exec gunicorn python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_user(username='testuser', password='testpass123', email='test@test.com')
User.objects.create_user(username='testuser2', password='testpass123', email='test2@test.com')
print('완료')
"
```

### 1.4 서버 종료

```bash
docker-compose down          # 컨테이너만 종료 (데이터 유지)
docker-compose down -v       # 컨테이너 + 볼륨 삭제 (데이터 초기화)
```

### 1.5 코드 수정 후 반영

```bash
# 파이썬 코드만 수정한 경우 (Dockerfile 변경 없음)
docker-compose restart gunicorn daphne

# Dockerfile / requirements.txt 수정한 경우
docker-compose up -d --build
```

---

## 2. 기능 테스트 (API)

> Swagger UI: `http://localhost:80/`
> 아래는 curl 기반 전체 기능 검증 스크립트.

### 2.1 한 번에 전체 테스트 실행

```bash
bash test_all_apis.sh
```

스크립트 없이 직접 실행하려면 아래 2.2 ~ 2.6 순서대로.

---

### 2.2 인증 API

```bash
# 회원가입
curl -s -X POST http://localhost:80/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123", "email": "test@test.com"}' \
  | python3 -m json.tool

# 로그인 (토큰 저장)
TOKEN_DATA=$(curl -s -X POST http://localhost:80/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}')
ACCESS_TOKEN=$(echo $TOKEN_DATA | python3 -c "import sys,json; print(json.load(sys.stdin)['token']['access'])")

# 닉네임 중복 확인
curl -s -X POST http://localhost:80/users/nickname/ \
  -H "Content-Type: application/json" \
  -d '{"nickname": "testuser"}' | python3 -m json.tool

# 로그아웃 (쿠키 기반 — 로그인 시 set-cookie 된 refresh 쿠키 사용)
COOKIE_JAR=$(mktemp)
curl -s -X POST http://localhost:80/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}' \
  -c "$COOKIE_JAR" > /dev/null
curl -s -X POST http://localhost:80/users/logout/ \
  -b "$COOKIE_JAR" | python3 -m json.tool
rm "$COOKIE_JAR"
```

---

### 2.3 게시글 API

```bash
ACCESS_TOKEN=<위에서 발급받은 토큰>

# 게시글 작성 (이미지 없음)
curl -s -X POST http://localhost:80/posts/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "title=테스트 게시글" \
  -F "content=테스트 내용" \
  -F "write_tags=재난" \
  -F "write_tags=테스트" | python3 -m json.tool

# 게시글 작성 (이미지 포함)
curl -s -X POST http://localhost:80/posts/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "title=이미지 게시글" \
  -F "content=이미지 포함 테스트" \
  -F "image=@/path/to/image.jpg" | python3 -m json.tool

# 게시글 목록 (페이지네이션)
curl -s "http://localhost:80/posts/" | python3 -m json.tool
curl -s "http://localhost:80/posts/?page=2" | python3 -m json.tool

# 게시글 검색
curl -s "http://localhost:80/posts/?search_title=재난" | python3 -m json.tool
curl -s "http://localhost:80/posts/?search_all=테스트" | python3 -m json.tool

# 게시글 상세 (조회수 증가 확인)
curl -s "http://localhost:80/posts/1/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# 홈 Top6
curl -s http://localhost:80/posts/home/ | python3 -m json.tool

# 좋아요
curl -s -X POST http://localhost:80/posts/1/likes/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# 게시글 삭제
curl -s -X DELETE http://localhost:80/posts/1/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" -w "HTTP Status: %{http_code}\n"
```

---

### 2.4 지역 API

```bash
ACCESS_TOKEN=<토큰>

# 지역 추가
curl -s -X POST http://localhost:80/regions/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "서울특별시", "address": "서울"}' | python3 -m json.tool

# 지역 목록 (exist 필드: 지역 등록 여부)
curl -s http://localhost:80/regions/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# 지역 ON/OFF 토글
curl -s -X POST http://localhost:80/regions/1/onoff/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# 기본 지역 설정
curl -s -X POST http://localhost:80/regions/1/default/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# 지역 삭제
curl -s -X DELETE http://localhost:80/regions/1/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" -w "HTTP Status: %{http_code}\n"
```

---

### 2.5 알림 API

> 알림은 **다른 유저가 내 게시글에 좋아요**를 눌러야 생성됨 (Django Signal).

```bash
ACCESS_TOKEN_1=<testuser 토큰>
ACCESS_TOKEN_2=<testuser2 토큰>

# testuser가 게시글 작성
curl -s -X POST http://localhost:80/posts/ \
  -H "Authorization: Bearer $ACCESS_TOKEN_1" \
  -F "title=알림 테스트 게시글" \
  -F "content=내용" | python3 -m json.tool

# testuser2가 좋아요 → testuser에게 알림 생성
curl -s -X POST http://localhost:80/posts/1/likes/ \
  -H "Authorization: Bearer $ACCESS_TOKEN_2" | python3 -m json.tool

# testuser 알림 목록 확인
curl -s http://localhost:80/notifications/ \
  -H "Authorization: Bearer $ACCESS_TOKEN_1" | python3 -m json.tool

# 미읽음 개수
curl -s http://localhost:80/notifications/unread-count/ \
  -H "Authorization: Bearer $ACCESS_TOKEN_1" | python3 -m json.tool

# 알림 읽음 처리
curl -s -X PATCH http://localhost:80/notifications/1/read/ \
  -H "Authorization: Bearer $ACCESS_TOKEN_1" | python3 -m json.tool

# 전체 읽음 처리
curl -s -X PATCH http://localhost:80/notifications/read-all/ \
  -H "Authorization: Bearer $ACCESS_TOKEN_1" | python3 -m json.tool

# 알림 삭제
curl -s -X DELETE http://localhost:80/notifications/1/ \
  -H "Authorization: Bearer $ACCESS_TOKEN_1" -w "HTTP Status: %{http_code}\n"
```

---

### 2.6 WebSocket 테스트

```bash
# wscat 설치 (없으면)
npm install -g wscat

# WebSocket 연결 (JWT 토큰 필요)
wscat -c "ws://localhost:80/ws/notifications/?token=$ACCESS_TOKEN"

# 연결 후 다른 터미널에서 좋아요 → 실시간 메시지 수신 확인
```

---

### 2.7 비정상 케이스 확인

```bash
# 존재하지 않는 지역 ON/OFF → 404 응답 확인
curl -s -X POST http://localhost:80/regions/99999/onoff/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# 인증 없이 보호된 API 접근 → 401 확인
curl -s http://localhost:80/notifications/ | python3 -m json.tool

# 잘못된 토큰 → 401 확인
curl -s http://localhost:80/notifications/ \
  -H "Authorization: Bearer invalid_token" | python3 -m json.tool
```

---

## 3. 부하 테스트

> 상세 시나리오는 `LOAD_TEST_PORTFOLIO.md` 참고.
> 여기서는 실행 방법만 기록.

### 3.1 k6 설치

```bash
# macOS
brew install k6

# Docker
docker pull grafana/k6
```

### 3.2 베이스라인 측정 스크립트

`load_tests/baseline.js` 생성 후 실행:

```javascript
// load_tests/baseline.js
import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },   // 워밍업
    { duration: '1m',  target: 100 },  // 평상시
    { duration: '30s', target: 500 },  // 지역 재난
    { duration: '1m',  target: 500 },  // 유지
    { duration: '30s', target: 0 },    // 종료
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95%ile < 500ms
    http_req_failed: ['rate<0.005'],   // 에러율 < 0.5%
  },
};

const BASE_URL = 'http://localhost:80';

export function setup() {
  const res = http.post(`${BASE_URL}/users/login/`,
    JSON.stringify({ username: 'testuser', password: 'testpass123' }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  return { token: res.json('token.access') };
}

export default function (data) {
  const headers = { Authorization: `Bearer ${data.token}` };
  const rand = Math.random();

  if (rand < 0.40) {
    // 게시글 목록 (40%)
    const r = http.get(`${BASE_URL}/posts/`, { headers });
    check(r, { 'posts list 200': (res) => res.status === 200 });
  } else if (rand < 0.65) {
    // 게시글 상세 (25%)
    const r = http.get(`${BASE_URL}/posts/1/`, { headers });
    check(r, { 'post detail 200': (res) => res.status === 200 });
  } else if (rand < 0.80) {
    // 좋아요 (15%)
    const r = http.post(`${BASE_URL}/posts/1/likes/`, null, { headers });
    check(r, { 'like 200': (res) => res.status === 200 });
  } else if (rand < 0.90) {
    // 알림 목록 (10%)
    const r = http.get(`${BASE_URL}/notifications/`, { headers });
    check(r, { 'notifications 200': (res) => res.status === 200 });
  } else {
    // 미읽음 개수 (10%)
    const r = http.get(`${BASE_URL}/notifications/unread-count/`, { headers });
    check(r, { 'unread count 200': (res) => res.status === 200 });
  }

  sleep(1);
}
```

```bash
# 실행
k6 run load_tests/baseline.js

# 결과를 JSON으로 저장
k6 run --out json=load_tests/results/baseline_$(date +%Y%m%d_%H%M%S).json load_tests/baseline.js
```

### 3.3 결과 기록 양식

테스트 후 아래 표를 채워서 커밋:

| 항목 | 베이스라인 | 코드 최적화 후 | 인프라 고도화 후 |
|------|-----------|--------------|---------------|
| 평균 응답시간 | - | - | - |
| p95 응답시간 | - | - | - |
| 에러율 | - | - | - |
| 최대 동시접속 | - | - | - |
| DB 쿼리 수 (게시글 목록) | - | - | - |

### 3.4 DB 쿼리 수 측정 (Django Debug Toolbar)

```bash
# base.py에 debug toolbar 설치 확인 후
pip install django-debug-toolbar

# 브라우저에서 http://localhost:80/posts/ 접속
# 오른쪽 패널 → SQL 탭 → 쿼리 수 기록
```

---

## 4. 버그 수정 이력

> **수정일**: 2026-03-23
> **수정 전 상태**: 모든 기능 테스트 통과 못함

### BUG-01. 이미지 다중 업로드 불가 (기능 버그)

- **파일**: `post/views/postListAPIView.py`
- **원인**: `request.FILES.get('image')` 는 단일 파일만 반환
- **수정**: `request.FILES.getlist('image')`

```python
# Before
img_set = request.FILES.get('image', [])
img_set = list(img_set) if img_set else []

# After
img_set = request.FILES.getlist('image')
```

---

### BUG-02. 태그 글자 단위로 쪼개지는 버그 (기능 버그)

- **파일**: `post/views/postListAPIView.py`
- **원인**: `request.data.get('write_tags')` 가 multipart에서 마지막 값 하나만 반환 → 문자열 반복 시 글자 단위로 이터레이션
- **수정**: `request.data.getlist('write_tags')`
- **재현**: `write_tags=재난&write_tags=테스트` 전송 시 태그가 ["테","스","트"]로 저장됨

```python
# Before
tag_set = request.data.get('write_tags', [])

# After
tag_set = request.data.getlist('write_tags', [])
```

---

### BUG-03. 네이버 로그인 로직 역전 (기능 버그)

- **파일**: `user/views/naverLoginUserView.py`
- **원인**: `naverId` 가 이미 존재하는 경우(기존 유저 로그인 시도)에 새 유저 생성을 시도 → unique 제약 위반으로 500 에러
- **수정**: naverId 존재 시 로그인, 미존재 시 신규 가입으로 분기 수정

```python
# Before (naverId 있는 경우에 새 유저 생성 시도 → 에러)
if User.objects.filter(naverId=naverId).exists():
    if User.objects.filter(email=email).exists():
        return Response({"message": "이미 가입된 이메일..."}, ...)
    User(naverId=naverId, ...).save()  # unique 충돌!

# After
if User.objects.filter(naverId=naverId).exists():
    user = User.objects.get(naverId=naverId)  # 로그인
    ...
else:
    if User.objects.filter(email=email).exists():
        return Response({"message": "이미 가입된 이메일..."}, ...)
    user = User.objects.create(naverId=naverId, ...)  # 신규 가입
```

---

### BUG-04. 소셜 로그인 외부 API 호출 예외 처리 없음 (보안/안정성)

- **파일**: `user/views/kakaoLoginUserView.py`, `naverLoginUserView.py`, `googleLoginUserView.py`
- **원인**: `requests.post()`, `requests.get()` 에 try-except 없음
- **영향**: 카카오/네이버/구글 서버 장애 시 Django 500 에러 그대로 노출
- **수정**: 각 외부 API 호출에 `requests.RequestException` 처리 추가, 503 반환

```python
# After
try:
    token_request = requests.post(url, data=data)
    token_json = token_request.json()
except requests.RequestException:
    return Response({"message": "카카오 토큰 요청에 실패했습니다."}, status=503)
```

---

### BUG-05. 지역 API 존재하지 않는 ID 요청 시 500 에러 (보안/안정성)

- **파일**: `region/views/regiononoffAPIView.py`, `regiondefaultAPIView.py`
- **원인**: `Region.objects.get(id=region_id)` 에서 DoesNotExist 미처리 → 500 Internal Server Error 반환
- **수정**: `get_object_or_404()` 로 교체 → 404 반환

```python
# Before
region = Region.objects.get(id=region_id)  # 없으면 500

# After
region = get_object_or_404(Region, id=region_id)  # 없으면 404
```

---

### BUG-06. 닉네임 중복 확인 API URL 미등록 (기능 버그)

- **파일**: `user/views/__init__.py`, `user/urls.py`
- **원인**: `DuplicateNickameAPIView` 클래스가 `__init__.py` import 및 `urls.py` 등록 누락
- **영향**: `/users/nickname/` 엔드포인트가 404 반환
- **수정**: 두 파일에 각각 추가

---

## 5. 코드 개선 대기 목록

> **베이스라인 측정 후 순서대로 진행. 수정 전후 수치를 반드시 기록할 것.**

### Phase 2 — 성능 개선 (측정 후 진행)

| # | 파일 | 문제 | 예상 효과 |
|---|------|------|---------|
| P2-01 | `region/views/regiondefaultAPIView.py` | N+1 UPDATE (지역 수만큼 쿼리 발생) | `bulk_update()` 1회로 감소 |
| P2-02 | `user/views/kakaoLoginUserView.py` | `exists()` + `get()` 이중 쿼리 → `get_or_create()` | DB 쿼리 1회 감소 |
| P2-03 | `user/models/user.py` | `googleId`, `kakaoId`, `naverId` 인덱스 미명시 | 소셜 로그인 조회 속도 향상 |
| P2-04 | `user/models/user.py` | `nickname` 인덱스 없음 | 중복 확인 쿼리 속도 향상 |
| P2-05 | `notification/models/notificationMessage.py` | `is_read` 인덱스 없음 | 알림 목록/미읽음 쿼리 속도 향상 |
| P2-06 | `region/views/regionListCreateAPIView.py` | `get_queryset()`과 `perform_create()` 에서 `get_or_create()` 중복 호출 | 쿼리 1회 감소 |

### Phase 3 — 코드 품질 (인프라 작업 병행 가능)

| # | 파일 | 문제 |
|---|------|------|
| P3-01 | `post/serializers/postSerializer.py` | `like`, `view` 필드에 불필요한 SerializerMethodField |
| P3-02 | `post/views/postListAPIView.py` | 이미지/태그 생성 로직이 View에 있음 → Serializer `create()`로 이동 |
| P3-03 | `user/views/naverLoginUserView.py` | 동일 유저 생성 코드 중복 (정리됐으나 전체 구조 재검토) |
| P3-04 | `user/views/loginAPIView.py` | `if regions:` → `if regions.exists()` (불필요한 전체 로드) |
| P3-05 | `user/views/nicknameduplicateAPIView.py` | 클래스명 오타: `DuplicateNickame` → `DuplicateNickname` |
| P3-06 | `user/models/user.py` | 주석 처리된 죽은 코드 정리 (91-93, 106-110번 줄) |
