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

import abc
import datetime
import logging

from dateutil.parser import ParserError
from majormode.perseus.constant.contact import ContactName
from majormode.perseus.model.contact import Contact
from majormode.perseus.utils import cast

from majormode.xebus.sis.connector.model.family import FamilyList


@abc.ABC
class SisConnector:
    def convert_field_boolean_value(self, value: str) -> bool:
        """
        Return the boolean value corresponding to the specified string
        representation.


        :note: We cannot make this function static because it must respect a
            common interface with other data conversion functions, some of
            which need access to protected/private members of this class.

        :param value: A string representation of a boolean.


        :return: A boolean.
        """
        return cast.string_to_boolean(value)

    def convert_field_date_value(self, value: str) -> datetime.datetime:
        """
        Return the date value of a property of the family list data.


        :note: We cannot make this function static because it must respect a
            common interface with other data conversion functions, some of
            which need access to protected/private members of this class.


        :param value:


        :return: A date.


        :raise ValueError: If the string representation of the date doesn't
            comply with ISO 8601.
        """
        try:
            date = cast.string_to_date(value)
        except (ParserError, OverflowError) as error:
            logging.error(f"Invalid string representation \"{value}\" of a date")
            raise ValueError(str(error))

        return date

    def convert_field_email_address_value(self, value: str) -> Contact:
        """
        Return the contact information representing the specified email
        address.


        :note: We cannot make this function static because it must respect a
            common interface with other data conversion functions, some of
            which need access to protected/private members of this class.

        :param value: A string representation of an email address.

        :return: A contact information.
        """
        return value and Contact(
            ContactName.EMAIL,
            value.lower(),
            is_primary=True,
            strict=True
        )

    def convert_field_phone_number_value(self, value: str) -> Contact | None:
        """
        Return the contact information representing the specified phone number.


        :note: We cannot make this function static because it must respect a
            common interface with other data conversion functions, some of
            which need access to protected/private members of this class.

        :param value: A string representation of an international phone number.


        :return: A contact information.
        """
        return value and Contact(
            ContactName.PHONE,
            value.replace(' ', ''),
            is_primary=True,
            strict=True
        )

    @abc.abstractmethod
    def fetch_family_list(self) -> FamilyList:
        """
        Returns the data of the families to synchronize.


        :return: The data of the families to synchronize.
        """
