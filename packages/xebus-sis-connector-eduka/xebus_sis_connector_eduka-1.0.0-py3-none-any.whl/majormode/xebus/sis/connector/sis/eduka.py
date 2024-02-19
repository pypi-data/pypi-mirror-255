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

import csv
import json
import logging
import re
from typing import Callable, Any

import requests

from majormode.perseus.model.country import Country
from majormode.perseus.model.country import InvalidCountryCode
from majormode.perseus.model.locale import Locale
from majormode.perseus.utils import cast

from majormode.xebus.sis.connector.constant.family import FamilyPropertyName
from majormode.xebus.sis.connector.model.family import FamilyList
from majormode.xebus.sis.connector.sis_connector import SisConnector

# Regular expression to match an Eduka error returned either by the URL
# to request generating a specific list (`Erreur n°XXXYYY`), either by
# the URL to fetch the content of this list (`Error #XXXYYY`).
#
# Eduka doesn't raise an HTTP error using a proper HTTP status code, but
# instead returns a HTTP status code `200`, and returned a HTTP content
# that includes a message containing a HTTP status code `XXX` combined
# with another code `YYY` specific to Eduak.
REGEX_PATTERN_EDUKA_ERROR_CODE = r'Err(eu|o)r (#|n°)(?P<http_status_code>\d{3})(?P<eduka_error_code>\d*)'
REGEX_EDUKA_ERROR_CODE = re.compile(REGEX_PATTERN_EDUKA_ERROR_CODE)

REGEX_PATTERN_EDUKA_GRADE_NAME = r'.*\((?P<grade_name>.*)\).*'  # :todo: Might be specified to a given school
REGEX_EDUKA_GRADE_NAME = re.compile(REGEX_PATTERN_EDUKA_GRADE_NAME)

EDUKA_CSV_DELIMITER_CHARACTER = ';'
EDUKA_CSV_ESCAPE_CHARACTER = None
EDUKA_CSV_QUOTE_CHARACTER = '"'


class EdukaError(Exception):
    """
    Represent an error that a school's Eduka system raises.
    """
    def __init__(
            self,
            http_status_code: int,
            eduka_error_code: int
    ):
        """
        Build a new ``EdukaError`` exception.


        :param http_status_code: The HTTP status code that a school's Eduka
            system returns.

        :param eduka_error_code: The specific error code that a school's Eduka
            system raises.
        """
        self.__http_status_code = http_status_code
        self.__eduka_error_code = eduka_error_code

    @property
    def eduka_error_code(self) -> int:
        """
        Return the specific error code that a school's Eduka system raises.


        :return: The specific error code that a school's Eduka system raises.
        """
        return self.__eduka_error_code

    @property
    def http_status_code(self) -> int:
        """
        Return the HTTP status code that a school's Eduka system returns.


        :return: The HTTP status code that a school's Eduka system returns.
        """
        return self.__http_status_code


class EdukaConnector(SisConnector):
    def __convert_field_grade_name_value(self, value: str) -> int | None:
        match = REGEX_EDUKA_GRADE_NAME.match(value)
        if not match:
            message = f"Invalid Eduka string representation \"{value}\" of a grade name"
            logging.error(message)
            raise ValueError(message)

        grade_name = match.group('grade_name').upper()

        grade_level = self.__eduka_grades_names_mapping.get(grade_name)
        if grade_level is None:
            message = f"Invalid Eduka string representation \"{grade_name}\" of a grade name"
            logging.error(message)
            raise ValueError(message)

        return grade_level

    def __convert_field_languages_value(self, value: str) -> list[Locale] | None:
        if value:
            locales = [
                self.__convert_language_value(language.strip())
                for language in value.split(',')
            ]
            return locales

    def __convert_field_nationalities_value(self, value: str) -> list[Country] | None:
        if value:
            countries = [
                self.__convert_nationality_value(nationality.strip())
                for nationality in value.split(',')
            ]
            return countries

    # Mapping between family properties and functions responsible for
    # converting their values from Eduka data.
    FIELD_VALUE_CONVERTERS: dict[FamilyPropertyName, Callable[[Any, str], Any]] = {
        FamilyPropertyName.child_date_of_birth: SisConnector._convert_field_date_value,
        FamilyPropertyName.child_grade_level: __convert_field_grade_name_value,
        FamilyPropertyName.child_languages: __convert_field_languages_value,
        FamilyPropertyName.child_nationalities: __convert_field_nationalities_value,
        FamilyPropertyName.child_use_transport: SisConnector._convert_field_boolean_value,
        FamilyPropertyName.primary_guardian_email_address: SisConnector._convert_field_email_address_value,
        FamilyPropertyName.primary_guardian_languages: __convert_field_languages_value,
        FamilyPropertyName.primary_guardian_nationalities: __convert_field_nationalities_value,
        FamilyPropertyName.primary_guardian_phone_number: SisConnector._convert_field_phone_number_value,
        FamilyPropertyName.secondary_guardian_email_address: SisConnector._convert_field_email_address_value,
        FamilyPropertyName.secondary_guardian_languages: __convert_field_languages_value,
        FamilyPropertyName.secondary_guardian_nationalities: __convert_field_nationalities_value,
        FamilyPropertyName.secondary_guardian_phone_number: SisConnector._convert_field_phone_number_value,
    }

    def __convert_eduka_rows(
            self,
            rows: list[str]
    ) -> list[dict[FamilyPropertyName, Any]]:
        """
        Convert rows of information about children and their parents extracted
        from a school's Eduka system to their standard representation in Xebus.


        :param rows: The rows of information about children and their parents
            extracted from a school's Eduka system.


        :return: A list of Python dictionaries.  Each dictionary represents
            the information about a child and their parents.  Each key of the
            dictionary corresponds to the name of a Family property, while the
            value corresponds to the information about a child or their parent
            represented with a Python datum.
        """
        csv_reader = csv.DictReader(
            rows,
            delimiter=EDUKA_CSV_DELIMITER_CHARACTER,
            escapechar=EDUKA_CSV_ESCAPE_CHARACTER,
            quotechar=EDUKA_CSV_QUOTE_CHARACTER
        )

        # Check that all the required fields are not missing.
        ignored_eduka_field_names = []
        for field_name in csv_reader.fieldnames:
            # @note: The Eduka list may contain more fields that those required.
            if field_name not in self.__eduka_properties_mapping:
                logging.debug(f'"Ignoring the Eduka CSV field name "{field_name}"')
                ignored_eduka_field_names.append(field_name)

        for field_name in self.__eduka_properties_mapping:
            if field_name not in csv_reader.fieldnames:
                raise ValueError(f'The Eduka CSV field name "{field_name}" is missing')

        # Translate the Eduka fields names and values in their corresponding
        # Xebus fields names and values.

        # :note: Type annotation to avoid the linter to complain that
        #     "Unresolved attribute reference 'items' for class 'str'" for the
        #     expression "eduka_row.items()".
        eduka_row: dict[str, Any]

        rows = []
        for eduka_row in csv_reader:
            fields = {}
            for eduka_field_name, eduka_field_value in eduka_row.items():
                if eduka_field_name not in ignored_eduka_field_names:
                    field_name = self.__eduka_properties_mapping[eduka_field_name]

                    field_value_converter_function = self.FIELD_VALUE_CONVERTERS.get(field_name)
                    field_value = eduka_field_value if field_value_converter_function is None \
                        else field_value_converter_function(self, eduka_field_value)

                    fields[field_name] = field_value

            rows.append(fields)

        return rows

    def __convert_language_value(self, value: str) -> Locale:
        """
        Return the locale corresponding to the string representation of a
        language.


        :param value: A string representation of a language.


        :return: A locale.


        :raise ValueError: If the Eduka value is not a valid string
            representation of a language.
        """
        try:
            locale = cast.string_to_locale(value)
        except Locale.MalformedLocaleException as error:
            locale = self.__eduka_languages_names_mapping and self.__eduka_languages_names_mapping.get(value)
            if not locale:
                logging.error(f"Invalid Eduka string representation \"{value}\" of a language")
                raise ValueError(str(error))

        return locale

    def __convert_nationality_value(self, value: str) -> Country:
        """
        Return the country corresponding to the string representation of a
        nationality.


        :param value: A string representation of a nationality.


        :return: A country.


        :raise ValueError: If the Eduka value is not a valid string
            representation of a nationality.
        """
        try:
            country = Country.from_string(value)
        except InvalidCountryCode as error:
            country = self.__eduka_nationalities_names_mapping and self.__eduka_nationalities_names_mapping.get(value)
            if not country:
                logging.error(f"Invalid Eduka string representation \"{value}\" of a nationality")
                raise ValueError(str(error))

        return country

    @staticmethod
    def __fetch_eduka_list_data(
            list_url: str
    ) -> list[str]:
        """
        Fetch and return the school's family data.


        :param list_url: The school's Eduka list containing the family data to
            synchronize.


        :return: A list of CSV rows corresponding to information about
            children and their guardianships.


        :raise ValueError: If the HTTP request to fetch the family data from
            the school's Eduka information system failed, or if some Eduka
            fields are missing.
        """
        response = requests.get(list_url)
        if response.status_code != 200:
            error_message = f'The HTTP request "{list_url}" failed with status code {response.status_code}'
            logging.error(error_message)
            raise ValueError(error_message)

        data = response.text
        match = REGEX_EDUKA_ERROR_CODE.search(data)
        if match:
            http_status_code = match.group('http_status_code')
            eduka_error_code = match.group('eduka_error_code')
            raise EdukaError(int(http_status_code), int(eduka_error_code))

        rows = data.splitlines()
        return rows

    @staticmethod
    def __fetch_eduka_list_url(
            eduka_school_hostname: str,
            api_key: str,
            list_id: int,
    ) -> str:
        """
        Request the generation of a predefined list, generated by the school
        organization, corresponding to the family data and return the URL of
        the generated list.

        The school organization is responsible for creating a predefined list
        corresponding to the family data with all the required fields for the
        children and the primary and secondary parents of these children.

        The function requests the Eduka school information system to generate
        the data in CSV (Comma-Separated Values) format, with the semicolon
        character as a delimiter.

        The generated list is only valid for a limited period of time, after
        which the list is no longer available for download.


        :param eduka_school_hostname: The hostname of the school's Eduka.

        :param api_key: The API key that allows to access the predefined list
            corresponding to the school's family data.

        :param list_id: The identifier of the predefined list corresponding to
             the school's family data.


        :return: The Uniform Resource Locator (URL) of the generated list
            corresponding to the school's family data.  This URL is only valid
            for a limited period of time.


    :raise UnauthorizedAccess: If the access to the predefined list is not
        authorized.  This could happen when the IP address of the machine
        that requests the predefined list has not been authorized to
        access the school's Eduka platform.
        """
        response = requests.get(
            f'https://{eduka_school_hostname}/api.php',
            params={
                'A': 'GENLIST',
                'FORMAT': 'csvs',
                'K': api_key,
                'LIST': list_id
            }
        )

        if response.status_code == 200:
            data = response.text
            data = '{"confirm":"OK","url":"https:\/\/lpehcm.eduka.school\/download\/ticket\/241\/ncroiazvudfraawhm1ly4tlkd1swun"}'

            try:
                payload = json.loads(data)
                return payload['url']

            except json.decoder.JSONDecodeError:
                match = REGEX_EDUKA_ERROR_CODE.search(data)
                if match:
                    http_status_code = match.group('http_status_code')
                    eduka_error_code = match.group('eduka_error_code')
                    raise EdukaError(int(http_status_code), int(eduka_error_code))

                else:
                    print(data)
        else:
            print("Request failed with status code:", response.status_code)

    def __init__(
            self,
            eduka_hostname: str,
            eduka_api_key: str,
            eduka_list_id: int,
            eduka_properties_mapping: dict[str, FamilyPropertyName],
            eduka_grades_names_mapping: dict[str, int] = None,
            eduka_languages_names_mapping: dict[str, Locale] = None,
            eduka_nationalities_names_mapping: dict[str, Country] = None
    ):
        """
        Build an ``EdukaConnector`` object.


        :param eduka_hostname: The hostname of the Eduka server of a school.

        :param eduka_api_key: The Eduka API key to use to access the family
            list.

        :param eduka_list_id: The list ID that the school has created and
            shared.

        :param eduka_properties_mapping: The mapping between the Xebus and the
            Eduka properties representing the information about a child and
            their parent.

        :param eduka_grades_names_mapping: The mapping between the names of the
            education grades used in Eduka and their corresponding levels.

        :param eduka_languages_names_mapping: The mapping between names of
            languages used in Eduka and their corresponding ISO 639-3:2007
            code.

        :param eduka_nationalities_names_mapping: The mapping between names of
            nationalities names used in Eduka and their corresponding ISO
            3166-1 alpha-2 code.
        """
        self.__eduka_hostname = eduka_hostname
        self.__eduka_api_key = eduka_api_key
        self.__eduka_list_id = eduka_list_id

        self.__eduka_properties_mapping = eduka_properties_mapping
        self.__eduka_grades_names_mapping = eduka_grades_names_mapping
        self.__eduka_languages_names_mapping = eduka_languages_names_mapping
        self.__eduka_nationalities_names_mapping = eduka_nationalities_names_mapping

    def fetch_family_list(self) -> FamilyList:
        """
        Returns the data of the families to synchronize.


        :return: The data of the families to synchronize.
        """
        # Fetch the URL of the Eduka list containing the families data to
        # synchronize.
        eduka_list_url = self.__fetch_eduka_list_url(
            self.__eduka_hostname,
            self.__eduka_api_key,
            self.__eduka_list_id
        )

        # Fetch the families data from the list URL.
        eduka_rows = self.__fetch_eduka_list_data(eduka_list_url)

        # Convert the Eduka CSV family list into a Xebus data structure.
        xebus_rows = self.__convert_eduka_rows(eduka_rows)

        # Build the families entities.
        family_list = FamilyList(xebus_rows)

        return family_list
