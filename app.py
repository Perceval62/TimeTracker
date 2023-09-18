from flask import Flask, render_template, request, redirect, url_for
from io import StringIO

import datetime
import csv

app = Flask(__name__)

class TimesheetEntry:
    def __init__(self, task, start_time):
        self.task = task
        self.start_time = start_time
        self.end_time = None

    def stop(self):
        self.end_time = datetime.datetime.now()

    def get_duration(self):
        if self.end_time is None:
            return None
        return self.end_time - self.start_time

timesheet_entries = []
active_tasks = []  # List to store active tasks

@app.route('/')
def index():
    return render_template('index.html', active_tasks=active_tasks, timesheet_entries=timesheet_entries)

@app.route('/start', methods=['POST'])
def start_task():
    task = request.form['task']
    entry = TimesheetEntry(task, datetime.datetime.now())
    active_tasks.append(entry)  # Add the new task to active tasks
    return redirect(url_for('index'))

@app.route('/stop/<int:index>', methods=['POST'])
def stop_task(index):
    if index < len(active_tasks):
        entry = active_tasks[index]
        entry.stop()
        timesheet_entries.append(entry)  # Move the completed task to timesheet_entries
        del active_tasks[index]  # Remove the task from active tasks
    return redirect(url_for('index'))

@app.route('/exportcsv')
def export_csv():
    output = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(["Task", "Start Time", "End Time", "Duration"])

    for entry in timesheet_entries:
        duration = entry.get_duration()
        csv_writer.writerow([entry.task, entry.start_time, entry.end_time, duration])

    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Disposition': 'attachment; filename=timesheet.csv',
        'Content-Type': 'text/csv'
    }

if __name__ == "__main__":
    app.run(debug=False)