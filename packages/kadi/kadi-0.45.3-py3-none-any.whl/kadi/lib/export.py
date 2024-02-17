# Copyright 2022 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os

from flask import current_app
from flask_babel import format_datetime
from flask_babel import gettext as _
from fpdf import FPDF
from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import SDO
from rdflib import URIRef
from zipstream import ZipStream

import kadi.lib.constants as const
from kadi.lib.utils import formatted_json
from kadi.lib.utils import utcnow
from kadi.lib.web import url_for


class PDF(FPDF):
    """Base PDF export class using FPDF.

    :param title: (optional) The title of the PDF, which will appear in the header on
        each page and in the metadata of the PDF itself.
    """

    def __init__(self, title=""):
        super().__init__()

        self.title = title
        self.generated_at = utcnow()

        fonts_path = current_app.config["FONTS_PATH"]

        self.add_font(
            "DejaVuSans", fname=os.path.join(fonts_path, "dejavu", "DejaVuSans.ttf")
        )
        self.add_font(
            "DejaVuSans",
            fname=os.path.join(fonts_path, "dejavu", "DejaVuSans-Bold.ttf"),
            style="B",
        )
        self.add_font(
            "DejaVuSans",
            fname=os.path.join(fonts_path, "dejavu", "DejaVuSans-Oblique.ttf"),
            style="I",
        )
        self.add_font(
            "DejaVuSansMono",
            fname=os.path.join(fonts_path, "dejavu", "DejaVuSansMono.ttf"),
        )

        self.set_font(size=10, family="DejaVuSans")
        self.set_title(self.title)
        self.add_page()

    @staticmethod
    def format_date(date_time):
        """Format a datetime object in a user-readable manner.

        :param date_time: The datetime object to format as specified in Python's
            ``datetime`` module.
        :return: The formatted datetime string.
        """
        return format_datetime(date_time, format="long", rebase=False)

    def header(self):
        """Automatically prints a header on each page of the generated PDF."""
        self.set_font(size=10)
        self.truncated_cell(self.epw * 0.85, text=self.title, align="L")
        self.cell(w=self.epw * 0.15, text="Kadi4Mat", align="R")
        self.ln(self.font_size + 1)
        self.line(self.l_margin, self.y, self.w - self.r_margin, self.y)
        self.ln(h=5)

    def footer(self):
        """Automatically prints a footer on each page of the generated PDF."""
        self.set_font(size=10)
        self.set_text_color(r=150, g=150, b=150)
        self.set_y(-10)
        self.cell(
            w=self.epw / 2,
            text="{} {}".format(_("Generated at"), self.format_date(self.generated_at)),
            align="L",
        )
        self.cell(w=self.epw / 2, text=str(self.page), align="R")

    def truncated_cell(self, w, text="", **kwargs):
        r"""Print a cell with potentially truncated text based on the cell's width.

        :param w: The width of the cell.
        :param text: (optional) The text content of the cell.
        :param \**kwargs: Additional keyword arguments to pass to fpdf2's ``cell``
            function.
        """
        truncated_text = text

        while self.get_string_width(truncated_text) > w:
            truncated_text = truncated_text[:-1]

        if truncated_text != text:
            truncated_text = f"{truncated_text[:-3]}..."

        self.cell(w=w, text=truncated_text, **kwargs)

    def calculate_max_height(self, contents):
        """Calculate the maximum height that will be required by multiple multi-cells.

        Note that this method always uses the current font family and size for its
        calculations.

        :param contents: A list of tuples containing the width, the text content and the
            font style of each cell.
        :return: The maximum height the cells will require.
        """
        num_lines = 0
        font_style = self.font_style

        for width, text, style in contents:
            self.set_font(style=style)
            num_lines = max(
                num_lines,
                len(self.multi_cell(width, text=text, dry_run=True, output="LINES")),
            )

        # Switch back to the original font style.
        self.set_font(style=font_style)
        return num_lines * self.font_size


class ROCrate(ZipStream):
    r"""Base RO-Crate export class.

    This class behaves like a ``ZipStream``, which can be used to attach file paths and
    streams. Note that the files and the content of the metadata are currently not
    synchronized automatically.

    :param \*args: Additional arguments to pass to the ``ZipStream``.
    :param version: (optional) A version string that represents the current
        specification that is used for the RO-Crate, which will be saved as "version" in
        the metadata describing the main metadata file.
    :param sized: (optional) Whether the crate should keep track of its size.
    :param \**kwargs: Additional keyword arguments to pass to the ``ZipStream``.
    """

    def __init__(self, *args, version=None, sized=True, **kwargs):
        super().__init__(*args, sized=sized, **kwargs)

        ro_crate_spec = "https://w3id.org/ro/crate/1.1"

        self.metadata = {
            "@context": f"{ro_crate_spec}/context",
            "@graph": [
                {
                    "@type": "CreativeWork",
                    "@id": "ro-crate-metadata.json",
                    "about": {
                        "@id": "./",
                    },
                    "conformsTo": {
                        "@id": ro_crate_spec,
                    },
                    "dateCreated": utcnow().isoformat(),
                    "sdPublisher": {
                        "@id": const.URL_INDEX,
                    },
                },
                {
                    "@id": "./",
                    "@type": ["Dataset"],
                    "hasPart": [],
                },
            ],
        }

        self.root_graph.append(
            {
                "@id": const.URL_INDEX,
                "@type": "Organization",
                "name": "Kadi4Mat",
                "description": "An open source software for managing research data.",
                "url": const.URL_INDEX,
            }
        )

        if version is not None:
            self.root_graph[0]["version"] = version

    @property
    def root_graph(self):
        """Get the root graph of the RO-Crate metadata."""
        return self.metadata["@graph"]

    @property
    def root_dataset(self):
        """Get the root dataset of the RO-Crate metadata."""
        return self.root_graph[1]

    def get_entity(self, entity_id):
        """Get an entity of the root graph by its ID.

        :param entity_id: The ID of the entity to retrieve.
        :return: The entity or ``None`` if no suitable entity could be found.
        """
        for entity in self.root_graph:
            if entity.get("@id") == entity_id:
                return entity

        return None

    def dump_metadata(self):
        """Dump the RO-Crate metadata as formatted JSON string.

        :return: The JSON formatted string.
        """
        return formatted_json(self.metadata)


class RDFGraph(Graph):
    """Base RDF graph export class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, bind_namespaces="rdflib", **kwargs)

    def author_ref(self, user_data):
        """Create a URI reference of an author.

        :param user_data: The serialized data of the user, via :class:`.UserSchema`, to
            use as an author.
        :return: The created URI reference.
        """
        if user_data["orcid"]:
            author_ref = URIRef(f"{const.URL_ORCID}/{user_data['orcid']}")
        else:
            author_ref = URIRef(url_for("accounts.view_user", id=user_data["id"]))

        self.add((author_ref, RDF.type, SDO.Person))
        self.add((author_ref, SDO.name, Literal(user_data["displayname"])))

        return author_ref
