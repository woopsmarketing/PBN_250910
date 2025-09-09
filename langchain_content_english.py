import re
import time
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

content_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.8,
    openai_api_key=OPENAI_API_KEY,
    max_tokens=4096,
)


def format_markdown_to_html(text: str) -> str:
    """
    Replace markdown in the input text with simple HTML tags.
    Remove code block markers and unnecessary words like 'markdown'.
    """
    # text = re.sub(r"[" "]'", "", text)
    text = re.sub(r"`", "", text)
    text = re.sub(r"```", "", text)
    text = re.sub(r"(?i)markdown", "", text)
    text = re.sub(r"###### (.*)", r"<h6>\1</h6>", text)
    text = re.sub(r"##### (.*)", r"<h5>\1</h5>", text)
    text = re.sub(r"#### (.*)", r"<h4>\1</h4>", text)
    text = re.sub(r"### (.*)", r"<h3>\1</h3>", text)
    text = re.sub(r"## (.*)", r"<h2>\1</h2>", text)
    text = re.sub(r"# (.*)", r"<h1>\1</h1>", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!</p>)\n(?!<p>)", r"<br>", text)
    paragraphs = text.split("\n")
    paragraphs = [f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()]
    return "\n".join(paragraphs)


# 1. Initial content chain (no conclusion)
initial_content_prompt = PromptTemplate(
    input_variables=["title", "keyword"],
    template="""
You are a skilled English content writer.
Based on the following details, please write a detailed and informative blog post content excluding any conclusion section.
Title: {title}
Keyword: {keyword}

Requirements:
- Only write in English.
- Incorporate subheadings, examples, and tips.
- Do NOT include words like 'Conclusion', 'Summary', or 'In closing' in the body.
- Provide roughly 300-400 words of content.
Output only the blog post content (without the conclusion).
""",
)
initial_content_chain = initial_content_prompt | content_llm | StrOutputParser()

# 2. Additional content chain (to reach word count)
additional_content_prompt = PromptTemplate(
    input_variables=["existing_content", "word_count"],
    template="""
The current blog post content is approximately {word_count} words.
Based on the existing content below, please continue writing additional content in English.

Requirements:
1. Write in Markdown format
2. Begin your output with a new primary section heading using Markdown h2 (i.e., start with "##" followed by the title of the new section, for example "## New Insights").
3. After the main heading, develop the content in cohesive paragraphs. If needed, naturally introduce subordinate section headings using h3 (i.e., "###") to further organize the content.
4. Avoid excessive or redundant use of headings; use only one new h2 heading and only as many h3 headings as needed to logically structure the new material.
5. Do NOT repeat subheadings or details from the existing content, and do NOT include any concluding or summary phrases.
6. Focus on providing fresh perspectives, specific examples, and concrete data that build naturally on the existing content.
7. Only write in English.
Existing Content:
{existing_content}

Please continue writing additional content (in English) that flows naturally from the above.
""",
)
additional_content_chain = additional_content_prompt | content_llm | StrOutputParser()

# 3. Conclusion chain
result_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.8,
    openai_api_key=OPENAI_API_KEY,
    max_tokens=1024,
)

conclusion_prompt = PromptTemplate(
    input_variables=["existing_content"],
    template="""
Based on the blog post content provided below, write a conclusion (in English).

Requirements:
1. Write in Markdown format
2. You may introduce the conclusion with a single main heading (##) using terms like 'Conclusion', 'Summary', or 'In closing'.
3. Summarize key points from the existing content in 1~2 paragraphs.
4. Do NOT introduce new subheadings beyond the main conclusion heading.
5. Keep it concise and coherent, directly following from the existing content.
6. Only write in English.
Existing Content:
{existing_content}

Write only the conclusion section in English, following these rules.
""",
)
conclusion_chain = conclusion_prompt | result_llm | StrOutputParser()

# 4. Main function to generate full blog content in English


def generate_long_blog_content_with_chain_english(
    title: str, keyword: str, desired_word_count: int = 800
) -> str:
    """
    Generate a full blog post in English (including conclusion) using LangChain based on the given title and keyword.
    :param title: Blog post title
    :param keyword: Blog post keyword
    :param desired_word_count: Minimum word count for the final content (default=800)
    :return: Final blog post HTML content
    """
    content = initial_content_chain.invoke({"title": title, "keyword": keyword})
    current_word_count = len(content.split())
    while current_word_count < desired_word_count:
        additional = additional_content_chain.invoke(
            {"existing_content": content, "word_count": str(current_word_count)}
        )
        content += "\n" + additional
        current_word_count = len(content.split())
    conclusion = conclusion_chain.invoke({"existing_content": content})
    final_content = content + "\n\n" + conclusion
    final_content = format_markdown_to_html(final_content)
    return final_content
