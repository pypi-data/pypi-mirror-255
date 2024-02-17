# Copyright 2023 Karlsruhe Institute of Technology
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
from urllib.parse import parse_qs

from kadi.ext.db import db
from kadi.lib.db import composite_index
from kadi.lib.db import generate_check_constraints
from kadi.lib.db import SimpleTimestampMixin
from kadi.lib.utils import SimpleReprMixin


class SavedSearch(SimpleReprMixin, SimpleTimestampMixin, db.Model):
    """Model representing saved searches."""

    class Meta:
        """Container to store meta class attributes."""

        representation = ["id", "user_id", "name", "object"]
        """See :class:`.SimpleReprMixin`."""

        check_constraints = {
            "name": {"length": {"max": 150}},
            "query_string": {"length": {"max": 4096}},
        }
        """See :func:`kadi.lib.db.generate_check_constraints`."""

    __tablename__ = "saved_search"

    __table_args__ = (
        *generate_check_constraints(Meta.check_constraints),
        composite_index(__tablename__, "user_id", "object"),
    )

    id = db.Column(db.Integer, primary_key=True)
    """The ID of the saved search, auto incremented."""

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    """The ID of the :class:`.User` the saved search belongs to."""

    name = db.Column(db.Text, nullable=False)
    """The name of the saved search.

    Restricted to a maximum length of ``150`` characters.
    """

    object = db.Column(db.Text, nullable=False)
    """The type of object the saved search refers to.

    Currently always refers to a specific searchable model via its table name.
    """

    query_string = db.Column(db.Text, nullable=False)
    """The query string representing the saved search.

    This simply corresponds to the raw URL query parameter string used when searching
    the corresponding object. May be stored with or without a leading question mark.

    Restricted to a maximum length of ``4096`` characters.
    """

    user = db.relationship("User", back_populates="saved_searches")

    @property
    def qparams(self):
        """Get a dictionary representation of the query string of this saved search.

        Corresponds to the results of Python's ``urllib.parse.parse_qs``.
        """
        query_string = self.query_string

        if self.query_string.startswith("?"):
            query_string = query_string[:1]

        return parse_qs(query_string)

    @classmethod
    def create(cls, *, user, name, object, query_string):
        """Create a new saved search and add it to the database session.

        :param user: The user the saved search belongs to.
        :param name: The name of the saved search.
        :param object: The object the saved search refers to.
        :param query_string: The query string of the saved search.
        :return: The new :class:`SavedSearch` object.
        """
        saved_search = cls(
            user=user, name=name, object=object, query_string=query_string
        )
        db.session.add(saved_search)

        return saved_search
