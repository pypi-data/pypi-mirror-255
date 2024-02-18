# Copyright (C) 2020 Dremio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Use AWS4Auth and botocore to fetch credentials and sign requests."""
from typing import Optional

from botocore.credentials import get_credentials
from botocore.session import Session
from requests_aws4auth import AWS4Auth


def setup_aws_auth(region: str, profile: Optional[str] = None) -> AWS4Auth:
    """For a given region sign a request to the execute-api with standard credentials."""
    credentials = get_credentials(Session(profile=profile))
    auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, "execute-api", session_token=credentials.token)
    return auth
