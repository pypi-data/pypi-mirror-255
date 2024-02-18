import os
import shutil
import zipfile

import filetype
import tiktoken
from llama_index import (
    Document,
    ServiceContext,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.callbacks import CallbackManager, TokenCountingHandler
from llama_index.node_parser import SimpleNodeParser
from llama_index.vector_stores import VectorStoreQuery, VectorStoreQueryResult
from unstract.sdk.constants import LogLevel
from unstract.sdk.embedding import ToolEmbedding
from unstract.sdk.llm_whisperer import ToolLLMWhisperer
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.utils import ToolUtils
from unstract.sdk.vector_db import ToolVectorDB
from unstract.sdk.x2txt import X2Text

allowed_pdf_to_text_converters = [
    "default",
    "unstract_llm_whisperer",
    "unstract_camelot",
]
db_name = "unstract_vector_db"


class ToolIndex:
    def __init__(self, tool: BaseTool):
        self.tool = tool

    def get_text_from_index(
        self,
        project_id: str,
        embedding_type: str,
        vector_db: str,
        doc_id: str,
        embedding_suffix: str,
    ):
        embedd_helper = ToolEmbedding(tool=self.tool)
        embedding_li = embedd_helper.get_embedding(
            adapter_instance_id=embedding_type
        )
        if embedding_li is None:
            self.tool.stream_log(
                f"Error loading {embedding_type}", level=LogLevel.ERROR
            )
            raise Exception(f"Error loading {embedding_type}")

        vdb_helper = ToolVectorDB(
            tool=self.tool,
        )
        vector_db_li = vdb_helper.get_vector_db(
            adapter_instance_id=vector_db,
            embedding_type=embedding_suffix,
            collection_name_prefix="unstract_vector_db",
        )

        if vector_db_li is None:
            self.tool.stream_log(
                f"Error loading {vector_db}", level=LogLevel.ERROR
            )
            raise Exception(f"Error loading {vector_db}")

        # TODO: Handle different llms and their embedding models
        token_counter = TokenCountingHandler(
            tokenizer=tiktoken.encoding_for_model(
                "gpt-3.5-turbo-16k-0613"
            ).encode
        )
        callback_manager = CallbackManager([token_counter])

        service_context = ServiceContext.from_defaults(  # noqa: F841
            embed_model=embedding_li,
            callback_manager=callback_manager,
        )

        try:
            self.tool.stream_log(f">>> Querying {vector_db}...")
            self.tool.stream_log(f">>> {doc_id}")
            q = VectorStoreQuery(
                query_embedding=embedding_li.get_query_embedding(" "),
                doc_ids=[doc_id],
                similarity_top_k=10000,
            )
        except Exception as e:
            self.tool.stream_log(
                f"Error querying {vector_db}: {e}", level=LogLevel.ERROR
            )
            raise Exception(f"Error querying {vector_db}: {e}")

        n: VectorStoreQueryResult = vector_db_li.query(query=q)
        if len(n.nodes) > 0:
            self.tool.stream_log(f"Found {len(n.nodes)} nodes for {doc_id}")
            all_text = ""
            for node in n.nodes:
                all_text += node.get_content()
            return all_text
        else:
            self.tool.stream_log(f"No nodes found for {doc_id}")
            return None

    def cleanup_text(self, full_text):
        # Remove text which is not requried
        full_text_lines = full_text.split("\n")
        new_context_lines = []
        empty_line_count = 0
        for line in full_text_lines:
            if line.strip() == "":
                empty_line_count += 1
            else:
                if empty_line_count >= 3:
                    empty_line_count = 3
                for i in range(empty_line_count):
                    new_context_lines.append("")
                empty_line_count = 0
                new_context_lines.append(line.rstrip())
        print(
            f"Old context length: {len(full_text_lines)}, "
            f"New context length: {len(new_context_lines)}"
        )
        return "\n".join(new_context_lines)

    def index_file(
        self,
        project_id: str,
        embedding_type: str,
        vector_db: str,
        file_path: str,
        chunk_size: int,
        chunk_overlap: int,
        embedding_suffix: str,
        reindex: bool = False,
        converter: str = "default",
    ):
        if converter not in allowed_pdf_to_text_converters:
            self.tool.stream_log(
                "pdf-to-text-converters must be one of "
                f"{allowed_pdf_to_text_converters}",
                level=LogLevel.ERROR,
            )
            raise Exception(
                "pdf-to-text-converters must be one of "
                f"{allowed_pdf_to_text_converters}"
            )

        input_file_type = None
        input_file_type_mime = None
        with open(file_path, mode="rb") as input_file_obj:
            sample_contents = input_file_obj.read(100)
            input_file_type = filetype.guess(sample_contents)

        if input_file_type is None:
            input_file_type_mime = "text/plain"
        else:
            input_file_type_mime = input_file_type.MIME

        self.tool.stream_log(f"Input file type: {input_file_type_mime}")

        full_text = []

        if input_file_type_mime == "text/plain":
            with open(file_path) as input_file_obj:
                full_text.append(
                    {
                        "section": "full",
                        "text_contents": self.cleanup_text(
                            input_file_obj.read()
                        ),
                    }
                )

        elif input_file_type_mime == "application/pdf":
            self.tool.stream_log(f"PDF to text converter: {converter}")
            if converter == "unstract_llm_whisperer" or converter == "default":
                x2txt = ToolLLMWhisperer(tool=self.tool)
                full_text.append(
                    {
                        "section": "full",
                        "text_contents": self.cleanup_text(
                            x2txt.generate_whisper(
                                input_file=file_path,
                                mode="text",
                                dump_text=True,
                            )
                        ),
                    }
                )
            else:
                # TODO : Support for Camelot
                x2txt = X2Text(tool=self.tool)

        elif input_file_type_mime == "application/zip":
            self.tool.stream_log("Zip file extraction required")
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                file_name_from_path = os.path.basename(file_path)
                temp_directory = f"/tmp/unstract_zip/{file_name_from_path}"
                # If temp_directory exists, delete it and create it again
                if os.path.exists(temp_directory):
                    shutil.rmtree(temp_directory)
                os.makedirs(temp_directory)
                zip_ref.extractall(temp_directory)
        else:
            self.tool.stream_log(
                f"Unsupported file type: {input_file_type_mime}",
                level=LogLevel.ERROR,
            )
            raise Exception(f"Unsupported file type: {input_file_type_mime}")

        with open("/tmp/dump.txt", mode="w") as output_file_obj:
            for item in full_text:
                output_file_obj.write(f"Section: {item['section']}\n")
                output_file_obj.write(f"Text: {item['text_contents']}\n")

        doc_id = ToolUtils.generate_file_id(
            project_guid=project_id,
            file_name=file_path,
            vector_db=vector_db,
            embedding=embedding_type,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self.tool.stream_log(f"Checking for doc_id {doc_id} exists")

        vdb_helper = ToolVectorDB(
            tool=self.tool,
        )

        embedd_helper = ToolEmbedding(tool=self.tool)

        embedding_li = embedd_helper.get_embedding(
            adapter_instance_id=embedding_type
        )
        if embedding_li is None:
            self.tool.stream_log(
                f"Error loading {embedding_type}", level=LogLevel.ERROR
            )
            raise Exception(f"Error loading {embedding_type}")

        vector_db_li = vdb_helper.get_vector_db(
            adapter_instance_id=vector_db,
            embedding_type=embedding_suffix,
            collection_name_prefix="unstract_vector_db",
        )
        if vector_db_li is None:
            self.tool.stream_log(
                f"Error loading {vector_db}", level=LogLevel.ERROR
            )
            raise Exception(f"Error loading {vector_db}")

        q = VectorStoreQuery(
            query_embedding=embedding_li.get_query_embedding(" "),
            doc_ids=[doc_id],
        )

        doc_id_not_found = True
        try:
            n: VectorStoreQueryResult = vector_db_li.query(query=q)
            if len(n.nodes) > 0:
                doc_id_not_found = False
                self.tool.stream_log(f"Found {len(n.nodes)} nodes for {doc_id}")
            else:
                self.tool.stream_log(f"No nodes found for {doc_id}")
        except Exception as e:
            self.tool.stream_log(
                f"Error querying {vector_db}: {e}", level=LogLevel.ERROR
            )

        if doc_id_not_found is False and reindex:
            # Delete the nodes for the doc_id
            try:
                vector_db_li.delete(ref_doc_id=doc_id)
                self.tool.stream_log(f"Deleted nodes for {doc_id}")
            except Exception as e:
                self.tool.stream_log(
                    f"Error deleting nodes for {doc_id}: {e}",
                    level=LogLevel.ERROR,
                )
                raise Exception(f"Error deleting nodes for {doc_id}: {e}")
            doc_id_not_found = True

        if doc_id_not_found:
            # Check if chunking is required
            documents = []
            for item in full_text:
                text = item["text_contents"]
                self.tool.stream_log("Indexing file...")
                document = Document(
                    text=text,
                    doc_id=doc_id,
                    metadata={"section": item["section"]},
                )
                document.id_ = doc_id
                documents.append(document)
            self.tool.stream_log(f"Number of documents: {len(documents)}")
            if chunk_size == 0:
                parser = SimpleNodeParser.from_defaults(
                    chunk_size=len(documents[0].text) + 10, chunk_overlap=0
                )
                nodes = parser.get_nodes_from_documents(
                    documents, show_progress=True
                )
                node = nodes[0]
                node.embedding = embedding_li.get_query_embedding(" ")
                vector_db_li.add(nodes=[node])
                self.tool.stream_log("Added node to vector db")
            else:
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_db_li
                )
                parser = SimpleNodeParser.from_defaults(
                    chunk_size=chunk_size, chunk_overlap=chunk_overlap
                )

                token_counter = TokenCountingHandler(
                    tokenizer=tiktoken.encoding_for_model(
                        "gpt-3.5-turbo"
                    ).encode
                )
                callback_manager = CallbackManager([token_counter])

                service_context = ServiceContext.from_defaults(
                    llm=None,
                    embed_model=embedding_li,
                    node_parser=parser,
                    callback_manager=callback_manager,
                )

                self.tool.stream_log("Adding nodes to vector db...")
                try:
                    VectorStoreIndex.from_documents(
                        documents,
                        storage_context=storage_context,
                        show_progress=True,
                        service_context=service_context,
                    )
                except Exception as e:
                    self.tool.stream_log(
                        f"Error adding nodes to vector db: {e}",
                        level=LogLevel.ERROR,
                    )
                    raise Exception(f"Error adding nodes to vector db: {e}")
                self.tool.stream_log("Added nodes to vector db")

        self.tool.stream_log("Done indexing file")
        return doc_id
