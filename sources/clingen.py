import re

from yaml import parse

from search import parse_search
from util import get_pdot_abbreviation

from .source_result import Source, SourceURL

HEADER_GENE_RE = re.compile("\((?!p\.)(?P<gene>[^\)]+)", re.IGNORECASE)
JSOND_RE = re.compile('href="(?P<url>/allele/[^"]+)"')

class Clingen(Source):
    def set_entries(self):
        self.entries = {
            ("transcript", "cdot"): self.transcript_cdot,
        }

    def is_hidden(self) -> bool:
        return True

    async def transcript_cdot(self):
        """
        Performs a search on the clingen website and parses the search result page
        for the link to an API url for the variant
        """
        transcript = self.variant['transcript']
        cdot = self.variant['cdot']
        transcript_cdot = f"{transcript}:{cdot}"

        url = f"https://reg.clinicalgenome.org/redmine/projects/registry/genboree_registry/allele?hgvsOrDescriptor={transcript_cdot}"

        resp, clingen_result = await self.async_get_text(url)

        if "We were not able to parse" in clingen_result:
            self.found = False
            self.log_warning("Variant not found")
            return

        jsond_url_match = JSOND_RE.search(clingen_result)

        if not jsond_url_match:
            self.found = False
            return
        
        jsond_url = jsond_url_match.group("url")
        jsond_url = f"https://reg.clinicalgenome.org{jsond_url}"

        resp, jsond = await self.async_get_json(jsond_url)
        
        if "communityStandardTitle" in jsond:
            standard_titles = jsond["communityStandardTitle"]
            for standard_title in standard_titles:
                parsed_search = parse_search(standard_title)
                if "pdot" in parsed_search:
                    parsed_search["pdot"] = get_pdot_abbreviation(parsed_search["pdot"])
                self.new_variant_data.update(parsed_search)
                if m := HEADER_GENE_RE.search(standard_title):
                    self.new_variant_data.update(m.groupdict())
        
        self.complete = True

        
        
        
