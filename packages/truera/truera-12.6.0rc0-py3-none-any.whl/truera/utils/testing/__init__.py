"""
unittest.TestCase subclass with custom comparisons for protobuf messages and
json-like data. Also supports "update mode" which updates expected data instead
of performing the comparison.
"""

import inspect
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple, Union
import unittest

from google.protobuf import text_format
from google.protobuf.message import Message

from truera.utils.testing.proto_utils import \
    assertProtosAreAlmostEqualWithTestCase

# Either the populated message or path to a txtproto and message blank.
MessageLike = Union[Message, Tuple[Path, Message]]

# json base types
JSONBase = Union[str, int, float]

# json except allow base or sequence roots
JSONLike = Union[str, int, float, Sequence['JSONLike'], Dict[str, 'JSONLike']]


def _read_message(
    file: Path, proto: Message, replacements: Dict[str, str] = None
):
    """
    Read a protobuf message from a txtproto file.
    """

    with file.open('r') as f:
        strings = f.readlines()

    string = ''.join(strings)

    if replacements is not None:
        for key, value in replacements.items():
            string = string.replace(key, value)

    text_format.Parse(string, proto)

    return proto


def _message_of_messagelike(proto: MessageLike, replacements: Dict = None):
    if isinstance(proto, Message):
        return proto
    elif isinstance(proto, Tuple):
        file, proto_type = proto
        return _read_message(file, proto_type, replacements=replacements)
    else:
        raise RuntimeError(f"Unexpected proto type: {type(proto)} .")


def _update_messagelike(
    proto: MessageLike,
    actual: MessageLike,
    float_format: Optional[str] = None,
    replacements: Optional[Dict[str, str]] = None
):
    assert isinstance(
        proto, Tuple
    ), "To update a protobuf message, provide it as (Path, Any) tuple."
    file, _ = proto

    actual = _message_of_messagelike(actual)

    content = text_format.MessageToString(actual, float_format=float_format)

    if replacements is not None:
        for key, value in replacements.items():
            content = content.replace(value, key)

    with file.open('w') as f:
        f.write(content)

    return False


class ProtoTestCase(unittest.TestCase):

    def setUp(self):
        """
        Set various default values:

        - replacements: Dict[str, str] - replace keys with values in txtproto
          contents before any comparisons
        - atol: float - absolute float tolerence for *AlmostEqual assertions
        - rtol: float - relative float tolerance for *AlmostEqual assertions
        - ignore_repeated_order: bool - do not compare order of repeated
          elements in assertions
        - update_expected: bool - replace expected message (must be given by
          filename) with specified actual data.
        """

        super().setUp()

        self.replacements = dict()
        self.atol = 1e-3
        self.rtol = 1e-3
        self.ignore_repeated_order = False
        self.float_format = None
        self.update_expected = False

    def tearDown(self):
        super().tearDown()

    @classmethod
    def setUpClass(cls):
        unittest.TestCase.setUpClass()

    @classmethod
    def tearDownClass(cls):
        unittest.TestCase.tearDownClass()

    def _get_defaults(self):
        # Get values for various arguments whether from defaults or explicit.
        # Gets values either from caller's locals or from self.
        locs = inspect.stack()[1].frame.f_locals

        rets = dict()

        for var in ["replacements", "atol", "rtol", "ignore_repeated_order"]:
            for var, val in locs.items():
                if val is None:
                    rets[var] = getattr(self, var)
                else:
                    rets[var] = val

        return rets

    def assertProtosAlmostEqual(
        self,
        actual: MessageLike,
        expected: MessageLike,
        atol: Optional[float] = None,
        rtol: Optional[float] = None,
        ignore_repeated_order: Optional[bool] = None,
        replacements: Optional[Dict[str, str]] = None,
        float_format: Optional[str] = None,
        update_expected: Optional[bool] = None,
    ):
        """
        Compare two messages with approximate floating point comparison and
        optionally unordered sequences (repeats). See TestCase.__init__ for
        arguments.
        """

        defaults = self._get_defaults()

        actual = _message_of_messagelike(
            actual, replacements=defaults['replacements']
        )

        if defaults['update_expected']:
            _update_messagelike(
                proto=expected,
                actual=actual,
                replacements=defaults['replacements'],
                float_format=defaults['float_format']
            )
            self.fail(f"Expected data {expected} updated.")

        else:

            expected = _message_of_messagelike(
                expected, replacements=defaults['replacements']
            )

            assertProtosAreAlmostEqualWithTestCase(
                test_case=self,
                proto1=actual,
                proto2=expected,
                atol=defaults['atol'],
                rtol=defaults['rtol'],
                ignore_repeated_order=defaults['ignore_repeated_order']
            )

    def assertProtosEqual(
        self,
        actual: MessageLike,
        expected: MessageLike,
        replacements: Optional[Dict[str, str]] = None,
        float_format: Optional[str] = None,
        update_expected: Optional[bool] = None
    ):
        """
        Compare two messages. See TestCase.__init__ for arguments.
        """

        defaults = self._get_defaults()

        # Copied from proto_utils.py equivalent of this method. Do not know purpose.
        self.maxDiff = None

        actual = _message_of_messagelike(
            actual, replacements=defaults['replacements']
        )

        if defaults['update_expected']:
            _update_messagelike(
                proto=expected,
                actual=actual,
                replacements=defaults['replacements'],
                float_format=defaults['float_format']
            )
            self.fail(f"Expected data {expected} updated.")

        else:

            expected = _message_of_messagelike(
                expected, replacements=defaults['replacements']
            )

            self.assertEqual(
                text_format.MessageToString(actual),
                text_format.MessageToString(expected)
            )
