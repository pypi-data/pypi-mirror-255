# Copyright (C) 2023 Bootloader.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Bootloader or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Bootloader.
#
# BOOTLOADER MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE
# SUITABILITY OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR
# A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.  BOOTLOADER SHALL NOT BE
# LIABLE FOR ANY LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF
# USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

from majormode.perseus.model.locale import Locale


class LocalizedString:
    def __init__(
            self,
            locale: Locale,
            text: str):
        self.__locale = locale
        self.__text = text

    @staticmethod
    def from_json(payload):
        return payload and LocalizedString(
            Locale.from_string(payload['locale']),
            payload['text']
        )

    @property
    def locale(self) -> Locale:
        return self.__locale

    @property
    def text(self) -> str:
        return self.__text

    def to_json(self):
        return {
            'locale': self.__locale,
            'text': self.__text,
        }


class LocalizedStringBundle:
    def __init__(self, strings: list[LocalizedString]):
        self.__strings: dict[Locale, LocalizedString] = {
            string.locale: string.text
            for string in strings
        }

    @staticmethod
    def from_json(payload):
        if not payload:
            return None

        if isinstance(payload, dict):
            payload = [payload]
        elif not isinstance(payload, (list, set, tuple)):
            raise ValueError(f"Invalid argument type {payload.__class__.__name__}")

        return LocalizedStringBundle([
            LocalizedString.from_json(_)
            for _ in payload
        ])

    def get_string(self, locale: Locale):
        string = self.__strings[locale]
        if string:
            return string

    def to_json(self):
        return [
            string.to_json()
            for string in self.__strings.values()
        ]

