# v1.0 - 고도화된 목차 생성기 (PBN 시스템용)
# SEO 최적화된 목차 및 섹션 구조 생성

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

class SectionType(Enum):
    """섹션 유형 정의"""
    INTRODUCTION = "introduction"
    MAIN_CONTENT = "main_content"
    TIPS = "tips"
    EXAMPLES = "examples"
    CONCLUSION = "conclusion"
    FAQ = "faq"
    RESOURCES = "resources"

@dataclass
class Section:
    """섹션 정보"""
    title: str
    content: str
    section_type: SectionType
    order: int
    anchor: str
    keywords: List[str] = None
    word_count: int = 0

@dataclass
class OutlineConfig:
    """목차 생성 설정"""
    min_sections: int = 7
    max_sections: int = 10
    include_faq: bool = True
    include_tips: bool = True
    include_examples: bool = True
    target_word_count: int = 2000
    keyword_density: float = 0.02

class AdvancedOutlineGenerator:
    """고도화된 목차 생성기"""
    
    def __init__(self, config: OutlineConfig = None):
        self.config = config or OutlineConfig()
        self.section_templates = {
            SectionType.INTRODUCTION: [
                "{keyword}에 대한 완벽한 이해",
                "{keyword}란 무엇인가?",
                "{keyword}의 모든 것",
                "{keyword} 시작하기"
            ],
            SectionType.MAIN_CONTENT: [
                "{keyword}의 핵심 원리",
                "{keyword} 작동 방식",
                "{keyword}의 주요 특징",
                "{keyword} 이해하기"
            ],
            SectionType.TIPS: [
                "{keyword} 성공을 위한 핵심 팁",
                "{keyword} 전문가 조언",
                "{keyword} 효과적인 방법",
                "{keyword} 실전 노하우"
            ],
            SectionType.EXAMPLES: [
                "{keyword} 실제 사례",
                "{keyword} 성공 스토리",
                "{keyword} 구체적 예시",
                "{keyword} 실제 적용 사례"
            ],
            SectionType.CONCLUSION: [
                "{keyword} 마무리",
                "{keyword} 요약",
                "{keyword} 결론",
                "{keyword} 마지막 조언"
            ],
            SectionType.FAQ: [
                "{keyword} 자주 묻는 질문",
                "{keyword} FAQ",
                "{keyword} 궁금한 점들",
                "{keyword} 질문과 답변"
            ],
            SectionType.RESOURCES: [
                "{keyword} 유용한 자료",
                "{keyword} 추가 리소스",
                "{keyword} 참고 자료",
                "{keyword} 더 알아보기"
            ]
        }
    
    def generate_outline(self, 
                        topic: str, 
                        target_keyword: str,
                        lsi_keywords: List[str] = None,
                        content_type: str = "guide") -> Dict[str, any]:
        """
        SEO 최적화된 목차를 생성합니다.
        
        Args:
            topic: 주제
            target_keyword: 타겟 키워드
            lsi_keywords: LSI 키워드 목록
            content_type: 콘텐츠 유형 (guide, tutorial, review, news)
            
        Returns:
            목차 정보 딕셔너리
        """
        # 섹션 구조 생성
        sections = self._generate_sections(topic, target_keyword, lsi_keywords, content_type)
        
        # 목차 HTML 생성
        toc_html = self._generate_toc_html(sections)
        
        # 앵커 링크 생성
        anchors = self._generate_anchors(sections)
        
        return {
            "sections": sections,
            "toc_html": toc_html,
            "anchors": anchors,
            "total_sections": len(sections),
            "estimated_word_count": self._estimate_word_count(sections),
            "seo_score": self._calculate_seo_score(sections, target_keyword)
        }
    
    def _generate_sections(self, 
                          topic: str, 
                          target_keyword: str,
                          lsi_keywords: List[str],
                          content_type: str) -> List[Section]:
        """섹션들을 생성합니다."""
        sections = []
        
        # 콘텐츠 유형별 섹션 순서 정의
        if content_type == "guide":
            section_order = [
                SectionType.INTRODUCTION,
                SectionType.MAIN_CONTENT,
                SectionType.TIPS,
                SectionType.EXAMPLES,
                SectionType.FAQ,
                SectionType.CONCLUSION
            ]
        elif content_type == "tutorial":
            section_order = [
                SectionType.INTRODUCTION,
                SectionType.MAIN_CONTENT,
                SectionType.TIPS,
                SectionType.EXAMPLES,
                SectionType.RESOURCES,
                SectionType.CONCLUSION
            ]
        else:  # review, news
            section_order = [
                SectionType.INTRODUCTION,
                SectionType.MAIN_CONTENT,
                SectionType.EXAMPLES,
                SectionType.TIPS,
                SectionType.CONCLUSION
            ]
        
        # 각 섹션 생성
        for i, section_type in enumerate(section_order):
            if i >= self.config.max_sections:
                break
                
            section = self._create_section(
                section_type, topic, target_keyword, lsi_keywords, i
            )
            if section:
                sections.append(section)
        
        return sections
    
    def _create_section(self, 
                       section_type: SectionType,
                       topic: str,
                       target_keyword: str,
                       lsi_keywords: List[str],
                       order: int) -> Optional[Section]:
        """개별 섹션을 생성합니다."""
        
        # 섹션 제목 생성
        title = self._generate_section_title(section_type, target_keyword, lsi_keywords)
        
        # 앵커 생성
        anchor = self._generate_anchor(title)
        
        # 키워드 추출
        keywords = self._extract_keywords(title, target_keyword, lsi_keywords)
        
        # 예상 단어 수 계산
        word_count = self._estimate_section_word_count(section_type)
        
        return Section(
            title=title,
            content="",  # 실제 콘텐츠는 별도 생성
            section_type=section_type,
            order=order,
            anchor=anchor,
            keywords=keywords,
            word_count=word_count
        )
    
    def _generate_section_title(self, 
                               section_type: SectionType,
                               target_keyword: str,
                               lsi_keywords: List[str]) -> str:
        """섹션 제목을 생성합니다."""
        templates = self.section_templates.get(section_type, [])
        
        if not templates:
            return f"{target_keyword} 섹션"
        
        # LSI 키워드가 있으면 활용
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            template = templates[0].replace("{keyword}", f"{target_keyword} {lsi}")
        else:
            template = templates[0].replace("{keyword}", target_keyword)
        
        return template
    
    def _generate_anchor(self, title: str) -> str:
        """앵커 링크를 생성합니다."""
        # 한글을 영문으로 변환 (간단한 매핑)
        korean_to_english = {
            "에": "e", "의": "ui", "을": "eul", "를": "reul",
            "이": "i", "가": "ga", "은": "eun", "는": "neun",
            "에서": "eseo", "로": "ro", "으로": "euro",
            "와": "wa", "과": "gwa", "도": "do", "만": "man",
            "부터": "buteo", "까지": "kkaji", "에서": "eseo",
            "로부터": "robuteo", "에게": "ege", "한테": "hante",
            "보다": "boda", "처럼": "cheoreom", "같이": "gachi"
        }
        
        # 특수문자 제거 및 소문자 변환
        anchor = title.lower()
        for korean, english in korean_to_english.items():
            anchor = anchor.replace(korean, english)
        
        # 공백을 하이픈으로 변환
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'[-\s]+', '-', anchor)
        anchor = anchor.strip('-')
        
        return anchor
    
    def _extract_keywords(self, 
                         title: str, 
                         target_keyword: str,
                         lsi_keywords: List[str]) -> List[str]:
        """섹션에서 키워드를 추출합니다."""
        keywords = [target_keyword]
        
        if lsi_keywords:
            keywords.extend(lsi_keywords[:2])  # 상위 2개만 사용
        
        return keywords
    
    def _estimate_section_word_count(self, section_type: SectionType) -> int:
        """섹션별 예상 단어 수를 계산합니다."""
        word_counts = {
            SectionType.INTRODUCTION: 300,
            SectionType.MAIN_CONTENT: 500,
            SectionType.TIPS: 400,
            SectionType.EXAMPLES: 350,
            SectionType.CONCLUSION: 200,
            SectionType.FAQ: 300,
            SectionType.RESOURCES: 150
        }
        
        return word_counts.get(section_type, 300)
    
    def _generate_toc_html(self, sections: List[Section]) -> str:
        """목차 HTML을 생성합니다."""
        toc_html = '<div class="table-of-contents">\n'
        toc_html += '<h3>목차</h3>\n'
        toc_html += '<ul>\n'
        
        for section in sections:
            toc_html += f'<li><a href="#{section.anchor}">{section.title}</a></li>\n'
        
        toc_html += '</ul>\n'
        toc_html += '</div>\n'
        
        return toc_html
    
    def _generate_anchors(self, sections: List[Section]) -> Dict[str, str]:
        """앵커 링크 맵을 생성합니다."""
        anchors = {}
        for section in sections:
            anchors[section.title] = section.anchor
        return anchors
    
    def _estimate_word_count(self, sections: List[Section]) -> int:
        """전체 예상 단어 수를 계산합니다."""
        return sum(section.word_count for section in sections)
    
    def _calculate_seo_score(self, sections: List[Section], target_keyword: str) -> int:
        """SEO 점수를 계산합니다."""
        score = 0
        
        # 섹션 수 점수
        section_count = len(sections)
        if 7 <= section_count <= 10:
            score += 20
        elif 5 <= section_count <= 12:
            score += 10
        
        # 타겟 키워드 포함 섹션 수
        keyword_sections = sum(1 for section in sections 
                             if target_keyword.lower() in section.title.lower())
        score += keyword_sections * 5
        
        # H2 태그 구조 점수
        if section_count >= 5:
            score += 15
        
        return score

# 사용 예시
if __name__ == "__main__":
    # 목차 생성기 설정
    config = OutlineConfig(
        min_sections=7,
        max_sections=10,
        include_faq=True,
        include_tips=True,
        target_word_count=2000
    )
    
    # 목차 생성기 인스턴스 생성
    generator = AdvancedOutlineGenerator(config)
    
    # 목차 생성
    outline = generator.generate_outline(
        topic="성공하는 방법",
        target_keyword="마케팅",
        lsi_keywords=["디지털", "온라인", "전략"],
        content_type="guide"
    )
    
    # 결과 출력
    print("=== 생성된 목차 ===")
    print(f"총 섹션 수: {outline['total_sections']}")
    print(f"예상 단어 수: {outline['estimated_word_count']}")
    print(f"SEO 점수: {outline['seo_score']}")
    print()
    
    print("=== 섹션 목록 ===")
    for i, section in enumerate(outline['sections'], 1):
        print(f"{i}. {section.title}")
        print(f"   앵커: #{section.anchor}")
        print(f"   유형: {section.section_type.value}")
        print(f"   예상 단어 수: {section.word_count}")
        print()
    
    print("=== 목차 HTML ===")
    print(outline['toc_html'])