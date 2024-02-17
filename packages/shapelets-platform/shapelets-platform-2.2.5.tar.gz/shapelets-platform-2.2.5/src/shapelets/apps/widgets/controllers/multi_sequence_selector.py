# from typing import List
#
# from ... import ArgumentType, ArgumentTypeEnum
# from ...widgets import Widget, AttributeNames
# from ....model import Collection, Sequence
#
#
# class MultiSequenceSelector(Widget):
#     def __init__(self,
#                  collection: Collection = None,
#                  sequences: List[Sequence] = None,
#                  default_sequence: List[Sequence] = None,
#                  name: str = None,
#                  title: str = None,
#                  **additional):
#         super().__init__(self.__class__.__name__,
#                          name,
#                          ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.SEQUENCE),
#                          default_sequence if default_sequence else list(),
#                          **additional)
#         self.collection = collection
#         self.sequences = sequences
#         self.title = title
#         self.default_sequence = default_sequence if default_sequence is not None else []
#
#     def to_dict_widget(self):
#         multi_sequence_selector_dict = super().to_dict_widget()
#         if self.collection is not None:
#             multi_sequence_selector_dict[AttributeNames.PROPERTIES.value].update(
#                 {AttributeNames.COLLECTION_ID.value: f"{self.collection.collection_id}"}
#             )
#         if self.sequences is not None:
#             sequences = [seq.sequence_id for seq in self.sequences]
#             multi_sequence_selector_dict[AttributeNames.PROPERTIES.value].update({
#                 f"{AttributeNames.SEQUENCE_ID.value}s": sequences
#             })
#         if self.title is not None:
#             multi_sequence_selector_dict[AttributeNames.PROPERTIES.value].update(
#                 {AttributeNames.TITLE.value: f"{self.title}"}
#             )
#         if self.default_sequence:
#             multi_sequence_selector_dict[AttributeNames.PROPERTIES.value].update({
#                 AttributeNames.DEFAULT.value: [sequence.sequence_id for sequence in self.default_sequence]
#             })
#         return multi_sequence_selector_dict
