from tabulato import colorful_tabulate, TableRowStyle

headers = ["Name", "Student Number", "DOB", "Email Address"]

data = [
    ["John Doe", "S12345", "1995-07-15", "john@example.com"],
    ["Alice Smith", "S67890", "1998-03-22", "alice@example.com"],
    ["Bob Johnson", "S54321", "1997-11-10", "bob@example.com"],
    ["Emma Brown", "S98765", "1996-09-18", "emma@example.com"],
    ["Michael Lee", "S24680", "1999-05-30", "michael@example.com"],
    ["Sophia Wang", "S13579", "1994-12-05", "sophia@example.com"],
    ["David Chen", "S75310", "1992-04-08", "david@example.com"],
    ["Olivia Kim", "S36924", "1993-10-25", "olivia@example.com"],
]


data = [
    {
        "name": "John Doe",
        "student number": "S12345",
        "dob": "1995-07-15",
        "email": "john@example.com",
    },
    {
        "name": "Alice Smith",
        "student number": "S67890",
        "dob": "1998-03-22",
        "email": "alice@example.com",
    },
    {
        "name": "Bob Johnson",
        "student number": "S54321",
        "dob": "1997-11-10",
        "email": "bob@example.com",
    },
    {
        "name": "Emma Brown",
        "student number": "S98765",
        "dob": "1996-09-18",
        "email": "emma@example.com",
    },
    {
        "name": "Michael Lee",
        "student number": "S24680",
        "dob": "1999-05-30",
        "email": "michael@example.com",
    },
    {
        "name": "Sophia Wang",
        "student number": "S13579",
        "dob": "1994-12-05",
        "email": "sophia@example.com",
    },
    {
        "name": "David Chen",
        "student number": "S75310",
        "dob": "1992-04-08",
        "email": "david@example.com",
    },
    {
        "name": "Olivia Kim",
        "student number": "S36924",
        "dob": "1993-10-25",
        "email": "olivia@example.com",
    },
]

print(data)

colorful_tabulate(
    data=data,
    column_widths=[20, 20, 20, 30],
)


colorful_tabulate(
    data=data,
    column_widths=[20, 20, 20, 30],
    header_style=TableRowStyle(
        bold=True,
        italic=False,
        color="BLUE",
        background="BG_BLUE",
    ),
    even_row_style=TableRowStyle(
        bold=False,
        italic=False,
        color="GREEN",
        underline=True,
    ),
    odd_row_style=TableRowStyle(
        bold=False,
        italic=False,
        color="YELLOW",
        strikethrough=True,
    ),
)
