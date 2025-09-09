# v2.0 - 고도화된 PBN 백링크 자동화 시스템
# 기존 시스템의 모든 기능 + 고품질 콘텐츠 생성 기능 통합

import sys
import os
import time
import random
import re
import base64
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
import requests
from PIL import Image
import ssl
import xmlrpc.client
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.compat import xmlrpc_client

# 기존 모듈 import
from controlDB import (
    ControlDB,
    get_active_clients,
    get_client_keywords,
    get_random_keyword_for_client,
    update_client_info,
    move_client_to_completed,
    get_all_pbn_sites,
    get_random_pbn_site,
    add_post,
    view_client_status,
    add_pbn_site,
    view_pbn_sites,
    delete_record_by_id,
    add_client,
    view_clients,
    view_completed_clients,
    pause_client,
    resume_client,
    pause_all_clients,
    resume_all_clients,
    fetch_all_posts,
    save_all_backlinks_to_excel,
    show_all_tables,
    add_client_keyword,
    remove_duplicate_clients,
)
from wordpress_functions import WordPressManager

# 고도화된 RAG 파이프라인 import
import asyncio
import json
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from langchain_core.messages import HumanMessage

# HTML 변환 모듈 import
from src.generators.html.simple_html_converter import SimpleHTMLConverter

# 새로운 링크 빌딩 시스템 import
from pbn_content_crawler import PBNContentCrawler
from intelligent_link_builder import IntelligentLinkBuilder
from improved_similarity_system import ImprovedSimilaritySystem

# 환경 변수 로드
load_dotenv()
api_key = os.getenv("OPENAI_DALLE_API_KEY")
client = OpenAI(api_key=api_key)


def insert_anchor_text(content: str, keyword: str, client_site_url: str) -> str:
    """
    [DEPRECATED] 기존 단순 앵커 텍스트 삽입 함수 (하위 호환성용)
    새로운 링크 빌딩 시스템을 사용하세요.
    """
    anchor = f'<a href="{client_site_url}" target="_blank" rel="noopener">{keyword}</a>'
    pattern = r"\b" + re.escape(keyword) + r"\b"
    new_content, count = re.subn(pattern, anchor, content, count=1, flags=re.IGNORECASE)
    if count == 0:
        new_content = anchor + " " + content
    return new_content


def input_with_validation(
    prompt,
    validation_func=lambda x: True,
    error_message="잘못된 입력입니다. 다시 시도하세요.",
):
    """입력 값을 검증하고 유효한 값만 반환하는 함수."""
    while True:
        value = input(prompt).strip()
        if validation_func(value):
            return value
        else:
            print(error_message)


def is_positive_int(x):
    return x.isdigit() and int(x) > 0


class EnhancedPBNSystem:
    """고도화된 PBN 백링크 자동화 시스템"""

    def __init__(self):
        """시스템 초기화"""
        self.db = ControlDB()
        self.wp_manager = WordPressManager()
        self.html_converter = SimpleHTMLConverter()

        # 새로운 링크 빌딩 시스템 초기화
        print("🔗 링크 빌딩 시스템 초기화 중...")
        self.pbn_crawler = PBNContentCrawler()

        # 🧠 AI 기반 유사도 시스템 초기화 (안전한 방식)
        try:
            print("   🤖 AI 유사도 시스템 초기화 중...")
            self.similarity_system = ImprovedSimilaritySystem()
            print("   ✅ AI 유사도 시스템 초기화 완료")

            # 초기화 후 상태 확인
            print(
                f"   🔍 초기화 확인 - faiss_index: {self.similarity_system.faiss_index is not None}"
            )
            print(
                f"   🔍 초기화 확인 - similarity_model: {self.similarity_system.similarity_model is not None}"
            )
            print(
                f"   🔍 초기화 확인 - post_metadata: {len(self.similarity_system.post_metadata) if self.similarity_system.post_metadata else 0}개"
            )

        except Exception as e:
            print(f"   ⚠️ AI 유사도 시스템 초기화 실패: {e}")
            print("   🔍 상세 오류 정보:")
            import traceback

            traceback.print_exc()
            print("   🔄 기본 키워드 매칭 방식으로 대체합니다.")
            self.similarity_system = None

        self.link_builder = IntelligentLinkBuilder(self.pbn_crawler)

        # 고도화된 RAG 파이프라인 초기화
        self.llm = client  # OpenAI 클라이언트
        self.cost_tracker = {
            "total_calls": 0,
            "total_tokens": {"prompt": 0, "completion": 0},
            "total_duration": 0,
            "total_images": 0,
            "step_details": [],
            "image_details": [],
        }

        # 디버깅용 데이터 저장 디렉토리 생성
        self.debug_dir = Path("data")
        self.debug_dir.mkdir(exist_ok=True)

        # 현재 세션용 타임스탬프
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print("🚀 고도화된 PBN 시스템이 초기화되었습니다.")
        print("=" * 50)

    def _safe_fragment(self, text: str, max_len: int = 120) -> str:
        """윈도우 호환 파일명 조각 생성 (금지문자 제거/치환)"""
        import re

        frag = re.sub(r"[\\/:*?\"<>|]", "_", text)
        frag = re.sub(r"\s+", "_", frag)
        frag = frag.strip("._")
        if not frag:
            frag = "output"
        return frag[:max_len]

    def save_debug_data(
        self, keyword: str, step: str, data: Any, file_extension: str = "json"
    ):
        """디버깅용 데이터를 파일로 저장"""
        try:
            safe_keyword = self._safe_fragment(keyword)
            filename = (
                f"{safe_keyword}_{step}_{self.session_timestamp}.{file_extension}"
            )
            filepath = self.debug_dir / filename

            if file_extension == "json":
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif file_extension == "md":
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(data)
            elif file_extension == "html":
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(data)
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(str(data))

            print(f"💾 디버깅 데이터 저장: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ 디버깅 데이터 저장 실패: {e}")
            return None

    def check_content_size(self, content: str, max_chars: int = 100000) -> bool:
        """콘텐츠 크기 검사 (워드프레스 제한 고려)"""
        char_count = len(content)
        word_count = len(content.split())

        print(f"📊 콘텐츠 크기 분석:")
        print(f"   📝 문자 수: {char_count:,}")
        print(f"   📝 단어 수: {word_count:,}")
        print(f"   📏 제한: {max_chars:,} 문자")

        if char_count > max_chars:
            print(f"⚠️ 콘텐츠가 너무 큽니다! ({char_count:,} > {max_chars:,})")
            return False
        else:
            print(f"✅ 콘텐츠 크기 적절함")
            return True

    def _truncate_content(self, content: str, max_chars: int) -> str:
        """콘텐츠를 지정된 길이로 축소 (HTML 태그 고려)"""
        if len(content) <= max_chars:
            return content

        # HTML 태그를 고려하여 안전하게 자르기
        truncated = content[:max_chars]

        # 마지막 완전한 태그를 찾아서 자르기
        last_tag_end = truncated.rfind(">")
        if last_tag_end > max_chars * 0.8:  # 80% 이상이면 태그로 끝내기
            truncated = truncated[: last_tag_end + 1]

        # 마지막 문단을 완성하기 위해 "..." 추가
        truncated += "\n\n<p>...</p>"

        return truncated

    def _clean_content_for_wordpress(self, content: str) -> str:
        """워드프레스 업로드를 위한 콘텐츠 정리"""
        import re

        print("🧹 워드프레스용 콘텐츠 정리 중...")

        # 1. 복잡한 CSS 클래스 제거하고 기본 HTML로 변환
        # fs-article, fs-section 등의 커스텀 클래스 제거
        content = re.sub(r'class="[^"]*fs-[^"]*"', "", content)
        content = re.sub(r'class=""', "", content)

        # 2. 불필요한 article, nav 태그를 div로 변환
        content = re.sub(r"<article[^>]*>", "<div>", content)
        content = re.sub(r"</article>", "</div>", content)
        content = re.sub(r"<nav[^>]*>", "<div>", content)
        content = re.sub(r"</nav>", "</div>", content)

        # 3. section을 div로 변환
        content = re.sub(r"<section[^>]*>", "<div>", content)
        content = re.sub(r"</section>", "</div>", content)

        # 4. 복잡한 목차 구조 단순화
        content = re.sub(r'<ol class="[^"]*">', "<ol>", content)
        content = re.sub(r'<dl class="[^"]*">', "<dl>", content)
        content = re.sub(r'<dt class="[^"]*">', "<dt>", content)
        content = re.sub(r'<dd class="[^"]*">', "<dd>", content)

        # 5. 테이블 클래스 제거
        content = re.sub(r'<table class="[^"]*">', "<table>", content)
        content = re.sub(r'<th class="[^"]*">', "<th>", content)
        content = re.sub(r'<td class="[^"]*">', "<td>", content)

        # 6. 빈 class 속성 제거
        content = re.sub(r'\s+class=""', "", content)

        # 7. 다중 공백 정리
        content = re.sub(r"\s+", " ", content)
        content = re.sub(r">\s+<", "><", content)

        # 8. 특수문자 처리 (일부 이모지 제거 또는 대체)
        emoji_replacements = {
            "📚": "[목차]",
            "📖": "[용어]",
            "🔄": "",
            "✅": "",
            "❌": "",
            "⚠️": "[주의]",
            "🎯": "[핵심]",
            "💡": "[팁]",
            "🚀": "",
            "📊": "[통계]",
            "🔍": "[분석]",
            "📈": "[성장]",
            "💼": "[비즈니스]",
        }

        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)

        # 9. 줄바꿈 정리
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

        print(f"✅ 콘텐츠 정리 완료 (크기: {len(content)} 바이트)")
        return content.strip()

    def _create_simple_html_content(self, content_data: dict) -> str:
        """매우 간단한 HTML 형태로 콘텐츠 생성 (호환성 최우선)"""
        print("🔧 간단한 HTML 콘텐츠 생성 중...")

        html_parts = []

        # 제목
        html_parts.append(f"<h1>{content_data['title']}</h1>")

        # Markdown 콘텐츠를 기본 HTML로 변환
        md_content = content_data["content"]

        # 기본적인 마크다운 변환
        import re

        # 헤딩 변환
        md_content = re.sub(
            r"^### (.+)$", r"<h3>\1</h3>", md_content, flags=re.MULTILINE
        )
        md_content = re.sub(
            r"^## (.+)$", r"<h2>\1</h2>", md_content, flags=re.MULTILINE
        )
        md_content = re.sub(r"^# (.+)$", r"<h1>\1</h1>", md_content, flags=re.MULTILINE)

        # 볼드/이탤릭 변환
        md_content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", md_content)
        md_content = re.sub(r"\*(.+?)\*", r"<em>\1</em>", md_content)

        # 링크 변환
        md_content = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', md_content)

        # 문단 변환 (빈 줄로 구분된 텍스트를 p 태그로)
        paragraphs = md_content.split("\n\n")
        html_paragraphs = []

        for para in paragraphs:
            para = para.strip()
            if para:
                # 이미 HTML 태그로 시작하는 경우 그대로 사용
                if para.startswith("<"):
                    html_paragraphs.append(para)
                else:
                    # 일반 텍스트는 p 태그로 감싸기
                    html_paragraphs.append(f"<p>{para}</p>")

        html_parts.extend(html_paragraphs)

        simple_html = "\n\n".join(html_parts)

        # 이모지 제거
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "]+",
            flags=re.UNICODE,
        )

        simple_html = emoji_pattern.sub("", simple_html)

        print(f"✅ 간단한 HTML 생성 완료 (크기: {len(simple_html)} 바이트)")
        return simple_html

    def _try_posting_with_retry(
        self,
        content,
        post_content,
        keyword,
        client_id,
        client_name,
        client_site_url,
        current_pbn_site=None,
    ):
        """PBN 사이트에 포스팅 시도 (실패 시 다른 랜덤 사이트에서 1번 재시도)"""
        from controlDB import get_all_pbn_sites, add_post
        import time
        import random

        print("🔄 PBN 사이트 목록 조회 중...")
        all_pbn_sites = get_all_pbn_sites()

        if not all_pbn_sites:
            print("❌ 사용 가능한 PBN 사이트가 없습니다.")
            return False

        # 앱 패스워드가 있는 사이트만 필터링
        valid_pbn_sites = [
            site for site in all_pbn_sites if site[4]
        ]  # site[4] = app_password

        if not valid_pbn_sites:
            print("❌ 앱 패스워드가 설정된 PBN 사이트가 없습니다.")
            return False

        # 1차 시도: 현재 PBN 사이트 또는 랜덤 선택
        if current_pbn_site and current_pbn_site in valid_pbn_sites:
            first_attempt_site = current_pbn_site
        else:
            first_attempt_site = random.choice(valid_pbn_sites)

        print(f"🎯 1차 시도 PBN 사이트: {first_attempt_site[1]}")

        success = self._try_single_pbn_posting(
            first_attempt_site,
            content,
            post_content,
            keyword,
            client_id,
            client_name,
            client_site_url,
        )

        if success:
            return True

        # 2차 시도: 다른 랜덤 PBN 사이트 선택
        remaining_sites = [
            site for site in valid_pbn_sites if site[0] != first_attempt_site[0]
        ]

        if not remaining_sites:
            print("❌ 재시도할 다른 PBN 사이트가 없습니다.")
            return False

        second_attempt_site = random.choice(remaining_sites)
        print(f"🔄 2차 시도 PBN 사이트: {second_attempt_site[1]}")

        success = self._try_single_pbn_posting(
            second_attempt_site,
            content,
            post_content,
            keyword,
            client_id,
            client_name,
            client_site_url,
        )

        if success:
            return True
        else:
            print("💥 2번의 PBN 사이트 시도 모두 실패")
            return False

    def _try_single_pbn_posting(
        self,
        pbn_site,
        content,
        post_content,
        keyword,
        client_id,
        client_name,
        client_site_url,
    ):
        """단일 PBN 사이트에서 포스팅 시도"""
        from controlDB import add_post
        import time

        pbn_site_id, pbn_url, pbn_user, pbn_pass, pbn_app_pass = pbn_site

        try:
            print(f"   📤 포스팅 시도 중... (사용자: {pbn_user})")

            # 워드프레스에 포스팅
            success = self.wp_manager.create_post(
                site_url=pbn_url,
                username=pbn_user,
                app_password=pbn_app_pass,
                title=content["title"],
                content=post_content,
                status="publish",
            )

            if success:
                print(f"   ✅ 포스팅 성공: {pbn_url}")
                print(f"   📝 생성된 포스트 ID: {success}")

                # DB에 포스트 기록
                post_url = f"{pbn_url}/?p={success}"
                add_post(
                    client_id,
                    client_name,
                    client_site_url,
                    keyword,
                    post_url,
                )
                print(f"   💾 포스트 기록 저장 완료: {post_url}")
                print(f"🎉 {client_name}에 대한 포스팅 완료!")
                time.sleep(10)
                return True
            else:
                print(f"   ❌ 포스팅 실패: {pbn_url}")
                return False

        except Exception as e:
            print(f"   ❌ 포스팅 중 오류 발생: {e}")
            return False

    def track_llm_call(
        self,
        step_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration: float,
        output: str,
        purpose: str,
    ):
        """LLM 호출 추적"""
        self.cost_tracker["total_calls"] += 1
        self.cost_tracker["total_tokens"]["prompt"] += prompt_tokens
        self.cost_tracker["total_tokens"]["completion"] += completion_tokens
        self.cost_tracker["total_duration"] += duration

        # GPT-4 비용 계산 (추정)
        input_cost_per_1k = 0.00003  # $0.03 per 1K tokens
        output_cost_per_1k = 0.00006  # $0.06 per 1K tokens

        step_cost = (prompt_tokens * input_cost_per_1k / 1000) + (
            completion_tokens * output_cost_per_1k / 1000
        )

        self.cost_tracker["step_details"].append(
            {
                "step": step_name,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "duration_seconds": duration,
                "tokens": {"prompt": prompt_tokens, "completion": completion_tokens},
                "estimated_cost_usd": step_cost,
                "purpose": purpose,
                "output_summary": output[:100] + "..." if len(output) > 100 else output,
            }
        )

    def load_active_clients_and_log(self):
        """활성 클라이언트를 조회하고, 목록을 출력한 후 반환합니다."""
        active_clients = get_active_clients()
        if not active_clients:
            print("현재 활성화된 클라이언트가 없습니다.")
            return []
        print("==== [작업 대상 클라이언트 목록] ====")
        for c in active_clients:
            (
                client_id,
                client_name,
                client_site_url,
                _,
                remain_days,
                _,
                _,
                daily_min,
                daily_max,
            ) = c
            print(f"[클라이언트ID: {client_id}] {client_name}")
            print(f" └ URL: {client_site_url}")
            print(
                f" └ 남은 일수: {remain_days}, 최소/최대 링크: {daily_min}/{daily_max}\n"
            )
        return active_clients

    def prepare_day_list(self, clients):
        """
        클라이언트별 오늘 작업 횟수를 결정하여 day_list를 구성하고,
        업데이트 대상인 client_id_set도 함께 반환합니다.
        """
        day_list = []
        client_id_set = set()
        for c in clients:
            (client_id, _, _, _, _, _, _, daily_min, daily_max) = c
            today_count = random.randint(daily_min, daily_max)
            for _ in range(today_count):
                day_list.append(c)
            client_id_set.add(client_id)
        random.shuffle(day_list)
        return day_list, client_id_set

    async def generate_title_keywords(self, keyword: str) -> Dict[str, Any]:
        """단일 호출: 제목, LSI 키워드, 롱테일 키워드 생성"""
        start_time = time.time()

        # 1단계: 키워드 먼저 생성
        keywords_prompt = f"""
메인 키워드: {keyword}

이 메인 키워드를 중심으로 아래를 생성하세요:

1) lsi_keywords: 의미적으로 연관된 LSI 키워드 5-10개 배열
2) longtail_keywords: 구체적인 롱테일 키워드 5-10개 배열

반드시 아래 형식의 JSON만 출력하세요:
{{
  "lsi_keywords": ["..."],
  "longtail_keywords": ["..."]
}}
"""
        print("   📝 1단계: LSI/롱테일 키워드 생성 중...")

        # 키워드 생성 호출
        keywords_response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": keywords_prompt}],
            temperature=0.7,
        )

        try:
            import re, json as _json

            response_content = keywords_response.choices[0].message.content
            m = re.search(r"\{[\s\S]*\}$", response_content.strip())
            keywords_data = (
                _json.loads(m.group(0)) if m else _json.loads(response_content)
            )
            lsi_keywords = keywords_data.get("lsi_keywords", [])
            longtail_keywords = keywords_data.get("longtail_keywords", [])
        except Exception:
            lsi_keywords = [f"{keyword} 팁", f"{keyword} 방법"]
            longtail_keywords = [f"{keyword} 초보 가이드"]

        print("   📝 2단계: 제목 생성 중...")

        # 2단계: 키워드들을 조합해서 제목 생성
        all_keywords = [keyword] + lsi_keywords[:5] + longtail_keywords[:3]

        title_prompt = f"""
메인 키워드: {keyword}
LSI 키워드: {', '.join(lsi_keywords[:5])}
롱테일 키워드: {', '.join(longtail_keywords[:3])}

위 키워드들을 자연스럽게 조합하여 SEO 최적화된 블로그 제목을 만드세요.
- 메인 키워드는 반드시 포함
- LSI나 롱테일 키워드 1-2개도 자연스럽게 포함
- 60자 이내
- 클릭을 유도하는 매력적인 제목

제목만 출력하세요 (JSON이나 다른 형식 없이):
"""

        # 제목 생성
        title_response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": title_prompt}],
            temperature=0.8,
        )
        generated_title = title_response.choices[0].message.content.strip().strip('"')

        print(f"   📝 생성된 제목: {generated_title}")

        # 비용 추적
        duration = time.time() - start_time
        prompt_tokens = int(len(keywords_prompt.split()) * 1.3) + int(
            len(title_prompt.split()) * 1.3
        )
        completion_tokens = int(
            len(keywords_response.choices[0].message.content.split()) * 1.3
        ) + int(len(title_response.choices[0].message.content.split()) * 1.3)

        self.track_llm_call(
            "generate_title_keywords",
            prompt_tokens,
            completion_tokens,
            duration,
            f"키워드: {len(lsi_keywords + longtail_keywords)}개, 제목: {generated_title}",
            "키워드 먼저 생성 → 제목 조합 생성",
        )

        result = {
            "title": generated_title,
            "lsi_keywords": lsi_keywords,
            "longtail_keywords": longtail_keywords,
            "notes": f"메인 키워드 '{keyword}' 기반으로 LSI/롱테일 키워드를 먼저 생성한 후 제목을 조합 생성",
        }

        # 디버깅용 데이터 저장
        self.save_debug_data(keyword, "title_keywords", result, "json")

        return result

    async def generate_structure_json(
        self, title: str, keyword: str, lsi: List[str], longtail: List[str]
    ) -> Dict[str, Any]:
        """블로그 구조 JSON 생성 (7-10개 H2 섹션, 개요+마무리+FAQ 포함)"""
        import random

        start_time = time.time()
        target_sections = random.randint(7, 10)
        joined = ", ".join((lsi or [])[:5] + (longtail or [])[:3])
        prompt = f"""
제목: {title}
키워드: {keyword}
연관 키워드: {joined}

아래 조건으로 블로그 문서 구조를 JSON으로 생성하세요.
- H2 섹션 수: 정확히 {target_sections}개
- 첫 번째 H2는 반드시 '개요', '소개', '시작하기' 중 하나의 성격을 가진 도입 섹션이어야 합니다 (자유롭게 표현 가능)
- 마지막에서 두 번째 H2는 '정리와 마무리', '요약과 결론', '핵심 포인트' 등 전체 내용을 요약하는 섹션이어야 합니다
- 마지막 H2는 반드시 '자주 묻는 질문', 'FAQ', '궁금한 점들' 등 질문-답변 형태의 섹션이어야 합니다
- 각 H2마다 H3/H4는 유동적으로 0개 이상 포함 가능
- 한국어 제목 사용, 키워드는 자연스럽게 포함

반환 형식 예시:
{{
  "title": "{title}",
  "sections": [
    {{
      "h2": "섹션 제목",
      "h3": ["소제목1", "소제목2"],
      "h4_map": {{"소제목1": ["항목1", "항목2"]}}
    }}
  ]
}}
반드시 위의 JSON 스키마만 출력하세요.
"""

        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        duration = time.time() - start_time
        prompt_tokens = int(len(prompt.split()) * 1.3)
        completion_tokens = int(len(response.choices[0].message.content.split()) * 1.3)

        self.track_llm_call(
            "structure_generation",
            prompt_tokens,
            completion_tokens,
            duration,
            response.choices[0].message.content,
            "7-10개의 H2와 유동 H3/H4 구조 JSON (개요+마무리+FAQ 포함)",
        )

        try:
            import re, json as _json

            response_content = response.choices[0].message.content
            m = re.search(r"\{[\s\S]*\}$", response_content.strip())
            data = _json.loads(m.group(0)) if m else _json.loads(response_content)

            # 디버깅용 데이터 저장
            self.save_debug_data(keyword, "structure", data, "json")

            return data
        except Exception as e:
            print(f"❌ 구조 생성 중 오류: {e}")
            fallback_data = {"title": title, "sections": []}
            self.save_debug_data(
                keyword,
                "structure_error",
                {"error": str(e), "fallback": fallback_data},
                "json",
            )
            return fallback_data

    async def generate_section_with_context(
        self,
        idx: int,
        total: int,
        section: Dict[str, Any],
        keyword: str,
        title: str,
        full_structure_json: Dict[str, Any],
        prev_summary: str = "",
        next_h2: str = "",
        lsi_keywords: List[str] = None,
        longtail_keywords: List[str] = None,
    ) -> Tuple[str, List[str]]:
        """섹션별 콘텐츠 생성 (컨텍스트와 티저 포함, 사용된 키워드 반환)"""
        start_time = time.time()
        structure_str = json.dumps(full_structure_json, ensure_ascii=False)
        ctx = f"이전 섹션 요약: {prev_summary}\n" if prev_summary else ""

        # 티저 문장 가이드 (명시적 표현 금지)
        teaser = (
            f"마지막 문장은 '{next_h2}'와 주제가 맞닿아 있음을 독자가 암시적으로 느끼도록, 구체적 정보 한 조각으로 마무리하세요. \n- 금지 표현: '다음', '다음 섹션', '다음 챕터', '자연스럽게 이어집니다'"
            if next_h2
            else ""
        )

        # 길이 정책: 1섹션 300자 내외, 그 외 500-800자
        length_rule = "분량: 약 300자" if idx == 1 else "분량: 500-800자"

        # LSI/롱테일 키워드를 섹션별로 확률적으로 0-1개 선택
        import random

        section_keywords = []

        combined_keywords = []
        if lsi_keywords:
            combined_keywords.extend(lsi_keywords)
        if longtail_keywords:
            combined_keywords.extend(longtail_keywords)

        # 섹션당 50% 확률로 최대 1개 키워드만 선택 (자연스러운 포함 유도)
        if combined_keywords and random.random() < 0.5:
            section_keywords.append(random.choice(combined_keywords))

        # 키워드 정보 구성 (선택적 사용을 강조)
        keywords_info = ""
        if section_keywords:
            keywords_info += (
                "선택적 키워드 목록 (자연스러운 경우에만 사용):\n"
                + "\n".join([f"- {kw}" for kw in section_keywords])
                + "\n※ 위 키워드들을 억지로 사용하지 마세요. 자연스러운 문맥에서만 사용하거나, 어색하다면 사용하지 않아도 됩니다."
            )

        prompt = f"""
문서 제목: {title}

전체 문서 구조(JSON): {structure_str}
현재 섹션: {idx}/{total} - H2: {section.get('h2')}
{ctx}
요구사항:
1) 한국어 자연스러운 본문
2) H3 소제목 2-3개 포함 가능 (있다면 Markdown ### 사용)
3) 실용적이고 구체적인 내용
4) {length_rule}
5) {teaser}
6) 출력은 "본문만" 작성. 섹션 제목이나 H2(##)를 출력하지 말 것. '섹션 본문:' 같은 안내 문구도 금지.
7) 첫 줄에 섹션 제목을 반복하지 말 것. 필요 시 H3(###)부터 시작.
8) 표 형태로 표현하면 더 효과적인 내용이 있다면 Markdown 표 문법 사용:
   - 비교표: | 항목 | 설명 | 비고 |
   - 단계별 표: | 단계 | 내용 | 팁 |
   - 특징표: | 특징 | 장점 | 단점 |
   - 예시: | 구분 | 방법 | 효과 |
   - 도구 비교: | 도구명 | 장점 | 단점 | 가격 |
   - 단계별 가이드: | 단계 | 설명 | 주의사항 |
   - 팁 정리: | 상황 | 해결방법 | 효과 |
9) {keywords_info}
본문 출력 시작:
"""

        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        duration = time.time() - start_time
        prompt_tokens = int(len(prompt.split()) * 1.3)
        completion_tokens = int(len(response.choices[0].message.content.split()) * 1.3)

        self.track_llm_call(
            f"section_{idx}",
            prompt_tokens,
            completion_tokens,
            duration,
            response.choices[0].message.content,
            f"섹션 {idx} 본문 생성",
        )

        return response.choices[0].message.content.strip(), section_keywords

    async def summarize_previous(self, text: str) -> str:
        """이전 섹션 내용 요약"""
        prompt = f"""
다음 텍스트의 핵심만 2-3문장으로 한국어 요약:
---
{text}
---
요약:
"""
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()

    def generate_table_of_contents(self, sections_content: List[Dict]) -> str:
        """H2 기반 목차 생성 (앵커 링크 포함, 핵심 용어 정리 포함)"""
        toc_lines = ["## 📚 목차\n"]

        # 첫 번째: 핵심 용어 정리
        toc_lines.append("1. [핵심 용어 정리](#핵심-용어-정리)")

        # 나머지 섹션들 (번호 +1)
        for i, section in enumerate(sections_content, 2):  # 2부터 시작
            h2_title = section.get("h2_title", f"섹션 {i}")
            # 마크다운 앵커 링크 생성 (한글 -> 영어, 공백 -> 하이픈)
            anchor_id = (
                h2_title.replace(" ", "-")
                .replace(":", "")
                .replace("?", "")
                .replace("!", "")
                .replace(",", "")
                .replace(".", "")
            )
            toc_lines.append(f"{i}. [{h2_title}](#{anchor_id})")

        return "\n".join(toc_lines) + "\n"

    async def extract_and_explain_terms(self, full_content: str, keyword: str) -> str:
        """콘텐츠에서 어려운 용어 추출 및 설명 생성"""
        start_time = time.time()

        prompt = f"""
다음은 '{keyword}' 주제의 블로그 콘텐츠입니다.
초보자나 중급자가 읽을 때 이해하기 어려울 수 있는 전문 용어를 5-8개 선별하고, 각각을 한 줄로 쉽게 설명해주세요.

=== 블로그 콘텐츠 ===
{full_content[:4000]}  # 토큰 제한을 위해 일부만 사용

=== 작업 지시 ===
1. 위 콘텐츠에서 초보자가 모를 만한 전문 용어를 선별하세요
2. 각 용어를 한 줄(25자 이내)로 간단명료하게 설명하세요
3. 중복 용어나 너무 쉬운 용어는 제외하세요
4. 반드시 아래 형식으로만 출력하세요

=== 출력 형식 (예시) ===
크롤링: 검색엔진이 웹페이지를 읽어가는 과정
백링크: 다른 사이트에서 내 사이트로 연결되는 링크
메타태그: 검색엔진에게 페이지 정보를 알려주는 코드
인덱싱: 검색엔진이 페이지를 데이터베이스에 저장하는 작업
앵커텍스트: 링크에 표시되는 클릭 가능한 텍스트

위 형식으로 용어와 설명만 출력하세요:
"""

        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        # 용어 섹션 포맷팅 (앙커 ID 포함)
        terms_section = '<h2 id="terms-section">📖 핵심 용어 정리</h2>\n\n'
        terms_section += "본문을 읽기 전에 알아두면 좋은 용어들입니다.\n\n"

        # LLM 응답을 파싱하여 용어 정리 (개선된 파싱)
        response_text = response.choices[0].message.content.strip()
        lines = response_text.split("\n")
        terms_found = 0

        for line in lines:
            line = line.strip()
            # 불필요한 텍스트 제거
            if any(
                skip in line.lower()
                for skip in ["출력 형식", "예시", "작업 지시", "블로그 콘텐츠", "==="]
            ):
                continue

            if ":" in line and len(line) > 8:  # 최소 길이 체크 강화
                try:
                    # 콜론으로 분할
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        term = (
                            parts[0]
                            .strip()
                            .replace("**", "")
                            .replace("-", "")
                            .replace("*", "")
                            .strip()
                        )
                        explanation = parts[1].strip()

                        # 유효성 검사
                        if (
                            term
                            and explanation
                            and len(term) > 1
                            and len(explanation) > 5
                            and not term.isdigit()
                        ):  # 숫자만인 용어 제외
                            terms_section += f"**{term}**: {explanation}\n\n"
                            terms_found += 1
                except Exception as e:
                    continue

        # 용어가 하나도 추출되지 않았다면 기본 용어 추가
        if terms_found == 0:
            terms_section += f"**{keyword}**: 이 글의 주요 주제입니다\n\n"
            terms_section += (
                f"**SEO**: 검색엔진 최적화로 웹사이트 노출을 높이는 기법\n\n"
            )
            terms_section += f"**키워드**: 검색할 때 사용하는 단어나 문구\n\n"

        duration = time.time() - start_time
        self.track_llm_call(
            "extract_terms",
            int(len(prompt.split()) * 1.3),
            int(len(response.choices[0].message.content.split()) * 1.3),
            duration,
            f"용어 {terms_found}개 추출",
            "어려운 용어 추출 및 설명",
        )

        return terms_section

    def create_markdown(
        self,
        title: str,
        keyword: str,
        sections_content: List[Dict[str, Any]],
        keywords: Dict[str, List[str]],
        images: Optional[Dict[str, str]] = None,
        table_of_contents: str = "",
        terms_section: str = "",
    ) -> str:
        """마크다운 형식 생성 (목차, 용어 정리, 이미지 포함)"""
        md_content = f"# {title}\n\n"
        # 1. 목차 추가 (최상단)
        if table_of_contents:
            md_content += table_of_contents + "\n"

        # 2. 메인 이미지 추가 (목차 다음)
        if images and "main" in images:
            md_content += f'![{title}]({images["main"]})\n\n'

        # 3. 용어 정리 추가 (이미지 다음)
        if terms_section:
            md_content += terms_section + "\n"

        # 4. 본문 섹션들 (마크다운 헤더로 생성, HTML 변환기에서 ID 추가)
        for i, section in enumerate(sections_content):
            # 마크다운 H2 헤더로 생성
            md_content += f'## {section["h2_title"]}\n\n'

            # 섹션 이미지 추가 (20% 확률로)
            section_image_key = f"section_{i+1}"
            if images and section_image_key in images:
                md_content += (
                    f'![{section["h2_title"]}]({images[section_image_key]})\n\n'
                )

            md_content += f"{section['content']}\n\n"

        return md_content

    async def generate_enhanced_content(
        self, client_tuple, keyword: str, pbn_site
    ) -> Optional[Dict[str, Any]]:
        """고도화된 RAG 파이프라인으로 콘텐츠를 생성합니다."""
        try:
            (client_id, client_name, client_site_url, _, _, _, _, _, _) = client_tuple

            print(f"📝 콘텐츠 생성 시작: {keyword}")
            start_time = time.time()

            # 1. 키워드와 제목 생성
            print("📝 제목 생성 중...")
            tk = await self.generate_title_keywords(keyword)
            print(f"✅ 제목 생성 완료: {tk['title']}")

            # 2. 구조 생성
            print("📋 목차 생성 중...")
            structure = await self.generate_structure_json(
                tk["title"],
                keyword,
                tk.get("lsi_keywords", []),
                tk.get("longtail_keywords", []),
            )
            sections = structure.get("sections", [])
            print(f"✅ 구조 생성 완료: {len(sections)}개 섹션")

            # 3. 섹션별 콘텐츠 생성
            print("📄 섹션 콘텐츠 생성 중...")
            sections_content = []
            prev_summary = ""
            all_section_keywords = []
            total = len(sections)

            for i, sec in enumerate(sections, 1):
                next_h2 = sections[i]["h2"] if i < total else ""
                raw, section_keywords = await self.generate_section_with_context(
                    idx=i,
                    total=total,
                    section=sec,
                    keyword=keyword,
                    title=tk["title"],
                    full_structure_json=structure,
                    prev_summary=prev_summary,
                    next_h2=next_h2,
                    lsi_keywords=tk.get("lsi_keywords", []),
                    longtail_keywords=tk.get("longtail_keywords", []),
                )

                all_section_keywords.extend(section_keywords)

                # 모델 응답 후 정리: 중복 H2/안내문 제거
                content = self._sanitize_section_content(sec.get("h2", ""), raw)
                sections_content.append(
                    {
                        "h2_title": sec.get("h2", f"섹션 {i}"),
                        "content": content,
                        "target_keywords": section_keywords,
                    }
                )

                # 다음을 위한 요약 생성
                prev_summary = await self.summarize_previous(content)

            print(f"✅ 섹션 콘텐츠 생성 완료: {len(sections_content)}개")

            # 4. 목차 생성
            print("📚 목차 생성 중...")
            table_of_contents = self.generate_table_of_contents(sections_content)
            print("✅ 목차 생성 완료")

            # 5. 핵심 용어 정리 생성
            print("🔑 키워드 정의 생성 중...")
            full_content = "\n".join([sec["content"] for sec in sections_content])
            terms_section = await self.extract_and_explain_terms(full_content, keyword)
            print("✅ 핵심 용어 정리 생성 완료")

            # 6. 마크다운 생성
            print("🔗 전체 콘텐츠 조합 중...")
            md_content = self.create_markdown(
                tk["title"],
                keyword,
                sections_content,
                {
                    "lsi_keywords": tk.get("lsi_keywords", []),
                    "longtail_keywords": tk.get("longtail_keywords", []),
                },
                {},  # 이미지는 일단 빈 딕셔너리
                table_of_contents,
                terms_section,
            )

            # 7. HTML 변환
            print("🔄 HTML 변환 중...")
            html_content = self.html_converter.convert_markdown_to_html(md_content)
            print("✅ HTML 변환 완료")

            # 8. 통계 계산
            total_word_count = sum(len(sec["content"]) for sec in sections_content)
            seo_score = (
                len(tk.get("lsi_keywords", [])) * 10
                + len(tk.get("longtail_keywords", [])) * 5
                + total_word_count // 10
            )

            # 결과 구성
            content = {
                "title": tk["title"],
                "content": md_content,
                "html_content": html_content,
                "statistics": {
                    "total_word_count": total_word_count,
                    "total_sections": len(sections_content),
                    "seo_score": seo_score,
                    "content_type": "guide",
                },
                "meta_data": {
                    "target_keyword": keyword,
                    "lsi_keywords": tk.get("lsi_keywords", []),
                    "longtail_keywords": tk.get("longtail_keywords", []),
                },
                "sections": sections_content,
            }

            # 9. 디버깅용 파일 저장
            print("💾 디버깅 데이터 저장 중...")
            self.save_debug_data(keyword, "final_content", content, "json")
            self.save_debug_data(keyword, "blog", md_content, "md")
            self.save_debug_data(keyword, "blog_html", html_content, "html")

            # 10. 콘텐츠 크기 검사
            print("📏 콘텐츠 크기 검사 중...")
            if not self.check_content_size(html_content, max_chars=50000):  # 50KB 제한
                print("⚠️ 콘텐츠가 너무 큽니다. 축소 버전을 생성합니다.")
                # 콘텐츠 축소 로직 (필요시)
                content["html_content"] = self._truncate_content(html_content, 50000)
                content["content"] = self._truncate_content(md_content, 50000)
                print("✅ 콘텐츠 축소 완료")

            duration = time.time() - start_time
            print(f"✅ 콘텐츠 생성 완료: {content['title']}")
            print(f"   📊 단어 수: {content['statistics']['total_word_count']}")
            print(f"   📋 섹션 수: {content['statistics']['total_sections']}")
            print(f"   🎯 SEO 점수: {content['statistics']['seo_score']}")
            print(f"   ⏱️ 생성 시간: {duration:.1f}초")

            return content

        except Exception as e:
            print(f"❌ 콘텐츠 생성 중 오류 발생: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _sanitize_section_content(self, h2_title: str, content: str) -> str:
        """모델 응답에서 중복 H2/안내문 등을 제거하여 깔끔한 본문만 남긴다."""
        import re

        lines = [ln.rstrip() for ln in content.strip().split("\n")]
        sanitized: list[str] = []
        skip_prefixes = {
            "섹션 본문:",
            "본문:",
            "본문 출력:",
            "본문 출력 시작:",
            "내용:",
        }

        for i, ln in enumerate(lines):
            # 첫 부분에서만 강제 제거 규칙 적용
            if i < 5:
                # '섹션 본문:' 류 안내문 제거
                if any(ln.strip().startswith(p) for p in skip_prefixes):
                    continue
                # 중복 H2 제거 (## ...)
                if ln.strip().startswith("## "):
                    continue
                # 섹션 제목 반복 텍스트 제거 (제목만 단독 라인)
                if ln.strip() == h2_title.strip():
                    continue
            sanitized.append(ln)

        # 앞뒤 공백 정리 및 연속 빈 줄 축소
        out = "\n".join(sanitized).strip()
        out = re.sub(r"\n\s*\n\s*\n+", "\n\n", out)
        return out

    def _convert_content_to_html(self, content: Dict[str, Any]) -> str:
        """콘텐츠를 HTML로 변환합니다."""
        try:
            html_content = self.html_converter.convert_markdown_to_html(
                content["content"]
            )
            html_with_meta = self._add_html_metadata(html_content, content)
            return html_with_meta
        except Exception as e:
            print(f"❌ HTML 변환 중 오류 발생: {e}")
            return content["content"]

    def _add_html_metadata(self, html_content: str, content: Dict[str, Any]) -> str:
        """HTML 콘텐츠에 메타데이터를 추가합니다."""
        try:
            stats = content["statistics"]
            meta_comment = f"""<!-- 
콘텐츠 생성 정보:
- 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 타겟 키워드: {content['meta_data']['target_keyword']}
- 단어 수: {stats['total_word_count']}
- 섹션 수: {stats['total_sections']}
- SEO 점수: {stats['seo_score']}
- 콘텐츠 유형: {stats['content_type']}
-->"""

            return meta_comment + "\n" + html_content
        except Exception as e:
            print(f"❌ HTML 메타데이터 추가 중 오류 발생: {e}")
            return html_content

    async def process_client(self, client_tuple, pbn_sites):
        """
        한 클라이언트에 대해 전체 포스팅 작업(키워드 선정, 콘텐츠 생성,
        워드프레스 업로드, DB 기록)을 수행합니다.
        """
        try:
            (client_id, client_name, client_site_url, _, _, _, _, _, _) = client_tuple

            # 키워드 선정
            keyword = get_random_keyword_for_client(client_id)
            if not keyword:
                print(f"클라이언트 {client_id}에 키워드가 없습니다. 건너뜁니다.")
                return False

            # PBN 사이트 랜덤 선택
            pbn_site = random.choice(pbn_sites)
            pbn_site_id, pbn_url, pbn_user, pbn_pass, pbn_app_pass = pbn_site

            print(f"🌐 PBN 사이트 처리 중: {pbn_url}")

            # 고도화된 콘텐츠 생성 (비동기)
            content = await self.generate_enhanced_content(
                client_tuple, keyword, pbn_site
            )
            if not content:
                print(f"❌ 콘텐츠 생성 실패: {keyword}")
                return False

            # 원본 HTML 콘텐츠 사용 (사용자 요청에 따라)
            if "html_content" in content and content["html_content"]:
                print("📄 원본 HTML 콘텐츠 사용 중...")
                post_content = content["html_content"]
                self.save_debug_data(keyword, "original_html", post_content, "html")
                print(
                    f"✅ 원본 HTML 콘텐츠 사용 완료 (크기: {len(post_content)} 바이트)"
                )
            else:
                # 대체 방안: 간단한 HTML 콘텐츠 생성
                try:
                    print("📄 간단한 HTML 콘텐츠 생성 중...")
                    post_content = self._create_simple_html_content(content)
                    self.save_debug_data(keyword, "simple_html", post_content, "html")
                    print(
                        f"✅ 간단한 HTML 콘텐츠 생성 완료 (크기: {len(post_content)} 바이트)"
                    )
                except Exception as e:
                    print(f"❌ 간단한 HTML 생성 실패: {e}")
                    # 최종 대체 방안: 기본 마크다운 콘텐츠 사용
                    try:
                        print("📄 기본 마크다운 콘텐츠 사용 중...")
                        post_content = content["content"].replace("\n", "<br>\n")
                        print(
                            f"✅ 기본 콘텐츠 사용 완료 (크기: {len(post_content)} 바이트)"
                        )
                    except Exception as e2:
                        print(f"❌ 기본 콘텐츠 사용도 실패: {e2}")
                        return False

            # 새로운 지능형 링크 빌딩 시스템 적용
            print("🔗 지능형 링크 빌딩 시작...")
            try:
                # 콘텐츠에서 키워드 정보 추출
                lsi_keywords = content.get("meta_data", {}).get("lsi_keywords", [])
                longtail_keywords = content.get("meta_data", {}).get(
                    "longtail_keywords", []
                )

                # 종합적인 링크 빌딩 수행
                link_result = self.link_builder.build_comprehensive_links(
                    post_content,
                    keyword,
                    client_site_url,
                    lsi_keywords,
                    longtail_keywords,
                )

                # 링크가 삽입된 콘텐츠 사용
                post_content = link_result["content"]
                link_report = link_result["report"]

                # 링크 빌딩 결과 저장
                self.save_debug_data(keyword, "link_report", link_report, "json")

                print(f"✅ 링크 빌딩 완료: 총 {link_report['total_links']}개 링크 삽입")
                print(
                    f"   🎯 클라이언트 링크: {1 if link_report['client_link'] else 0}개"
                )
                print(f"   🔗 내부링크: {len(link_report['internal_links'])}개")
                print(f"   🌐 외부링크: {len(link_report['external_links'])}개")

            except Exception as e:
                print(f"⚠️ 링크 빌딩 시스템 오류: {e}")
                print("   → 기존 방식으로 클라이언트 링크만 삽입합니다.")
                # 백업: 기존 방식으로 클라이언트 링크만 삽입
                post_content = insert_anchor_text(
                    post_content, keyword, client_site_url
                )

            # 워드프레스용 콘텐츠 정리
            print("🔧 워드프레스 호환성을 위한 콘텐츠 정리...")
            post_content = self._clean_content_for_wordpress(post_content)
            self.save_debug_data(keyword, "cleaned_content", post_content, "html")

            # 최종 업로드용 콘텐츠 크기 재검사
            print("🔍 최종 업로드 전 콘텐츠 검사...")
            if not self.check_content_size(
                post_content, max_chars=30000
            ):  # 더 보수적인 제한
                print("⚠️ 업로드용 콘텐츠가 너무 큽니다. 축소합니다.")
                post_content = self._truncate_content(post_content, 30000)
                self.save_debug_data(keyword, "truncated_content", post_content, "html")

            # 워드프레스 REST API 연결 테스트
            print("🔗 워드프레스 REST API 연결 테스트 중...")
            try:
                wp_api_url = f"{pbn_url.rstrip('/')}/wp-json/wp/v2"
                print(f"   📡 REST API URL: {wp_api_url}")

                # 간단한 연결 테스트 (인증 헤더로 사용자 정보 확인)
                import requests

                credentials = f"{pbn_user}:{pbn_app_pass}"
                token = base64.b64encode(credentials.encode())
                headers = {
                    "Authorization": f"Basic {token.decode('utf-8')}",
                    "Content-Type": "application/json",
                }

                # 사용자 정보 확인으로 연결 테스트 (타임아웃 1분)
                response = requests.get(
                    f"{wp_api_url}/users/me", headers=headers, timeout=60
                )
                if response.status_code == 200:
                    user_info = response.json()
                    print(
                        f"   ✅ REST API 연결 성공 - 사용자: {user_info.get('name', 'N/A')}"
                    )
                else:
                    print(f"   ⚠️ REST API 연결 확인 불가 - HTTP {response.status_code}")
                    # 연결 실패해도 계속 진행 (권한 문제일 수 있음)
            except Exception as e:
                print(f"   ⚠️ REST API 연결 테스트 실패: {e}")
                print("   → 포스팅은 계속 시도합니다.")

            # 워드프레스에 포스팅 (재시도 로직 포함)
            print("📤 워드프레스에 포스팅 시도 중...")

            # 현재 PBN 사이트에서 시도, 실패 시 다른 랜덤 PBN에서 1번 재시도
            success = self._try_posting_with_retry(
                content,
                post_content,
                keyword,
                client_id,
                client_name,
                client_site_url,
                current_pbn_site=(
                    pbn_site_id,
                    pbn_url,
                    pbn_user,
                    pbn_pass,
                    pbn_app_pass,
                ),
            )

            if success:
                return True
            else:
                print(f"❌ PBN 재시도 포스팅 실패")
                # 실패한 콘텐츠도 디버깅용으로 저장
                self.save_debug_data(
                    keyword,
                    "failed_content",
                    {
                        "title": content["title"],
                        "content": post_content,
                        "error": "PBN 재시도 포스팅 실패 (최대 2번 시도)",
                    },
                    "json",
                )
                return False

        except Exception as e:
            print(f"[ERROR] {client_name} / {pbn_url} 처리 중 예외 발생: {e}")
            print("→ 이번 포스팅 건너뛰고 계속 진행합니다.\n")
            return False

    def update_client_status(self, client_id_set):
        """작업 후 각 클라이언트의 remaining_days를 업데이트합니다."""
        for c_id in client_id_set:
            info = view_client_status(c_id)
            if info is None:
                continue
            built_count = info["built_count"]
            total_backlinks = info["remaining_count"] + built_count
            if built_count >= total_backlinks or info["remaining_days"] - 1 <= 0:
                move_client_to_completed(c_id)
                print(f"클라이언트 {c_id} 작업 완료 (백링크 목표 달성 또는 기간 만료).")
            else:
                update_client_info(c_id, remaining_days=info["remaining_days"] - 1)

    async def run_automated_campaign(self):
        """자동화된 백링크 캠페인을 실행합니다."""
        print("🚀 자동화된 백링크 캠페인 시작")
        print("=" * 50)

        # 1. 활성 클라이언트 조회 및 로그 출력
        active_clients = self.load_active_clients_and_log()
        if not active_clients:
            return

        # 2. 오늘 작업 대상 day_list와 업데이트할 client_id_set 구성
        day_list, client_id_set = self.prepare_day_list(active_clients)

        # PBN 사이트 목록 조회
        pbn_sites = get_all_pbn_sites()
        if not pbn_sites:
            print("PBN 사이트 정보가 없습니다.")
            return

        print(f"📊 총 {len(pbn_sites)}개의 PBN 사이트를 찾았습니다.")
        print(f"👥 총 {len(active_clients)}명의 클라이언트를 찾았습니다.")
        print(f"📝 오늘 처리할 총 작업 수: {len(day_list)}")

        # 3. 각 클라이언트에 대해 포스팅 작업 수행
        successful_posts = 0
        for idx, client_tuple in enumerate(day_list, start=1):
            success = await self.process_client(client_tuple, pbn_sites)
            result_text = "성공" if success else "실패"
            print(f"[{idx}/{len(day_list)}] 처리 결과: {result_text}")
            if success:
                successful_posts += 1

        # 4. 작업 후 클라이언트 상태 업데이트
        self.update_client_status(client_id_set)

        # 최종 결과 출력
        print("\n" + "=" * 50)
        print("🎉 자동화된 백링크 캠페인 완료")
        print(f"📊 총 포스트 수: {len(day_list)}")
        print(f"✅ 성공한 포스트: {successful_posts}")
        print(f"❌ 실패한 포스트: {len(day_list) - successful_posts}")
        print(
            f"📈 성공률: {(successful_posts/len(day_list)*100):.1f}%"
            if len(day_list) > 0
            else "0%"
        )
        print("오늘 작업을 모두 마쳤습니다.")

    # ========== 관리자 메뉴 기능들 ==========

    def display_menu(self):
        print("\n========== 고도화된 PBN 백링크 자동화 시스템 ==========")
        print("1. 자동화된 백링크 캠페인 실행")
        print("2. PBN 사이트 추가")
        print("3. PBN 사이트 조회")
        print("4. PBN 사이트 삭제")
        print("5. 클라이언트 추가")
        print("6. 클라이언트 조회")
        print("7. 클라이언트 정보 수정")
        print("8. 클라이언트 남은 기간 단축/연장")
        print("9. 클라이언트 작업 완료 처리")
        print("10. 완료된 클라이언트 조회")
        print("11. 모든 테이블 상태 확인")
        print("12. 특정 클라이언트 상태 조회")
        print("13. 특정 클라이언트 일시정지/재개")
        print("14. 모든 클라이언트 일시정지")
        print("15. 모든 클라이언트 재개")
        print("16. 백링크 보고서 엑셀로 저장")
        print("17. 특정 클라이언트 키워드 조회")
        print("18. 중복 클라이언트 제거")
        print("19. 활성 클라이언트 목록 조회")
        print("20. 포스트 기록 조회")
        print("21. 🔗 PBN 콘텐츠 크롤링 (링크 데이터베이스 구축)")
        print("22. 📊 PBN 콘텐츠 데이터베이스 통계 조회")
        print("23. 🔍 키워드 기반 유사 포스트 검색 테스트")
        print("q. 종료")
        print("==================================================")

    def add_pbn_site_prompt(self):
        site_url = input("PBN 사이트 URL 입력: ")
        username = input("PBN 사이트 관리자 아이디 입력: ")
        password = input("PBN 사이트 관리자 비밀번호 입력: ")
        app_password = input("PBN 사이트 응용프로그램 비밀번호 입력: ")
        add_pbn_site(site_url, username, password, app_password)
        print("PBN 사이트 추가 완료")

    def delete_pbn_site_prompt(self):
        view_pbn_sites()
        site_id = int(input("삭제할 PBN site_id 입력: "))
        delete_record_by_id("pbn_sites", site_id, "site_id")

    def add_client_prompt(self):
        client_name = input("클라이언트 이름: ").strip()
        site_url = input("클라이언트 사이트 주소: ").strip()
        total_backlinks = int(
            input_with_validation(
                "총 백링크 수: ", is_positive_int, "양의 정수를 입력하세요."
            )
        )
        remaining_days = int(
            input_with_validation(
                "업로드 기간(일): ", is_positive_int, "양의 정수를 입력하세요."
            )
        )
        daily_min = int(
            input_with_validation(
                "일일 최소 백링크 수(daily_min): ",
                is_positive_int,
                "양의 정수를 입력하세요.",
            )
        )
        daily_max = int(
            input_with_validation(
                "일일 최대 백링크 수(daily_max): ",
                is_positive_int,
                "양의 정수를 입력하세요.",
            )
        )
        if daily_min > daily_max:
            print("일일 최소수량이 최대수량보다 클 수 없습니다. 다시 입력하세요.")
            return

        client_id = add_client(
            client_name, site_url, total_backlinks, remaining_days, daily_min, daily_max
        )
        print(f"클라이언트 '{client_name}' 추가 완료. (ID: {client_id})")

        # 키워드 입력 부분
        keyword_str = input("추가할 키워드들(쉼표로 구분): ").strip()
        if keyword_str:
            for kw in keyword_str.split(","):
                add_client_keyword(client_id, kw.strip())
        print("키워드 추가 완료.")

    def update_client_prompt(self):
        view_clients()
        client_id = int(input("수정할 클라이언트 ID: "))
        print("\n수정할 내용을 선택하세요:")
        print("1. 클라이언트 이름")
        print("2. 사이트 주소")
        print("3. 키워드 입력")
        print("4. 백링크 수량(total_backlinks)")
        print("5. 남은 기간(단축/연장)")
        print("6. 일일 최소/최대 백링크 값(daily_min, daily_max) 수정")
        choice = input("선택: ").strip()

        if choice == "1":
            new_value = input("새 클라이언트 이름: ").strip()
            update_client_info(client_id, client_name=new_value)
        elif choice == "2":
            new_value = input("새 사이트 주소: ").strip()
            update_client_info(client_id, site_url=new_value)
        elif choice == "3":
            new_keywords = input("추가할 키워드(쉼표 구분): ").strip()
            if new_keywords:
                for kw in new_keywords.split(","):
                    add_client_keyword(client_id, kw.strip())
            print("키워드 추가 완료.")
        elif choice == "4":
            new_total = int(
                input_with_validation("새 백링크 수(양의 정수): ", is_positive_int)
            )
            update_client_info(client_id, total_backlinks=new_total)
        elif choice == "5":
            new_days = int(input_with_validation("새 남은 기간(일): ", is_positive_int))
            update_client_info(client_id, remaining_days=new_days)
        elif choice == "6":
            new_min = int(
                input_with_validation("새 일일 최소 백링크 수: ", is_positive_int)
            )
            new_max = int(
                input_with_validation("새 일일 최대 백링크 수: ", is_positive_int)
            )
            if new_min > new_max:
                print("최소수량이 최대수량보다 클 수 없습니다. 취소합니다.")
                return
            update_client_info(client_id, daily_min=new_min, daily_max=new_max)
            print("daily_min, daily_max 수정 완료.")
        else:
            print("잘못된 선택입니다.")

        print("클라이언트 정보 수정 완료")

    def extend_or_reduce_days_prompt(self):
        view_clients()
        client_id = int(input("기간 변경할 클라이언트 ID: "))
        change_days = int(input("변경할 일수(+는 연장, -는 단축): "))
        status = view_client_status(client_id)
        if not status:
            print("존재하지 않는 클라이언트입니다.")
            return
        new_days = status["remaining_days"] + change_days
        if new_days < 1:
            print("남은 기간은 1일 이상이어야 합니다.")
            return
        update_client_info(client_id, remaining_days=new_days)
        print(f"클라이언트 {client_id}의 남은 기간 변경 완료: {new_days}일")

    def complete_client_prompt(self):
        view_clients()
        client_id = int(input("작업 완료 처리할 클라이언트 ID: "))
        move_client_to_completed(client_id)
        print("클라이언트 작업 완료 처리 완료")

    def view_client_status_prompt(self):
        view_clients()
        client_id = int(input("상태 조회할 클라이언트 ID: "))
        status = view_client_status(client_id)
        if status:
            print(f"\n클라이언트 ID: {status['client_id']}")
            print(f"이름: {status['client_name']}")
            print(f"구축된 백링크 수: {status['built_count']}")
            print(f"남은 백링크 수: {status['remaining_count']}")
            print(f"남은 기간: {status['remaining_days']} 일")
        else:
            print("해당 클라이언트를 찾을 수 없습니다.")

    def pause_resume_client_prompt(self):
        view_clients()
        client_id = int(input("일시 정지/재개할 클라이언트 ID: "))
        action = input("일시정지(pause) / 재개(resume): ").strip().lower()
        if action == "pause":
            pause_client(client_id)
            print(f"{client_id} 클라이언트 일시정지 완료")
        elif action == "resume":
            resume_client(client_id)
            print(f"{client_id} 클라이언트 재개 완료")
        else:
            print("잘못된 명령입니다.")

    def view_client_keywords_prompt(self):
        """특정 클라이언트의 키워드를 확인하는 간단한 메뉴"""
        view_clients()
        cid = input_with_validation(
            "키워드를 조회할 클라이언트 ID: ", lambda x: x.isdigit()
        )
        cid = int(cid)
        keywords = get_client_keywords(cid)
        if keywords:
            print(f"클라이언트 {cid}의 키워드 목록:")
            for kw in keywords:
                print(" -", kw)
        else:
            print("등록된 키워드가 없습니다.")

    def crawl_pbn_content_prompt(self):
        """PBN 콘텐츠 크롤링 실행"""
        print("🕷️ PBN 콘텐츠 크롤링을 시작합니다...")
        print("⚠️ 이 작업은 시간이 오래 걸릴 수 있습니다.")

        confirm = input("계속하시겠습니까? (y/N): ").strip().lower()
        if confirm != "y":
            print("크롤링을 취소했습니다.")
            return

        try:
            # 동시 실행 수 설정
            max_workers = input("동시 크롤링 사이트 수 (기본값: 3): ").strip()
            max_workers = int(max_workers) if max_workers.isdigit() else 3

            # 크롤링 실행
            results = self.pbn_crawler.crawl_all_pbn_sites(max_workers=max_workers)

            print("\n🎉 크롤링 완료!")
            print(f"📊 처리된 사이트: {results['total_sites']}개")
            print(f"✅ 성공한 사이트: {results['successful_sites']}개")
            print(f"📄 총 수집된 포스트: {results['total_posts']:,}개")
            print(f"💾 저장된 포스트: {results['saved_posts']:,}개")

        except Exception as e:
            print(f"❌ 크롤링 중 오류 발생: {e}")

    def view_pbn_database_stats_prompt(self):
        """PBN 콘텐츠 데이터베이스 통계 조회"""
        try:
            stats = self.pbn_crawler.get_database_stats()

            print("\n📊 PBN 콘텐츠 데이터베이스 통계")
            print("=" * 50)
            print(f"📄 총 포스트 수: {stats['total_posts']:,}개")
            print(f"🌐 총 사이트 수: {stats['total_sites']}개")

            if stats["site_stats"]:
                print(f"\n📋 사이트별 포스트 수 (상위 10개):")
                for site_url, post_count in stats["site_stats"][:10]:
                    print(f"   • {site_url}: {post_count:,}개")

            if stats["recent_crawls"]:
                print(f"\n🕰️ 최근 크롤링 로그:")
                for site_url, total, success, status, created_at in stats[
                    "recent_crawls"
                ]:
                    print(
                        f"   • {site_url}: {success}/{total} ({status}) - {created_at}"
                    )

        except Exception as e:
            print(f"❌ 통계 조회 중 오류 발생: {e}")

    def test_similar_posts_prompt(self):
        """키워드 기반 유사 포스트 검색 테스트"""
        try:
            # 키워드 입력
            keywords_input = input(
                "검색할 키워드들을 입력하세요 (쉼표로 구분): "
            ).strip()
            if not keywords_input:
                print("키워드가 입력되지 않았습니다.")
                return

            keywords = [kw.strip() for kw in keywords_input.split(",")]

            # 검색 옵션
            limit_input = input("최대 결과 수 (기본값: 10): ").strip()
            limit = int(limit_input) if limit_input.isdigit() else 10

            similarity_input = input(
                "최소 유사도 점수 (0.0-1.0, 기본값: 0.3): "
            ).strip()
            min_similarity = float(similarity_input) if similarity_input else 0.3

            print(f"\n🔍 '{', '.join(keywords)}' 키워드로 유사한 포스트 검색 중...")

            # AI 기반 유사도 검사 시도
            if (
                hasattr(self, "similarity_system")
                and self.similarity_system is not None
                and self.similarity_system.faiss_index is not None
                and self.similarity_system.similarity_model is not None
            ):
                print("   🧠 AI 기반 FAISS 시스템 사용 중...")

                # 디버깅: similarity_system 내부 상태 확인
                print(
                    f"   🔍 디버깅 - faiss_index: {self.similarity_system.faiss_index is not None}"
                )
                print(
                    f"   🔍 디버깅 - similarity_model: {self.similarity_system.similarity_model is not None}"
                )
                print(
                    f"   🔍 디버깅 - post_metadata: {len(self.similarity_system.post_metadata) if self.similarity_system.post_metadata else 0}개"
                )

                # 검색 실행 (AI 기반 FAISS 시스템 사용)
                similar_posts = self.similarity_system.find_similar_posts_fast(
                    keywords,
                    limit=limit,
                    min_similarity=min_similarity,
                    random_selection=True,
                )
            else:
                print("   ⚠️ AI 유사도 시스템이 없어서 기본 키워드 매칭을 사용합니다.")
                print("   🔄 AI 시스템 강제 재초기화 시도 중...")
                try:
                    print("   🤖 ImprovedSimilaritySystem 강제 초기화 중...")
                    self.similarity_system = ImprovedSimilaritySystem()
                    print("   ✅ AI 유사도 시스템 재초기화 완료")

                    # 재초기화 후 상태 확인
                    print(
                        f"   🔍 재초기화 확인 - faiss_index: {self.similarity_system.faiss_index is not None}"
                    )
                    print(
                        f"   🔍 재초기화 확인 - similarity_model: {self.similarity_system.similarity_model is not None}"
                    )
                    print(
                        f"   🔍 재초기화 확인 - post_metadata: {len(self.similarity_system.post_metadata) if self.similarity_system.post_metadata else 0}개"
                    )

                    similar_posts = self.similarity_system.find_similar_posts_fast(
                        keywords,
                        limit=limit,
                        min_similarity=min_similarity,
                        random_selection=True,
                    )
                except Exception as e:
                    print(f"   ❌ AI 시스템 재초기화 실패: {e}")
                    print("   🔍 상세 오류 정보:")
                    import traceback

                    traceback.print_exc()
                    print("   🔄 기본 키워드 매칭으로 대체합니다.")
                    # 기본 키워드 매칭 방식 사용
                    similar_posts = self.pbn_crawler.find_similar_posts(
                        keywords, limit=limit, min_similarity=min_similarity
                    )

            if similar_posts:
                print(f"\n📋 검색 결과 ({len(similar_posts)}개):")
                print("=" * 80)

                for i, post in enumerate(similar_posts, 1):
                    similarity = post.get("similarity_score", 0)
                    print(f"{i}. 📄 {post['title']}")
                    print(f"   🔗 {post['url']}")
                    print(f"   📊 유사도: {similarity:.3f}")
                    print(f"   🌐 사이트: {post['site_url']}")
                    print(f"   📝 단어 수: {post.get('word_count', 0)}")
                    print("-" * 80)
            else:
                print("❌ 유사한 포스트를 찾을 수 없습니다.")
                print("   💡 팁: 다른 키워드를 시도하거나 유사도 점수를 낮춰보세요.")

        except Exception as e:
            print(f"❌ 검색 중 오류 발생: {e}")

    def main(self):
        """메인 실행 함수"""
        while True:
            self.display_menu()
            choice = input("작업 선택(q 종료): ").lower()

            if choice == "1":
                asyncio.run(self.run_automated_campaign())
            elif choice == "2":
                self.add_pbn_site_prompt()
            elif choice == "3":
                view_pbn_sites()
            elif choice == "4":
                self.delete_pbn_site_prompt()
            elif choice == "5":
                self.add_client_prompt()
            elif choice == "6":
                view_clients()
            elif choice == "7":
                self.update_client_prompt()
            elif choice == "8":
                self.extend_or_reduce_days_prompt()
            elif choice == "9":
                self.complete_client_prompt()
            elif choice == "10":
                view_completed_clients()
            elif choice == "11":
                show_all_tables()
            elif choice == "12":
                self.view_client_status_prompt()
            elif choice == "13":
                self.pause_resume_client_prompt()
            elif choice == "14":
                pause_all_clients()
                print("모든 클라이언트 일시정지 완료")
            elif choice == "15":
                resume_all_clients()
                print("모든 클라이언트 재개 완료")
            elif choice == "16":
                output_file = input("엑셀 파일명(기본: backlink_report.xlsx): ").strip()
                if not output_file:
                    output_file = "backlink_report.xlsx"
                save_all_backlinks_to_excel(output_file)
            elif choice == "17":
                self.view_client_keywords_prompt()
            elif choice == "18":
                remove_duplicate_clients()
            elif choice == "19":
                self.load_active_clients_and_log()
            elif choice == "20":
                posts = fetch_all_posts()
                if posts:
                    print("\n📋 포스트 기록:")
                    for post in posts[:10]:  # 최근 10개만 표시
                        print(
                            f"ID: {post[0]}, 클라이언트: {post[2]}, 키워드: {post[4]}"
                        )
                    if len(posts) > 10:
                        print(f"... 총 {len(posts)}개의 포스트가 있습니다.")
                else:
                    print("포스트 기록이 없습니다.")
            elif choice == "21":
                self.crawl_pbn_content_prompt()
            elif choice == "22":
                self.view_pbn_database_stats_prompt()
            elif choice == "23":
                self.test_similar_posts_prompt()
            elif choice == "q":
                print("👋 시스템을 종료합니다.")
                sys.exit(0)
            else:
                print("❌ 잘못된 선택입니다. 다시 시도하세요.")


def main():
    """메인 실행 함수"""
    print("🚀 고도화된 PBN 백링크 자동화 시스템 v2.0")
    print("=" * 60)

    # 시스템 초기화
    system = EnhancedPBNSystem()

    # 메인 메뉴 실행
    system.main()


if __name__ == "__main__":
    main()
