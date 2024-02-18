from colorful_terminal import TermAct, colored_print
from exception_details import print_exception_details
from .rounding import round_relative_to_decimal


def get_percentage_as_fitted_string(
    count: int, total: int, round_to: int = 2, with_percentage_symbol: bool = True
):
    if total == 0:
        count = 0
        perc = 100
    else:
        perc = count / total * 100
    perc = str(round_relative_to_decimal(perc, round_to))
    if with_percentage_symbol:
        perc += " %"
    return perc


def progress_printer(
    count: int, total: int, pre_string: str = "Progress: ", post_string: str = ""
):
    TermAct.Clear_Current_Line()
    print(
        f"\r{pre_string}{str(count).rjust(len(str(total)))} / {total}    ({get_percentage_as_fitted_string(count, total)}){post_string}",
        end="",
    )
    if count == total:
        print()


def main_and_sub_progress_printer(
    maincount: int,
    maintotal: int,
    subcount: int,
    subtotal: int,
    pre_string: str = "Progress: ",
    mainpre_string: str = "Main-Progress: ",
    subpre_string: str = "Sub-Progress: ",
    post_string: str = "",
    mainpost_string: str = "",
    subpost_string: str = "",
):
    if maincount == 0 and subcount == 0:
        print(TermAct.Hide_Cursor(), end="")

    if post_string == "":
        lines = 3
    else:
        lines = 4 + post_string.count("\n")
    if maincount != 0 and subcount != 0:
        for i in range(lines):
            colored_print(TermAct.Cursor_Previous_Line, end="")
    if len(mainpre_string) < len(subpre_string):
        mainpre_string = mainpre_string.ljust(len(subpre_string))
    elif len(mainpre_string) > len(subpre_string):
        subpre_string = subpre_string.ljust(len(mainpre_string))
    length = (
        len(str(subtotal))
        if len(str(subtotal)) > len(str(maintotal))
        else len(str(maintotal))
    )
    maintotal_str = str(maintotal).rjust(length)
    subtotal_str = str(subtotal).rjust(length)
    maincount_str = str(maincount).rjust(length)
    _subcount = subcount if subtotal != 0 else 0
    subcount_str = str(_subcount).rjust(length)

    try:
        # s = ""
        # s += f"{pre_string}" + "\n"
        # s += f"\r{mainpre_string}{maincount_str} / {maintotal_str}  ({get_percentage_as_fitted_string(maincount, maintotal)}){mainpost_string}" + "\n"
        # s += f"\r{subpre_string}{subcount_str} / {subtotal_str}  ({get_percentage_as_fitted_string(subcount, subtotal)}){subpost_string}" + "\n"
        # s += post_string + "\n"
        # print(s + "\r", end="")
        s = f"{pre_string}"
        TermAct.Clear_Current_Line()
        print(s)
        s = f"\r{mainpre_string}{maincount_str} / {maintotal_str}  ({get_percentage_as_fitted_string(maincount, maintotal)}){mainpost_string}"
        TermAct.Clear_Current_Line()
        print(s)
        s = f"\r{subpre_string}{subcount_str} / {subtotal_str}  ({get_percentage_as_fitted_string(subcount, subtotal)}){subpost_string}"
        TermAct.Clear_Current_Line()
        print(s)
        s = post_string
        TermAct.Clear_Current_Line()
        print(s)
    except Exception as e:
        print("\n" * 20)
        print_exception_details(e)
        print("\n" * 20)
    if maincount == maintotal and (subcount == subtotal or subtotal == 0):
        print(TermAct.Show_Cursor(), end="")
    else:
        print(TermAct.Cursor_Up * 4 + "\r", end="")
