"""
RAG (Retrieval-Augmented Generation) System for Knowledge Base
Handles document loading, embedding generation, and similarity search
"""

import os
import json
from typing import List, Dict, Any
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document

class RAGSystem:
    def __init__(self, knowledge_base_path: str = "../knowledge_base"):
        """
        Initialize RAG system with knowledge base path
        """
        self.knowledge_base_path = knowledge_base_path
        self.embeddings = None
        self.vector_store = None
        self.retriever = None
        
        # Initialize embeddings model
        self._initialize_embeddings()
        
        # Load and process documents
        self._load_documents()
    
    def _initialize_embeddings(self):
        """
        Initialize sentence transformer embeddings
        """
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("✅ Embeddings model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            raise
    
    def _load_documents(self):
        """
        Load documents from knowledge base and create vector store
        """
        try:
            # Load all text files from knowledge base
            loader = DirectoryLoader(
                self.knowledge_base_path,
                glob="**/*.txt",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            documents = loader.load()
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            # Create retriever
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            
            print(f"✅ Loaded {len(documents)} documents, created {len(chunks)} chunks")
            
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
            raise
    
    def retrieve_relevant_docs(self, query: str, k: int = 3) -> List[Document]:
        """
        Retrieve relevant documents for a given query
        """
        try:
            # Update retriever k parameter
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
            
            # Retrieve documents
            docs = self.retriever.get_relevant_documents(query)
            
            return docs
            
        except Exception as e:
            print(f"❌ Error retrieving documents: {e}")
            return []
    
    def get_context_with_scores(self, query: str, k: int = 3) -> Dict[str, Any]:
        """
        Retrieve documents with similarity scores
        """
        try:
            # Perform similarity search with scores
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query, k=k
            )
            
            # Format results
            results = []
            for doc, score in docs_with_scores:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            return {
                "query": query,
                "results": results,
                "total_results": len(results)
            }
            
        except Exception as e:
            print(f"❌ Error getting context with scores: {e}")
            return {"query": query, "results": [], "total_results": 0}
    
    def format_context_for_llm(self, documents: List[Document]) -> str:
        """
        Format retrieved documents for LLM prompt
        """
        if not documents:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source', 'Unknown')
            content = doc.page_content.strip()
            
            context_parts.append(
                f"Document {i} (Source: {source}):\n{content}"
            )
        
        return "\n\n".join(context_parts)
    
    def search_knowledge_base(self, query: str) -> Dict[str, Any]:
        """
        Main search method that returns formatted context
        """
        try:
            # Get documents with scores
            search_results = self.get_context_with_scores(query, k=3)
            
            # Format context for LLM
            documents = self.retrieve_relevant_docs(query, k=3)
            formatted_context = self.format_context_for_llm(documents)
            
            return {
                "query": query,
                "context": formatted_context,
                "search_results": search_results,
                "sources": [doc.metadata.get('source', 'Unknown') for doc in documents]
            }
            
        except Exception as e:
            print(f"❌ Error searching knowledge base: {e}")
            return {
                "query": query,
                "context": "Error searching knowledge base.",
                "search_results": {"results": [], "total_results": 0},
                "sources": []
            }

# Singleton instance for the application
rag_system = None

def get_rag_system() -> RAGSystem:
    """
    Get or create RAG system instance
    """
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
    return rag_system

if __name__ == "__main__":
    # Test the RAG system
    rag = RAGSystem()
    
    # Test queries
    test_queries = [
        "How do I fix a 500 error?",
        "What are the pricing plans?",
        "How do I set up my account?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        result = rag.search_knowledge_base(query)
        print(f"📄 Context length: {len(result['context'])} characters")
        print(f"📚 Sources: {result['sources']}")
