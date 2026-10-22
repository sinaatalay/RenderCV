// Dates: formatting dates, date ranges, and time spans with the CV's locale.
//
// RenderCV sends dates as dictionaries: `(year: 2020, month: 5, day: none)`,
// `(present: true)`, or `(text: ...)` for free text such as "Fall 2023".
// `normalize-date` fills in the missing keys so looks can rely on them.

#import "rich.typ": rich

/// Fills in the keys of a date dictionary RenderCV sent.
///
/// - value (dictionary, none): The date.
/// -> dictionary, none
#let normalize-date(value) = {
  if value == none {
    return none
  }
  (
    year: value.at("year", default: none),
    month: value.at("month", default: none),
    day: value.at("day", default: none),
    present: value.at("present", default: false),
    text: rich(value.at("text", default: none)),
  )
}

/// The default way a date with a month is written: "Sept 2023".
///
/// - date (dictionary): A normalized date with a year and a month.
/// - locale (dictionary): The locale.
/// -> content
#let month-abbreviation-and-year(date, locale) = [#locale.month_abbreviations.at(date.month - 1) #date.year]

/// Writes a date: "Sept 2023", "2023", "present", or the date's free text.
///
/// - date (dictionary, none): A normalized date.
/// - locale (dictionary): The locale.
/// - format (function): `(date, locale) => content` for dates with a month.
/// -> content, none
#let format-date(date, locale, format: month-abbreviation-and-year) = {
  if date == none {
    return none
  }
  if date.present {
    return [#locale.present]
  }
  if date.text != none {
    return date.text
  }
  if date.month == none {
    return [#date.year]
  }
  format(date, locale)
}

/// Writes when something happened: a single date, or a start–end range.
///
/// A single `date` wins over a range. With only an end date, the end date is
/// the single date. With only a start date, the range is still ongoing.
///
/// - date (dictionary, none): A single date.
/// - start (dictionary, none): The start of a range.
/// - end (dictionary, none): The end of a range.
/// - locale (dictionary): The locale.
/// - format (function): How to write a date with a month.
/// - range (function): `(start, end) => content` joining two written dates.
/// -> content, none
#let format-dates(
  locale,
  date: none,
  start: none,
  end: none,
  format: month-abbreviation-and-year,
  range: (start, end) => [#start – #end],
) = {
  if date != none {
    return format-date(date, locale, format: format)
  }
  if start == none {
    return format-date(end, locale, format: format)
  }
  let end = if end == none { (year: none, month: none, day: none, present: true, text: none) } else { end }
  range(format-date(start, locale, format: format), format-date(end, locale, format: format))
}

/// Turns a normalized date into a Typst datetime. "present" becomes the
/// current date.
#let to-datetime(date, current-date) = {
  let date = if date.present { current-date } else { date }
  datetime(
    year: date.year,
    month: if date.month == none { 1 } else { date.month },
    day: if date.day == none { 1 } else { date.day },
  )
}

/// Writes how long something lasted: "3 years 4 months".
///
/// Returns `none` if either end is free text.
///
/// - start (dictionary): The start date.
/// - end (dictionary, none): The end date; `none` means ongoing.
/// - locale (dictionary): The locale.
/// - current-date (dictionary): The date "present" stands for.
/// -> str, none
#let format-time-span(start, end, locale, current-date) = {
  let end = if end == none { (year: none, month: none, day: none, present: true, text: none) } else { end }
  if start == none or start.text != none or end.text != none {
    return none
  }
  let current = normalize-date(current-date)
  let start-is-year = start.month == none
  let end-is-year = not end.present and end.month == none
  if start-is-year or end-is-year {
    let years = to-datetime(end, current).year() - to-datetime(start, current).year()
    return if years < 2 { "1 " + locale.year } else { str(years) + " " + locale.years }
  }
  let days = (to-datetime(end, current) - to-datetime(start, current)).days()
  let years = calc.floor(days / 365)
  let months = calc.floor(calc.rem(days, 365) / 30) + 1
  years += calc.floor(months / 12)
  months = calc.rem(months, 12)
  let parts = ()
  if years == 1 {
    parts.push("1 " + locale.year)
  } else if years > 1 {
    parts.push(str(years) + " " + locale.years)
  }
  if months == 1 {
    parts.push("1 " + locale.month)
  } else if months > 1 {
    parts.push(str(months) + " " + locale.months)
  }
  parts.join(" ")
}
