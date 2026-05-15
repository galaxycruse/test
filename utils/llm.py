import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"환경변수 '{key}'가 설정되지 않았습니다. "
            ".env 파일에 해당 키를 추가해주세요."
        )
    return value


def get_llm(model: str = "mini") -> ChatAnthropic:
    api_key = _require_env("ANTHROPIC_API_KEY")
    model_name = (
        "claude-haiku-4-5-20251001"
        if model == "mini"
        else "claude-sonnet-4-6"
    )
    try:
        return ChatAnthropic(
            model=model_name,
            api_key=api_key,
            temperature=0.3,
        )
    except Exception as e:
        raise RuntimeError(f"LLM 초기화 실패 ({model_name}): {e}") from e


def get_embeddings() -> HuggingFaceEmbeddings:
    try:
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    except Exception as e:
        raise RuntimeError(
            f"임베딩 모델 로드 실패: {e}\n"
            "sentence-transformers 패키지가 설치되어 있는지 확인하세요."
        ) from e
