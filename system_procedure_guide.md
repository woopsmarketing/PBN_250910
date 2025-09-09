# PBN 링크 빌딩 시스템 절차 가이드

## 🎯 전체 시스템 구조

```
PBN 사이트들 → 크롤링 → 데이터 저장 → 임베딩 생성 → 유사도 검색 → 링크 삽입
     (34개)      ↓        ↓           ↓           ↓           ↓
                웹페이지   SQLite    FAISS Index   검색결과    최종콘텐츠
```

## 📋 단계별 상세 절차

### 1단계: PBN 콘텐츠 크롤링 🕷️

**데이터 수집:**
```python
# 34개 PBN 사이트에서 데이터 수집
for pbn_site in pbn_sites:
    posts = get_wordpress_posts(site_url)  # WordPress REST API 사용
    save_to_sqlite(posts)                  # SQLite에 저장
```

**수집되는 데이터:**
- 포스트 제목 (가장 중요!)
- URL
- 발행일
- 단어 수
- 요약문

### 2단계: 데이터 저장 방식 🗄️

#### 현재 방식: SQLite만 사용
```sql
CREATE TABLE pbn_posts (
    site_id INTEGER,
    title TEXT,          -- "백링크 테스트의 중요성"
    url TEXT,            -- "https://pbn1.com/post/123"
    word_count INTEGER   -- 1500
);
```

#### 개선된 방식: SQLite + FAISS 인덱스
```python
# 1. SQLite에 기본 데이터 저장 (기존과 동일)
sqlite_db.save(post_data)

# 2. 제목을 벡터로 변환
embedding = model.encode("백링크 테스트의 중요성")
# 결과: [0.123, -0.456, 0.789, ...] (384차원 벡터)

# 3. FAISS 인덱스에 벡터 저장
faiss_index.add(embedding)

# 4. 메타데이터 JSON 저장
metadata = {
    "index": 0,
    "title": "백링크 테스트의 중요성",
    "url": "https://pbn1.com/post/123"
}
```

### 3단계: 유사도 검사 방식 🔍

#### AI 기반 (Sentence Transformers) - LLM 호출 없음!

**모델 특징:**
- 로컬에서 실행 (인터넷 연결 불필요)
- OpenAI API 호출 없음
- 한 번 다운로드하면 오프라인 사용 가능
- 빠른 속도 (GPU 사용 시 더 빠름)

**작동 원리:**
```python
# 1. 검색 키워드
search_keywords = ["백링크", "SEO", "검색엔진최적화"]
search_text = "백링크 SEO 검색엔진최적화"

# 2. 키워드를 벡터로 변환
query_vector = model.encode(search_text)
# 결과: [0.234, -0.567, 0.891, ...] (384차원)

# 3. 기존 포스트 벡터들과 유사도 계산
similarities = cosine_similarity(query_vector, all_post_vectors)
# 결과: [0.85, 0.72, 0.65, 0.45, ...] (유사도 점수들)

# 4. 높은 점수 순으로 정렬
top_matches = get_top_similar(similarities, threshold=0.3)
```

#### 키워드 매칭 (백업 방식)
```sql
-- 단순한 문자열 매칭
SELECT * FROM pbn_posts 
WHERE title LIKE '%백링크%' 
   OR title LIKE '%SEO%' 
   OR title LIKE '%검색엔진최적화%'
ORDER BY word_count DESC;
```

### 4단계: 링크 삽입 과정 🔗

```python
def build_comprehensive_links(content, keyword, client_url):
    # 1. 클라이언트 링크 100% 삽입
    content = insert_client_link(content, keyword, client_url)
    
    # 2. 내부링크 후보 찾기
    similar_posts = find_similar_posts_fast(keywords)
    
    # 3. 적절한 앵커텍스트 위치 찾기
    for post in similar_posts:
        anchor_position = find_anchor_position(content, post.title)
        if anchor_position:
            content = insert_internal_link(content, anchor_position, post.url)
    
    return content
```

## ⚡ 성능 비교

### 현재 방식 (SQLite만)
```
포스트 10,000개 기준:
- 검색 시간: 2-5초
- 메모리 사용: 적음
- 정확도: 낮음 (단순 문자열 매칭)
```

### 개선된 방식 (SQLite + FAISS)
```
포스트 10,000개 기준:
- 최초 인덱스 구성: 30-60초 (한 번만)
- 검색 시간: 0.1-0.5초 (20배 빠름!)
- 메모리 사용: 중간 (벡터 저장)
- 정확도: 높음 (의미적 유사도)
```

## 🛠️ 실제 구현 절차

### 1. 의존성 설치
```bash
pip install sentence-transformers scikit-learn faiss-cpu numpy
```

### 2. 시스템 초기화
```python
from improved_similarity_system import ImprovedSimilaritySystem

# 시스템 생성 (최초 1회 시간 소요)
system = ImprovedSimilaritySystem()

# 인덱스 구성 (PBN 크롤링 후 실행)
system._rebuild_index()  # 10,000개 포스트 기준 30-60초
```

### 3. 일상적인 사용
```python
# 빠른 유사도 검색
similar_posts = system.find_similar_posts_fast(
    keywords=["백링크", "SEO"],
    limit=10,
    min_similarity=0.3
)

# 결과 예시:
# [
#   {
#     "title": "백링크 구축의 핵심 전략",
#     "url": "https://pbn1.com/post/456",
#     "similarity_score": 0.87
#   },
#   {
#     "title": "SEO 최적화 완벽 가이드", 
#     "url": "https://pbn2.com/post/789",
#     "similarity_score": 0.74
#   }
# ]
```

## 💡 핵심 포인트

### ✅ 장점
1. **LLM 호출 없음**: 로컬에서 실행, 비용 없음
2. **빠른 속도**: FAISS 인덱스로 밀리초 단위 검색
3. **높은 정확도**: 의미적 유사도로 더 관련성 높은 결과
4. **확장성**: 수십만 개 포스트까지 처리 가능

### ⚠️ 고려사항
1. **최초 설정 시간**: 인덱스 구성에 시간 소요 (한 번만)
2. **저장 공간**: 벡터 데이터 추가 저장 필요
3. **메모리 사용**: 실행 시 더 많은 메모리 사용

## 🎯 추천 구현 순서

1. **1단계**: 기존 시스템 그대로 사용하여 PBN 크롤링 완료
2. **2단계**: 개선된 시스템으로 인덱스 구성 (백그라운드)
3. **3단계**: 성능 테스트 후 점진적 전환
4. **4단계**: 완전 전환 및 최적화

이렇게 하면 기존 시스템을 중단하지 않고 점진적으로 개선할 수 있습니다!
