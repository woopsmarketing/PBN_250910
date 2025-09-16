# PBN 콘텐츠 크롤러 및 링크 빌더
# 모든 PBN 사이트의 블로그 글 제목과 URL을 수집하고 유사도 기반 링크 생성

import os
import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import urljoin, urlparse
import sqlite3
import re
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 텍스트 유사도 계산을 위한 라이브러리들
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    SIMILARITY_AVAILABLE = True
except ImportError:
    print("⚠️ sentence-transformers, scikit-learn이 설치되지 않았습니다.")
    print("pip install sentence-transformers scikit-learn numpy 를 실행하세요.")
    SIMILARITY_AVAILABLE = False

from controlDB import get_all_pbn_sites


@dataclass
class PBNPost:
    """PBN 포스트 데이터 클래스"""

    site_id: int
    site_url: str
    post_id: int
    title: str
    url: str
    excerpt: str
    date_published: str
    word_count: int = 0
    categories: List[str] = None
    tags: List[str] = None


class PBNContentCrawler:
    """PBN 사이트들의 콘텐츠를 크롤링하고 관리하는 클래스"""

    def __init__(self, db_path: str = "controlDB.db"):
        """
        PBN 콘텐츠 크롤러 초기화

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.session = self._create_session()
        self.lock = threading.Lock()

        # 텍스트 유사도 모델 초기화 (가능한 경우)
        self.similarity_model = None
        if SIMILARITY_AVAILABLE:
            try:
                print("🤖 텍스트 유사도 모델 로딩 중...")
                # 한국어에 적합한 다국어 모델 사용
                self.similarity_model = SentenceTransformer(
                    "paraphrase-multilingual-MiniLM-L12-v2"
                )
                print("✅ 텍스트 유사도 모델 로딩 완료")
            except Exception as e:
                print(f"⚠️ 유사도 모델 로딩 실패: {e}")
                self.similarity_model = None

        # 데이터베이스 초기화
        self._init_database()

        print(f"🗄️ PBN 콘텐츠 크롤러 초기화 완료 (DB: {db_path})")

    def _create_session(self) -> requests.Session:
        """HTTP 세션 생성 (재시도 로직 포함)"""
        session = requests.Session()

        # 재시도 전략 설정
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # 기본 헤더 설정
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        return session

    def _init_database(self):
        """SQLite 데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # PBN 포스트 테이블 생성
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS pbn_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER NOT NULL,
                    site_url TEXT NOT NULL,
                    post_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    excerpt TEXT,
                    date_published TEXT,
                    word_count INTEGER DEFAULT 0,
                    categories TEXT,  -- JSON 형태로 저장
                    tags TEXT,        -- JSON 형태로 저장
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # 크롤링 로그 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS crawl_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER NOT NULL,
                    site_url TEXT NOT NULL,
                    total_posts INTEGER DEFAULT 0,
                    successful_posts INTEGER DEFAULT 0,
                    failed_posts INTEGER DEFAULT 0,
                    crawl_duration REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # 인덱스 생성
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_site_id ON pbn_posts(site_id)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON pbn_posts(title)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_url ON pbn_posts(url)")

            conn.commit()

        print("✅ 데이터베이스 초기화 완료")

    def get_wordpress_posts(
        self, site_url: str, site_id: int, max_pages: int = 50
    ) -> List[PBNPost]:
        """
        워드프레스 사이트에서 포스트 목록을 가져옵니다.

        Args:
            site_url: 사이트 URL
            site_id: 사이트 ID
            max_pages: 최대 페이지 수

        Returns:
            PBNPost 객체 리스트
        """
        posts = []
        page = 1

        print(f"   📄 포스트 수집 시작: {site_url}")

        while page <= max_pages:
            try:
                # WordPress REST API 엔드포인트
                api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
                params = {
                    "page": page,
                    "per_page": 100,  # 한 번에 많이 가져오기
                    "status": "publish",
                    "_fields": "id,title,link,excerpt,date,categories,tags,content",  # 필요한 필드만
                }

                response = self.session.get(api_url, params=params, timeout=30)

                if response.status_code == 404:
                    print(f"   ⚠️ REST API를 찾을 수 없음: {site_url}")
                    break
                elif response.status_code != 200:
                    print(f"   ❌ API 요청 실패: {response.status_code}")
                    break

                page_posts = response.json()

                if not page_posts:  # 더 이상 포스트가 없음
                    break

                for post_data in page_posts:
                    try:
                        # HTML 태그 제거 함수
                        def clean_html(text):
                            if not text:
                                return ""
                            clean = re.sub("<.*?>", "", str(text))
                            return clean.strip()

                        # 제목 정리
                        title = clean_html(
                            post_data.get("title", {}).get("rendered", "")
                        )
                        if not title:
                            continue

                        # 본문에서 단어 수 계산 (대략적)
                        content = clean_html(
                            post_data.get("content", {}).get("rendered", "")
                        )
                        word_count = len(content.split()) if content else 0

                        post = PBNPost(
                            site_id=site_id,
                            site_url=site_url,
                            post_id=post_data.get("id", 0),
                            title=title,
                            url=post_data.get("link", ""),
                            excerpt=clean_html(
                                post_data.get("excerpt", {}).get("rendered", "")
                            ),
                            date_published=post_data.get("date", ""),
                            word_count=word_count,
                            categories=[],  # 카테고리 정보는 별도 API 호출 필요
                            tags=[],  # 태그 정보도 별도 API 호출 필요
                        )

                        posts.append(post)

                    except Exception as e:
                        print(f"   ⚠️ 포스트 파싱 오류: {e}")
                        continue

                print(f"   📄 페이지 {page} 완료: {len(page_posts)}개 포스트")
                page += 1

                # 요청 간격 (서버 부하 방지)
                time.sleep(0.5)

            except Exception as e:
                print(f"   ❌ 페이지 {page} 크롤링 실패: {e}")
                break

        print(f"   ✅ 총 {len(posts)}개 포스트 수집 완료: {site_url}")
        return posts

    def save_posts_to_db(self, posts: List[PBNPost]) -> int:
        """포스트들을 데이터베이스에 저장"""
        if not posts:
            return 0

        saved_count = 0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for post in posts:
                try:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO pbn_posts 
                        (site_id, site_url, post_id, title, url, excerpt, date_published, word_count, categories, tags, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                        (
                            post.site_id,
                            post.site_url,
                            post.post_id,
                            post.title,
                            post.url,
                            post.excerpt,
                            post.date_published,
                            post.word_count,
                            json.dumps(post.categories or [], ensure_ascii=False),
                            json.dumps(post.tags or [], ensure_ascii=False),
                        ),
                    )
                    saved_count += 1
                except sqlite3.IntegrityError:
                    # URL이 이미 존재하는 경우 (중복)
                    continue
                except Exception as e:
                    print(f"   ⚠️ 포스트 저장 실패: {e}")
                    continue

            conn.commit()

        return saved_count

    def log_crawl_result(
        self,
        site_id: int,
        site_url: str,
        total_posts: int,
        successful_posts: int,
        duration: float,
        status: str = "completed",
        error_message: str = None,
    ):
        """크롤링 결과를 로그에 기록"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO crawl_logs 
                (site_id, site_url, total_posts, successful_posts, failed_posts, crawl_duration, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    site_id,
                    site_url,
                    total_posts,
                    successful_posts,
                    total_posts - successful_posts,
                    duration,
                    status,
                    error_message,
                ),
            )
            conn.commit()

    def crawl_single_site(self, site_data: Tuple) -> Dict[str, Any]:
        """단일 PBN 사이트 크롤링"""
        site_id, site_url, username, password, app_password = site_data
        start_time = time.time()

        try:
            print(f"🕷️ 크롤링 시작: {site_url}")

            # 포스트 수집
            posts = self.get_wordpress_posts(site_url, site_id)

            # 데이터베이스에 저장
            saved_count = self.save_posts_to_db(posts)

            duration = time.time() - start_time

            # 로그 기록
            self.log_crawl_result(site_id, site_url, len(posts), saved_count, duration)

            result = {
                "site_id": site_id,
                "site_url": site_url,
                "total_posts": len(posts),
                "saved_posts": saved_count,
                "duration": duration,
                "status": "success",
            }

            print(
                f"✅ 크롤링 완료: {site_url} ({saved_count}/{len(posts)} 저장, {duration:.1f}초)"
            )
            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)

            # 에러 로그 기록
            self.log_crawl_result(
                site_id, site_url, 0, 0, duration, "failed", error_msg
            )

            print(f"❌ 크롤링 실패: {site_url} - {error_msg}")
            return {
                "site_id": site_id,
                "site_url": site_url,
                "total_posts": 0,
                "saved_posts": 0,
                "duration": duration,
                "status": "failed",
                "error": error_msg,
            }

    def crawl_all_pbn_sites(self, max_workers: int = 5) -> Dict[str, Any]:
        """모든 PBN 사이트를 병렬로 크롤링"""
        print("🚀 모든 PBN 사이트 크롤링 시작")
        print("=" * 50)

        # PBN 사이트 목록 가져오기
        pbn_sites = get_all_pbn_sites()

        if not pbn_sites:
            print("❌ PBN 사이트가 없습니다.")
            return {"total_sites": 0, "results": []}

        print(f"📊 총 {len(pbn_sites)}개의 PBN 사이트 발견")

        # 병렬 크롤링 실행
        results = []
        total_posts = 0
        total_saved = 0
        successful_sites = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 모든 사이트에 대해 크롤링 작업 제출
            future_to_site = {
                executor.submit(self.crawl_single_site, site): site
                for site in pbn_sites
            }

            # 완료된 작업들 처리
            for future in as_completed(future_to_site):
                site = future_to_site[future]
                try:
                    result = future.result()
                    results.append(result)

                    total_posts += result["total_posts"]
                    total_saved += result["saved_posts"]

                    if result["status"] == "success":
                        successful_sites += 1

                except Exception as e:
                    print(f"❌ 사이트 처리 중 예외 발생: {site[1]} - {e}")
                    results.append(
                        {
                            "site_id": site[0],
                            "site_url": site[1],
                            "total_posts": 0,
                            "saved_posts": 0,
                            "status": "exception",
                            "error": str(e),
                        }
                    )

        # 최종 결과 출력
        print("\n" + "=" * 50)
        print("🎉 PBN 사이트 크롤링 완료!")
        print(f"📊 처리된 사이트: {len(pbn_sites)}개")
        print(f"✅ 성공한 사이트: {successful_sites}개")
        print(f"❌ 실패한 사이트: {len(pbn_sites) - successful_sites}개")
        print(f"📄 총 수집된 포스트: {total_posts:,}개")
        print(f"💾 저장된 포스트: {total_saved:,}개")

        return {
            "total_sites": len(pbn_sites),
            "successful_sites": successful_sites,
            "total_posts": total_posts,
            "saved_posts": total_saved,
            "results": results,
        }

    def get_all_posts_from_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 모든 포스트 가져오기"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT site_id, site_url, post_id, title, url, excerpt, date_published, word_count
                FROM pbn_posts
                ORDER BY date_published DESC
            """
            )

            posts = []
            for row in cursor.fetchall():
                posts.append(
                    {
                        "site_id": row[0],
                        "site_url": row[1],
                        "post_id": row[2],
                        "title": row[3],
                        "url": row[4],
                        "excerpt": row[5],
                        "date_published": row[6],
                        "word_count": row[7],
                    }
                )

            return posts

    def find_similar_posts(
        self, keywords: List[str], limit: int = 10, min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        키워드와 유사한 제목을 가진 포스트들을 찾습니다.

        Args:
            keywords: 검색할 키워드 리스트
            limit: 반환할 최대 결과 수
            min_similarity: 최소 유사도 임계값

        Returns:
            유사한 포스트들의 리스트 (유사도 점수 포함)
        """
        if not self.similarity_model:
            print("⚠️ 유사도 모델이 없어서 키워드 매칭으로 대체합니다.")
            return self._find_similar_posts_keyword_matching(keywords, limit)

        try:
            # 데이터베이스에서 모든 포스트 가져오기
            posts = self.get_all_posts_from_db()

            if not posts:
                return []

            # 키워드 조합 생성
            search_text = " ".join(keywords)

            # 제목들 추출
            titles = [post["title"] for post in posts]

            # 임베딩 생성
            print(f"🔍 {len(titles)}개 포스트 제목에서 유사도 검사 중...")
            search_embedding = self.similarity_model.encode([search_text])
            title_embeddings = self.similarity_model.encode(titles)

            # 코사인 유사도 계산
            similarities = cosine_similarity(search_embedding, title_embeddings)[0]

            # 유사도가 높은 순으로 정렬
            similar_indices = np.argsort(similarities)[::-1]

            results = []
            for idx in similar_indices:
                similarity_score = similarities[idx]

                if similarity_score < min_similarity:
                    break

                if len(results) >= limit:
                    break

                post = posts[idx]
                post["similarity_score"] = float(similarity_score)
                results.append(post)

            # 최신 글 우선 정렬 (날짜 기준) - 개선된 버전
            from datetime import datetime

            def safe_date_sort(post):
                """안전한 날짜 정렬을 위한 함수"""
                try:
                    # ISO 형식 날짜 파싱
                    date_str = post.get("date_published", "")
                    if date_str:
                        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    else:
                        # 날짜가 없으면 매우 오래된 것으로 처리
                        return datetime.min
                except (ValueError, TypeError):
                    # 날짜 파싱 실패 시 오래된 것으로 처리
                    return datetime.min

            # 최신 글 우선으로 정렬 (날짜 내림차순)
            results.sort(key=safe_date_sort, reverse=True)

            # 최신 글 정보 출력
            if results:
                latest_date = safe_date_sort(results[0])
                oldest_date = safe_date_sort(results[-1])
                print(
                    f"📅 검색된 포스트 날짜 범위: {oldest_date.strftime('%Y-%m-%d')} ~ {latest_date.strftime('%Y-%m-%d')}"
                )

            print(f"✅ {len(results)}개의 유사한 포스트를 찾았습니다. (최신 글 우선)")
            return results

        except Exception as e:
            print(f"❌ 유사도 검사 중 오류: {e}")
            return self._find_similar_posts_keyword_matching(keywords, limit)

    def _find_similar_posts_keyword_matching(
        self, keywords: List[str], limit: int
    ) -> List[Dict[str, Any]]:
        """키워드 매칭 방식으로 유사한 포스트 찾기 (백업 방법)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # LIKE 쿼리로 키워드가 포함된 제목 찾기
            conditions = []
            params = []

            for keyword in keywords:
                conditions.append("title LIKE ?")
                params.append(f"%{keyword}%")

            query = f"""
                SELECT site_id, site_url, post_id, title, url, excerpt, date_published, word_count
                FROM pbn_posts
                WHERE {" OR ".join(conditions)}
                ORDER BY word_count DESC
                LIMIT ?
            """

            params.append(limit)
            cursor.execute(query, params)

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "site_id": row[0],
                        "site_url": row[1],
                        "post_id": row[2],
                        "title": row[3],
                        "url": row[4],
                        "excerpt": row[5],
                        "date_published": row[6],
                        "word_count": row[7],
                        "similarity_score": 0.5,  # 기본 점수
                    }
                )

            return results

    def get_database_stats(self) -> Dict[str, Any]:
        """데이터베이스 통계 정보 반환"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 전체 포스트 수
            cursor.execute("SELECT COUNT(*) FROM pbn_posts")
            total_posts = cursor.fetchone()[0]

            # 사이트별 포스트 수
            cursor.execute(
                """
                SELECT site_url, COUNT(*) as post_count
                FROM pbn_posts
                GROUP BY site_url
                ORDER BY post_count DESC
            """
            )
            site_stats = cursor.fetchall()

            # 최근 크롤링 로그
            cursor.execute(
                """
                SELECT site_url, total_posts, successful_posts, status, created_at
                FROM crawl_logs
                ORDER BY created_at DESC
                LIMIT 10
            """
            )
            recent_crawls = cursor.fetchall()

            return {
                "total_posts": total_posts,
                "total_sites": len(site_stats),
                "site_stats": site_stats,
                "recent_crawls": recent_crawls,
            }


# 테스트 및 실행 함수들
def test_crawler():
    """크롤러 테스트 함수"""
    print("🧪 PBN 콘텐츠 크롤러 테스트 시작")

    crawler = PBNContentCrawler()

    # 모든 PBN 사이트 크롤링
    results = crawler.crawl_all_pbn_sites(max_workers=3)  # 동시 실행 수 제한

    # 통계 출력
    stats = crawler.get_database_stats()
    print(f"\n📊 데이터베이스 통계:")
    print(f"   총 포스트: {stats['total_posts']:,}개")
    print(f"   총 사이트: {stats['total_sites']}개")

    # 유사도 테스트
    test_keywords = ["SEO", "백링크", "검색엔진최적화"]
    similar_posts = crawler.find_similar_posts(test_keywords, limit=5)

    print(f"\n🔍 '{', '.join(test_keywords)}' 키워드와 유사한 포스트:")
    for post in similar_posts:
        print(f"   📄 {post['title']} (유사도: {post.get('similarity_score', 0):.3f})")
        print(f"      🔗 {post['url']}")


if __name__ == "__main__":
    test_crawler()
