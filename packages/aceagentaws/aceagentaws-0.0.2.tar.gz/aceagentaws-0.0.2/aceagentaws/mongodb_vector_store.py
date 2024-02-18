import pymongo
import json
import time
import re
from typing import Any, Dict
from pymongo import MongoClient
from langchain.llms import AzureOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import MongoDBAtlasVectorSearch
import aceagentlogger 
from aceagentlogger.aws_logger import aws_logger
from mypy_extensions import TypedDict

deployment_name= "llmeast_ada_002" 
model_name= "text-embedding-ada-002"

db_name = "vector"
collection_name = "store" 
index_name = "vector_store_index"


def string_to_dict(string_data):
    return json.loads(string_data)

def remove_starting_period_and_spaces_string(input_string):
    sanitized_string = re.sub(r'^\.\s+', '', input_string)
    return sanitized_string

class mongodb_props(TypedDict):
    line_of_business: str
    content: str
    metadata: Dict[str, Any]
    chunk_size: int
    chunk_overlap: int
    chunk_id: int
    db_name: str

class mongodb_vector_store:
    @staticmethod
    def save_embeddings(mongo_db: MongoClient, logger: aws_logger, #AWSLogger,
                        props: mongodb_props):
        try:
            line_of_business: str = props['line_of_business']
            content: str = props['content']
            metadata: Dict[str, Any] = props['metadata']
            chunk_size: int = props['chunk_size']
            chunk_overlap: int = props['chunk_overlap']
            chunk_id: int = props['chunk_id']
            db_name: str = props['db_name']
            
            content = remove_starting_period_and_spaces_string(content)
           
            openai_api_key = props['OPEN_AI_API_KEY']
            openai_api_base= props['OPEN_AI_API_BASE']
            openai_api_version= props['OPEN_AI_API_VERSION']

            llm = AzureOpenAI(
                deployment_name=deployment_name,
                model_name=model_name,
                openai_api_key= openai_api_key,
                openai_api_base= openai_api_base,
                openai_api_version=openai_api_version
            )

            embedding_model = OpenAIEmbeddings(
                deployment=deployment_name,
                openai_api_key=openai_api_key,
                openai_api_base=openai_api_base,
                openai_api_version=openai_api_version,
                openai_api_type='azure'
            )

            characters_to_split_on = ['[\.\?!] ']  # end of sentence
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=True,
                separators=characters_to_split_on
            )
            docs = text_splitter.create_documents(texts=[content], metadatas=[metadata])

            texts = text_splitter.split_documents(docs)
            
            collection_name = f"{line_of_business}-{chunk_size}-{chunk_overlap}"

            logger.info(f"db: {db_name}  collection: {collection_name}")
            collection = mongo_db[db_name][collection_name]

            logger.info(f"{len(texts)} items are to be added to vector store")
            for i in range(len(texts)):
                text = texts[i]
                text.page_content = remove_starting_period_and_spaces_string(text.page_content)
                unique_identifier = f"{metadata.get('Chapter Name')}-{metadata.get('Chapter Number')}-{metadata.get('Section Name')}-{chunk_id}-{i}"
                logger.info(f"about to search for {unique_identifier}")
                existing_item = collection.find_one({"unique_identifier": unique_identifier})

                # Embed the current content
                doc_embedding = embedding_model.embed_documents([text.page_content])

                if existing_item:
                    logger.info(f"about to update for {unique_identifier}")

                    collection.update_one(
                        {"unique_identifier": unique_identifier},
                        {
                            "$set": {
                                "page_content": text.page_content,
                                "metadata": metadata,  
                                "embedding": doc_embedding[0]  
                            }
                        }
                    )
                else:
                    logger.info(f"about to add {unique_identifier}")

                    collection.insert_one({
                        "unique_identifier": unique_identifier, 
                        "page_content": text.page_content,
                        "metadata": metadata,
                        "embedding": doc_embedding[0]
                    })

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise
