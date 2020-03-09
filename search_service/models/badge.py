import attr
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class Badge:
    """
    This represents a badge object
    """
    tag_name: str
    tag_type: str = 'badge'

    def __init__(self, tag_name: str)-> None:
        self.tag_name = tag_name
        self.tag_type = 'badge'

    def __repr__(self) -> str:
        return 'Badge({!r}, {!r})'.format(self.tag_name, self.tag_type)


class BadgeSchema(AttrsSchema):
    class Meta:
        target = Badge
        register_as_scheme = True
