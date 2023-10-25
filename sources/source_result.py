import asyncio
import traceback
import inspect
from typing import List


import aiohttp

from templates import templates

class SourceURL:
    """
    Convenience class to style the urls on the source cards on the client webpage
    Optionally can set self.override to whatever to change the styling/behavior
    """
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
        """A read only copy of the current meta data"""
        
        self.consensus: dict = consensus
        """The consensus meta data"""

        self.logs: List[dict] = []
        """Holds the logs for this source for this iteration, should not be used directly, use the methods"""
        
        self.executed: bool = False
        """Is True only after the sources entry executes succesfully"""

        self.complete: bool = False
        """
        If it's true at the end of an iteration the source is considered 'complete',
        as in, no more meta data can be gotten from the source.
        If left on False, the source will be included again in the next iteration checking checking the next entry
        """
        
        self.error: bool = False
        """Did an error occur during this iteration?""" 

        self.timeout: bool = False
        """Did the source time out?"""

        self.found: bool = True
        """Should be set to True if there was no result found in the source database"""

        self.entries: dict = {}
        """
        Holds the 'entries', a ((key), func).
        See set_entries() for more info
        """

        self.new_variant_data = {}
        """Add new meta data to this"""

        self.matches_consensus = True
        """Does this source match with the consensus?"""

        self.matches_consensus_tooltip = []
        """A list of tooltips that will be displayed on the source on the client"""

        self.current_entry = ()
        """Stores the entry that is currently being executed so it can possibly be restored"""

        self.html_title = self.get_name()
        """The title of the source card on the client, defaults to self.get_name()"""

        self.html_subtitle = ""
        """An optional subtitle to the source card on the client"""

        self.html_text = ""
        """The body of the source card on the client"""

        self.html_links = {}
        """A dict of SourceURLs, that will be added to the footer of the source card on the client"""
        
        self.set_entries()

        self.name = self.get_name()
        """self.get_name()"""

    def set_entries(self) -> dict:
        """
        Should set self.entries to a dict of tuple -> func: 
        self.entries = {
            ('transcript', 'cdot'): self.transcript_cdot,
            ('gene',): self.gene, # Note the ',' even though it's only one tag
        }
        And then implementing self.transcript_cdot/self.gene to whatever queries the source with that meta datas
        """
        raise NotImplementedError(f"Need to implement 'set_entries' for {self.__class__.__name__}")

    def is_hidden(self) -> bool:
        """Can be used to hide a card on the client, useful for sources that are just there to increase consensus"""
        return False

    def is_complete(self) -> bool:
        """
        Can be used to check if a source has everything needed to get results.
        """
        return True

    async def execute(self, session: aiohttp.ClientSession):
        """
        Does some house keeping around executing the current entry (if it can)

        """
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
        """
        Goes through self.entries and returns the first entry that can be fulfilled with the current metadat
        """
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
        """
        If an entry isn't completed succesfully but might on the next iteration, 
        restore it so it can be called again
        """
        self.log_info("Restoring entry")
        keys, func = self.current_entry
        self.entries[keys] = func

    def get_html(self):
        """
        Uses the Jinja2 card.html.jinja2 template to render this source to html
        """
        return templates.get_template(
            "card.html.jinja2", 
        ).render(source=self)

    def log(self, message, level="info"):
        """
        Generic log function, should probably use the other logs functions (log_debug, log_info, etc)
        """
        self.logs.append({
            "level": level,
            "source": self.get_name(),
            "message": message
        })

    def log_debug(self, message):
        """self.log(message, level='debug')"""
        self.log(message, level="debug")

    def log_info(self, message):
        """self.log(message, level='info')"""
        self.log(message, level="info")
    
    def log_warning(self, message):
        """self.log(message, level='warning')"""
        self.log(message, level="warning")

    def log_error(self, message):
        """self.log(message, level='error')"""
        self.log(message, level="error")

    def consume_logs(self):
        """Returns self.logs while clearing it"""
        logs = self.logs
        self.logs = []
        return logs

    async def async_get_text(self, url, *args, **kwargs):
        """Uses the aiohttp pool to perform an asynchronous http GET request"""
        try:
            self.log_debug(f"get_text: {url}")
            async with self.session.get(url, *args, **kwargs) as response:
                resp = await response.text()
                return response, resp
        except asyncio.TimeoutError:
            self.timeout = True
            raise TimeoutError()

    async def async_post_text(self, url, *args, **kwargs):
        """Uses the aiohttp pool to perform an asynchronous http POST request"""
        try:
            self.log_debug(f"post_text: {url}")
            async with self.session.post(url, *args, **kwargs) as response:
                resp = await response.text()
                return response, resp
        except asyncio.TimeoutError:
            self.timeout = True
            raise TimeoutError()

    async def async_get_json(self, url, *args, **kwargs):
        """Uses the aiohttp pool to perform an asynchronous http GET request, returning it as parsed json"""
        try:
            self.log_debug(f"get_json: {url}")
            async with self.session.get(url, *args, **kwargs) as response:
                resp = await response.json()
                return response, resp
        except asyncio.TimeoutError:
            self.timeout = True
            raise TimeoutError()
    
    async def async_post_json(self, url, *args, **kwargs):
        """Uses the aiohttp pool to perform an asynchronous http POST request, returning it as parsed json"""
        try: 
            self.log_debug(f"post_json: {url}")
            async with self.session.post(url, *args, **kwargs) as response:
                resp = await response.json()
                return response, resp
        except asyncio.TimeoutError:
            self.timeout = True
            raise TimeoutError()

    def get_name(self):
        """str(self)"""
        return f"{self}"

    def __str__(self):
        """Returns the name of the source class"""
        return f"{self.__class__.__name__}"

class SourceResult:
    def __init__(self, name, new_data: dict, html, log=[], complete=True, error=""):
        self.name = name
        self.new_data: dict = new_data
        self.html = html
        self.log = log
        self.complete = complete
        self.error = ""