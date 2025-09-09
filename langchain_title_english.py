from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def replace_chars(title: str) -> str:
    """Remove quotes and # from the title."""
    return title.replace('"', "").replace("#", "")


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.8,
    openai_api_key=OPENAI_API_KEY,
    max_tokens=1000,
)

title_prompt = PromptTemplate(
    input_variables=["keyword"],
    template="""
You are a creative and versatile blog post title generator.
For the given keyword "{keyword}", brainstorm a variety of related themes, subtopics, and concepts.
Then, craft a compelling blog post title that captures the essence of these ideas.
#Note that the final title:
- Can incorporate the original keyword or its related ideas, but it does not have to include the keyword verbatim.
- Should be creative, engaging, and written in a natural style.
- Must be output as a single, concise line without any additional explanation or formatting.
Output only the final title.
#important:
- Please print in English only.
""",
)

title_chain = title_prompt | llm | StrOutputParser() | RunnableLambda(replace_chars)


def generate_blog_title_with_chain_english(keyword: str) -> str:
    """
    Generate a blog post title in English using LangChain based on the given keyword.
    :param keyword: The keyword for title generation
    :return: The generated blog title (unnecessary characters removed)
    """
    return title_chain.invoke({"keyword": keyword})
