# from typing import List
#
# from ..widget import Widget, AttributeNames
# from .filtering_context import FilteringContext
# from .metadata_field import MetadataField
#
#
# class MetadataFilter(Widget):
#     def __init__(self,
#                  metadata_elements: List[MetadataField],
#                  name: str = None,
#                  title: str = None,
#                  filtering_context: List[FilteringContext] = None,
#                  **additional):
#         super().__init__(widget_type=self.__class__.__name__,
#                          widget_name=name,
#                          **additional)
#         metadata_fields = []
#         for metadata in metadata_elements:
#             metadata_fields.append([metadata.field_name, metadata.frontend_type])
#         self.metadata_fields = metadata_fields
#         self.title = title
#         filtering_context_id = []
#         if filtering_context:
#             for filtering in filtering_context:
#                 filtering_context_id.append(filtering.context_id)
#                 filtering.input_filters.append(self.widget_id)
#         self.filtering_context = filtering_context_id
#
#     def to_dict_widget(self):
#         metadata_filter_dict = super().to_dict_widget()
#         metadata_filter_dict[AttributeNames.PROPERTIES.value].update({
#             AttributeNames.METADATA_FIELDS.value: self.metadata_fields,
#             AttributeNames.TITLE.value: self.title,
#         })
#         return metadata_filter_dict
