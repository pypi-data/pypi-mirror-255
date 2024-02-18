from django.core.exceptions import ImproperlyConfigured

from rest_framework import relations
from rest_framework import fields
from drf_auto_endpoint.metadata import AutoMetadata
from drf_auto_endpoint.get_field_dict import GetFieldDict


class DRFFieldDict(GetFieldDict):
    widgets = {}

    def __init__(self, instance=None, *args, **kwargs):
        self.instance = instance
        super().__init__(*args, **kwargs)

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return self.dict_for_field(*args, **kwargs)

    def customize_metadata(self, metadata, request, serializer):
        """
        Provide subclasses with the ability to modify or extend the field metadata
        established via the AutoMetadata.determine_metadata method
        """
        return metadata

    def get_base_dict_for_field(self, name, field_instance, serializer,
                                translated_fields, serializer_instance):
        base_dict = super().get_base_dict_for_field(
            name,
            field_instance,
            serializer,
            translated_fields,
            serializer_instance
        )

        field_name = field_instance.field_name

        widget_info_method_name = 'widget_info_for_{}'.format(field_name)
        if hasattr(self, widget_info_method_name):
            widget = getattr(self, widget_info_method_name)()
        else:
            widget = 'textfield'

            if field_name in self.widgets:
                widget = self.widgets[field_name]
            elif isinstance(field_instance, relations.ManyRelatedField):
                widget = 'itemlist'
            elif isinstance(field_instance, relations.HyperlinkedRelatedField):
                widget = 'select'
            elif field_instance.style.get('base_template') == 'textarea.html':
                widget = 'textarea'
            elif isinstance(field_instance, fields.DateField):
                widget = 'date'
            elif isinstance(field_instance, fields.DateTimeField):
                widget = 'datetime'

        base_dict['ui']['widget'] = widget

        return base_dict

    def update_choices_from_serializer(self, rv, field_instance, force=False):
        choices_method_name = 'get_choices_for_{}'.format(rv['key'])
        if hasattr(self, choices_method_name):
            rv['choices'] = getattr(self, choices_method_name)()
        else:
            super().update_choices_from_serializer(rv, field_instance, force)


class DRFMetadata(AutoMetadata):
    pass
    # TODO: Revise 'determine_metadata' to not depend on an instance of FieldDictClass, since
    # def determine_metadata(self, request, view):
    #     metadata = super().determine_metadata(request, view)
    #
    #     if hasattr(view, 'get_metadata_fielddict_class'):
    #         FieldDictClass = view.get_metadata_fielddict_class()
    #     elif hasattr(view, 'metadata_fielddict_class'):
    #         FieldDictClass = view.metadata_fielddict_class
    #     else:
    #         raise ImproperlyConfigured(
    #             "'%s' should either include a `metadata_fielddict_class` attribute, "
    #             "or override the `get_metadata_fielddict_class()` method."
    #             % view.__class__.__name__
    #         )
    #
    #     field_dict = FieldDictClass()
    #     serializer = view.get_serializer_class()
    #
    #     for metadata_item in metadata:
    #         field_info = field_dict(request, metadata_item['key'], serializer)
    #
    #         # Override some of the default metadata resolved by AutoMetadata
    #         for key in ['ui', 'choices']:
    #             if key in field_info:
    #                 metadata_item[key] = field_info[key]
    #
    #     metadata = field_dict.customize_metadata(metadata, request, serializer)
    #     return metadata

