import os

import aiofiles
import yaml
from jinja2 import Environment, BaseLoader
from pydantic import BaseSettings, Field, BaseModel
from pydantic.error_wrappers import ValidationError

from .source_result import Source

TEMPLATE = """
<table class="table">
<tr>
<th>List</th>
<th>Message</th>
</tr>
{% for message in messages %}
    <tr>
        <td><a target="_blank" href="{{message[2]}}">{{message[0]}}</a></td>
        <td>{{message[1]}}</td>
    </tr>
{% endfor %}
</table>
"""

class GeneList(BaseModel):
    name: str
    genes: list[str]
    url: str
    message: str


class GeneListsSchema(BaseModel):
    __root__: list[GeneList]

class Secrets(BaseSettings):
    gene_lists: str = Field(default="databases/gene_lists.yml", env="GENE_LISTS")


secrets = Secrets()

class GeneLists(Source):
    def set_entries(self):
        self.entries = {
            ("gene",): self.gene,
        }

    def is_complete(self) -> bool:
        if os.path.exists(secrets.gene_lists):
            with open(secrets.gene_lists, "r") as gene_list_config:
                data = yaml.safe_load(gene_list_config)
                try:
                    GeneListsSchema.parse_obj(data)
                    return True
                except ValidationError as e:
                    print("Gene list config did not match expected schema:", e)
        else:
            print("Could not find  gene lists config:", secrets.gene_lists)
        return False
    
    async def gene(self):
        async with aiofiles.open(secrets.gene_lists, "r") as gene_list_config:
            data = await gene_list_config.read()
            gene_lists = yaml.safe_load(data)

        messages = set()
        for gene_list in gene_lists:
            if self.variant["gene"].upper() in gene_list["genes"]:
                messages.add((gene_list["name"], gene_list["message"], gene_list["url"]))
        
        if len(messages) > 0 :
            template = Environment(loader=BaseLoader).from_string(TEMPLATE)
            self.html_text = template.render(messages=messages)
        else:
            self.html_text = "Not present in configured gene list."
            self.found = False

    def get_name(self):
        return "Gene Lists"
