import enum
import io
import json
from pprint import pformat
import types
from typing import IO, Any, Dict, Iterator, List, Optional

from pydantic import BaseModel, Field

from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text


class Markdownable:
    def to_markdown(self) -> str:
        return self.__repr__()


class FormattingOptions(BaseModel):
    force_list: bool = Field(default=False)
    table_columns: Optional[List[str]] = Field(default=None)


_formatting_options: Optional[FormattingOptions] = None


def set_formatting_options(formatting_options: FormattingOptions):
    global _formatting_options
    _formatting_options = formatting_options


def get_formatting_options() -> FormattingOptions:
    return _formatting_options or FormattingOptions()


class Formatter:
    name = "str"

    def __init__(self, args: Any):
        self.args = args

    def stringify_one(self, value: Any) -> str:
        return str(value)

    def format(self, out_io: IO, lines: Iterator[Any], raw_output: bool = False) -> None:
        # this may raise user exceptions, or SystemExit for wrapped exceptions
        for line in lines:
            # print the line as soon as it is generated to ensure that it is
            # displayed to the user before anything else happens, e.g.
            # raw_input() is called
            out_io.write(self.stringify_one(line))
            if not raw_output:
                # in most cases user wants one message per line
                out_io.write("\n")


class PPrintFormatter(Formatter):
    name = "pprint"

    def stringify_one(self, value: Any) -> str:
        return pformat(value.dict() if isinstance(value, BaseModel) else value)


class NullFormatter(Formatter):
    name = "null"

    def format(self, out_io: IO, lines: Iterator[Any], raw_output: bool = False):
        return list(lines)


class JSONFormatter(Formatter):
    name = "json"

    JOINER = ",\n"

    def stringify_one(self, value: Any) -> str:
        return value.json(indent=2) if isinstance(value, BaseModel) else json.dumps(value)

    def format(self, out_io: IO, lines: Iterator[Any], raw_output: bool = False) -> None:
        all_lines = [self.stringify_one(line) for line in lines]
        if not get_formatting_options().force_list and len(all_lines) == 1:
            out_io.write(all_lines[0])
        else:
            out_io.write(f"[{self.JOINER.join(all_lines)}]")


def is_str_enum(cls: types):
    return (
        type(cls) == enum.EnumMeta
        and cls._member_type_ == str  # pylint:disable=protected-access,unidiomatic-typecheck
    )


class RichFormatter(Formatter):
    name = "rich"
    LIST_JOINER = ", "

    def stringify_one(self, value: Any) -> str:
        if isinstance(value, list):
            return f"[{self.LIST_JOINER.join([self.stringify_one(element) for element in value])}]"
        if is_str_enum(type(value)):
            return value.value
        if isinstance(value, Markdownable):
            return value.to_markdown()
        if isinstance(value, BaseModel):
            return value.json(indent=2)
        if isinstance(value, dict):
            return json.dumps(value, indent=2)
        return super().stringify_one(value)

    def get_column_headers(self, rows: List[Dict[str, Any]]) -> List[str]:
        column_headers = get_formatting_options().table_columns
        if column_headers is None and len(rows) > 0:
            column_headers = sorted(list(rows[0].keys()))
        if column_headers is None:
            column_headers = ["output"]
        return column_headers

    def get_table_title(self) -> str:
        return f"Output of {self.args._functions_stack[0].__self__.command_group_name} {self.args._functions_stack[0].__name__}"

    def get_obj_fields(self, obj: Any) -> Dict[str, Any]:
        return obj if isinstance(obj, dict) else obj.__dict__

    def format_table(self, console: Console, rows: List[Dict[str, Any]], raw_output: bool = False):
        table = Table(title=self.get_table_title())
        column_headers = self.get_column_headers(rows)
        for column_header in column_headers:
            if column_header == "id":
                table.add_column(column_header, style="yellow")
            else:
                table.add_column(column_header)
        for row in rows:
            table.add_row(*[self.stringify_one(row.get(col)) for col in column_headers])
        if raw_output:
            console.out(table)
        else:
            console.print(table)

    def get_rows(self, all_lines: List[Any]) -> List[Dict[str, Any]]:
        if len(all_lines) == 0:
            return []
        sample_line = all_lines[0]
        if isinstance(sample_line, BaseModel):
            return [self.get_obj_fields(line) for line in all_lines]
        if isinstance(sample_line, str):
            return [{"output": line} for line in all_lines]
        return [self.get_obj_fields(line) for line in all_lines]

    def format_object(self, console: Console, obj: Any, raw_output: bool = False):
        output = None
        if isinstance(obj, Markdownable):
            output = Markdown(obj.to_markdown())
        elif isinstance(obj, str):
            output = obj
        else:
            output = Table(title=self.get_table_title())
            output.add_column("field")
            output.add_column("value")
            for field, value in self.get_obj_fields(obj).items():
                output.add_row(field, self.stringify_one(value))
        if raw_output:
            console.out(output)
        else:
            console.print(output)

    def format(self, out_io: IO, lines: Iterator[Any], raw_output: bool = False) -> None:
        console = Console(file=out_io)
        all_lines = list(lines)
        # We want to display results as a table if there's multiple rows or
        # the command forced table view
        # If there are no rows, display this error message
        if len(all_lines) > 0:
            if len(all_lines) > 1 or get_formatting_options().force_list:
                self.format_table(console, self.get_rows(all_lines), raw_output)
            else:
                self.format_object(console, all_lines[0], raw_output)


AVAILABLE_FORMATTERS = {
    formatter_cls.name: formatter_cls for formatter_cls in [*Formatter.__subclasses__(), Formatter]
}
