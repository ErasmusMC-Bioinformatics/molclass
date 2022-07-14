import traceback
import inspect
from typing import List


import aiohttp

from templates import templates

class Source:
    def __init__(self, variant):
        self.variant: dict = variant
        self.html = ""
        self.logs: List[dict] = []
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

        self.log_debug(f"Starting execute()")
        entry = self.get_entry()
        
        if self.error:  # something wrong with entries
            return self
        if not entry:
            self.log_debug(f"No entry")
            return
        self.log_debug(f"Entry: {entry}")
        if not inspect.iscoroutinefunction(entry):
            self.error = True
            self.log_error(f"{entry} is not async!")
            return self
        try:
            await entry()
            self.executed = True
        except Exception as e:
            self.error = True
            self.log_error(traceback.format_exc())
            print(f"Error {self}\n", "".join(self.logs))
        self.log_debug(f"Finished execute()")
        return self


    def get_entry(self):
        for keys, entry in self.entries.items():
            if type(keys) != tuple:
                self.error = True
                self.log_error(f"Not a tuple: {keys}")
                break
            all_keys_in_variant = all([key in self.variant for key in keys])
            if all_keys_in_variant:
                self.entries.pop(keys, None)
                return entry
        return None

    def set_html(self, title="", text="", subtitle="", links=[]):
        if not title:
            title = f"{self}"
        self.html = templates.get_template(
            "card.html.jinja2", 
        ).render(title=title, text=text, subtitle=subtitle, links=links)

    def log(self, message, level="info"):
        self.logs.append({
            "level": level,
            "source": self.get_name(),
            "message": message
        })

    def log_debug(self, message):
        self.log(message, level="debug")

    def log_info(self, message):
        self.log(message, level="info")
    
    def log_warning(self, message):
        self.log(message, level="warning")

    def log_error(self, message):
        self.log(message, level="error")

    def consume_logs(self):
        logs = self.logs
        self.logs = []
        return logs

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