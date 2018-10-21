from typing import List

from django.utils import safestring
from django.utils.safestring import mark_safe


def wrap_html_tag(tag_name: str, elements: List[str]) -> str:
    return f"<{tag_name}>" + f"</{tag_name}><{tag_name}>".join(str(el) for el in elements) + f"</{tag_name}>"


def create_table(header: List[str], rows: List[List[str]]) -> safestring:
    headers_html = wrap_html_tag("th", header)
    rows_html = wrap_html_tag("tr", [wrap_html_tag("td", row) for row in rows])
    return mark_safe(f"""
        <table class='table table-hover table-responsive'>
                    <thead>
                    <tr>
                        {headers_html}
                    </tr>
                    </thead>
                    <tbody>
                    {rows_html}
                    </tbody>
                </table>
        """)
