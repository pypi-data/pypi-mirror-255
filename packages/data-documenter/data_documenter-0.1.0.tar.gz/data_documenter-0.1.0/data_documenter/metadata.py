import pandas as pd
import os
import shutil
import subprocess
from .metadocs import MetaDocs

class DataEntry:
    def __init__(self, name, eltype, updated):
        self.name = name
        self.eltype = eltype
        self.updated = updated

class Metadata:
    def __init__(self, name="", description=""):
        self.name = name
        self.description = description
        self.items = []

    def fit(self, dataframe):
        for column in dataframe.columns:
            # Create a DataEntry for each column in the DataFrame
            name = column
            eltype = dataframe[column].dtype.name
            updated = dataframe[column].count()
            self.items.append(DataEntry(name, eltype, updated))

    def markdown(self):
        md = f"# {self.name}\n{self.description}\n\n"
        for item in self.items:
            md += f"???+ note \"{item.name}\"\n"
            md += f"\telement type: {item.eltype}  \n"
            md += f"\tNot nulls: {item.updated}  \n\n"
        return md

    def make_docs(self, path):
        # Path to the mkdocs_template.yml within your package
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'mkdocs.yml')
        yml_path = os.path.join(path, "mkdocs.yml")

        # Ensure docs directory exists
        docs_path = os.path.join(path, "docs")
        os.makedirs(docs_path, exist_ok=True)

        # Save markdown content to index.md
        markdown_content = self.markdown()
        with open(os.path.join(docs_path, "index.md"), "w") as f:
            f.write(markdown_content)

        shutil.copyfile(template_path, yml_path)

        subprocess.run([
            "mkdocs",
            "build",
            "-f", yml_path,
            "--no-directory-urls"
            ],
            check=True
        )
        return MetaDocs(path)