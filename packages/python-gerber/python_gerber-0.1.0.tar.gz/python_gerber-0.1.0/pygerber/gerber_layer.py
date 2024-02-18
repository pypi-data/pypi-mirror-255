import copy
import enum
import logging
import os
import re
from typing import List, NamedTuple, Tuple

import pygerber.aperture as aperture_lib
import pygerber.standards.gerber as gf


class Units(enum.Enum):
    """Enums of unit options in Gerbers (millimeters / inches)"""

    MM = "MM"
    INCH = "IN"
    UNKNOWN = "XX"


class OperationState(NamedTuple):
    """
    Represents the state of the Gerber files at an operation.
    Gerber files are read sequentially so when an operation is perform the state of the parameters needs to be saved
    """

    aperture: aperture_lib.Aperture
    interpolation: gf.GerberFormat
    point: tuple
    previous_point: tuple
    polarity: bool
    quadrant_mode: gf.GerberFormat
    scalars: tuple
    units: Units


class GerberLayerBaseException(Exception):
    pass


class UnknownApertureError(GerberLayerBaseException):
    pass


class GerberLayer:
    """
    Represents a Gerber layer or one file in the Gerber format
    """

    def __init__(self):
        self._in_header = True
        self.header = []
        self.current_aperture = None
        self.interpolation = None
        self.attributes = {}
        self.region = False
        self.polarity = None
        self.apertures = {}
        self.current_point = None
        self.comments = []
        self.units = Units.UNKNOWN
        self.quadrant_mode = None
        self.scalars = ()
        self.decimal_digits = (0, 0)
        self.integer_digits = (0, 0)
        self.operations: List[Tuple[gf.GerberFormat, OperationState]] = []
        self._regions = []
        self.aperture_factory = aperture_lib.ApertureFactory()
        self.collection_of_region = []
        self._set_standard_layer()

    def read(self, path, raise_on_unknown_command=False):
        _, extension = os.path.splitext(path.lower())
        if extension not in gf.FILE_EXT_TO_NAME:
            raise ValueError(f"Unknown file: {path}")
        file_type = gf.FILE_EXT_TO_NAME[extension]

        logging.info(f"Starting gerber layer importer:")
        logging.info(f"\tFile: {path}")
        logging.info(f"\tType: {file_type.upper()}")
        multiline = False
        with open(path, "r") as f:
            buffer = ""
            for index, line in enumerate(f.readlines()):
                if not line.strip():
                    continue
                buffer += line
                if line.count("%") not in [0, 2]:
                    multiline = not multiline
                if multiline:
                    continue
                buffer = buffer.strip()
                if buffer.startswith("%") and buffer.endswith("%"):
                    buffer = buffer[1:-1]
                if buffer.endswith("*"):
                    buffer = buffer[:-1]
                logging.debug(f"Line: {index}, Processing: {buffer}")
                self._process(buffer, raise_on_unknown_command)
                buffer = ""
        return self.operations, self.collection_of_region

    def _process(self, data, raise_on_unknown_command):
        op_type, content = gf.GerberFormat.lookup(data)

        if op_type in [
            gf.GerberFormat.INTERP_MODE_LINEAR,
            gf.GerberFormat.INTERP_MODE_CW,
            gf.GerberFormat.INTERP_MODE_CCW,
        ]:
            self.interpolation = op_type
            if content:  # this is rare and poor syntax
                self._process(content, raise_on_unknown_command)
        elif op_type == gf.GerberFormat.COMMENT:
            if self._in_header:
                self.header.append(content)
            else:
                self.comments.append(content)
        elif op_type == gf.GerberFormat.UNITS:
            self._in_header = False
            self.units = Units(data[2:])
            logging.info(f"Switching units to {self.units}")
        elif op_type in [
            gf.GerberFormat.DEPRECATED_UNITS_MM,
            gf.GerberFormat.DEPRECATED_UNITS_INCH,
        ]:
            u = "MM" if op_type == gf.GerberFormat.DEPRECATED_UNITS_MM else "INCH"
            self.units = Units(u)
            logging.info(f"Switching units to {self.units}")
        elif op_type in [
            gf.GerberFormat.QUADMODE_SINGLE,
            gf.GerberFormat.QUADMODE_MULTI,
        ]:
            logging.info(f"Switching quadrant mode to: {op_type}")
            self.quadrant_mode = op_type
        elif op_type == gf.GerberFormat.FORMAT:
            self._set_format_spec(data)
            logging.info(f"Got decimal places: {self.scalars}")
        elif op_type == gf.GerberFormat.LOAD_POLARITY:
            self.polarity = content == "D"
            logging.info(f"Setting polarity to {self.polarity}")
        elif op_type == gf.GerberFormat.APERTURE_DEFINE:
            aperture = self.aperture_factory.from_aperture_define(
                content, copy.deepcopy(self.comments)
            )
            self.apertures[aperture.index] = aperture
            self.comments.clear()
            logging.info(f"Add aperture: {aperture.index}")
        elif op_type == gf.GerberFormat.APERTURE_MACRO:
            self.aperture_factory.define_macro(content)
            logging.info(f"Processed aperture macro: {content}")
        elif op_type == gf.GerberFormat.SET_APERTURE:
            self.current_aperture = int(data[1:])
            logging.info(f"Current aperture set to: {self.current_aperture}")
        elif op_type == gf.GerberFormat.ATTRIBUTE_FILE:
            params = content.split(",")
            self.attributes[params[0][1:]] = params[1:]
        elif op_type in [
            gf.GerberFormat.ATTRIBUTE_OBJECT,
            gf.GerberFormat.ATTRIBUTE_DELETE,
            gf.GerberFormat.ATTRIBUTE_APERTURE,
        ]:
            pass  # TODO: no-op for now - these are just comments
        elif op_type in [
            gf.GerberFormat.OPERATION_FLASH,
            gf.GerberFormat.OPERATION_MOVE,
            gf.GerberFormat.OPERATION_INTERP,
        ]:
            op = self._run_operation(content)
            logging.info(f"Operation: {op_type}, point: {self.current_point}")
            self.current_point = op.point
            if self.region:
                self._regions.append((op_type, op))
            else:
                self.operations.append((op_type, op))
        elif op_type in [gf.GerberFormat.REGION_START, gf.GerberFormat.REGION_END]:
            self.region = op_type == gf.GerberFormat.REGION_START
            if not self.region:
                region = copy.deepcopy(self._regions)
                self.collection_of_region.append(region)
                self._regions.clear()
            logging.info(f"{'START' if self.region else 'END'} Region")
        elif op_type in [gf.GerberFormat.DEPRECATED_SELECT_APERTURE]:
            self._process(content, raise_on_unknown_command)  # no-op
        elif op_type in [
            gf.GerberFormat.DEPRECATED_PROGRAM_STOP,
            gf.GerberFormat.DEPRECATED_ABSOLUTE_NOTATION,
        ]:
            pass  # no-op
        elif op_type == gf.GerberFormat.END_OF_FILE:
            logging.info("End of file command.")
        else:
            logging.warning(f"Unknown command: {data}")
            if raise_on_unknown_command:
                raise ValueError(f"Unknown command: {data}")

    def point_to_text(self, point):
        assert point[0] < pow(10, self.integer_digits.x), "Overflow x value"
        assert point[1] < pow(10, self.integer_digits.y), "Overflow y value"
        x = int(point[0] * pow(10, self.decimal_digits.x))
        y = int(point[1] * pow(10, self.decimal_digits.y))
        return f"X{x}Y{y}"

    def write(self, filename):
        def write_line(message: str, _file, grouped=False):
            message += "*"
            if grouped:
                message = f"%{message}%"
            _file.write(message + "\n")

        state = self.operations[0][1]
        with open(filename, "w") as f:
            current_aperture = None
            for comment in self.header:
                write_line(gf.GerberFormat.COMMENT.value + comment, f)
            write_line(gf.GerberFormat.UNITS.value + state.units.value, f, True)
            format_spec = gf.Point(
                x=(self.integer_digits.x * 10 + self.decimal_digits.x),
                y=(self.integer_digits.y * 10 + self.decimal_digits.y),
            )

            write_line("FSLA" + format_spec.to_text(), f, True)
            write_line(state.quadrant_mode.value, f)
            for macro in self.aperture_factory.macros.values():
                write_line(self.aperture_factory.macro_to_str(macro), f)
            for aperture in self.apertures.values():
                for comment in aperture.comments:
                    write_line(gf.GerberFormat.COMMENT.value + comment, f)
                statement = self.aperture_factory.to_aperture_define(aperture)
                write_line(statement, f, True)
            polarity = gf.GerberFormat.LOAD_POLARITY.value
            polarity += "D" if state.polarity else "C"
            write_line(polarity, f, True)
            for op_type, op in self.operations:
                if op.aperture and op.aperture != current_aperture:
                    write_line(f"D{op.aperture.index}", f)
                    current_aperture = op.aperture
                write_line(self.point_to_text(op.point) + op_type.value, f)
            write_line(gf.GerberFormat.END_OF_FILE.value, f)

    def scale(self, point):
        x = round(point[0] * self.scalars[0], self.decimal_digits.x)
        y = round(point[1] * self.scalars[1], self.decimal_digits.y)
        return x, y

    def _run_operation(self, content: str):
        values = re.findall(r"[A-Z]([\+|-]*\d+)", content)
        assert len(values) in [2, 4], f"Invalid operation parsing: {content}"
        assert self.region or self.current_aperture, "Invalid operation: no aperture!"

        point = self.scale((float(values[0]), float(values[1])))
        if len(values) == 4:
            x, y, i, j = values
            point = self.scale((float(x), float(y))), self.scale((float(i), float(j)))
        if self.region:
            return self.get_operation_state(None, point)

        aperture = self.apertures.get(self.current_aperture)
        if aperture is None:
            raise UnknownApertureError(f"Unknown aperture: {self.current_aperture}!")
        return self.get_operation_state(aperture, point)

    def get_operation_state(self, aperture, point):
        return OperationState(
            aperture=aperture if not self.region else None,
            polarity=self.polarity,
            units=self.units,
            quadrant_mode=self.quadrant_mode,
            scalars=self.scalars,
            interpolation=self.interpolation,
            previous_point=self.current_point,
            point=point,
        )

    def _set_format_spec(self, data):
        regex = r"FSLAX(\d)(\d)Y(\d)(\d)"
        match = re.search(regex, data)
        if not match:
            raise RuntimeError("No decimal places available!")
        intx, decx, inty, decy = match.groups()
        self.scalars = (pow(10, -int(decx)), pow(10, -int(decy)))
        self.integer_digits = gf.Point(int(intx), int(inty))
        self.decimal_digits = gf.Point(int(decx), int(decy))

    def _set_standard_layer(self):
        self.integer_digits = gf.Point(4, 4)
        self.decimal_digits = gf.Point(6, 6)
        self.scalars = (pow(10, -6), pow(10, -6))
        self.quadrant_mode = gf.GerberFormat.QUADMODE_MULTI
        self.units = gf.GerberFormat.UNITS
        self.interpolation = gf.GerberFormat.INTERP_MODE_LINEAR
        self.polarity = True

    def flash(
        self, aperture: aperture_lib.APERTURES, position: Tuple[float, float]
    ) -> None:
        if aperture not in self.apertures:
            index = len(self.apertures) + 1
            self.apertures[index] = aperture
        state = self.get_operation_state(aperture, position)
        self.operations.append((gf.GerberFormat.OPERATION_FLASH, state))
