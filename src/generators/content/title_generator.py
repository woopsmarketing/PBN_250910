# v1.0 - 고도화된 제목 생성기 (PBN 시스템용)
# SEO 최적화된 제목 생성 및 A/B 테스트 지원

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TitleType(Enum):
    """제목 유형 정의"""
    HOW_TO = "how_to"
    WHAT_IS = "what_is"
    WHY = "why"
    COMPARISON = "comparison"
    LIST = "list"
    TUTORIAL = "tutorial"
    GUIDE = "guide"
    TIPS = "tips"
    REVIEW = "review"
    NEWS = "news"

@dataclass
class TitleConfig:
    """제목 생성 설정"""
    max_length: int = 60
    min_length: int = 30
    include_numbers: bool = True
    include_power_words: bool = True
    include_emotional_triggers: bool = True
    target_keyword: str = ""
    lsi_keywords: List[str] = None
    tone: str = "professional"  # professional, casual, authoritative

class AdvancedTitleGenerator:
    """고도화된 제목 생성기"""
    
    def __init__(self, config: TitleConfig = None):
        self.config = config or TitleConfig()
        self.power_words = [
            "최고의", "완벽한", "궁극의", "전문가", "비밀", "혁신적인",
            "효과적인", "검증된", "실용적인", "필수적인", "핵심"
        ]
        self.emotional_triggers = [
            "놀라운", "충격적인", "놀라운", "놀라운", "놀라운",
            "놀라운", "놀라운", "놀라운", "놀라운", "놀라운"
        ]
        self.number_words = [
            "10가지", "5가지", "7가지", "3가지", "15가지",
            "완벽한", "궁극의", "핵심", "필수", "실용적인"
        ]
    
    def generate_titles(self, 
                       topic: str, 
                       target_keyword: str,
                       lsi_keywords: List[str] = None,
                       num_titles: int = 5) -> List[Dict[str, str]]:
        """
        다양한 유형의 제목들을 생성합니다.
        
        Args:
            topic: 주제
            target_keyword: 타겟 키워드
            lsi_keywords: LSI 키워드 목록
            num_titles: 생성할 제목 개수
            
        Returns:
            제목 정보 딕셔너리 리스트
        """
        titles = []
        
        # 다양한 제목 유형별로 생성
        title_types = [
            TitleType.HOW_TO,
            TitleType.WHAT_IS,
            TitleType.WHY,
            TitleType.LIST,
            TitleType.GUIDE
        ]
        
        for i, title_type in enumerate(title_types[:num_titles]):
            title = self._generate_title_by_type(
                topic, target_keyword, lsi_keywords, title_type
            )
            
            if title:
                titles.append({
                    "title": title,
                    "type": title_type.value,
                    "length": len(title),
                    "seo_score": self._calculate_seo_score(title, target_keyword),
                    "emotional_score": self._calculate_emotional_score(title)
                })
        
        # SEO 점수 기준으로 정렬
        titles.sort(key=lambda x: x["seo_score"], reverse=True)
        
        return titles
    
    def _generate_title_by_type(self, 
                               topic: str, 
                               target_keyword: str,
                               lsi_keywords: List[str],
                               title_type: TitleType) -> str:
        """제목 유형별로 제목을 생성합니다."""
        
        if title_type == TitleType.HOW_TO:
            return self._generate_how_to_title(topic, target_keyword, lsi_keywords)
        elif title_type == TitleType.WHAT_IS:
            return self._generate_what_is_title(topic, target_keyword, lsi_keywords)
        elif title_type == TitleType.WHY:
            return self._generate_why_title(topic, target_keyword, lsi_keywords)
        elif title_type == TitleType.LIST:
            return self._generate_list_title(topic, target_keyword, lsi_keywords)
        elif title_type == TitleType.GUIDE:
            return self._generate_guide_title(topic, target_keyword, lsi_keywords)
        
        return ""
    
    def _generate_how_to_title(self, topic: str, target_keyword: str, lsi_keywords: List[str]) -> str:
        """How-to 제목 생성"""
        templates = [
            f"{target_keyword} 완벽 가이드: {topic}하는 방법",
            f"전문가가 알려주는 {target_keyword} {topic} 방법",
            f"{target_keyword} {topic}하는 궁극의 가이드",
            f"초보자도 따라할 수 있는 {target_keyword} {topic} 방법"
        ]
        
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            templates.append(f"{target_keyword} {lsi} {topic}하는 방법")
        
        return self._select_best_template(templates, target_keyword)
    
    def _generate_what_is_title(self, topic: str, target_keyword: str, lsi_keywords: List[str]) -> str:
        """What is 제목 생성"""
        templates = [
            f"{target_keyword}란? {topic}에 대한 완벽한 이해",
            f"{target_keyword} {topic}: 모든 것을 알아야 할 것들",
            f"{target_keyword} {topic}의 모든 것 - 전문가 가이드"
        ]
        
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            templates.append(f"{target_keyword} {lsi} {topic}: 완벽 가이드")
        
        return self._select_best_template(templates, target_keyword)
    
    def _generate_why_title(self, topic: str, target_keyword: str, lsi_keywords: List[str]) -> str:
        """Why 제목 생성"""
        templates = [
            f"왜 {target_keyword} {topic}이 중요한가?",
            f"{target_keyword} {topic}의 놀라운 효과와 장점",
            f"{target_keyword} {topic}이 성공의 열쇠인 이유"
        ]
        
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            templates.append(f"왜 {target_keyword} {lsi} {topic}이 필수인가?")
        
        return self._select_best_template(templates, target_keyword)
    
    def _generate_list_title(self, topic: str, target_keyword: str, lsi_keywords: List[str]) -> str:
        """리스트 제목 생성"""
        numbers = ["10가지", "7가지", "5가지", "15가지"]
        templates = []
        
        for num in numbers:
            templates.extend([
                f"{target_keyword} {topic} {num} 방법",
                f"{num} {target_keyword} {topic} 팁과 요령",
                f"{target_keyword} {topic} {num} 핵심 포인트"
            ])
        
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            templates.append(f"{target_keyword} {lsi} {topic} 10가지 방법")
        
        return self._select_best_template(templates, target_keyword)
    
    def _generate_guide_title(self, topic: str, target_keyword: str, lsi_keywords: List[str]) -> str:
        """가이드 제목 생성"""
        templates = [
            f"{target_keyword} {topic} 완벽 가이드",
            f"전문가가 알려주는 {target_keyword} {topic} 가이드",
            f"{target_keyword} {topic} 궁극의 가이드"
        ]
        
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            templates.append(f"{target_keyword} {lsi} {topic} 전문 가이드")
        
        return self._select_best_template(templates, target_keyword)
    
    def _select_best_template(self, templates: List[str], target_keyword: str) -> str:
        """가장 적합한 템플릿을 선택합니다."""
        best_template = ""
        best_score = 0
        
        for template in templates:
            score = self._calculate_seo_score(template, target_keyword)
            if score > best_score and len(template) <= self.config.max_length:
                best_score = score
                best_template = template
        
        return best_template or templates[0]
    
    def _calculate_seo_score(self, title: str, target_keyword: str) -> int:
        """SEO 점수를 계산합니다."""
        score = 0
        
        # 타겟 키워드 포함 여부
        if target_keyword.lower() in title.lower():
            score += 30
        
        # 길이 점수 (30-60자 사이가 최적)
        length = len(title)
        if 30 <= length <= 60:
            score += 20
        elif 25 <= length <= 65:
            score += 10
        
        # 파워 워드 포함 여부
        for word in self.power_words:
            if word in title:
                score += 5
        
        # 숫자 포함 여부
        if re.search(r'\d+', title):
            score += 10
        
        # 감정적 트리거 포함 여부
        for trigger in self.emotional_triggers:
            if trigger in title:
                score += 5
        
        return score
    
    def _calculate_emotional_score(self, title: str) -> int:
        """감정적 점수를 계산합니다."""
        score = 0
        
        for trigger in self.emotional_triggers:
            if trigger in title:
                score += 10
        
        for word in self.power_words:
            if word in title:
                score += 5
        
        return score

# 사용 예시
if __name__ == "__main__":
    # 제목 생성기 설정
    config = TitleConfig(
        max_length=60,
        min_length=30,
        include_numbers=True,
        include_power_words=True,
        target_keyword="마케팅"
    )
    
    # 제목 생성기 인스턴스 생성
    generator = AdvancedTitleGenerator(config)
    
    # 제목 생성
    titles = generator.generate_titles(
        topic="성공하는 방법",
        target_keyword="마케팅",
        lsi_keywords=["디지털", "온라인", "전략"],
        num_titles=5
    )
    
    # 결과 출력
    print("=== 생성된 제목들 ===")
    for i, title_info in enumerate(titles, 1):
        print(f"{i}. {title_info['title']}")
        print(f"   유형: {title_info['type']}")
        print(f"   길이: {title_info['length']}자")
        print(f"   SEO 점수: {title_info['seo_score']}")
        print(f"   감정 점수: {title_info['emotional_score']}")
        print()