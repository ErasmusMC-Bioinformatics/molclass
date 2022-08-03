from jinja2 import Environment, BaseLoader

from .source_result import Source, SourceURL
from search import parse_cdot, parse_transcript

CORRECTION_BUTTONS = """
{% if correction %}
    <button class='btn btn-success'>{{ correction }} <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16">
  <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/>
</svg></button>
{% endif %}
{% for correction in corrections %}
    <a target="_blank" class="btn btn-warning my-1" href="/search?search={{ correction|safe }}">{{ correction }}</a>
{% endfor %}
"""

class Mutalyzer(Source):
    def set_entries(self):
        self.entries = {
            ("transcript", "cdot"): self.transcript_cdot,
        }

    async def transcript_cdot(self):
        transcript = self.variant["transcript"]
        cdot = self.variant["cdot"]

        transcript_cdot = f"{transcript}:{cdot}"
        self.html_links["main"] = SourceURL("Go", f"https://v3.mutalyzer.nl/namechecker/{transcript_cdot}")
        
        # https://v3.mutalyzer.nl/api/name_check/NM_002691.3%3Ac.1958G%3ET
        name_check_url = f"https://v3.mutalyzer.nl/api/name_check/{transcript_cdot}"

        resp, name_check_json = await self.async_get_json(name_check_url)

        corrections = []
        if "input_description" in name_check_json:
            if "corrected_description" in name_check_json:
                corrected = name_check_json["corrected_description"]
                corrected_cdot = parse_cdot(corrected)
                if corrected_cdot and cdot != corrected_cdot["cdot"]:
                    corrections.append(corrected)
            if "normalized_description" in name_check_json:
                normalized = name_check_json["normalized_description"]
                normalized_cdot = parse_cdot(normalized)
                if normalized_cdot and cdot != normalized_cdot["cdot"]:
                    corrections.append(normalized)
                
                normalized_transcript = parse_transcript(normalized)

                self.new_variant_data.update(normalized_cdot)
                self.new_variant_data.update(normalized_transcript)
        
        template = Environment(loader=BaseLoader).from_string(CORRECTION_BUTTONS)
        if corrections:
            self.html_text = template.render(corrections=set(corrections))
        else:
            self.html_text = template.render(correction=transcript_cdot)
        
        reference_url = f"https://v3.mutalyzer.nl/api/reference_model/?reference_id={transcript}"
        resp, reference_json = await self.async_get_json(reference_url)
        
        if "features" not in reference_json:
            self.log_info("No features")
            return 
        if "features" in reference_json:
            features = reference_json["features"]
            for feature in features:
                if feature["type"] == "gene":
                    self.new_variant_data["gene"] = feature["id"]

                    if "qualifiers" in feature:
                        qualifiers = feature["qualifiers"]
                        if "HGNC" in qualifiers:
                            self.new_variant_data["hgnc_id"] = qualifiers["HGNC"]
        
        self.complete = True





