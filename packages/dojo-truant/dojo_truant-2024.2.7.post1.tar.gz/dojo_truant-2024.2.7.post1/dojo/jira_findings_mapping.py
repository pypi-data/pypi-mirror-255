#!/usr/bin/env python3

import logging
import urllib.parse
import string

import requests

import dojo


class Jira_Findings_Mapping(dojo.DAPI):
    _endpoint = string.Template("/api/v2/jira_finding_mappings/${id}/")
    _post_endpoint = "/api/v2/jira_finding_mappings/"
    _search_endpoint = "/api/v2/jira_finding_mappings/"

    _model_validation = {"jira_id": {"type": int,
                                     "required": True},
                         "jira_key": {"type": str,
                                      "required": True},
                         "jira_creation": {"type": str,
                                           "required": False},
                         "jira_change": {"type": str,
                                         "required": False},
                         "finding": {"type": int,
                                     "required": False},
                         "engagement": {"type": int,
                                        "required": False},
                         "finding_group": {"type": int,
                                           "required": False}
                         }

    _obj_iterate = ".results[]"

    _type = "jira_findings_mapping"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.logger = logging.getLogger("DAPI.Jira_Findings_Mappings")
