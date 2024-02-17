# SPDX-FileCopyrightText: 2021-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from typing_extensions import Literal

from onetl.file.format.file_format import ReadOnlyFileFormat
from onetl.hooks import slot, support_hooks

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


READ_WRITE_OPTIONS = frozenset(
    (
        "dateFormat",
        "enableDateTimeParsingFallback",
        "timestampFormat",
        "timestampNTZFormat",
        "timeZone",
    ),
)

READ_OPTIONS = frozenset(
    (
        "allowBackslashEscapingAnyCharacter",
        "allowComments",
        "allowNonNumericNumbers",
        "allowNumericLeadingZeros",
        "allowSingleQuotes",
        "allowUnquotedControlChars",
        "allowUnquotedFieldNames",
        "columnNameOfCorruptRecord",
        "dropFieldIfAllNull",
        "locale",
        "mode",
        "prefersDecimal",
        "primitivesAsString",
        "samplingRatio",
    ),
)

WRITE_OPTIONS = frozenset(
    (
        "compression",
        "ignoreNullFields",
    ),
)


@support_hooks
class JSON(ReadOnlyFileFormat):
    """
    JSON file format. |support_hooks|

    Based on `Spark JSON <https://spark.apache.org/docs/latest/sql-data-sources-json.html>`_ file format.

    Supports reading (but **NOT** writing) files with ``.json`` extension with content like:

    .. code-block:: json
        :caption: example.json

        [
            {"key": "value1"},
            {"key": "value2"}
        ]

    .. warning::

        For writing prefer using :obj:`JSONLine <onetl.file.format.jsonline.JSONLine>`.

    .. note ::

        You can pass any option to the constructor, even if it is not mentioned in this documentation.
        **Option names should be in** ``camelCase``!

        The set of supported options depends on Spark version. See link above.

    Examples
    --------

    Describe options how to read from/write to JSON file with specific options:

    .. code:: python

        json = JSON(encoding="utf-8", compression="gzip")

    """

    name: ClassVar[str] = "json"

    multiLine: Literal[True] = True  # noqa: N815
    encoding: str = "utf-8"
    lineSep: str = "\n"  # noqa: N815

    class Config:
        known_options = READ_WRITE_OPTIONS | READ_OPTIONS | WRITE_OPTIONS
        extra = "allow"

    @slot
    def check_if_supported(self, spark: SparkSession) -> None:
        # always available
        pass
