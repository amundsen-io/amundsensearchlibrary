# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import attr

from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class Badge:
    badge_name: str
    category: str
    badge_type: str

    def __init__(self, badge_name, category, badge_type):
        self.badge_name = badge_name
        self.category = category
        self.badge_type = badge_type


class BadgeSchema(AttrsSchema):
    class Meta:
        target = Badge
        register_as_scheme = True
