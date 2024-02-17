# Copyright (C) 2024 Majormode.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Majormode or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Majormode.
#
# MAJORMODE MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY
# OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT.  MAJORMODE SHALL NOT BE LIABLE FOR ANY
# LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING
# OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

from __future__ import annotations

import datetime
import logging
from typing import Any

from majormode.xebus.constant.guardian import GuardianRole

from majormode.xebus.sis.connector.constant.family import FamilyPropertyName
from majormode.xebus.sis.connector.model.child import Child
from majormode.xebus.sis.connector.model.error import MissingPersonDataException
from majormode.xebus.sis.connector.model.guardian import Guardian
from majormode.xebus.sis.connector.model.guardian import Guardianship


class FamilyList:
    """
    Represent the information of children and their respective guardians.
    """
    def __build_child(
            self,
            row_index: int,
            strict_prosoponym: bool = False
    ) -> Child:
        """
        Build an object representing a child defined in the specified row of
        the family data list.


        :note: The function doesn't check, nor format, the child's first name,
            last name, and full name.


        :param row_index: The index of the row to read the child's information.


        :return: An object representing a child.


        :raise CountryNameNotFoundException: If the English name of the
            child's nationality is not defined in the core data.  Either this
            name is misspelled, either the core data are missing this name.

        :raise InvalidDateOfBirthException: If the child's birthdate is not
            formatted according the ISO 8601 specifications.

        :raise LanguageNameNotFoundException: If the English name of the
            child's language is not defined in the core data.  Either this
            name is misspelled, either the core data are missing this name.
        """
        # Read the child's information.
        sis_account_id = self.__get_property_value(row_index, FamilyPropertyName.child_sis_id, is_required=True)
        first_name = self.__get_property_value(row_index, FamilyPropertyName.child_first_name, is_required=True)
        last_name = self.__get_property_value(row_index, FamilyPropertyName.child_last_name, is_required=True)
        full_name = self.__get_property_value(row_index, FamilyPropertyName.child_full_name, is_required=True)
        dob = self.__get_property_value(row_index, FamilyPropertyName.child_date_of_birth, is_required=True)
        grade_level = self.__get_property_value(row_index, FamilyPropertyName.child_grade_level, is_required=True)
        class_name = self.__get_property_value(row_index, FamilyPropertyName.child_class_name, is_required=False)
        languages = self.__get_property_value(row_index, FamilyPropertyName.child_languages, is_required=True)
        nationalities = self.__get_property_value(row_index, FamilyPropertyName.child_nationalities, is_required=True)
        use_transport = self.__get_property_value(row_index, FamilyPropertyName.child_use_transport, is_required=False)

        # Build the object representing the child.
        child = Child(
            sis_account_id,
            first_name,
            last_name,
            full_name,
            dob,
            grade_level,
            class_name=class_name,
            languages=languages,
            nationalities=nationalities,
            use_transport=use_transport
        )

        return child

    def __build_children_and_their_guardianships(
            self,
            row_index: int,
            strict_prosoponym: bool = False
    ) -> None:
        """
        Build and index the child and parents' information contained in the
        specified row of the family list data.


        :param row_index: The index of the data row to read.

        :param strict_prosoponym: Indicate whether full names MUST be
            formatted according to the lexical name related to the culture of
            each person.


        :raise ValueError: If the child or one of their parent has been
            defined multiple times but with different information.
        """
        child = self.__build_child(row_index)
        self.__index_child_in_cache(child)

        # Collect the information of the child's primary parent, and build the
        # guardianship between this primary parent and the child.
        primary_parent_guardianship = self.__build_primary_parent_guardianship(
            row_index,
            strict_prosoponym=strict_prosoponym
        )
        self.__index_parent_in_cache(primary_parent_guardianship.guardian)
        child.add_guardianship(primary_parent_guardianship)

        # Collect the information of the child's secondary parent, if any
        # defined, and build the guardianship between the secondary parent and
        # the child.
        secondary_parent_guardianship = self.__build_secondary_parent_guardianship(
            row_index,
            strict_prosoponym=strict_prosoponym
        )
        if secondary_parent_guardianship:
            self.__index_parent_in_cache(secondary_parent_guardianship.guardian)
            child.add_guardianship(secondary_parent_guardianship)

    def __build_families(self, strict_prosoponym: bool = False) -> None:
        """
        Build objects representing the children and their guardians from the
        family list data.

        The function reads each row of the family list data representing a
        child and the primary and possible the secondary guardians who are
        legally responsible for this child.


        :param strict_prosoponym: Indicate whether full names MUST be
            formatted according to the lexical name related to the culture of
            each person.


        :raise ValueError: If a child or one of their parent has been defined
            multiple times but with different information.
        """
        for row_index in range(self.row_count):
            self.__build_children_and_their_guardianships(row_index, strict_prosoponym=strict_prosoponym)

    def __build_primary_parent_guardianship(
            self,
            row_index: int,
            strict_prosoponym: bool = False
    ) -> Guardianship:
        """

        :param row_index:
        :param strict_prosoponym:
        :return:
        """
        # Collect the primary parent's information.
        sis_account_id = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_sis_id)
        first_name = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_first_name)
        last_name = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_last_name)
        full_name = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_full_name)
        languages = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_languages)
        nationalities = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_nationalities)
        email_address = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_email_address)
        phone_number = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_phone_number, is_required=False)

        contacts = [email_address]
        if phone_number:
            contacts.append(phone_number)

        # Collect the postal address where the primary parent puts their child
        # in.
        home_address = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_home_address, is_required=False)

        # Build the objects representing the primary parent and their
        # guardianship towards the child.
        primary_parent = Guardian(
            sis_account_id,
            first_name,
            last_name,
            full_name,
            contacts=contacts,
            languages=languages,
            nationalities=nationalities
        )

        primary_parent_guardianship = Guardianship(
            primary_parent,
            GuardianRole.legal,
            home_address
        )

        return primary_parent_guardianship

    def __build_secondary_parent_guardianship(
            self,
            row_index: int,
            strict_prosoponym: bool = False
    ) -> Guardianship | None:
        """

        :param row_index:
        :param strict_prosoponym:
        :return:
        """
        # Collect the secondary parent's nominative information.
        sis_account_id = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_sis_id, is_required=False)
        first_name = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_first_name, is_required=False)
        last_name = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_last_name, is_required=False)
        full_name = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_full_name, is_required=False)
        languages = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_languages, is_required=False)
        nationalities = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_nationalities, is_required=False)
        email_address = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_email_address, is_required=False)
        phone_number = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_phone_number, is_required=False)

        contacts = []
        if email_address:
            contacts.append(email_address)
        if phone_number:
            contacts.append(phone_number)

        # Collect the postal address where the secondary parent puts their child
        # in.
        home_address = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_home_address, is_required=False)

        # Check that all the required information about a secondary parent are
        # provided defined, or none of them.
        required_values = [sis_account_id, first_name, last_name, full_name, languages, nationalities, email_address]
        optional_values = [phone_number, home_address]
        all_values = required_values + optional_values

        if not any(all_values):
            return None  # No secondary parent is defined for the child.

        if not all(required_values):
            if sis_account_id and full_name:
                message = f"Information required from the secondary parent \"{full_name}\" " \
                          f"({sis_account_id}) is missing"
            else:
                message = f"Information required from a secondary parent is missing"
            logging.error(message)
            raise MissingPersonDataException(message)

        # Build the objects representing the primary parent and their
        # guardianship towards the child.
        secondary_parent = Guardian(
            sis_account_id,
            first_name,
            last_name,
            full_name,
            contacts=contacts,
            languages=languages,
            nationalities=nationalities
        )

        secondary_parent_guardianship = Guardianship(
            secondary_parent,
            GuardianRole.legal,
            home_address=home_address
        )

        return secondary_parent_guardianship

    def __get_property_value(
            self,
            row_index: int,
            property_name: FamilyPropertyName,
            is_required: bool = True
    ) -> Any | None:
        """
        Return the value of a property of the family list data.


        :param row_index: The row index of the property to return the value.  A
            row index starts with ``0``.

        :param property_name: The name of the properties to return the value.

        :param is_required: Indicate whether this property MUST contain a
            value.


        :return: The property value.
        """
        if row_index < 0 or row_index >= self.row_count:
            raise IndexError(f"Row index {row_index} out of bound")

        value = self.__rows[row_index][property_name]

        if is_required and not value:
            error_message = f'The required field "{property_name}" is empty at row {row_index}'
            logging.error(error_message)
            raise ValueError(error_message)

        return value if value else None

    def __init__(
            self,
            rows: list[dict[FamilyPropertyName, Any]],
            strict_prosoponym: bool = False
    ):
        self.__rows = rows

        # The cache of children indexed with their SIS identifier.
        self.__children_cache: dict[str, Child] = {}

        # The cache of parents indexed with SIS identifier, their email
        # address, and their possible phone number.
        self.__parents_cache: dict[str, Guardian] = {}

        self.__build_families(strict_prosoponym=strict_prosoponym)

    def __index_child_in_cache(self, child: Child) -> Child:
        """
        Index a child in the app's cache for further access.


        :param child: A child.


        :return: The child.


        :raise ValueError: If the child has already been defined but with
            different information.
        """
        # Check the child has not been cached with different information.
        cached_child = self.__children_cache.get(child.sis_account_id)
        if cached_child and cached_child != child:
            raise ValueError(
                f"The child {child.sis_account_id} has already been defined but with "
                "different information"
            )

        # Cache the child with their SIS identifier.
        self.__children_cache[child.sis_account_id] = child

        return child

    def __index_parent_in_cache(self, parent: Guardian) -> Guardian:
        """
        Index a parent in the app's cache for further access.


        :param parent: A parent.


        :return: The parent.


        :raise ValueError: If the parent has already been defined but with
            different information.
        """
        # Check that the parent has not been cached with different information.
        cached_parents = [
            self.__parents_cache.get(parent.sis_account_id),
            self.__parents_cache.get(parent.email_address),
            self.__parents_cache.get(parent.phone_number)
        ]

        for cached_parent in cached_parents:
            if cached_parent and cached_parent != parent:
                raise ValueError(
                    f"The parent {parent.sis_account_id} has already been defined but with "
                    "different information"
                )

        # Cache the parent with their SIS identifier, email address, and phone
        # number if any defined.
        self.__parents_cache[parent.sis_account_id] = parent
        self.__parents_cache[parent.email_address] = parent
        if parent.phone_number:
            self.__parents_cache[parent.phone_number] = parent

        return parent

    @property
    def row_count(self) -> int:
        return len(self.__rows)

