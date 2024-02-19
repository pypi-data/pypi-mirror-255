from typing import Optional
from tabulato.utils import COLOR_LITERAL, get_color, CONFIG, get_bg, BG_COLOR_LITERAL
from dataclasses import dataclass, field


@dataclass(kw_only=True, repr=False)
class TableRowStyle:
    bold: bool = field(default=False)
    italic: bool = field(default=False)
    underline: bool = field(default=False)
    strikethrough: bool = field(default=False)
    color: COLOR_LITERAL = field(default="")
    background: BG_COLOR_LITERAL = field(default="")


class DataMalformedException(Exception):
    pass


def colorful_tabulate(
    data: list[list | dict],
    headers: list[str] | None = None,
    colorful: bool = True,
    bold_header: bool = True,
    header_style: Optional[TableRowStyle] = TableRowStyle(
        bold=True, italic=False, color="BLUE", background=None
    ),
    even_row_style: Optional[TableRowStyle] = TableRowStyle(
        bold=False, italic=False, color="GREEN", background=None
    ),
    odd_row_style: Optional[TableRowStyle] = TableRowStyle(
        bold=False, italic=False, color="YELLOW", background=None
    ),
    column_widths: list[int] = [],
) -> None:
    """
    Generates a colorful tabular representation of data.
    Args:
        data (list[list | dict]): The data to be tabulated. Each element in the
            outer list represents a row, and each inner list or dictionary
            represents a cell.
        headers (list[str] | None, optional): List of strings representing the
            column headers. If None, no headers will be displayed. Defaults to None.
        colorful (bool, optional): Flag indicating whether to use colors for
            styling. Defaults to True.
        bold_header (bool, optional): Flag indicating whether to make the header
            text bold. Defaults to True.
        header_style (Optional[TableRowStyle], optional): Style for the header
            row. Defaults to a bold, blue text.
        even_row_style (Optional[TableRowStyle], optional): Style for even-numbered
            rows. Defaults to plain green text.
        odd_row_style (Optional[TableRowStyle], optional): Style for odd-numbered
            rows. Defaults to plain yellow text.
        column_widths (list[int], optional): List of integers representing the
            widths of each column. If provided, the table will attempt to adjust
            the column widths accordingly. Defaults to an empty list.

    Example:
        >>> data = [
        ...     ["John", 30, "Male"],
        ...     ["Jane", 28, "Female"],
        ...     ["Doe", 35, "Male"]
        ... ]
        >>> headers = ["Name", "Age", "Gender"]
        >>> colorful_tabulate(data, headers=headers)
    """
    lens = [len(row) for row in data]
    _max = lens[0]
    if not all([_max == length for length in lens]):
        raise DataMalformedException("The row values must have the same length.")

    if isinstance(data[0], dict):
        headers = list(data[0].keys())
        data = [d.values() for d in data]
    elif isinstance(data[0], list):
        if headers is None:
            headers = [f"Column {i+1}" for i, _ in enumerate(data[0])]

    if len(headers) != len(column_widths) and len(column_widths) != 0:
        raise DataMalformedException(
            f"The headers and column_width must have the same length but received ({len(headers), len(column_widths)})."
        )

    num_columns = len(data[0])
    if len(headers) != num_columns:
        raise DataMalformedException(
            f"The headers and rows must have the same length but received ({len(headers), len(data[0])})."
        )

    # Calculate the maximum width for each column
    column_widths = (
        column_widths
        if len(column_widths) != 0
        else [max(len(str(row[i])) for row in data) for i in range(num_columns)]
    )

    # Adjust column widths if headers are longer
    for i, header in enumerate(headers):
        column_widths[i] = max(column_widths[i], len(header))

    # Print the headers
    print("+", end="")
    for width in column_widths:
        print("-" * (width + 2) + "+", end="")
    print()
    for i, header in enumerate(headers):
        if colorful:
            print("| ", end="")
            styled_text(style=header_style, width=column_widths[i], text=header)
        else:
            print("| ", end="")
            print(
                (CONFIG.BOLD if bold_header else "")
                + f"{str(header):<{column_widths[i]}} "
                + CONFIG.RESET,
                end="",
            )
    print("|")

    # Print the separator
    print("+", end="")
    for width in column_widths:
        print("-" * (width + 2) + "+", end="")
    print()

    # Print the data rows
    for index, row in enumerate(data):
        for i, cell in enumerate(row):
            print("| ", end="")
            if colorful:
                if index % 2 == 0:
                    styled_text(
                        style=even_row_style, text=str(cell), width=column_widths[i]
                    )
                else:
                    styled_text(
                        style=odd_row_style, text=str(cell), width=column_widths[i]
                    )
            else:
                print(
                    f"{str(cell):<{column_widths[i]}} ",
                    end="",
                )
        print("|")

    # Print the bottom line
    print("+", end="")
    for width in column_widths:
        print("-" * (width + 2) + "+", end="")
    print()


def styled_text(style: TableRowStyle, text: str, width: int):
    print(
        get_bg(style.background)
        + get_color(style.color)
        + (CONFIG.BOLD if style.bold else "")
        + (CONFIG.ITALIC if style.italic else "")
        + (CONFIG.ITALIC if style.italic else "")
        + (CONFIG.STRIKETHROUGH if style.strikethrough else "")
        + (CONFIG.UNDERLINE if style.underline else "")
        + f"{str(text):<{width}} "
        + CONFIG.RESET,
        end="",
    )
