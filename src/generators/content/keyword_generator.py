# v1.0 - 핵심 용어 정리 생성기 (PBN 시스템용)
# 전문적인 용어 정의 및 설명 생성

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

class TermType(Enum):
    """용어 유형 정의"""
    DEFINITION = "definition"
    CONCEPT = "concept"
    METHOD = "method"
    TOOL = "tool"
    STRATEGY = "strategy"
    TECHNIQUE = "technique"

@dataclass
class TermDefinition:
    """용어 정의 정보"""
    term: str
    definition: str
    explanation: str
    examples: List[str]
    related_terms: List[str]
    term_type: TermType
    importance: int  # 1-5 중요도

@dataclass
class KeywordConfig:
    """키워드 생성 설정"""
    min_terms: int = 5
    max_terms: int = 10
    include_examples: bool = True
    include_related_terms: bool = True
    explanation_length: str = "medium"  # short, medium, long

class AdvancedKeywordGenerator:
    """고도화된 키워드 생성기"""
    
    def __init__(self, config: KeywordConfig = None):
        self.config = config or KeywordConfig()
        self.term_templates = {
            TermType.DEFINITION: [
                "{term}는 {definition}을 의미합니다.",
                "{term}은 {definition}의 개념입니다.",
                "{term}는 {definition}를 가리키는 용어입니다."
            ],
            TermType.CONCEPT: [
                "{term}는 {definition}라는 개념입니다.",
                "{term}은 {definition}을 나타내는 핵심 개념입니다.",
                "{term}는 {definition}와 관련된 중요한 개념입니다."
            ],
            TermType.METHOD: [
                "{term}는 {definition}하는 방법입니다.",
                "{term}은 {definition}을 위한 방법론입니다.",
                "{term}는 {definition}하는 실용적인 방법입니다."
            ],
            TermType.TOOL: [
                "{term}는 {definition}을 위한 도구입니다.",
                "{term}은 {definition}에 사용되는 도구입니다.",
                "{term}는 {definition}을 지원하는 도구입니다."
            ],
            TermType.STRATEGY: [
                "{term}는 {definition}을 위한 전략입니다.",
                "{term}은 {definition}에 효과적인 전략입니다.",
                "{term}는 {definition}을 달성하기 위한 전략입니다."
            ],
            TermType.TECHNIQUE: [
                "{term}는 {definition}하는 기법입니다.",
                "{term}은 {definition}을 위한 기술입니다.",
                "{term}는 {definition}하는 전문 기법입니다."
            ]
        }
        
        self.example_templates = [
            "예를 들어, {example}",
            "구체적으로는 {example}",
            "실제 사례로는 {example}",
            "대표적인 예시로 {example}",
            "이를 통해 {example}"
        ]
    
    def generate_keyword_definitions(self, 
                                   topic: str, 
                                   target_keyword: str,
                                   lsi_keywords: List[str] = None,
                                   content_type: str = "guide") -> Dict[str, any]:
        """
        핵심 용어 정의들을 생성합니다.
        
        Args:
            topic: 주제
            target_keyword: 타겟 키워드
            lsi_keywords: LSI 키워드 목록
            content_type: 콘텐츠 유형
            
        Returns:
            용어 정의 정보 딕셔너리
        """
        # 핵심 용어 추출
        core_terms = self._extract_core_terms(topic, target_keyword, lsi_keywords)
        
        # 용어 정의 생성
        term_definitions = []
        for term in core_terms:
            definition = self._create_term_definition(term, topic, target_keyword)
            if definition:
                term_definitions.append(definition)
        
        # 중요도 기준으로 정렬
        term_definitions.sort(key=lambda x: x.importance, reverse=True)
        
        # HTML 생성
        html_content = self._generate_html_content(term_definitions)
        
        return {
            "terms": term_definitions,
            "html_content": html_content,
            "total_terms": len(term_definitions),
            "seo_score": self._calculate_seo_score(term_definitions, target_keyword)
        }
    
    def _extract_core_terms(self, 
                           topic: str, 
                           target_keyword: str,
                           lsi_keywords: List[str]) -> List[str]:
        """핵심 용어들을 추출합니다."""
        terms = [target_keyword]
        
        # LSI 키워드 추가
        if lsi_keywords:
            terms.extend(lsi_keywords[:3])  # 상위 3개만 사용
        
        # 주제 관련 용어 추가
        topic_terms = self._generate_topic_terms(topic, target_keyword)
        terms.extend(topic_terms)
        
        # 중복 제거 및 제한
        unique_terms = list(dict.fromkeys(terms))
        return unique_terms[:self.config.max_terms]
    
    def _generate_topic_terms(self, topic: str, target_keyword: str) -> List[str]:
        """주제 관련 용어들을 생성합니다."""
        # 기본 용어 매핑
        term_mappings = {
            "마케팅": ["SEO", "콘텐츠 마케팅", "브랜딩", "타겟팅", "전환율"],
            "비즈니스": ["전략", "운영", "관리", "성장", "수익성"],
            "기술": ["구현", "개발", "최적화", "통합", "자동화"],
            "교육": ["학습", "훈련", "개발", "성장", "역량"],
            "건강": ["운동", "영양", "웰빙", "관리", "예방"]
        }
        
        # 주제에 맞는 용어 찾기
        for key, terms in term_mappings.items():
            if key in topic or key in target_keyword:
                return terms[:3]  # 상위 3개만 반환
        
        # 기본 용어 반환
        return ["전략", "방법", "기법", "도구", "원리"]
    
    def _create_term_definition(self, 
                               term: str, 
                               topic: str, 
                               target_keyword: str) -> Optional[TermDefinition]:
        """개별 용어 정의를 생성합니다."""
        
        # 용어 유형 결정
        term_type = self._determine_term_type(term, topic)
        
        # 정의 생성
        definition = self._generate_definition(term, term_type, topic)
        if not definition:
            return None
        
        # 설명 생성
        explanation = self._generate_explanation(term, definition, topic)
        
        # 예시 생성
        examples = self._generate_examples(term, definition, topic)
        
        # 관련 용어 생성
        related_terms = self._generate_related_terms(term, topic)
        
        # 중요도 계산
        importance = self._calculate_importance(term, target_keyword, topic)
        
        return TermDefinition(
            term=term,
            definition=definition,
            explanation=explanation,
            examples=examples,
            related_terms=related_terms,
            term_type=term_type,
            importance=importance
        )
    
    def _determine_term_type(self, term: str, topic: str) -> TermType:
        """용어 유형을 결정합니다."""
        # 용어 유형 키워드 매핑
        type_keywords = {
            TermType.DEFINITION: ["정의", "의미", "개념"],
            TermType.CONCEPT: ["개념", "이론", "원리"],
            TermType.METHOD: ["방법", "기법", "절차"],
            TermType.TOOL: ["도구", "기술", "시스템"],
            TermType.STRATEGY: ["전략", "계획", "접근"],
            TermType.TECHNIQUE: ["기법", "기술", "방법"]
        }
        
        # 용어에 포함된 키워드로 유형 결정
        for term_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in term:
                    return term_type
        
        # 기본값
        return TermType.CONCEPT
    
    def _generate_definition(self, 
                            term: str, 
                            term_type: TermType, 
                            topic: str) -> str:
        """용어 정의를 생성합니다."""
        templates = self.term_templates.get(term_type, [])
        
        if not templates:
            return f"{term}는 {topic}과 관련된 중요한 개념입니다."
        
        # 기본 정의 생성
        base_definition = f"{topic}에서 사용되는 핵심 개념"
        
        # 템플릿 적용
        template = templates[0]
        definition = template.replace("{term}", term).replace("{definition}", base_definition)
        
        return definition
    
    def _generate_explanation(self, 
                             term: str, 
                             definition: str, 
                             topic: str) -> str:
        """용어 설명을 생성합니다."""
        explanations = [
            f"{term}는 {topic}의 성공을 위해 반드시 이해해야 할 핵심 요소입니다.",
            f"{term}는 {topic}에서 매우 중요한 역할을 하는 개념으로, 효과적인 활용이 필요합니다.",
            f"{term}는 {topic}의 기본 원리 중 하나로, 올바른 이해가 중요합니다.",
            f"{term}는 {topic}에서 성과를 높이기 위한 필수 요소입니다."
        ]
        
        return explanations[0]  # 첫 번째 설명 사용
    
    def _generate_examples(self, 
                          term: str, 
                          definition: str, 
                          topic: str) -> List[str]:
        """용어 예시들을 생성합니다."""
        if not self.config.include_examples:
            return []
        
        examples = [
            f"{term}의 실제 적용 사례",
            f"{term}를 활용한 성공 사례",
            f"{term}의 구체적인 사용 예시",
            f"{term}를 통한 효과적인 접근"
        ]
        
        return examples[:2]  # 최대 2개 예시
    
    def _generate_related_terms(self, term: str, topic: str) -> List[str]:
        """관련 용어들을 생성합니다."""
        if not self.config.include_related_terms:
            return []
        
        # 기본 관련 용어
        related = [f"{term} 관련 개념", f"{term}와 유사한 용어", f"{term}의 파생 개념"]
        
        return related[:2]  # 최대 2개 관련 용어
    
    def _calculate_importance(self, 
                            term: str, 
                            target_keyword: str, 
                            topic: str) -> int:
        """용어 중요도를 계산합니다."""
        importance = 3  # 기본 중요도
        
        # 타겟 키워드와 일치하면 높은 중요도
        if term.lower() == target_keyword.lower():
            importance = 5
        elif target_keyword.lower() in term.lower():
            importance = 4
        
        # 주제와 관련성이 높으면 중요도 증가
        if any(word in term for word in topic.split()):
            importance += 1
        
        return min(importance, 5)  # 최대 5
    
    def _generate_html_content(self, term_definitions: List[TermDefinition]) -> str:
        """HTML 콘텐츠를 생성합니다."""
        html = '<div class="keyword-definitions">\n'
        html += '<h3>핵심 용어 정리</h3>\n'
        html += '<div class="terms-list">\n'
        
        for term_def in term_definitions:
            html += f'<div class="term-item">\n'
            html += f'<h4>{term_def.term}</h4>\n'
            html += f'<p class="definition">{term_def.definition}</p>\n'
            html += f'<p class="explanation">{term_def.explanation}</p>\n'
            
            if term_def.examples:
                html += '<ul class="examples">\n'
                for example in term_def.examples:
                    html += f'<li>{example}</li>\n'
                html += '</ul>\n'
            
            if term_def.related_terms:
                html += '<div class="related-terms">\n'
                html += '<strong>관련 용어:</strong> '
                html += ', '.join(term_def.related_terms)
                html += '</div>\n'
            
            html += '</div>\n'
        
        html += '</div>\n'
        html += '</div>\n'
        
        return html
    
    def _calculate_seo_score(self, 
                           term_definitions: List[TermDefinition], 
                           target_keyword: str) -> int:
        """SEO 점수를 계산합니다."""
        score = 0
        
        # 용어 수 점수
        term_count = len(term_definitions)
        if 5 <= term_count <= 10:
            score += 20
        elif 3 <= term_count <= 12:
            score += 10
        
        # 타겟 키워드 포함 용어 수
        keyword_terms = sum(1 for term_def in term_definitions 
                          if target_keyword.lower() in term_def.term.lower())
        score += keyword_terms * 10
        
        # 중요도 5인 용어 수
        high_importance_terms = sum(1 for term_def in term_definitions 
                                  if term_def.importance == 5)
        score += high_importance_terms * 5
        
        return score

# 사용 예시
if __name__ == "__main__":
    # 키워드 생성기 설정
    config = KeywordConfig(
        min_terms=5,
        max_terms=8,
        include_examples=True,
        include_related_terms=True
    )
    
    # 키워드 생성기 인스턴스 생성
    generator = AdvancedKeywordGenerator(config)
    
    # 용어 정의 생성
    result = generator.generate_keyword_definitions(
        topic="성공하는 방법",
        target_keyword="마케팅",
        lsi_keywords=["디지털", "온라인", "전략"],
        content_type="guide"
    )
    
    # 결과 출력
    print("=== 핵심 용어 정리 ===")
    print(f"총 용어 수: {result['total_terms']}")
    print(f"SEO 점수: {result['seo_score']}")
    print()
    
    for i, term_def in enumerate(result['terms'], 1):
        print(f"{i}. {term_def.term}")
        print(f"   정의: {term_def.definition}")
        print(f"   설명: {term_def.explanation}")
        print(f"   중요도: {term_def.importance}/5")
        if term_def.examples:
            print(f"   예시: {', '.join(term_def.examples)}")
        if term_def.related_terms:
            print(f"   관련 용어: {', '.join(term_def.related_terms)}")
        print()
    
    print("=== HTML 콘텐츠 ===")
    print(result['html_content'])