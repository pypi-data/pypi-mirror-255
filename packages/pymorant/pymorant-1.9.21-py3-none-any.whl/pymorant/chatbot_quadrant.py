# Implementación de un chatbot que se alimenta a partir docx, pdf y txt
import os
import inspect
import qdrant_client
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate # noqa
from qdrant_client.http import models


class Chatbot:

    def __init__(self, openai_api_key, qdrant_api_key, qdrant_host, model, search_kwargs): # noqa
        self.openai_api_key = openai_api_key
        self.qdrant_api_key = qdrant_api_key
        self.qdrant_host = qdrant_host
        self.model = model
        self.search_kwargs = search_kwargs

    def create_qdrant_collection(self, qdrant_collection_name):

        client = qdrant_client.QdrantClient(
            self.qdrant_host,
            api_key=self.qdrant_api_key
        )

        vectors_configuration = models.VectorParams(
            size=1536,
            distance=models.Distance.COSINE
        )

        client.recreate_collection(
            collection_name=qdrant_collection_name,
            vectors_config=vectors_configuration,
        )

    def create_vectorstore(self, qdrant_collection_name):

        documents = []
        frame = inspect.currentframe()
        caller_file = inspect.getouterframes(frame)[-1].filename
        basedir = os.path.dirname(os.path.abspath(caller_file))
        docsdir = os.path.join(basedir, "documents")

        if not os.path.exists(docsdir):
            print("No documents directory found")
            return

        for file_name in os.listdir(docsdir):
            file_path = os.path.join(docsdir, file_name)
            if file_name.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif file_name.endswith(".docx") or file_name.endswith(".doc"):
                loader = Docx2txtLoader(file_path)
                documents.extend(loader.load())
            elif file_name.endswith(".txt"):
                loader = TextLoader(file_path)
                documents.extend(loader.load())

        text_splitter = CharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

        documents = text_splitter.split_documents(documents)

        client = qdrant_client.QdrantClient(
            self.qdrant_host,
            api_key=self.qdrant_api_key
        )

        # Se carga el vectorstore
        embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key
        )
        vectorstore = Qdrant(
            client=client,
            collection_name=qdrant_collection_name,
            embeddings=embeddings
        )

        # Se agregan los embeddings de los documentos al vectorstore
        vectorstore.add_documents(
            documents,
        )

    def load_chain(self, qdrant_collection_name):

        general_system_template = r"""
        Dado el context, eres experto en analizar distintos mensajes de texto
        y sacar conclusiones muy acertadas.
        ----
        {context}
        ----

        """
        general_user_template = "Question:{question}"

        messages = [
            SystemMessagePromptTemplate.from_template(general_system_template),
            HumanMessagePromptTemplate.from_template(general_user_template)
        ]

        qa_prompt = ChatPromptTemplate.from_messages(messages)

        client = qdrant_client.QdrantClient(
            self.qdrant_host,
            api_key=self.qdrant_api_key
        )

        vectorstore = Qdrant(
            client=client,
            collection_name=qdrant_collection_name,
            embeddings=OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        )

        chain = ConversationalRetrievalChain.from_llm(
            ChatOpenAI(temperature=0.3, model_name=self.model, openai_api_key=self.openai_api_key), # noqa
            vectorstore.as_retriever(search_kwargs={'k': self.search_kwargs}), # noqa
            combine_docs_chain_kwargs={"prompt": qa_prompt}, # noqa
            return_source_documents=False,
            verbose=False,
        )

        return chain

    def get_chatbot_answer(self, chain, question, chat_history=[]):

        '''returns a dict with the answer and the chat history'''
        return chain({
            "question": question, "chat_history": chat_history
        })
