import datetime
import json
import os
import tarfile
from pathlib import Path

from mwparserfromhtml.parse.article import Article


class HTMLDump:
    """
    Class file to create instances of Wikimedia Enterprise HTML Dumps
    """

    def __init__(self, filepath: str) -> None:
        """
        Contructor for HTMLDump class
        """
        self.file_path = filepath
        self.size = os.path.getsize(self.file_path) / (1024 * 1024 * 1024)
        self.database = str(Path(self.file_path).name).split("-")[0]

    def __str__(self) -> str:
        """
        String representation of the HTMLDump class
        """
        return f" HTMLDump (database = {self.database}, size = {self.size} GB"

    def __repr__(self) -> str:
        """
        String representation of the HTMLDump class
        """
        return str(self)

    def __iter__(self):
        """
        Iterator of the Article class
        """
        return self.read_dump_local(filepath=self.file_path)

    def read_dump_local(self, filepath: str):
        """
        Reads a local dump file and returns an iterator of the rows.
        Args:
            filepath (str): path to the dump file
        Returns:
            Iterator[List[Any]]: iterator of the rows
        """

        source_path = filepath
        tar_file_ = tarfile.open(source_path, mode="r:gz")
        count = 0
        while True:
            html_fn = tar_file_.next()
            if html_fn is None:
                tar_file_.close()
                return

            else:
                with tar_file_.extractfile(html_fn) as file_input:
                    for line in file_input:
                        article = json.loads(line)
                        count += 1
                        try:
                            yield Document(article)
                        except Exception:
                            print(f"Article parsing failed for: {article}")
                            continue


class Document:
    """
    Class file to create instances of documents within Wikimedia Enterprise HTML Dumps
    """

    def __init__(self, document) -> None:
        """
        Constructor for Article class
        """
        self.document = document
        self.html = Article(document["article_body"]["html"])

    def __str__(self):
        """
        String representation of the Article class
        """
        return f"Document({self.get_title()})"

    def __repr__(self):
        return str(self)

    def get_namespace(self) -> int:
        return self.document["namespace"]["identifier"]

    def get_title(self) -> str:
        return self.document["name"]

    def get_page_id(self) -> int:
        return self.document["identifier"]

    def get_wikitext(self) -> str:
        return self.document["article_body"]["wikitext"]

    def get_qid(self) -> str:
        return self.document["main_entity"]["identifier"]

    def get_article_creation_date(self) -> datetime.date:
        return datetime.datetime.strptime(
            self.document["date_created"], "%Y-%m-%dT%H:%M:%SZ"
        )

    def get_curr_revision_time(self) -> datetime.date:
        return datetime.datetime.strptime(
            self.document["date_modified"], "%Y-%m-%dT%H:%M:%SZ"
        )

    def get_prev_revision_time(self) -> datetime.date:
        return datetime.datetime.strptime(
            self.document["date_previously_modified"], "%Y-%m-%dT%H:%M:%SZ"
        )
