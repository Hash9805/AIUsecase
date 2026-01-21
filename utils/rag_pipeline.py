# RAGPipeline v2 - OpenAI removed

import os
from typing import List
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from config import CHUNK_SIZE, CHUNK_OVERLAP, VECTOR_STORE_DIR
import pickle


class RAGPipeline:
    """
    RAG Pipeline using local embeddings + FAISS
    (NO OpenAI, NO paid APIs)
    """

    def __init__(self):
        # Free local embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        self.vector_store = None
        self.documents: List[str] = []

        VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
        self.index_path = VECTOR_STORE_DIR / "faiss.index"
        self.docs_path = VECTOR_STORE_DIR / "documents.pkl"

    # -----------------------------
    # Embedding helpers
    # -----------------------------
    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        return self.embedding_model.encode(texts, show_progress_bar=False)

    def _embed_query(self, query: str) -> np.ndarray:
        return self.embedding_model.encode([query])[0]

    # -----------------------------
    # Load existing vector store
    # -----------------------------
    def load_existing_vector_store(self) -> bool:
        try:
            if self.index_path.exists() and self.docs_path.exists():
                self.vector_store = faiss.read_index(str(self.index_path))
                with open(self.docs_path, "rb") as f:
                    self.documents = pickle.load(f)
                return True
        except Exception as e:
            print("Error loading vector store:", e)
        return False

    # -----------------------------
    # PDF processing
    # -----------------------------
    def process_pdfs(self, pdf_paths: List[str]) -> bool:
        try:
            all_text = []

            for pdf_path in pdf_paths:
                loader = PyPDFLoader(pdf_path)
                pages = loader.load()
                all_text.extend([page.page_content for page in pages])

            if not all_text:
                return False

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )

            chunks = splitter.split_text("\n".join(all_text))
            self._build_vector_store(chunks)
            self._save_vector_store()
            return True

        except Exception as e:
            print("Error processing PDFs:", e)
            return False

    # -----------------------------
    # Vector store logic
    # -----------------------------
    def _build_vector_store(self, chunks: List[str]):
        embeddings = self._embed_texts(chunks).astype("float32")

        dim = embeddings.shape[1]
        self.vector_store = faiss.IndexFlatL2(dim)
        self.vector_store.add(embeddings)

        self.documents = chunks

    def _save_vector_store(self):
        faiss.write_index(self.vector_store, str(self.index_path))
        with open(self.docs_path, "wb") as f:
            pickle.dump(self.documents, f)

    # -----------------------------
    # Retrieval (RAG)
    # -----------------------------
    def rag_tool(self, query: str, top_k: int = 3):
        if not self.vector_store:
            return {"success": False, "answer": None}

        query_embedding = self._embed_query(query).astype("float32")
        distances, indices = self.vector_store.search(
            np.array([query_embedding]), top_k
        )

        results = [self.documents[i] for i in indices[0]]
        answer = "\n".join(results)

        return {"success": True, "answer": answer}

    # -----------------------------
    # Clear store
    # -----------------------------
    def clear_vector_store(self):
        self.vector_store = None
        self.documents = []

        if self.index_path.exists():
            os.remove(self.index_path)
        if self.docs_path.exists():
            os.remove(self.docs_path)
