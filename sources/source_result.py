import asyncio
import traceback
import inspect
from typing import List


import aiohttp

from templates import templates

class SourceURL:
    def __init__(self, text, url, override=""):
        self.text = text
        self.url = url
        self.override = override
    
    def __str__(self):
        if self.override:
            return self.override
        else:
            return f"<a target='_blank' class='btn btn-primary btn-sm my-1' href='{self.url}'>{self.text}</a>"

class Source:
    def __init__(self, variant, consensus):
        self.variant: dict = variant
        self.consensus: dict = consensus
        self.logs: List[dict] = []
        self.executed: bool = False
        self.complete: bool = False
        self.error: bool = False
        self.timeout: bool = False
        self.found: bool = True
        self.entries: dict = {}
        self.new_variant_data = {}
        self.matches_consensus = True
        self.matches_consensus_tooltip = []

        self.current_entry = ()  # stores the entry ((key), func) that is currently being executed so it can possibly be restored

        self.html_title = self.get_name()
        self.html_subtitle = ""
        self.html_text = ""
        self.html_links = {}
        self.set_entries()

        self.name = self.get_name()

    def set_entries(self) -> dict:
        raise NotImplementedError(f"Need to implement 'set_entries' for {self.__class__.__name__}")

    def is_hidden(self) -> bool:
        return False

    def is_complete(self) -> bool:
        """
        Can be used to check if a source has everything needed to get results.
        """
        return True

    async def execute(self, session: aiohttp.ClientSession):
        self.session = session
        self.executed = False
        self.complete = False
        self.found = True
        self.error = False
        self.timeout = False
        self.matches_consensus = True
        self.matches_consensus_tooltip = []

        entry = self.get_entry()
        
        if self.error:  # something wrong with entries
            return self
        if not entry:
            self.log_debug(f"No entry")
            return
        self.log_debug(f"Entry: {entry.__name__}")
        if not inspect.iscoroutinefunction(entry):
            self.error = True
            self.log_error(f"{entry} is not async!")
            return self
        try:
            await entry()
            self.executed = True
        except TimeoutError as e:
            self.timeout = True
            self.log_error("Timeout")
        except Exception as e:
            self.error = True
            self.log_error(traceback.format_exc())
            print(f"Error {self}\n", "".join([m["message"] for m in self.logs]))
        return self


    def get_entry(self):
        for keys, entry in self.entries.items():
            if type(keys) != tuple:
                self.error = True
                self.log_error(f"Not a tuple: {keys}")
                break
            all_keys_in_variant = all([key in self.variant for key in keys])
            if all_keys_in_variant:
                self.current_entry = self.entries.pop(keys, None)
                self.current_entry = (keys, entry)
                return entry
        return None

    def restore_entry(self):
        self.log_info("Restoring entry")
        keys, func = self.current_entry
        self.entries[keys] = func

    def get_html(self):
        return templates.get_template(
            "card.html.jinja2", 
        ).render(source=self)

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

    async def async_get_text(self, url, *args, **kwargs):
        try:
            self.log_debug(f"get_text: {url}")
            async with self.session.get(url, *args, **kwargs) as response:
                resp = await response.text()
                return response, resp
        except asyncio.TimeoutError:
            self.timeout = True
            raise TimeoutError()

    async def async_post_text(self, url, *args, **kwargs):
        try:
            self.log_debug(f"post_text: {url}")
            async with self.session.post(url, *args, **kwargs) as response:
                resp = await response.text()
                return response, resp
        except asyncio.TimeoutError:
            self.timeout = True
            raise TimeoutError()

    async def async_get_json(self, url, *args, **kwargs):
        try:
            self.log_debug(f"get_json: {url}")
            async with self.session.get(url, *args, **kwargs) as response:
                resp = await response.json()
                return response, resp
        except asyncio.TimeoutError:
            self.timeout = True
            raise TimeoutError()
    
    async def async_post_json(self, url, *args, **kwargs):
        try: 
            self.log_debug(f"post_json: {url}")
            async with self.session.post(url, *args, **kwargs) as response:
                resp = await response.json()
                return response, resp
        except asyncio.TimeoutError:
            self.timeout = True
            raise TimeoutError()

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