import traceback
import inspect
from typing import List


import aiohttp

from templates import templates

class Source:
    def __init__(self, variant):
        self.variant: dict = variant
        self.html = ""
        self.log: List[dict] = []
        self.executed: bool = False
        self.complete: bool = False
        self.error: bool = False
        self.entries: dict = {}
        self.new_variant_data = {}
        self.set_entries()

    def set_entries(self) -> dict:
        raise NotImplementedError(f"Need to implement 'set_entries' for {self.__class__.__name__}")

    async def execute(self, session: aiohttp.ClientSession):
        self.session = session
        self.executed = False
        self.complete = False
        self.error = False
        entry = self.get_entry()
        if not entry:
            return

        if not inspect.iscoroutinefunction(entry):
            self.error = True
            self.log.append(f"{self} {entry} is not async!")
            return self
        try:
            await entry()
            self.executed = True
        except Exception as e:
            self.error = True
            self.log.append(traceback.format_exc())
            print(f"Error {self}\n", "".join(self.log))
                
        return self


    def get_entry(self):
        for keys, entry in self.entries.items():
            all_keys_in_variant = all([key in self.variant for key in keys])
            if all_keys_in_variant:
                self.entries.pop(keys, None)
                return entry
        return None

    def set_html(self, title="", text="", subtitle="", links=[]):
        self.html = templates.get_template(
            "card.html.jinja2", 
        ).render(title=title, text=text, subtitle=subtitle, links=links)

    def get_name(self):
        return f"{self}"

    def __str__(self):
        return f"{self.__class__.__name__}"

class SourceResult:
    def __init__(self, name, new_data: dict, html, log=[], complete=True, error=""):
        self.name = name
        self.new_data: dict = new_data
        self.html = html
        self.log = log
        self.complete = complete
        self.error = ""