import os
import sqlite3
import commands.calendrier.errors as errors
import datetime as dt
import calendar
from html2image import Html2Image

path = os.getcwd()

c = calendar.HTMLCalendar(calendar.MONDAY)
css = """
        body {
            background: white;
            font-family: "Lucida Console", monospace;
            font-weight: normal;
            font-style: normal;
        }
        table {
            border: none;
            cellpadding: 20;
            cellspacing: 2;
        }
        .month {
            border: none;
        }
        li {
            /* Text color */
            list-style-type: none;
        }
        li:before {
            /* Unicode bullet symbol */
            content: '\\2022';
            /* Bullet color */
            color: yellow;
        }
        th, td {border-radius: 15%;}
        td {text-align: center;}
        .mon, .tue, .wed, .thu, .fri {background: #67e3e7;}
        .sat, .sun, .noday {background: grey;}
        .today {background: #ff3535;}
    """


def today_css(cal: str, current_day: int) -> str:
    """Function used to modify the css class of the current day.

    Args:
        `cal`(str): the html calendar to transform.
        `current_day`(int): the current day to select the current week.

    Returns:
        `str`: the calendar transformed.
    """
    lines = cal.splitlines()
    w = "" # string to store the line of the current week
    i = 0 # index of the lines
    for line in lines: # check each lines for the current day
        if line.__contains__(f">{current_day}<"):
            w = line
            i += 1
            break
        i += 1
    ## change the css class of the current day in "today" ##
    days = w.split("=")
    target = ""
    for day in days:
        if day.__contains__(f">{current_day}<"):
            target = day
    day_name = target.split('"')[1]
    new_line = w.replace(day_name, "today")
    ## replace the line with the new one ##
    lines.remove(w)
    lines.insert(i-1, new_line)
    ## build the new calendar ##
    new_cal = ""
    for line in lines:
        new_cal = new_cal + line + "\n"
    return new_cal


def format_cal(cal: str) -> str:
    """Function used to format and make the calendar look better.

    Args:
        `cal`(str): a calendar in HTML format.
    Returns:
        `str`: the calendar formatted.
    """
    html = cal.replace(
    "<table border=\"0\" cellpadding=\"0\" cellspacing=\"0\" class=\"month\">",
    "<table border=\"1\" cellpadding=\"20\" cellspacing=\"2\" class=\"month\">"
    )
    head = "<body>" 
    foot = "</body>"
    html = html.join([head, foot])
    return html


def week_cal(cal: str, current_day: int) -> str:
    """Function used to transform a HTML month calendar into a week calendar.

    Args:
        `cal`(str): the html calendar to transform.
        `current_day`(int): the current day to select the current week.

    Returns:
        `str`: the calendar transformed.
    """
    lines = cal.splitlines()
    w = "" # string to store the line of the desired week
    for line in lines: # check each lines for the current day
        if line.__contains__(f">{current_day}<"):
            w = line
    ## build the week calendar ##
    new_cal = lines[0] + "\n" + lines[1] + "\n" + lines[2] + "\n" + w + "\n" + lines[-1]
    return new_cal


def day_cal(cal: str, current_day: int) -> str:
    """Function used to transform a HTML month calendar into a day calendar.

    Args:
        `cal`(str): the html calendar to transform.
        `current_day`(int): the current day to select the current week.

    Returns:
        `str`: the calendar transformed.
    """
    cal = week_cal(cal, current_day)
    lines = cal.splitlines()
    ## retrieve needed information ##
    for line in lines: # check each lines for the current day
        if line.__contains__(f">{current_day}<"):
            w = line
    days = w.split("=")
    target = ""
    for day in days: # check each day for the current day
        if day.__contains__(f">{current_day}<"):
            target = day
    day_name = target.split('"')[1]
    ## build the daily calendar ##
    new_cal = lines[0] + "\n" + lines[1] + "\n" + f"<tr><th class=\"{day_name}"
    new_cal += f"\">{day_name.capitalize()}</th></tr>" + "\n"
    new_cal += f"<tr><td class=\"{day_name}\">{current_day}</td></tr>" + "\n"
    new_cal += "</table>"
    return new_cal


def user_events(cal: str, mm: int, uid: str) -> str:
    """Function used to add user events to the final calendar. 

    Args:
        `cal`(str): the final calendar to edit.
        `mm`(int): the current month.
        `uid`(str): discord user id.

    Returns:
        `str`: the edited calendar.
    """
    ## retrieve events ##
    connection = connection = sqlite3.connect("assets/db/calendar.db")
    cursor = connection.cursor()
    #TODO: simplifier la requêtes pour avoir seulement la date
    cursor.execute("""
        SELECT events.name, events.desc, events.date, events.time,
        events.server_id FROM events JOIN u_to_e ON events.id = u_to_e.event_id
        JOIN users ON users.uid = u_to_e.uid
        WHERE users.uid = (?);""", (uid,))
    events = cursor.fetchall()
    connection.close()
    ## affect the event to the correct day ##
    day_checked = []
    for event in events:
        date = event[2]
        month = int(date.split("-")[1])
        if month == mm:
            j = date.split("-")[0]
            if j not in day_checked:
                # check if the day is in the calendar
                start_ind = cal.find(f">{j}")
                if start_ind != -1:
                    # add the dot to the desired day
                    split = cal.split(f">{j}")
                    new_cal = split[0] + f">{j}" + "<li></li>" + split[1]
                    cal = new_cal
                    # to prevent adding multiple dot to the same day
                    day_checked += [j]
    return cal


def gen_cal(format: str, file_name: str, uid: str) -> None:
    """Function to generate an HTML Calendar and then transform it into an image (png).

    Args:
        `format`(str): should be `"day"` or `"week"` or `"month"` according to the
                        format needed.
        `file_name`(str): the name of the file which will be generated.
        `uid` (str): Discord user id to retrieve events info from db.
    """
    ## Check if the argument is correct ##
    if format != "day" and format != "week" and format != "month":
        raise errors.IncorrectFormat(format)
    ## Retrieve current date ##
    current_date = dt.datetime.now().date()
    yyyy = int(str(current_date).split("-")[0])
    mm = int(str(current_date).split("-")[1])
    dd = int(str(current_date).split("-")[2])
    ## Generate calendar ##
    month_cal = c.formatmonth(yyyy, mm)
    ## Transform calendar into the desired one ##
    if format == "month":
        cal = month_cal
    elif format == "week":
        cal = week_cal(month_cal, dd)
    elif format == "day":
        cal = day_cal(month_cal, dd)
    ## Format calendar ##
    cal = format_cal(cal)
    cal = today_css(cal, dd)
    cal = user_events(cal, mm, uid)
    # Calendar image generation ##
    hti = Html2Image(size=(535,455), # 515,455
        output_path=f'{path}\\commands\\calendrier\\generated')
    # name = str(dt.datetime.now().date())
    hti.screenshot(html_str=cal, css_str=css, save_as=file_name)