# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.util.schema as Schema
import typing
from logging import Logger
import os
import json
import time
import ifcopenshell.util.attribute
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
from typing import Union, Any

class Patcher:
    def __init__(
        self,
        src: str,
        file: ifcopenshell.file,
        logger: Logger,
        schema: typing.Literal["IFC2X3", "IFC4", "IFC4X3"] = "IFC4",
    ):
        """Migrate from one IFC version to another

        Note that this is experimental and will try to preserve as much data as
        possible. Upgrading to IFC4 is more stable than downgrading to IFC2X3.

        :param schema: The schema identifier of the IFC version to migrate to.
        :type schema: str

        Example:

        .. code:: python

            # Upgrade an IFC2X3 model to IFC4
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "Migrate", "arguments": ["IFC4"]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.schema = schema

    def patch(self):
        self.file_patched = ifcopenshell.file(schema=self.schema)
        migrator = Schema.Migrator()
        migrator.preprocess(self.file, self.file_patched)
        for element in self.file:
            new_element = migrator.migrate(element, self.file_patched)
            print("Migrating", element)
            print("Successfully converted to", new_element)



# class Migrator:
#     def __init__(self):
#         self.migrated_ids = {}
#         self.attribute_overrides = {}
#         self.class_4_to_2x3 = json.load(open(os.path.join("assets/class_4_to_2x3.json"), "r"))
#         self.class_2x3_to_4 = json.load(open(os.path.join("assets/class_2x3_to_4.json"), "r"))

#         # IFC classes, and their IFC attributes mapping
#         self.attributes_mapping = {
#             ("IFC4", "IFC2X3"): json.load(open(os.path.join("assets/attribute_4_to_2x3.json"), "r")),
#             ("IFC4X3", "IFC4"): json.load(open(os.path.join("assets/attribute_4x3_to_4.json"), "r")),
#         }

#         self.default_values = {
#             "ChangeAction": "NOCHANGE",
#             "CompositionType": "ELEMENT",
#             "CrossSectionArea": 1,
#             "DataValue": 0,
#             "DefinedValues": [0],
#             "DefiningValues": [0],
#             "DestabilizingLoad": False,
#             "Edition": "",
#             "EndParam": 1.0,
#             "EnumerationValues": [0],
#             "GeodeticDatum": "",
#             "Intent": "",
#             "IsHeading": False,
#             "ListValues": [0],
#             "LongitudinalBarCrossSectionArea": 1,
#             "LongitudinalBarNominalDiameter": 1,
#             "LongitudinalBarSpacing": 1,
#             "Name": "",
#             "NominalDiameter": 1,
#             "PredefinedType": "NOTDEFINED",
#             "RowCells": [0],
#             "SequenceType": "NOTDEFINED",
#             "Source": "",
#             "StartParam": 0.0,
#             "TransverseBarCrossSectionArea": 1,
#             "TransverseBarNominalDiameter": 1,
#             "TransverseBarSpacing": 1,
#             # Manual additions from experience
#             "InteriorOrExteriorSpace": "NOTDEFINED",
#             "AssemblyPlace": "NOTDEFINED",  # See bug https://github.com/Autodesk/revit-ifc/issues/395
#         }
#         self.default_entities = {
#             "CurrentValue": None,
#             "DepreciatedValue": None,
#             "Jurisdiction": None,
#             "OriginalValue": None,
#             "Owner": None,
#             "OwnerHistory": None,
#             "Position": None,
#             "PropertyReference": None,
#             "RepresentationContexts": None,
#             "ResponsiblePerson": None,
#             "ResponsiblePersons": None,
#             "Rows": None,
#             "TotalReplacementCost": None,
#             "UnitsInContext": None,
#             "User": None,
#         }

#     def preprocess(self, old_file: ifcopenshell.file, new_file: ifcopenshell.file):
#         to_delete = set()

#         if old_file.schema == "IFC2X3" and new_file.schema == "IFC4":
#             # IfcCalendarDate is deprecated in IFC4
#             for element in old_file.by_type("IfcCalendarDate"):
#                 for inverse, attribute_index in old_file.get_inverse(
#                     element, allow_duplicate=True, with_attribute_indices=True
#                 ):
#                     self.attribute_overrides.setdefault(inverse.id(), {})[
#                         attribute_index
#                     ] = f"{element[2]}-{element[1]}-{element[0]}"
#                 to_delete.add(element)

#         if old_file.schema == "IFC4" and new_file.schema == "IFC4X3":
#             # IfcPresentationStyleAssignment is deprecated
#             for assignment in old_file.by_type("IfcPresentationStyleAssignment"):
#                 for styled_item in old_file.get_inverse(assignment):
#                     if not styled_item.is_a("IfcStyledItem"):
#                         continue
#                     styled_item.Styles = [s for s in styled_item.Styles if s.is_a("IfcPresentationStyle")] + list(
#                         assignment.Styles
#                     )
#                 to_delete.add(assignment)

#         for element in to_delete:
#             old_file.remove(element)

#     def migrate(
#         self, element: ifcopenshell.entity_instance, new_file: ifcopenshell.file
#     ) -> ifcopenshell.entity_instance:
#         if element.id() == 0:
#             return new_file.create_entity(element.is_a(), element.wrappedValue)
#         try:
#             return new_file.by_id(self.migrated_ids[element.id()])
#         except:
#             pass
#         # print("Migrating", element)
#         schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(new_file.schema_identifier)
#         new_element = self.migrate_class(element, new_file)
#         # print("Migrated class from {} to {}".format(element, new_element))
#         new_element_schema = schema.declaration_by_name(new_element.is_a())
#         if not hasattr(new_element_schema, "all_attributes"):
#             return element  # The element has no attributes, so migration is done
#         new_element = self.migrate_attributes(element, new_file, new_element, new_element_schema)
#         self.migrated_ids[element.id()] = new_element.id()
#         return new_element

#     def migrate_class(
#         self, element: ifcopenshell.entity_instance, new_file: ifcopenshell.file
#     ) -> ifcopenshell.entity_instance:
#         try:
#             new_element = new_file.create_entity(element.is_a())
#         except:
#             # The element does not exist in this schema
#             # Complex migration is not yet supported (e.g. polygonal face set to faceted brep)
#             if new_file.schema == "IFC2X3":
#                 new_element = new_file.create_entity(self.class_4_to_2x3[element.is_a()])
#             elif new_file.schema == "IFC4":
#                 new_element = new_file.create_entity(self.class_2x3_to_4[element.is_a()])
#         return new_element

#     def migrate_attributes(self, element, new_file, new_element, new_element_schema):
#         for attribute_index, value in self.attribute_overrides.get(element.id(), {}).items():
#             new_element[attribute_index] = value
#         for i, attribute in enumerate(new_element_schema.all_attributes()):
#             if new_element_schema.derived()[i]:
#                 continue
#             self.migrate_attribute(attribute, element, new_file, new_element, new_element_schema)
#         return new_element

#     def find_equivalent_attribute(
#         self,
#         new_element: ifcopenshell.entity_instance,
#         attribute: ifcopenshell_wrapper.attribute,
#         element: ifcopenshell.entity_instance,
#         attributes_mapping: dict[str, dict[str, str]],
#         reverse_mapping: bool = False,
#     ) -> Union[Any, None]:
#         # print("Searching for an equivalent", element, new_element, attribute.name())
#         try:
#             if reverse_mapping:
#                 equivalent_map = attributes_mapping[new_element.is_a()]
#                 equivalent = list(equivalent_map.keys())[list(equivalent_map.values()).index(attribute.name())]
#             else:
#                 equivalent = attributes_mapping[new_element.is_a()][attribute.name()]
#             if hasattr(element, equivalent):
#                 # print("Equivalent found", equivalent)
#                 return getattr(element, equivalent)
#             else:
#                 return
#         except Exception as e:
#             print(
#                 "Unable to find equivalent attribute of {} to migrate from {} to {}".format(
#                     attribute.name(), element, new_element
#                 )
#             )
#             raise e

#     def migrate_attribute(
#         self,
#         attribute: ifcopenshell_wrapper.attribute,
#         element: ifcopenshell.entity_instance,
#         new_file: ifcopenshell.file,
#         new_element: ifcopenshell.entity_instance,
#         new_element_schema: ifcopenshell_wrapper.declaration,
#     ) -> None:
#         # NOTE: `attribute` is an attribute in new file schema
#         # print("Migrating attribute", element, new_element, attribute.name())
#         old_file = element.wrapped_data.file
#         if hasattr(element, attribute.name()):
#             value = getattr(element, attribute.name())
#             # print("Attribute names matched", value)

#         elif new_file.schema == "IFC2X3" and old_file.schema == "IFC4":
#             # IFC4 to IFC2X3: We know the IFC2X3 attribute name, but not its IFC4 equivalent
#             try:
#                 value = self.find_equivalent_attribute(
#                     new_element, attribute, element, self.attributes_mapping[("IFC4", "IFC2X3")], reverse_mapping=True
#                 )
#             except:  # We tried our best
#                 return

#         elif new_file.schema == "IFC4" and old_file.schema == "IFC2X3":
#             # IFC2X3 to IFC4: We know the IFC4 attribute name, but not its IFC2X3 equivalent
#             try:
#                 value = self.find_equivalent_attribute(
#                     new_element, attribute, element, self.attributes_mapping[("IFC4", "IFC2X3")]
#                 )
#             except:  # We tried our best
#                 return

#         elif new_file.schema == "IFC4X3" and old_file.schema == "IFC4":
#             try:
#                 value = self.find_equivalent_attribute(
#                     new_element, attribute, element, self.attributes_mapping[("IFC4X3", "IFC4")]
#                 )
#             except:  # We tried our best
#                 return

#         elif new_file.schema == "IFC4" and old_file.schema == "IFC4X3":
#             try:
#                 value = self.find_equivalent_attribute(
#                     new_element, attribute, element, self.attributes_mapping[("IFC4X3", "IFC4")], reverse_mapping=True
#                 )
#             except:  # We tried our best
#                 return

#         try:
#             value
#         except UnboundLocalError:
#             print(
#                 f"Couldn't match attribute {attribute.name()} by name to migrate from {element} "
#                 f"to {new_element} and there is no special mapping to handle migration "
#                 f"from {old_file.schema} -> {new_file.schema}"
#             )
#             return

#         # print("Continuing migration of {} to migrate from {} to {}".format(attribute.name(), element, new_element))
#         if value is None and not attribute.optional():
#             value = self.generate_default_value(attribute, new_file)
#             if value is None:
#                 print("Failed to generate default value for {} on {}".format(attribute.name(), element))
#         elif isinstance(value, ifcopenshell.entity_instance):
#             value = self.migrate(value, new_file)
#         elif isinstance(value, (list, tuple)):
#             if value and isinstance(value[0], ifcopenshell.entity_instance):
#                 new_value = []
#                 for item in value:
#                     new_value.append(self.migrate(item, new_file))
#                 value = new_value
#         if value is not None:
#             setattr(new_element, attribute.name(), value)

#     def generate_default_value(self, attribute: ifcopenshell_wrapper.attribute, new_file: ifcopenshell.file) -> Any:
#         if attribute.name() in self.default_values:
#             return self.default_values[attribute.name()]
#         elif attribute.name() == "OwnerHistory":
#             self.default_entities[attribute.name()] = new_file.create_entity(
#                 "IfcOwnerHistory",
#                 **{
#                     "OwningUser": new_file.create_entity(
#                         "IfcPersonAndOrganization",
#                         **{
#                             "ThePerson": new_file.create_entity("IfcPerson"),
#                             "TheOrganization": new_file.create_entity(
#                                 "IfcOrganization", **{"Name": "IfcOpenShell Migrator"}
#                             ),
#                         },
#                     ),
#                     "OwningApplication": new_file.create_entity(
#                         "IfcApplication",
#                         **{
#                             "ApplicationDeveloper": new_file.create_entity(
#                                 "IfcOrganization", **{"Name": "IfcOpenShell Migrator"}
#                             ),
#                             "Version": "Works for me",
#                             "ApplicationFullName": "IfcOpenShell Migrator",
#                             "ApplicationIdentifier": "IfcOpenShell Migrator",
#                         },
#                     ),
#                     "ChangeAction": "NOCHANGE",
#                     "CreationDate": int(time.time()),
#                 },
#             )
#         return self.default_entities.get(attribute.name(), None)
