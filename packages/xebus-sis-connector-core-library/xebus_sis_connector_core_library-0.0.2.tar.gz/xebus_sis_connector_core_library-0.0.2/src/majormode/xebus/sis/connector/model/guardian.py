# Copyright (C) 2021 Majormode.  All rights reserved.
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

from majormode.perseus.model.contact import Contact
from majormode.perseus.model.locale import Locale
from majormode.xebus.constant.guardian import GuardianRole

from majormode.xebus.sis.connector.model.person import Person


class Guardian(Person):
    """
    Represent the guardian of children enrolled to a school.
    """
    def __hash__(self):
        return hash(self._sis_account_id or self.email_address or self.phone_number)

    def __init__(
            self,
            sis_account_id: str,
            first_name: str,
            last_name: str,
            full_name: str,
            contacts: list[Contact] = None,
            languages: list[Locale] = None,
            nationalities: list[str] = None):
        """
        Build a new object representing a guardian.


        :param sis_account_id: The identifier of the guardian registered in
            the school information system (SIS) of the organization.

        :param first_name: The forename of the guardian.

        :param last_name: The surname of the guardian.

        :param full_name: The complete personal name by which guardian is
            known, including their surname, forename and middle name(s), in
            the correct lexical name order depending on the culture of the
            guardian.

        :param contacts: The list of the contact information of the guardian.

        :param languages: The spoken languages of the guardian.

        :param nationalities: The countries the guardian's citizenship belong
            to.
        """
        super().__init__(
            sis_account_id,
            first_name,
            last_name,
            full_name,
            contacts=contacts,
            languages=languages,
            nationalities=nationalities
        )
        self.__password = None

    @property
    def password(self):
        """
        Return the password that has been generated for this guardian.


        :return: The generated password of the guardian.
        """
        return self.__password

    @password.setter
    def password(self, password):
        """
        Set the password for this guardian.


        :param password: A generated password.


        :raise ValueError: If a password has been already generated for this
            guardian.
        """
        if self.__password:
            raise ValueError("Cannot redefine the password of a guardian")

        self.__password = password


class Guardianship:
    """
    Represent the relationship between a guardian and a child.
    """
    def __init__(
            self,
            guardian: Guardian,
            role: GuardianRole,
            home_address: str = None
    ):
        """
        Build a guardian relationship towards a child.


        :param guardian: A guardian responsible for a child.

        :param role: The role of the guardian towards the child.

        :param home_address: The postal address of the residence where the
            guardian puts their child up.
        """
        self.__guardian = guardian
        self.__role = role
        self.__home_address = home_address

    @property
    def guardian(self) -> Guardian:
        """
        Return the guardian responsible for a child.


        :return: A guardian.
        """
        return self.__guardian

    @property
    def home_address(self) -> str:
        """
        Return the postal address of the residence where the guardian puts
        their child up.


        :return: A postal address.
        """
        return self.__home_address

    @property
    def role(self) -> GuardianRole:
        """
        Return the role of the guardian towards the child.


        :return: The role of this guardian towards the child.
        """
        return self.__role
