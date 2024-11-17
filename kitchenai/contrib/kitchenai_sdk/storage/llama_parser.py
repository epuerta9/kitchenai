import logging
from typing import TypedDict

from llama_index.core import Document
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import DocxReader
from llama_index.readers.file import FlatReader
from llama_index.readers.file import HTMLTagReader
from llama_index.readers.file import ImageReader
from llama_index.readers.file import MarkdownReader
from llama_index.readers.file import PandasCSVReader
from llama_index.readers.file import PDFReader
from llama_parse import LlamaParse


logger = logging.getLogger(__name__)
import nest_asyncio; nest_asyncio.apply()



class ParserResponse(TypedDict):
    documents: list[Document]
    is_llama_api: bool

class Parser:

    def __init__(self, api_key: str = None):
        #PDF Reader with `SimpleDirectoryReader`
        self.llama_parse = LlamaParse(
            result_type="markdown",
            api_key=api_key
        ) if api_key else None

        pdf_parser = PDFReader()

        # Docx Reader example
        docx_parser = DocxReader()

        # Flat Reader example
        text_reader = FlatReader()


        # HTML Tag Reader example
        html_reader = HTMLTagReader()


        # Image Reader example
        image_reader = ImageReader()

        # Markdown Reader example
        md_parser = MarkdownReader()


        csv_parser = PandasCSVReader()

        # PyMuPDF Reader example

        self.file_extractor = {
            ".pdf": pdf_parser,
            ".csv": csv_parser,
            ".md": md_parser,
            ".jpg": image_reader,
            ".jpeg": image_reader,
            ".png": image_reader,
            ".html": html_reader,
            ".txt": text_reader,
            ".docx": docx_parser
        }


    def load(self, dir: str, metadata: dict[str,str] = None,  extension=None, file_size_mb=None) -> ParserResponse:
        """
            load uses a filename and simple directory loader to load the PDF
        """

        def add_meta(filename: str) -> dict[str,str]:
            return metadata
            #to keep track if we used the llama api or loaded the file locally. For billing purposes later
        is_llama_api = False
        if file_size_mb:
            if file_size_mb > 150 and self.llama_parse:

                is_llama_api = True
                if extension:
                    #reset the file extractor and try again with llama_parse
                    self.file_extractor[extension] = self.llama_parse

                    reader = SimpleDirectoryReader(
                        dir, file_extractor=self.file_extractor, file_metadata=add_meta
                    )

                    documents = reader.load_data()
            else:
                reader = SimpleDirectoryReader(
                    dir, file_extractor=self.file_extractor, file_metadata=add_meta
                )

                documents = reader.load_data()
        else:

            reader = SimpleDirectoryReader(
                dir, file_extractor=self.file_extractor, file_metadata=add_meta
            )

            documents = reader.load_data()


        if documents:
            if not documents[0].text:
                #use llama parse as a backup
                is_llama_api = True
                logger.warning("documents text was empty, re-trying with llamaparse")
                if extension and self.llama_parse:
                    #reset the file extractor and try again with llama_parse
                    self.file_extractor[extension] = self.llama_parse

                    reader = SimpleDirectoryReader(
                        dir, file_extractor=self.file_extractor, file_metadata=add_meta
                    )

                    documents = reader.load_data()
                else:
                    logger.error("error llama parse and default loaders failed to extract any text from document")
                    raise Exception("error llama parse and default loaders failed to extract any text from document")


        if documents and not documents[0].text:
            logger.error("error llama parse and default loaders failed to extract any text from document")

            #update the project with a total internal fail
            raise Exception("error llama parse and default loaders failed to extract any text from document")

        return {
            "documents": documents,
            "is_llama_api" : is_llama_api
        }


    def load_string(self, body: str, metadata: dict[str,str] = None) -> list[Document]:
        """
            loads a single document
        """
        doc = Document(text=body, metadata=metadata)


        return doc
