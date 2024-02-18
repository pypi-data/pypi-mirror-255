from rest_framework.fields import Field
from wagtail.templatetags import wagtailcore_tags


class RichTextSerializer(Field):
    def to_representation(self, value):
        return wagtailcore_tags.richtext(value)
