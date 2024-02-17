# Copyright 2020 Karlsruhe Institute of Technology
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
from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import request
from flask import session
from flask_babel import gettext as _
from flask_login import current_user

import kadi.lib.constants as const
from .utils import logout_user
from kadi.lib.api.core import json_error_response
from kadi.lib.api.utils import is_api_request
from kadi.lib.web import flash_danger
from kadi.lib.web import url_for
from kadi.modules.accounts.models import UserState


bp = Blueprint("accounts", __name__, template_folder="templates")


@bp.before_app_request
def _before_app_request():
    if current_user.is_authenticated:
        # Clean up the session.
        session.pop(const.SESSION_KEY_NEXT_URL, None)
        session.pop(const.SESSION_KEY_OIDC_DATA, None)

        # If the current user was merged or does not have a valid latest identity, they
        # are logged out completely.
        if (
            current_user.is_merged
            or current_user.identity is None
            or current_user.identity.type not in current_app.config["AUTH_PROVIDERS"]
        ):
            redirect_url = logout_user()
            error_msg = _("This account is currently inactive.")

            if is_api_request():
                return json_error_response(401, description=error_msg)

            flash_danger(error_msg)
            return redirect(redirect_url)

        # These endpoints should still work even if the current user needs email
        # confirmation, is inactive or needs to accept the legal notices before
        # proceeding.
        if request.endpoint in [
            "accounts.logout",
            "main.about",
            "main.help",
            "main.terms_of_use",
            "main.privacy_policy",
            "main.legal_notice",
            "static",
        ]:
            return None

        # Check if the current user's latest identity needs email confirmation. We check
        # this before the user state, so inactive users can still confirm their email
        # address.
        if current_user.identity.needs_email_confirmation:
            if request.endpoint in [
                "accounts.request_email_confirmation",
                "accounts.confirm_email",
            ]:
                return None

            if is_api_request():
                return json_error_response(
                    401, description="Please confirm your email address."
                )

            return redirect(url_for("accounts.request_email_confirmation"))

        # Check if the state of the current user is active.
        if current_user.state != UserState.ACTIVE:
            endpoint = "accounts.inactive_user"

            if request.endpoint == endpoint:
                return None

            if is_api_request():
                return json_error_response(
                    401, description="This account is currently inactive."
                )

            return redirect(url_for(endpoint))

        # Check if the current user needs to accept the legal notices.
        if current_user.needs_legals_acceptance:
            endpoint = "accounts.request_legals_acceptance"

            if request.endpoint == endpoint:
                return None

            if is_api_request():
                return json_error_response(
                    401, description="Please accept all legal notices."
                )

            return redirect(url_for(endpoint))


from . import views  # pylint: disable=unused-import
