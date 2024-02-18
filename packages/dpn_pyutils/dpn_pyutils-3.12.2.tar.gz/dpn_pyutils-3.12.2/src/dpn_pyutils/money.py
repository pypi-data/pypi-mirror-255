def format_currency_market_display_float(
    value: float, currency_symbol: str = "$", suffix: str = ""
) -> str:
    """
    Formats a value according to conventional market display using floats.
    NOTE: Floats should not be used for calculation on currency amounts

    General conventions:
        Less than 0.000001 -> Show leading prefix "<", show leading minus, currency symbol, and literal "0.000001"
            E.g. <$0.000001 or <-$0.000001
        Between 0.000001 and 0.01 -> Show leading minus, show currency symbol, 6 decimal places
            E.g. $0.002895 or -$0.000690
        Between 0.01 and 0.99 -> Show leading minus, show currency symbol, 2 decimal places
        Between $1.00 and $999.99 -> Show 2 decimal places
        Between $1,000 and $999,999 -> Show leading minus, currency symbol, 2 decimal places and a 'K' suffix
        Between $1,000,000 and $999,999,999 -> Show leading minus, currency symbol, 1 decimal places, and 'M' suffix
        >$1,000,000,000 -> show leading minus, currency symbol, 1 decimal place, and 'B' suffix
        >$1,000,000,000,000 -> show leading minus, currency symbol, 1 decimal place, and 'T' suffix
    """

    value_opts = {
        "negative_qty": False if value >= 0 else True,
        "prefix": "",
        "currency_symbol": currency_symbol,
        "value": "",
        "summary_suffix": "",
        "suffix": suffix,
    }

    # Format Trillions
    if abs(value) >= float(1e12):
        chopped_value = value / 1e12
        value_opts["value"] = "{:.1f}".format(abs(chopped_value))
        value_opts["summary_suffix"] = "T"

    # Format Billions
    elif abs(value) >= float(1e9):
        chopped_value = value / 1e9
        value_opts["value"] = "{:.1f}".format(abs(chopped_value))
        value_opts["summary_suffix"] = "B"

    # Format Millions
    elif abs(value) >= float(1e6):
        chopped_value = value / float(1e6)
        value_opts["value"] = "{:.1f}".format(abs(chopped_value))
        value_opts["summary_suffix"] = "M"

    # Format Thousands
    elif abs(value) >= float(1e3):
        chopped_value = value / float(1e3)
        value_opts["value"] = "{:.2f}".format(abs(chopped_value))
        value_opts["summary_suffix"] = "k"

    # Format Fractional
    elif abs(value) > 0 and abs(value) < 1:
        # If the fractional value is greater than 0.01
        if abs(value) > float(1e-2):
            value_opts["value"] = "{:.2f}".format(abs(value))

        # If the fractional value is greater than 6 decimal places (i.e. >=0.000001)
        elif abs(value) > float(1e-6):
            # Due to python's formatting of values with lots of leading zeroes into scientific
            # notation, we need to we need to truncate
            value_opts["value"] = "{:.17f}".format(
                float("{:.6f}".format(abs(value)))
            ).rstrip("0")

        # If the fractional value is less than 6 decimal places (i.e. <0.000001)
        else:
            value_opts["prefix"] = "<"
            value_opts["value"] = "0.000001"

    # Format small numbers
    else:
        value_opts["value"] = "{:.2f}".format(abs(value))

    # Generate our formatted value
    formatted_value = "{}{}{}{}{}{}".format(
        value_opts["prefix"],
        "-" if value_opts["negative_qty"] else "",
        value_opts["currency_symbol"],
        value_opts["value"],
        value_opts["summary_suffix"],
        value_opts["suffix"],
    )

    return formatted_value
