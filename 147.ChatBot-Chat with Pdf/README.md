
## Intelligent Intercompany Agreement Knowledge Chatbot

## 1. Document Preprocessing and Key Information Extraction:

- Uploaded PDFs are preprocessed using a PDF loader to extract their content. The extracted content is split into manageable chunks using text-splitting techniques (chunk size of 5000 with an overlap of 500). This ensures efficient retrieval of relevant information without losing context.

## 2. Embedding Generation and Vector Database Creation:
- Embeddings for document chunks are generated using the HuggingFace embedding model (all-MiniLM-L6-v2). These embeddings are stored in a vector database (Chroma) to enable efficient and contextually accurate retrieval of relevant content.

## 3. Context-Aware Question Reformulation:
The system uses a Large Language Model (LLM) with a custom prompt to analyze the user’s question and chat history. It reformulates the question to make it standalone and interpretable without requiring prior chat context. This is achieved using a history-aware retriever.

## 4. Question Answering and Retrieval-Augmented Generation (RAG):
- The reformulated question is passed to a retrieval chain that fetches the most relevant document chunks from the vector database. These retrieved chunks are then processed by a question-answering chain to generate concise and contextually accurate responses.

## 5. Chat History Management:
- A session-specific chat history is maintained to track ongoing conversations. The history ensures that responses are aligned with previous interactions, providing a seamless and coherent chat experience.

## 6. Integration and Deployment:
- The solution is integrated into a user-friendly Streamlit web interface, allowing users to upload PDFs, input questions, and view chat histories. The chatbot is powered by Groq API for conversational abilities and deployed on a cloud platform for scalability and accessibility.

### This approach ensures efficient handling of large documents, provides accurate responses, and maintains a seamless user experience with personalized session tracking.

