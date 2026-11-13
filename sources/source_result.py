import asyncio
import inspect
import json
import traceback

import aiohttp
from icecream import ic

ic.configureOutput(prefix="debug-", includeContext=True)

import coordinates
from templates import templates


# the look of a card that is only there for some variants, so it is noticed when it is
HIGHLIGHT = "border-warning border-2 bg-warning bg-opacity-10"


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
    """
    A class representing a source with its meta data and logs.

    Attributes:
    variant (dict): A read-only copy of the current meta data.
    consensus (dict): The consensus meta data.
    logs (List[dict]): Holds the logs for this source for this iteration, should not be used directly, use the methods.
    executed (bool): Is True only after the source's entry executes successfully.
    complete (bool): If true at the end of an iteration, the source is considered 'complete', meaning no more meta data can be gotten from the source. If false, the source will be included again in the next iteration checking the next entry.
    error (bool): Indicates if an error occurred during this iteration.
    timeout (bool): Indicates if the source timed out.
    found (bool): Should be set to True if there was no result found in the source database.
    hidden (bool): Set to True to remove the source card from the client, for a source that has nothing to say about this variant.
    entries (dict): Holds the 'entries', a ((key), func). See set_entries() for more info.
    new_variant_data (dict): Add new meta data to this.
    matches_consensus (bool): Indicates if this source matches with the consensus.
    matches_consensus_tooltip (List[str]): A list of tooltips that will be displayed on the source on the client.
    current_entry (Tuple): Stores the entry that is currently being executed so it can possibly be restored.
    html_title (str): The title of the source card on the client, defaults to self.get_name().
    html_subtitle (str): An optional subtitle to the source card on the client.
    html_text (str): The body of the source card on the client.
    html_links (Dict): A dict of SourceURLs that will be added to the footer of the source card on the client.
    html_class (str): Extra css classes for the source card, HIGHLIGHT for a card that should be noticed.
    shared_links (Dict): A dict of SourceURLs that will be added to the Links card on the client, the text should say where it goes. The key is the name used in links_order in the config.
    """

    def __init__(self, variant, consensus):
        self.variant: dict = variant
        self.consensus: dict = consensus
        self.logs: list[dict] = []
        self.executed: bool = False
        self.complete: bool = False
        self.error: bool = False
        self.timeout: bool = False
        self.found: bool = True
        self.hidden: bool = False
        self.entries: dict = {}
        self.new_variant_data = {}
        self.matches_consensus: bool = True
        self.matches_consensus_tooltip = []
        self.current_entry = ()
        self.html_title: str = self.get_name()
        self.html_subtitle: str = ""
        self.html_text: str = ""
        self.html_links = {}
        self.html_class: str = ""
        self.shared_links = {}
        self.set_entries()
        self.name: str = self.get_name()
        self.session: aiohttp.ClientSession

    def set_entries(self):
        """
        Should set self.entries to a dict of tuple -> func:
        self.entries = {
            ('transcript', 'cdot'): self.transcript_cdot,
            ('gene',): self.gene, # Note the ',' even though it's only one tag
        }
        And then implementing self.transcript_cdot/self.gene to whatever queries the source with that meta datas
        """
        raise NotImplementedError(
            f"Need to implement 'set_entries' for {self.__class__.__name__}"
        )

    def is_hidden(self) -> bool:
        """Can be used to hide a card on the client, useful for sources that are just there to increase consensus"""
        return False

    def is_link(self) -> bool:
        """
        A source that only has links doesn't get a card of its own, its links are shown on the Links card,
        with the name of the source as text. The place of the link is set with links_order in the config.
        """
        return False

    def is_optional(self) -> bool:
        """
        An optional source only gets a card once it has a result, instead of a card that says it is loading.
        For a source that has nothing to say about most variants, it should set hidden for those.
        """
        return False

    def is_banner(self) -> bool:
        """
        A banner is shown over the full width of the page instead of as a card, and only once it has a result.
        Put these sources at the start of the sources in the config, so they are above the cards.
        """
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
        self.hidden = False
        self.error = False
        self.timeout = False
        self.matches_consensus = True
        self.matches_consensus_tooltip = []

        entry = self.get_entry()

        if self.error:  # something wrong with entries
            return self
        if not entry:
            self.log_debug("No entry")
            return
        self.log_debug(f"Entry: {entry.__name__}")
        if not inspect.iscoroutinefunction(entry):
            self.error = True
            self.log_error(f"{entry} is not async!")
            return self
        try:
            await entry()
            self.executed = True
        except TimeoutError:
            self.timeout = True
            self.log_error("Timeout")
        except Exception:
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
        self.logs.append(
            {"level": level, "source": self.get_name(), "message": message}
        )

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
                resp = await response.read()
                try:
                    resp = await response.json()
                except json.JSONDecodeError:
                    resp = await response.text()
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

    async def resolve_coordinates(self, build: str = "GRCh37") -> coordinates.Coordinates | None:
        """
        Returns the genomic coordinates of the transcript:cdot of the variant, None if they can't be determined.
        They are also added to the meta data: gdot, g_chr, g_pos, g_ref and g_alt (gdot38, g38_chr, ... for GRCh38).
        Unlike ref/alt, which are the bases of the cdot, these are always on the forward strand.
        """
        hgvs = f"{self.variant['transcript']}:{self.variant['cdot']}"
        resolved = await coordinates.resolve(self.session, hgvs, build)
        if resolved is None:
            self.log_warning(f"Could not map {hgvs} to {build} (Mutalyzer and Ensembl VEP both failed)")
            return None

        suffix = "" if build == "GRCh37" else "38"
        self.new_variant_data[f"gdot{suffix}"] = resolved.gdot
        self.new_variant_data[f"g{suffix}_chr"] = resolved.chr
        self.new_variant_data[f"g{suffix}_pos"] = resolved.pos
        self.new_variant_data[f"g{suffix}_ref"] = resolved.ref
        self.new_variant_data[f"g{suffix}_alt"] = resolved.alt
        return resolved

    async def resolve_gdot(self, build: str = "GRCh37") -> str | None:
        """
        Returns the hgvs genomic notation of the transcript:cdot of the variant, and adds it to the meta data
        as gdot (gdot38 for GRCh38). Use this when the position and bases of resolve_coordinates() are not needed.
        """
        hgvs = f"{self.variant['transcript']}:{self.variant['cdot']}"
        gdot = await coordinates.resolve_gdot(self.session, hgvs, build)
        if gdot:
            self.new_variant_data["gdot" if build == "GRCh37" else "gdot38"] = gdot
        return gdot

    async def resolve_gene(self) -> str | None:
        """
        Returns the gene of the transcript of the variant, None if it can't be determined.
        Use this instead of waiting for the gene in the meta data, which another source has to supply first.
        """
        return await coordinates.resolve_gene(self.session, str(self.variant["transcript"]))

    def get_name(self):
        """str(self)"""
        return f"{self}"

    def __str__(self):
        """Returns the name of the source class"""
        return f"{self.__class__.__name__}"

    def _get(self, data: dict, key: str) -> str | None:
        value = data.get(key)
        return value[0] if value and len(value) > 0 and value[0] != "" else None
