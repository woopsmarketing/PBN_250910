# 개선된 PBN 콘텐츠 유사도 검사 시스템
# 효율적인 벡터 저장과 빠른 검색을 위한 시스템

import os
import json
import sqlite3
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import time
from dataclasses import dataclass

# 텍스트 유사도 계산을 위한 라이브러리들
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import faiss

    ADVANCED_SIMILARITY_AVAILABLE = True
except ImportError:
    print("⚠️ 고급 유사도 라이브러리가 설치되지 않았습니다.")
    print("pip install sentence-transformers scikit-learn faiss-cpu numpy")
    ADVANCED_SIMILARITY_AVAILABLE = False


@dataclass
class PostEmbedding:
    """포스트 임베딩 데이터 클래스"""

    post_id: int
    site_id: int
    title: str
    url: str
    embedding: np.ndarray
    word_count: int


class ImprovedSimilaritySystem:
    """개선된 유사도 검사 시스템"""

    def __init__(
        self,
        db_path: str = "controlDB.db",
        embedding_cache_dir: str = "embedding_cache",
    ):
        """
        개선된 유사도 시스템 초기화

        Args:
            db_path: SQLite 데이터베이스 경로
            embedding_cache_dir: 임베딩 캐시 디렉토리
        """
        self.db_path = db_path
        self.embedding_cache_dir = Path(embedding_cache_dir)
        self.embedding_cache_dir.mkdir(exist_ok=True)

        # 파일 경로들
        self.embeddings_file = self.embedding_cache_dir / "post_embeddings.pkl"
        self.faiss_index_file = self.embedding_cache_dir / "faiss_index.bin"
        self.metadata_file = self.embedding_cache_dir / "post_metadata.json"

        # 모델 및 인덱스 초기화
        self.similarity_model = None
        self.faiss_index = None
        self.post_metadata = []

        if ADVANCED_SIMILARITY_AVAILABLE:
            self._initialize_model()
            self._load_or_create_index()

        print(f"🔍 개선된 유사도 시스템 초기화 완료")

    def _initialize_model(self):
        """유사도 모델 초기화"""
        try:
            print("🤖 텍스트 유사도 모델 로딩 중...")
            # 한국어에 최적화된 다국어 모델 사용
            self.similarity_model = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2"
            )
            print("✅ 유사도 모델 로딩 완료")
        except Exception as e:
            print(f"⚠️ 유사도 모델 로딩 실패: {e}")
            self.similarity_model = None

    def _load_or_create_index(self):
        """FAISS 인덱스 로드 또는 생성"""
        if (
            self.faiss_index_file.exists()
            and self.metadata_file.exists()
            and self.similarity_model
        ):

            try:
                # 기존 인덱스 로드
                print("📂 기존 FAISS 인덱스 로딩 중...")
                self.faiss_index = faiss.read_index(str(self.faiss_index_file))

                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    self.post_metadata = json.load(f)

                print(f"✅ FAISS 인덱스 로드 완료: {len(self.post_metadata)}개 포스트")
                return
            except Exception as e:
                print(f"⚠️ 기존 인덱스 로드 실패: {e}")

        # 새로운 인덱스 생성
        print("🔨 새로운 FAISS 인덱스 생성 중...")
        self._rebuild_index()

    def _rebuild_index(self):
        """FAISS 인덱스 재구성"""
        if not self.similarity_model:
            print("❌ 유사도 모델이 없어서 인덱스를 생성할 수 없습니다.")
            return

        # 데이터베이스에서 모든 포스트 가져오기
        posts = self._get_all_posts_from_db()

        if not posts:
            print("❌ 데이터베이스에 포스트가 없습니다.")
            return

        print(f"📄 {len(posts)}개 포스트의 임베딩 생성 중...")

        # 제목들 추출
        titles = [post["title"] for post in posts]

        # 배치로 임베딩 생성 (효율성 향상)
        batch_size = 100
        all_embeddings = []

        for i in range(0, len(titles), batch_size):
            batch_titles = titles[i : i + batch_size]
            batch_embeddings = self.similarity_model.encode(
                batch_titles, batch_size=batch_size, show_progress_bar=True
            )
            all_embeddings.extend(batch_embeddings)

            if i % (batch_size * 5) == 0:  # 500개마다 진행상황 출력
                print(f"   진행률: {min(i+batch_size, len(titles))}/{len(titles)}")

        # NumPy 배열로 변환
        embeddings_matrix = np.array(all_embeddings, dtype=np.float32)

        # FAISS 인덱스 생성
        dimension = embeddings_matrix.shape[1]

        # IndexFlatIP: 내적 기반 유사도 (코사인 유사도와 유사)
        # 정규화된 벡터에 대해 내적 = 코사인 유사도
        self.faiss_index = faiss.IndexFlatIP(dimension)

        # 벡터 정규화 (코사인 유사도를 위해)
        faiss.normalize_L2(embeddings_matrix)

        # 인덱스에 벡터 추가
        self.faiss_index.add(embeddings_matrix)

        # 메타데이터 준비
        self.post_metadata = []
        for i, post in enumerate(posts):
            self.post_metadata.append(
                {
                    "index": i,
                    "post_id": post["post_id"],
                    "site_id": post["site_id"],
                    "site_url": post["site_url"],
                    "title": post["title"],
                    "url": post["url"],
                    "excerpt": post.get("excerpt", ""),
                    "word_count": post.get("word_count", 0),
                    "date_published": post.get("date_published", ""),
                }
            )

        # 인덱스와 메타데이터 저장
        self._save_index()

        print(f"✅ FAISS 인덱스 생성 완료: {len(self.post_metadata)}개 포스트")

    def _save_index(self):
        """FAISS 인덱스와 메타데이터 저장"""
        try:
            # FAISS 인덱스 저장
            faiss.write_index(self.faiss_index, str(self.faiss_index_file))

            # 메타데이터 저장
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.post_metadata, f, ensure_ascii=False, indent=2)

            print("💾 인덱스와 메타데이터 저장 완료")
        except Exception as e:
            print(f"❌ 인덱스 저장 실패: {e}")

    def _get_all_posts_from_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 모든 포스트 가져오기"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT site_id, site_url, post_id, title, url, excerpt, 
                       date_published, word_count
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

    def find_similar_posts_fast(
        self,
        keywords: List[str],
        limit: int = 10,
        min_similarity: float = 0.3,
        random_selection: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        빠른 유사도 검색 (FAISS 인덱스 사용) - 랜덤 선택 옵션 포함

        Args:
            keywords: 검색할 키워드 리스트
            limit: 반환할 최대 결과 수
            min_similarity: 최소 유사도 임계값
            random_selection: 랜덤 선택 여부 (True: 상위 그룹에서 랜덤, False: 상위 순서대로)

        Returns:
            유사한 포스트들의 리스트 (유사도 점수 포함)
        """
        if not self.faiss_index or not self.similarity_model:
            print("⚠️ FAISS 인덱스나 유사도 모델이 없어서 기본 방식을 사용합니다.")
            return self._find_similar_posts_basic(keywords, limit)

        try:
            # 키워드 조합 생성
            search_text = " ".join(keywords)

            # 검색 쿼리 임베딩 생성
            query_embedding = self.similarity_model.encode([search_text])
            query_embedding = query_embedding.astype(np.float32)

            # 벡터 정규화
            faiss.normalize_L2(query_embedding)

            # FAISS로 빠른 검색 수행
            # 랜덤 선택을 위해 더 많은 후보 검색
            search_limit = min(
                limit * 5 if random_selection else limit * 3, len(self.post_metadata)
            )
            similarities, indices = self.faiss_index.search(
                query_embedding, search_limit
            )

            # 결과 처리
            candidates = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if similarity < min_similarity:
                    continue

                metadata = self.post_metadata[idx]
                result = {
                    "site_id": metadata["site_id"],
                    "site_url": metadata["site_url"],
                    "post_id": metadata["post_id"],
                    "title": metadata["title"],
                    "url": metadata["url"],
                    "excerpt": metadata["excerpt"],
                    "date_published": metadata["date_published"],
                    "word_count": metadata["word_count"],
                    "similarity_score": float(similarity),
                }
                candidates.append(result)

            # 랜덤 선택 또는 상위 선택
            if random_selection and len(candidates) > limit:
                import random

                # 상위 50% 또는 최소 limit*2개 중에서 선택
                top_group_size = max(limit * 2, len(candidates) // 2)
                top_candidates = candidates[:top_group_size]

                # 랜덤으로 limit개 선택
                selected = random.sample(
                    top_candidates, min(limit, len(top_candidates))
                )

                print(
                    f"🎲 {len(candidates)}개 후보 중 상위 {top_group_size}개에서 랜덤 선택: {len(selected)}개"
                )
                return selected
            else:
                results = candidates[:limit]
                print(f"🚀 FAISS 검색 완료: {len(results)}개 유사 포스트 발견")
                return results

        except Exception as e:
            print(f"❌ FAISS 검색 중 오류: {e}")
            return self._find_similar_posts_basic(keywords, limit)

    def _find_similar_posts_basic(
        self, keywords: List[str], limit: int
    ) -> List[Dict[str, Any]]:
        """기본 키워드 매칭 방식 (백업)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # LIKE 쿼리로 키워드가 포함된 제목 찾기
            conditions = []
            params = []

            for keyword in keywords:
                conditions.append("title LIKE ?")
                params.append(f"%{keyword}%")

            query = f"""
                SELECT site_id, site_url, post_id, title, url, excerpt, 
                       date_published, word_count
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

    def update_index_with_new_posts(self):
        """새로운 포스트가 추가된 경우 인덱스 업데이트"""
        print("🔄 인덱스 업데이트 확인 중...")

        # 현재 데이터베이스의 포스트 수 확인
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pbn_posts")
            current_count = cursor.fetchone()[0]

        # 인덱스의 포스트 수와 비교
        indexed_count = len(self.post_metadata) if self.post_metadata else 0

        if current_count > indexed_count:
            print(f"📈 새로운 포스트 발견: {current_count - indexed_count}개")
            print("🔨 인덱스 재구성 중...")
            self._rebuild_index()
        else:
            print("✅ 인덱스가 최신 상태입니다.")

    def get_index_stats(self) -> Dict[str, Any]:
        """인덱스 통계 정보 반환"""
        stats = {
            "total_posts": len(self.post_metadata) if self.post_metadata else 0,
            "index_exists": self.faiss_index is not None,
            "model_loaded": self.similarity_model is not None,
            "embedding_dimension": self.faiss_index.d if self.faiss_index else 0,
            "cache_dir": str(self.embedding_cache_dir),
            "index_file_size": 0,
            "metadata_file_size": 0,
        }

        # 파일 크기 정보
        if self.faiss_index_file.exists():
            stats["index_file_size"] = self.faiss_index_file.stat().st_size

        if self.metadata_file.exists():
            stats["metadata_file_size"] = self.metadata_file.stat().st_size

        # 인덱스 크기 (MB)
        stats["index_size_mb"] = stats["index_file_size"] / (1024 * 1024)

        return stats


# 성능 비교 테스트 함수
def performance_comparison_test():
    """기존 방식과 개선된 방식의 성능 비교"""
    print("⚡ 성능 비교 테스트 시작")
    print("=" * 50)

    # 시스템 초기화
    improved_system = ImprovedSimilaritySystem()

    # 테스트 키워드
    test_keywords = ["SEO", "백링크", "검색엔진최적화"]

    # FAISS 방식 테스트
    if improved_system.faiss_index:
        print("🚀 FAISS 인덱스 방식 테스트...")
        start_time = time.time()
        faiss_results = improved_system.find_similar_posts_fast(test_keywords, limit=10)
        faiss_duration = time.time() - start_time
        print(f"   결과: {len(faiss_results)}개, 소요시간: {faiss_duration:.3f}초")

    # 기본 방식 테스트
    print("📝 기본 키워드 매칭 방식 테스트...")
    start_time = time.time()
    basic_results = improved_system._find_similar_posts_basic(test_keywords, limit=10)
    basic_duration = time.time() - start_time
    print(f"   결과: {len(basic_results)}개, 소요시간: {basic_duration:.3f}초")

    # 성능 개선 비율 계산
    if improved_system.faiss_index and basic_duration > 0:
        improvement = (basic_duration - faiss_duration) / basic_duration * 100
        print(f"\n⚡ 성능 개선: {improvement:.1f}% 빠름")


if __name__ == "__main__":
    # 시스템 테스트
    system = ImprovedSimilaritySystem()

    # 통계 출력
    stats = system.get_index_stats()
    print(f"\n📊 시스템 통계:")
    print(f"   총 포스트: {stats['total_posts']:,}개")
    print(f"   FAISS 인덱스: {'✅' if stats['index_exists'] else '❌'}")
    print(f"   유사도 모델: {'✅' if stats['model_loaded'] else '❌'}")

    # 성능 비교 테스트
    if stats["total_posts"] > 0:
        performance_comparison_test()
