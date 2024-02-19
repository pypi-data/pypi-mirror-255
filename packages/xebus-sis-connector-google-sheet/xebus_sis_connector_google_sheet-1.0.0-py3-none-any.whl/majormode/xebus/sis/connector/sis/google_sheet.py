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

import logging
from os import PathLike
from pathlib import Path
from typing import Any, Callable

import gspread
from majormode.perseus.model.country import Country, InvalidCountryCode
from majormode.perseus.model.locale import Locale
from majormode.perseus.utils import cast
from majormode.xebus.sis.connector import utils
from majormode.xebus.sis.connector.constant.family import FamilyPropertyName
from majormode.xebus.sis.connector.model.family import FamilyList
from majormode.xebus.sis.connector.sis_connector import SisConnector

from majormode.xebus.sis.connector.sis.sheet_utils import SectionedSheet

from settings import LIBRARY_DATA_PATH


class GoogleSheetConnector(SisConnector):
    DEFAULT_FAMILIES_SHEET_NAME = 'Families'

    # Column names of the primary header (sections) of the sheet.
    SECTION_NAME_CHILD = 'Child'
    SECTION_NAME_PRIMARY_PARENT = 'Parent 1'
    SECTION_NAME_SECONDARY_PARENT = 'Parent 2'

    # Column names of the secondary header (fields) of the CSV file.
    FIELD_NAME_IS_CHILD_REMOVED = '🗑'
    FIELD_NAME_ACCOUNT_ID = 'SIS ID'
    FIELD_NAME_DOB = "Date of Birth"
    FIELD_NAME_EMAIL_ADDRESS = 'Email Address'
    FIELD_NAME_FIRST_NAME = 'First Name'
    FIELD_NAME_FULL_NAME = 'Full Name'
    FIELD_NAME_GRADE_NAME = 'Grade Name'
    FIELD_NAME_CLASS_NAME = 'Class Name'
    FIELD_NAME_HOME_ADDRESS = 'Home Address'
    FIELD_NAME_LANGUAGE = 'Language'
    FIELD_NAME_LAST_NAME = 'Last Name'
    FIELD_NAME_NATIONALITY = 'Nationality'
    FIELD_NAME_PHONE_NUMBER = 'Phone Number'
    FIELD_NAME_USE_TRANSPORT = 'Transport?'

    GOOGLE_SHEET_PROPERTIES_MAPPING = {
        SECTION_NAME_CHILD: {
            FIELD_NAME_ACCOUNT_ID: FamilyPropertyName.child_sis_id,
            FIELD_NAME_CLASS_NAME: FamilyPropertyName.child_class_name,
            FIELD_NAME_DOB: FamilyPropertyName.child_date_of_birth,
            FIELD_NAME_FIRST_NAME: FamilyPropertyName.child_first_name,
            FIELD_NAME_FULL_NAME: FamilyPropertyName.child_full_name,
            FIELD_NAME_GRADE_NAME: FamilyPropertyName.child_grade_level,
            FIELD_NAME_LANGUAGE: FamilyPropertyName.child_languages,
            FIELD_NAME_LAST_NAME: FamilyPropertyName.child_last_name,
            FIELD_NAME_NATIONALITY: FamilyPropertyName.child_nationalities,
            FIELD_NAME_USE_TRANSPORT: FamilyPropertyName.child_use_transport
        },
        SECTION_NAME_PRIMARY_PARENT: {
            FIELD_NAME_ACCOUNT_ID: FamilyPropertyName.primary_guardian_sis_id,
            FIELD_NAME_EMAIL_ADDRESS: FamilyPropertyName.primary_guardian_email_address,
            FIELD_NAME_FIRST_NAME: FamilyPropertyName.primary_guardian_first_name,
            FIELD_NAME_FULL_NAME: FamilyPropertyName.primary_guardian_full_name,
            FIELD_NAME_HOME_ADDRESS: FamilyPropertyName.primary_guardian_home_address,
            FIELD_NAME_LANGUAGE: FamilyPropertyName.primary_guardian_languages,
            FIELD_NAME_LAST_NAME: FamilyPropertyName.primary_guardian_last_name,
            FIELD_NAME_NATIONALITY: FamilyPropertyName.primary_guardian_nationalities,
            FIELD_NAME_PHONE_NUMBER:  FamilyPropertyName.primary_guardian_phone_number,
        },
        SECTION_NAME_SECONDARY_PARENT: {
            FIELD_NAME_ACCOUNT_ID: FamilyPropertyName.secondary_guardian_sis_id,
            FIELD_NAME_EMAIL_ADDRESS: FamilyPropertyName.secondary_guardian_email_address,
            FIELD_NAME_FIRST_NAME: FamilyPropertyName.secondary_guardian_first_name,
            FIELD_NAME_FULL_NAME: FamilyPropertyName.secondary_guardian_full_name,
            FIELD_NAME_HOME_ADDRESS: FamilyPropertyName.secondary_guardian_home_address,
            FIELD_NAME_LANGUAGE: FamilyPropertyName.secondary_guardian_languages,
            FIELD_NAME_LAST_NAME: FamilyPropertyName.secondary_guardian_last_name,
            FIELD_NAME_NATIONALITY: FamilyPropertyName.secondary_guardian_nationalities,
            FIELD_NAME_PHONE_NUMBER:  FamilyPropertyName.secondary_guardian_phone_number,
        }
    }

    def __convert_field_grade_name_value(self, value: str) -> int | None:
        grade_level = self.__grades_names_mapping.get(value)
        if grade_level is None:
            message = f"Invalid Eduka string representation \"{value}\" of a grade name"
            logging.error(message)
            raise ValueError(message)

        return grade_level

    def __convert_field_language_value(self, value: str) -> Locale:
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
            locale = self.__languages_names_mapping and self.__languages_names_mapping.get(value)
            if not locale:
                logging.error(f"Invalid string representation \"{value}\" of a language")
                raise ValueError(str(error))

        return locale

    def __convert_field_nationality_value(self, value: str) -> Country:
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
            country = self.__nationalities_names_mapping and self.__nationalities_names_mapping.get(value)
            if not country:
                logging.error(f"Invalid string representation \"{value}\" of a nationality")
                raise ValueError(str(error))

        return country

    # Mapping between family properties and functions responsible for
    # converting their values from Google Sheet data.
    FIELD_VALUE_CONVERTERS: dict[FamilyPropertyName, Callable[[Any, str], Any]] = {
        FamilyPropertyName.child_date_of_birth: SisConnector._convert_field_date_value,
        FamilyPropertyName.child_grade_level: __convert_field_grade_name_value,
        FamilyPropertyName.child_languages: __convert_field_language_value,
        FamilyPropertyName.child_nationalities: __convert_field_nationality_value,
        FamilyPropertyName.child_use_transport: SisConnector._convert_field_boolean_value,
        FamilyPropertyName.primary_guardian_email_address: SisConnector._convert_field_email_address_value,
        FamilyPropertyName.primary_guardian_languages: __convert_field_language_value,
        FamilyPropertyName.primary_guardian_nationalities: __convert_field_nationality_value,
        FamilyPropertyName.primary_guardian_phone_number: SisConnector._convert_field_phone_number_value,
        FamilyPropertyName.secondary_guardian_email_address: SisConnector._convert_field_email_address_value,
        FamilyPropertyName.secondary_guardian_languages: __convert_field_language_value,
        FamilyPropertyName.secondary_guardian_nationalities: __convert_field_nationality_value,
        FamilyPropertyName.secondary_guardian_phone_number: SisConnector._convert_field_phone_number_value,
    }

    def __convert_sheet_rows(
            self,
            rows: list[list[str]]
    ) -> list[dict[FamilyPropertyName, Any]]:
        """

        :param rows:


        :return:
        """
        sectioned_sheet = SectionedSheet(rows)

        rows = []
        for row_index in range(sectioned_sheet.data_row_count):
            # Check whether the current row is empty, meaning that we have reached
            # the end of the family data list.
            if self.__is_row_empty(sectioned_sheet, row_index):
                break

            # Check whether the child has been marked as no longer with the school
            # and should be removed from the list.
            is_child_removed = self._convert_field_boolean_value(
                sectioned_sheet.get_field_value(row_index, self.SECTION_NAME_CHILD, self.FIELD_NAME_IS_CHILD_REMOVED, is_required=True)
            )

            if is_child_removed:
                continue

            # Convert the sheet fields names and their values.
            fields = {}
            for sheet_section_name, sheet_fields_names in self.GOOGLE_SHEET_PROPERTIES_MAPPING.items():
                for sheet_field_name, field_name in sheet_fields_names.items():
                    sheet_field_value = sectioned_sheet.get_field_value(row_index, sheet_section_name, sheet_field_name, is_required=False)

                    field_value_converter_function = self.FIELD_VALUE_CONVERTERS.get(field_name)
                    field_value = sheet_field_value if field_value_converter_function is None \
                        else field_value_converter_function(self, sheet_field_value)

                    fields[field_name] = field_value

            rows.append(fields)

        return rows

    def __init__(
            self,
            google_service_account_file_path_name: PathLike,
            spreadsheet_url: str,
            grades_names_mapping: dict[str, int],
            families_sheet_name: str = None
    ):
        self.__google_client = gspread.service_account(filename=str(google_service_account_file_path_name))
        self.__spreadsheet_url = spreadsheet_url
        self.__grades_names_mapping = grades_names_mapping
        self.__families_sheet_name = families_sheet_name or GoogleSheetConnector.DEFAULT_FAMILIES_SHEET_NAME

        self.__languages_names_mapping = self.__load_languages_names_mapping_from_default_csv_file()
        self.__nationalities_names_mapping = self.__load_nationalities_names_mapping_from_default_csv_file()

    def __is_row_empty(self, sectioned_sheet: SectionedSheet, row_index: int) -> bool:
        """
        Indicate if the specified row is empty.


        :param sectioned_sheet: The sheet containing the row.

        :param row_index: The index of the row in the sheet.


        :return: ``True`` if the row is empty; ``False`` otherwise.
        """
        # Check whether some fields contain a value.
        #
        # :note: The code commented out below is a shorter version, however it
        # requires checking each field, which is slower.
        #
        # ```python
        # non_empty_fields = [
        #     field_name
        #     for sheet_section_name, sheet_fields_names in self.GOOGLE_SHEET_PROPERTIES_MAPPING.items()
        #     for sheet_field_name, field_name in sheet_fields_names.items()
        #     if field_name != FamilyPropertyName.child_use_transport
        #        and sectioned_sheet.get_field_value(
        #            row_index,
        #            sheet_section_name,
        #            sheet_field_name,
        #            is_required=False
        #        ) is not None
        # ]
        #
        # return not non_empty_fields
        # ```
        for sheet_section_name, sheet_fields_names in self.GOOGLE_SHEET_PROPERTIES_MAPPING.items():
            for sheet_field_name, field_name in sheet_fields_names.items():
                # The field `FamilyPropertyName.child_use_transport` is never empty
                # because it contains either the value `TRUE` or `FALSE`.
                if field_name != FamilyPropertyName.child_use_transport:
                    sheet_field_value = sectioned_sheet.get_field_value(
                        row_index,
                        sheet_section_name,
                        sheet_field_name,
                        is_required=False
                    )

                    if sheet_field_value:
                        return False

        return True

    @staticmethod
    def __fetch_family_list_from_google_sheet(
            google_client: gspread.client.Client,
            spreadsheet_url: str,
            sheet_name: str
    ) -> list[list[str]]:
        spreadsheet = google_client.open_by_url(spreadsheet_url)
        print(spreadsheet.lastUpdateTime)
        worksheet = spreadsheet.worksheet(sheet_name)
        print(worksheet.updated)

        # Read the whole content of the sheet in one go.
        #
        # @note: This code is faster than the simpler following version that
        #     does multiple API network calls:
        #
        # ```python
        # rows = [
        #     worksheet.row_values(i)
        #     for i in range(1, worksheet.row_count + 1)
        # ]
        # ```
        cells = worksheet.range(1, 1, worksheet.row_count, worksheet.col_count)
        rows = [
            [
                cell.value
                for cell in cells[row_index * worksheet.col_count: (row_index + 1) * worksheet.col_count]
            ]
            for row_index in range(worksheet.row_count)
        ]

        return rows

    @staticmethod
    def __load_languages_names_mapping_from_default_csv_file() -> dict[str, Locale]:
        """
        Return the mapping between the names of languages and their respective
        ISO 639-3:2007 codes as identified in the default Eduka languages
        file.


        :return: A dictionary representing a mapping between the names of
            languages (the keys), localized in the specified language, and
            their corresponding ISO 639-3:2007 codes (the values).
        """
        default_file_path_name = Path(LIBRARY_DATA_PATH, f'languages_names.csv')
        return utils.load_languages_names_iso_codes_mapping_from_csv_file(default_file_path_name)

    @staticmethod
    def __load_nationalities_names_mapping_from_default_csv_file() -> dict[str, Country]:
        """
        Return the mapping between the names of nationalities and their
        respective ISO 3166-1 alpha-2 codes as identified in the default Eduka
        nationalities file.


        :return: A dictionary representing a mapping between the names of
            nationalities (the keys), localized in the specified langauge, and
            their corresponding ISO 3166-1 alpha-2 codes (the values).
        """
        default_file_path_name = Path(LIBRARY_DATA_PATH, f'countries_names.csv')
        return utils.load_nationalities_names_iso_codes_mapping_from_csv_file(default_file_path_name)

    def fetch_family_list(self) -> FamilyList:
        # Read thw whole content of the Google Sheet.
        rows = self.__fetch_family_list_from_google_sheet(
            self.__google_client,
            self.__spreadsheet_url,
            self.__families_sheet_name
        )

        # Convert the Google Sheet rows into a Xebus data structure.
        xebus_rows = self.__convert_sheet_rows(rows)

        # Build the families entities.
        family_list = FamilyList(xebus_rows)

        return family_list

