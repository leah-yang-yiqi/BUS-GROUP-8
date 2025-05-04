import os
from uuid import uuid4

from flask import render_template, redirect, url_for, flash, send_file, send_from_directory
from werkzeug.utils import secure_filename
from wtforms.fields.choices import SelectField

from app import app
from app.forms import ChooseForm, SelectForm, CSVUploadForm
import csv
import io

@app.route("/")
def home():
    return render_template('home.html', title="Home")


@app.route("/timeslot/<day>/<hour>/<item>")
def timeslot(day,hour,item):
    list=[]
    try:
        day=int(day)
        hour=int(hour)
        if day<1 or day>5:
            flash("Invalid day, it outside the range 1-5",'error')
            return redirect(url_for("home.html"))
        if hour<9 or hour>17:
            flash("Invalid hour, it outside the range 9-17", 'error')
            return redirect(url_for("home.html"))

        list=[day,hour,item]
        print(day)
        return render_template("calendar.html",title='My Calendar',list=list,day=day
                               ,hour=hour,item=item)
    except ValueError:
        flash("Invalid input", "error")
        return redirect(url_for('home'))

@app.route("/display_calendar")
def display_calendar():
    form=SelectForm()
    if form.validate_on_submit():
        day=form.day.data
        hour=form.hour.data
        item=form.item.data
        if day=='Monday':
            day=1
        elif day=='Tuesday':
            day=2
        elif day=='Wednesday':
            day=3
        elif day=='Thursday':
            day=4
        elif day=='Friday':
            day=5
        else:
            flash("Invalid choice", 'error')
            return redirect(url_for("home.html"))
        return render_template("calendar.html",title='My calendar',day=day,hour=hour,item=item)


def is_valid_day(day):
    if day < 1 or day > 5:
        return None
    return day


def is_valid_hour(hour):
    if hour<9 or hour>17:
        return None
    return hour


@app.route('/upload_slots', methods=['GET', 'POST'])
def upload_csv_file():

    global contacts
    contacts = []


    form =CSVUploadForm()
    if form.validate_on_submit():
        if form.file.data:
            unique_str = str(uuid4())
            filename = secure_filename(f'{unique_str}-{form.file.data.filename}')
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.file.data.save(filepath)
            try:
                with open(filepath, newline='') as csvFile:
                    reader = csv.reader(csvFile)
                    error_count = 0
                    header_row = next(reader)
                    if header_row != ['Day','Hour','Item']:
                        form.file.errors.append(
                            'First row of file must be a Header row containing "Day,Hour,Item"')
                        raise ValueError()
                    contacts.append(header_row)
                    for idx, row in enumerate(reader):
                        row_num = idx + 2
                        if error_count > 10:
                            form.file.errors.append('Too many errors found, any further errors omitted')
                            raise ValueError()
                        if len(row) != 3:
                            form.file.errors.append(f'Row {row_num} does not have exactly 3 fields')
                            error_count += 1
                            continue
                        if any(len(cell.strip()) == 0 for cell in row):
                            form.file.errors.append(f'Row {row_num} has empty fields')
                            error_count += 1
                            continue
                        if not is_valid_day(row[0]):
                            form.file.errors.append(f'Row {row_num} has an invalid day: "{row[0]}"')
                        if not is_valid_hour(row[1]):
                                form.file.errors.append(f'Row {row_num} has an invalid hour: "{row[1]}"')
                        item_data=row[2]
                        if item_data==None:
                            form.file.errors.append(f'Row {row_num} has an empty items')

                if error_count > 0:
                    raise ValueError

                return render_template('home.html', title='Home' )
            except Exception as err:
                flash(f'File upload failed. Please correct your file and try again', 'danger')
                app.logger.error(f'Exception occurred: {err=}')

    return render_template('upload_file.html', title='Upload CSV File', form=form)


@app.route('/download_csv', methods=['GET', 'POST'])
def download_csv():



# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403

# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404

@app.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413

# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500