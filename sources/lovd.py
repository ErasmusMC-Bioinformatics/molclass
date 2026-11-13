import asyncio
import json
import re
import time
import urllib.parse
from collections import defaultdict

import aiohttp
from jinja2 import BaseLoader, Environment

from util import get_release_tag
from .source_result import Source, SourceURL

_LOVD_BOT_PROTECTION_RE = re.compile(r"checking your browser", re.I)

# LOVD can be slow, and the answer for a gene with many entries is large: it gets more time than the 5 seconds
# of the other sources. A request that LOVD didn't answer in time, or answered with a server error, is tried
# once more after waiting this many seconds. Nothing else is tried again: LOVD blocks clients that send
# too many requests, or the same request over and over.
LOVD_TIMEOUT = aiohttp.ClientTimeout(total=10)
RETRY_WAITS = (2,)
# LOVD asks clients of its API to say who they are
USER_AGENT = f"Molclass/{get_release_tag()} (+https://github.com/ErasmusMC-Bioinformatics/molclass)"
# when LOVD refuses (blocked, too many requests), it is not asked again for this many seconds
PAUSE_AFTER_REFUSAL = 30 * 60
_paused_until = 0.0
_LOVD_BLOCKED_RE = re.compile(r"blacklisted|too many requests", re.I)
# LOVD's answer, instead of a list of variants, for a gene it doesn't have
GENE_NOT_FOUND = "This gene does not exist."
SUMMARY_TABLE_TEMPLATE = """
<table class='table caption-top'>
    <caption>{{ entries }} entries - {{ vkgl_entries }} VKGL-NL</caption>
{% for summ, count in vkgl_summary.items() %}
    <tr>
        <td>{{ summ }}</td>
        <td>{{ count }}</td>
    </tr>
{% endfor %}
</table>

{% if insight_summary %}
    <table class='table caption-top'>
        <caption>{{ insight_entries }} InSiGHT</caption>
    {% for summ, count in insight_summary.items() %}
        <tr>
            <td>{{ summ }}</td>
            <td>{{ count }}</td>
        </tr>
    {% endfor %}
    </table>
{% endif %}
"""


class LOVDRefused(Exception):
    """LOVD refuses requests from this server: it blocked it, or it sent too many requests"""


class LOVD(Source):
    def set_entries(self):
        self.entries = {
            ("gene", "cdot"): self.gene_cdot,
        }
        return self.entries

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://databases.lovd.nl/shared/variants/{gene}/unique"
        self.found = False

        self.html_links["main"] = SourceURL("Gene", url)

    async def gene_cdot(self):
        """
        Searches the LOVD website for a variant, then performs a secondary request and
        parses the variant page, if it exists
        """
        gene = self.variant["gene"]
        cdot = self.variant["cdot"]
        enc_gene = urllib.parse.quote(gene)
        enc_cdot = urllib.parse.quote(cdot)
        gene_url = f"https://databases.lovd.nl/shared/variants/{enc_gene}/unique"
        query_url = f"https://databases.lovd.nl/shared/api/rest.php/variants/{enc_gene}?search_position={enc_cdot}&show_variant_effect=1&format=application/json"
        try:
            json = await self._lovd_get_json(query_url)
        except LOVDRefused as e:
            self.log_warning(str(e))
            self.html_text = (
                "LOVD refuses requests from this server at the moment, Molclass doesn't ask it again for "
                f"{PAUSE_AFTER_REFUSAL // 60} minutes. Look the variant up on the gene page."
            )
            self.html_links["gene"] = SourceURL("Gene", gene_url)
            return
        except (asyncio.TimeoutError, aiohttp.ClientError, ValueError) as e:
            # the link to the gene works without the answer
            self.log_warning(f"LOVD did not answer after {len(RETRY_WAITS) + 1} tries: {type(e).__name__}: {e}")
            self.timeout = True
            self.html_text = "LOVD did not answer. Search again, or look the variant up on the gene page."
            self.html_links["gene"] = SourceURL("Gene", gene_url)
            return
        # a gene that is not in LOVD is answered right away, there is nothing to link to
        if isinstance(json, str) and json.strip() == GENE_NOT_FOUND:
            self.html_text = f"{gene} is not in LOVD"
            self.found = False
            return
        if isinstance(json, str):
            self.html_text = f"Variant not found. LOVD reports the following: {json}"
            self.found = False
            return
        if not json:
            self.log_warning(f"No rows found for '{cdot}'")
            self.found = False
            self.html_text = "Variant not found"
            self.html_links["gene"] = SourceURL("Gene", gene_url)
            return

        transcript = json[0]["position_mRNA"][0].split(":")[0]
        dbid = json[0]["Variant/DBID"]

        transcript_url = f"https://databases.lovd.nl/shared/transcripts/{transcript}"
        variant_url = f"https://databases.lovd.nl/shared/variants/{enc_gene}?search_VariantOnGenome%2FDBID={dbid}"

        self.html_links["gene"] = SourceURL("Gene", gene_url)
        self.html_links["transcript"] = SourceURL("Transcript", transcript_url)
        self.html_links["variant"] = SourceURL("Variant", variant_url)

        vkgl_summary_dict = defaultdict(int)
        insight_dict = defaultdict(int)
        row_count = 0

        for gene_object in json:
            if "VKGL-NL" in gene_object["owned_by"][0]:
                vkgl_summary_dict[gene_object["effect_reported"][0]] += 1
            if "InSiGHT" in gene_object["owned_by"][0]:
                insight_dict[gene_object["effect_reported"][0]] += 1
            row_count += 1

        if gene not in ["MLH1", "PMS2", "MSH2", "MSH6"]:
            insight_dict = {}

        template = Environment(loader=BaseLoader()).from_string(SUMMARY_TABLE_TEMPLATE)
        self.html_text = template.render(
            vkgl_summary=vkgl_summary_dict,
            vkgl_entries=sum(vkgl_summary_dict.values()),
            insight_summary=insight_dict,
            insight_entries=sum(insight_dict.values()),
            entries=row_count,
        )

    async def _lovd_get_json(self, url: str) -> dict[str, object] | list[object]:
        """
        Returns the answer of LOVD. Only a request that LOVD didn't answer in time or answered with a server error
        is tried again, see RETRY_WAITS. When LOVD refuses, it is not asked again for a while, see PAUSE_AFTER_REFUSAL.
        """
        global _paused_until
        if time.time() < _paused_until:
            raise LOVDRefused(f"LOVD refused an earlier request, it is asked again after {time.strftime('%H:%M', time.localtime(_paused_until))}")

        error: Exception = ValueError("no answer")
        for wait in (0, *RETRY_WAITS):
            await asyncio.sleep(wait)
            try:
                return await self._lovd_request(url)
            except LOVDRefused:
                _paused_until = time.time() + PAUSE_AFTER_REFUSAL
                raise
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                error = e
                self.log_info(f"LOVD try failed: {type(e).__name__}: {e}")
        raise error

    async def _lovd_request(self, url: str) -> dict[str, object] | list[object]:
        """LOVD url's contain a js redirect for access validation.

        The request returns HTML and sets cookie headers. Afterwards it expects a
        reload of the page with '&ncr' appended to the url
        """
        headers = {"User-Agent": USER_AGENT}
        async with self.session.get(url, timeout=LOVD_TIMEOUT, headers=headers) as resp:
            ctype = resp.headers.get("Content-Type", "")
            body = await resp.text()
            if resp.status in (403, 429) or (resp.status != 200 and _LOVD_BLOCKED_RE.search(body)):
                raise LOVDRefused(f"LOVD refused the request ({resp.status}){': blocked' if _LOVD_BLOCKED_RE.search(body) else ''}")
            if resp.status >= 500:
                raise aiohttp.ClientError(f"LOVD server error {resp.status}")

        # a variant that is not in LOVD is a 404 with an empty list, a gene that is not in LOVD a 404 with a sentence
        if body.strip() == GENE_NOT_FOUND:
            return GENE_NOT_FOUND
        if "json" in ctype:
            return json.loads(body)

        if _LOVD_BOT_PROTECTION_RE.search(body):
            async with self.session.get(url + "&ncr", timeout=LOVD_TIMEOUT, headers=headers) as resp2:
                if resp2.status in (403, 429):
                    raise LOVDRefused(f"LOVD refused the request ({resp2.status})")
                if resp2.status >= 500:
                    raise aiohttp.ClientError(f"LOVD server error {resp2.status}")
                return await resp2.json(content_type=None)

        raise ValueError(f"Unexpected LOVD response ({ctype}): {body[:200]}")
