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

import csv
from os import PathLike

from majormode.perseus.model.country import Country
from majormode.perseus.model.locale import Locale

# The default character used to separate each CSV field.
DEFAULT_CSV_DELIMITER_CHARACTER = ','

# The default character used to escape the delimiter character, in case
# quotes aren't used.
DEFAULT_CSV_ESCAPE_CHARACTER = None

# The default character used to surround fields that contain the
# delimiter character.
DEFAULT_CSV_QUOTE_CHARACTER = '"'


def load_languages_names_iso_codes_mapping_from_csv_file(file_path_name: PathLike) -> dict[str, Locale]:
    """
    Return the mapping between the names of languages and their respective
    ISO 639-3:2007 codes as identified in the specified file.


    :param file_path_name: The absolute path and name of a CSV file
        containing a list of names of languages and their corresponding
        ISO 639-3:2007 codes (the values).


    :return: A dictionary representing a mapping between the names of
        languages (the keys), localized in a particular language, and
        their corresponding ISO 639-3:2007 codes (the values).
    """
    names_values_mapping = load_names_values_mapping_from_csv_file(file_path_name)

    languages_names_iso_codes_mapping = {
        name: Locale(iso_639_3_code)
        for name, iso_639_3_code in names_values_mapping.items()
    }

    return languages_names_iso_codes_mapping


def load_names_values_mapping_from_csv_file(
        file_path_name: PathLike,
        delimiter_character: str = None,
        escape_character: str = None,
        quote_character: str = None
) -> dict[str, str]:
    """
    Return a dictionary of entities names with their respective values.


    :param file_path_name: The absolute path and name of the file
        containing names and their respective values.

    :param delimiter_character: The character used to separate each CSV
        field.

    :param escape_character: The character used to escape the delimiter
        character, in case quotes aren't used.

    :param quote_character: The character used to surround fields that
        contain the delimiter character.


    :return: A dictionary where the key corresponds to an entity name
        and the value corresponds to the entity value.
    """
    with open(file_path_name, 'rt') as fd:
        csv_reader = csv.reader(
            fd,
            delimiter=delimiter_character or DEFAULT_CSV_DELIMITER_CHARACTER,
            escapechar=escape_character or DEFAULT_CSV_ESCAPE_CHARACTER,
            quotechar=quote_character or DEFAULT_CSV_QUOTE_CHARACTER
        )

        names_values_mapping: dict[str, str] = {
            language_name: iso_code
            for iso_code, language_name in csv_reader
        }

    return names_values_mapping


def load_nationalities_names_iso_codes_mapping_from_csv_file(file_path_name: PathLike) -> dict[str, Country]:
    """
    Return the mapping between the names of languages and their respective
    ISO 639-3:2007 codes as identified in the specified file.


    :param file_path_name: The absolute path and name of a CSV file
        containing a list of names of languages and their corresponding
        ISO 3166-1 alpha-2 codes (the values).


    :return: A dictionary representing a mapping between the names of
        languages (the keys), localized in a particular language, and
        their corresponding ISO 3166-1 alpha-2 codes (the values).
    """
    names_values_mapping = load_names_values_mapping_from_csv_file(file_path_name)

    nationalities_names_iso_codes_mapping = {
        name: Country(iso_3166_alpha2_code)
        for name, iso_3166_alpha2_code in names_values_mapping.items()
    }

    return nationalities_names_iso_codes_mapping
