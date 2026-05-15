import os
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from utils.llm import get_embeddings

DOCS_DIR = Path(__file__).parent.parent / "data" / "python_docs"
INDEX_PATH = Path(__file__).parent.parent / "data" / "faiss_index"


def build_index(force_rebuild: bool = False) -> FAISS:
    if not force_rebuild and INDEX_PATH.exists():
        try:
            return load_index()
        except Exception as e:
            print(f"[indexer] 기존 인덱스 로드 실패, 재빌드합니다: {e}")

    if not DOCS_DIR.exists():
        raise FileNotFoundError(
            f"학습 자료 디렉토리를 찾을 수 없습니다: {DOCS_DIR}\n"
            "data/python_docs/ 폴더와 마크다운 파일이 있는지 확인하세요."
        )

    docs = []
    for md_file in DOCS_DIR.glob("*.md"):
        try:
            loader = TextLoader(str(md_file), encoding="utf-8")
            loaded = loader.load()
            for doc in loaded:
                doc.metadata["source"] = md_file.name
            docs.extend(loaded)
        except Exception as e:
            print(f"[indexer] {md_file.name} 로드 실패, 건너뜁니다: {e}")

    if not docs:
        raise ValueError(
            f"{DOCS_DIR} 에서 로드된 문서가 없습니다. "
            ".md 파일이 존재하는지 확인하세요."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n## ", "\n### ", "\n```", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)

    try:
        embeddings = get_embeddings()
        vectorstore = FAISS.from_documents(chunks, embeddings)
        INDEX_PATH.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(INDEX_PATH))
        return vectorstore
    except Exception as e:
        raise RuntimeError(f"FAISS 인덱스 빌드 실패: {e}") from e


def load_index() -> FAISS:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"저장된 인덱스가 없습니다: {INDEX_PATH}")
    try:
        embeddings = get_embeddings()
        return FAISS.load_local(
            str(INDEX_PATH),
            embeddings,
            allow_dangerous_deserialization=True,
        )
    except Exception as e:
        raise RuntimeError(f"FAISS 인덱스 로드 실패: {e}") from e


def get_vectorstore(force_rebuild: bool = False) -> FAISS:
    return build_index(force_rebuild=force_rebuild)
