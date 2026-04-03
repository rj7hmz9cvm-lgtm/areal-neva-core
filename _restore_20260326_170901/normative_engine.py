import logging
import sys
from pathlib import Path
from typing import Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger("normative_engine")


class NormativeEngine:
    def __init__(self, persist_dir: str = "/root/.areal-neva-core/db/norms") -> None:
        self.persist_dir = persist_dir
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        self.emb = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.emb,
        )

    def search(self, query: str, k: int = 4) -> List[Dict[str, object]]:
        try:
            docs = self.db.similarity_search(query, k=k)
            out = []
            for d in docs:
                out.append({
                    "text": d.page_content,
                    "src": d.metadata.get("source", "unknown"),
                    "page": d.metadata.get("page"),
                })
            return out
        except Exception as e:
            logger.exception("normative search failed")
            return [{"error": str(e)}]

    def load_pdf(self, file_path: str) -> int:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
        )
        chunks = splitter.split_documents(pages)
        self.db.add_documents(chunks)
        return len(chunks)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: normative_engine.py <pdf>")
        sys.exit(1)

    engine = NormativeEngine()
    chunks = engine.load_pdf(sys.argv[1])
    print(f"LOADED: {sys.argv[1]} ({chunks} chunks)")
