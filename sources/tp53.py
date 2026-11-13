from collections import defaultdict

from jinja2 import Environment, BaseLoader

from .source_result import HIGHLIGHT, Source, SourceURL

SUMMARY_TABLE_TEMPLATE = """
<table class='table'>
{% for summ, count in summary.items() %}
    <tr>
        <td>{{ summ }}</td>
        <td>{{ count }}</td>
    </tr>
{% else %}
    <tr>
        <td>No matches</td>
    </tr>
{% endfor %}
</table>
"""


class TP53(Source):
    def set_entries(self):
        self.entries = {
            ("transcript", "cdot"): self.transcript_cdot,
            ("gene", "cdot"): self.gene_cdot,
            ("gene", "gene_cdot"): self.gene_cdot,
        }

    def is_optional(self) -> bool:
        return True

    async def transcript_cdot(self):
        """
        Looks up the gene of the transcript, so this doesn't have to wait for another source to supply the gene
        """
        gene = await self.resolve_gene()
        if gene:
            await self.report(gene, self.variant["cdot"])
        else:
            # not complete, so gene_cdot() is tried when the meta data has a gene
            self.hidden = True

    async def gene_cdot(self):
        cdot = (
            self.variant["gene_cdot"]
            if "gene_cdot" in self.variant
            else self.variant["cdot"]
        )
        await self.report(self.variant["gene"], cdot)

    async def report(self, gene, cdot):
        """
        Queries the tp53 isb cgc database if the variant is in tp53
        """
        if gene != "TP53":
            self.complete = True
            self.hidden = True
            return

        self.html_class = HIGHLIGHT

        url = "https://tp53.cancer.gov/results_somatic_mutation_list"

        text = f"""
        <form target="_blank" action="{url}" method="post">
            <input name="sm_include_cdna_list" value="{cdot}" type="hidden" />
            <input type="submit" value="Go"  class="btn btn-primary">
        </input>"""

        self.html_links["main"] = SourceURL("Go", url, override=text)
        """
        form_data = {
            "start": 0,
            "length": 100,
            "query_dataset": "Somatic",
            "criteria": {
                "exclude":[],
                "include":[{
                    "between_op":False,
                    "column_name":"c_description",
                    "or_group":"variation",
                    "vals":[cdot],
                    "wrap_with":"\""
                }]
            },
            "order[0][column]": 2,
            "order[0][dir]": "asc",
            "draw": 7
        }
        headers = {
            'content-type': "multipart/form-data",
            'Accept-Encoding': "gzip, deflate, br",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'X-Requested-With': "XMLHttpRequest",
            'cache-control': "no-cache",
            'Postman-Token': "5eef6fb6-c48d-4d80-872c-bb8031153c5a"
        }
        url = "https://tp53.isb-cgc.org/mutation_query"
        async with self.session.post(url, data=form_data, headers={}) as response:
            print(await response.text())
            resp = await response.json()
            
        response, mutation_json = await self.async_post_json(url, data=form_data, headers=headers)
        self.log_warning(f"{response.status}")
        """

        url = "https://tp53.cancer.gov/mutation_query"

        # super meh, but this is what tp53 accepts...
        # somewhere in this monstrosity is the cdot that's the actualy query
        payload = f'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="start"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="length"\r\n\r\n100\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query_dataset"\r\n\r\nSomatic\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="criteria"\r\n\r\n{{"exclude":[],"include":[{{"between_op":false,"column_name":"c_description","or_group":"variation","vals":["{cdot}"],"wrap_with":"\\""}}]}}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="order[0][column]"\r\n\r\n2\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="order[0][dir]"\r\n\r\nasc\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="draw"\r\n\r\n7\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--'
        headers = {
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            "cache-control": "no-cache",
            "Postman-Token": "cbd812d6-803d-420e-adfa-c16aff8eee8b",
        }

        resp, response = await self.async_post_json(url, data=payload, headers=headers)

        if resp.status != 200:
            self.log_warning("Could not load TP53 mutation_query result")
            return

        summary_dict = defaultdict(int)
        for entry in response["data"]:
            if "TransactivationClass" not in entry:
                ta_class = "NA"
            else:
                ta_class = entry["TransactivationClass"]

            summary_dict[ta_class] += 1

        template = Environment(loader=BaseLoader()).from_string(SUMMARY_TABLE_TEMPLATE)
        self.html_text = template.render(summary=summary_dict)

        self.complete = True

    def get_name(self):
        return "The TP53 Database"
