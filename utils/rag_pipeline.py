import os
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, VECTOR_STORE_DIR
import pickle

class RAGPipeline:
    """RAG Pipeline for PDF processing and question answering"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model=EMBEDDING_MODEL
        )
        self.vector_store = None
        self.vector_store_path = VECTOR_STORE_DIR / "faiss_index"
        
    def load_existing_vector_store(self):
        """Load existing vector store if available"""
        try:
            if os.path.exists(self.vector_store_path):
                self.vector_store = FAISS.load_local(
                    str(self.vector_store_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
        return False
    
    def process_pdfs(self, pdf_paths: List[str]) -> bool:
        """Process uploaded PDFs and create vector store"""
        try:
            all_documents = []
            
            # Load and process each PDF
            for pdf_path in pdf_paths:
                loader = PyPDFLoader(pdf_path)
                documents = loader.load()
                all_documents.extend(documents)
            
            if not all_documents:
                return False
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                length_function=len
            )
            chunks = text_splitter.split_documents(all_documents)
            
            # Create or update vector store
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            else:
                new_vector_store = FAISS.from_documents(chunks, self.embeddings)
                self.vector_store.merge_from(new_vector_store)
            
            # Save vector store
            self.vector_store.save_local(str(self.vector_store_path))
            return True
            
        except Exception as e:
            print(f"Error processing PDFs: {e}")
            return False
    
    def query(self, question: str, k: int = 3) -> str:
        """Query the vector store and return answer"""
        try:
            if self.vector_store is None:
                return "No documents have been uploaded yet. Please upload PDF documents first."
            
            # Retrieve relevant documents
            docs = self.vector_store.similarity_search(question, k=k)
            
            if not docs:
                return "I couldn't find relevant information in the uploaded documents."
            
            # Combine retrieved content
            context = "\n\n".join([doc.page_content for doc in docs])
            
            return context
            
        except Exception as e:
            print(f"Error querying vector store: {e}")
            return "Sorry, I encountered an error while searching the documents."
    
    def clear_vector_store(self):
        """Clear the vector store"""
        self.vector_store = None
        if os.path.exists(self.vector_store_path):
            import shutil
            shutil.rmtree(self.vector_store_path)