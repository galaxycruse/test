import os
import pickle
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from utils.llm import get_embeddings

DOCS_DIR = Path(__file__).parent.parent / "data" / "python_docs"
INDEX_PATH = Path(__file__).parent.parent / "data" / "faiss_index"


def build_index(force_rebuild: bool = False) -> FAISS:
    if not force_rebuild and INDEX_PATH.exists():
        return load_index()

    docs = []
    for md_file in DOCS_DIR.glob("*.md"):
        loader = TextLoader(str(md_file), encoding="utf-8")
        docs.extend(loader.load())
        for doc in docs[-1:]:
            doc.metadata["source"] = md_file.name

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n## ", "\n### ", "\n```", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(INDEX_PATH))
    return vectorstore


def load_index() -> FAISS:
    embeddings = get_embeddings()
    return FAISS.load_local(
        str(INDEX_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def get_vectorstore(force_rebuild: bool = False) -> FAISS:
    return build_index(force_rebuild=force_rebuild)
