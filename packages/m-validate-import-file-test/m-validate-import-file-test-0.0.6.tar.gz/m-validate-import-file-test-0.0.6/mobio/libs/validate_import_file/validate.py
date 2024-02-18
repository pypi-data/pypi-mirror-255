#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Author: tungdd
    Company: MobioVN
    Date created: 02/03/2023
"""


import os
import re
import zipfile
from io import BytesIO
from typing import IO, Iterator

import python_calamine

from mobio.libs.filetypes.common import ExtensionDocument
from mobio.libs.filetypes.custom_mimetypes import CustomMimetypes
from mobio.libs.filetypes.file import File
from mobio.libs.logging import MobioLogging
from mobio.libs.validate_import_file.common import KeyConstantError
from mobio.libs.monitor import Monitor

monitor = Monitor()
monitor.config(func_threshold=0.01)


class ValidateImportFile(object):
    def __init__(self, number_row_limit=None, capacity_limit=None):
        """
        Parameters: number_row_limit số dòng giới hạn
        Parameters: capacity_limit giới hạn dụng lượng file
        """

        self.number_row_limit = number_row_limit
        self.capacity_limit = capacity_limit

    @classmethod
    def get_number_row_excel_calamine(
        cls, file: IO[bytes]
    ) -> Iterator[dict[str, object]]:
        workbook = python_calamine.CalamineWorkbook.from_filelike(file)  # type: ignore[arg-type]
        number_rows = len(
            workbook.get_sheet_by_index(0).to_python(skip_empty_area=True)
        )
        return number_rows

    @classmethod
    def validate_format_file_upload(cls, file_upload):
        mimetype_file_upload = file_upload.mimetype
        MobioLogging().info(
            "ValidateImportFile :: validate_format_file_upload :: mimetype_file_upload :: %s"
            % mimetype_file_upload
        )
        format_file = CustomMimetypes().mimetypes.guess_extension(mimetype_file_upload)
        MobioLogging().info(
            "ValidateImportFile :: validate_format_file :: format_file :: %s"
            % format_file
        )

        if format_file in ["." + ExtensionDocument.XLS, "." + ExtensionDocument.XLSX]:
            result_validate = File.check_filetype_by_file_extensions(
                file_binary=file_upload,  # Check filetype của định dạng file binary.Mặc định None
                extensions=[
                    ExtensionDocument.XLS,
                    ExtensionDocument.XLSX,
                ],  # Danh sách extension cần check.
            )
            MobioLogging().info(
                "ValidateImportFile :: result_validate :: {}".format(result_validate)
            )
            if not result_validate.get("status"):
                return {
                    "status": False,
                    "reason": KeyConstantError.FAIL_VALIDATE_FILE_TYPE,
                }
        elif format_file != ".csv":
            return {"status": False, "reason": KeyConstantError.FAIL_VALIDATE_FILE_TYPE}
        return {"status": True, "mime_type": format_file}
    
    @monitor.monitor_func(args_log_enable=True)
    def file_upload(self, file):
        result_mimetype_file = self.validate_format_file_upload(file)
        if not result_mimetype_file.get("status"):
            return result_mimetype_file
        mimetype_file = result_mimetype_file.get("mime_type")

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        if self.capacity_limit is not None and file_size > self.capacity_limit:
            return {
                "status": False,
                "reason": KeyConstantError.FAIL_VALIDATE_FILE_CAPACITY,
            }
        file.seek(0)
        total_row_file_upload = None

        if self.number_row_limit is not None:
            if mimetype_file == ".xlsx":
                archive = zipfile.ZipFile(BytesIO(initial_bytes=file.read()), "r")
                with archive.open("xl/worksheets/sheet1.xml") as f:
                    text = f.read().decode("utf-8").strip()
                    try:
                        re_group = re.match(
                            r'.*[\r\n]*.*<dimension ref="[^:]+:[^0-9]+([0-9]+).*', text
                        )
                        total_row_file_upload = re_group.group(1)
                    except Exception:
                        MobioLogging().debug(
                            "ValidateImportFile :: Not read by regex pattern"
                        )

            elif mimetype_file == ".csv":
                total_row_file_upload = sum(1 for _ in file.stream.readlines())

            if total_row_file_upload is None and mimetype_file == ".xlsx":
                file.seek(0)
                total_row_file_upload = self.get_number_row_excel_calamine(file)
            if total_row_file_upload > self.number_row_limit:
                return {
                    "status": False,
                    "reason": KeyConstantError.FAIL_VALIDATE_FILE_NUMBER_ROW,
                }
        file.seek(0)
        return {"status": True}
