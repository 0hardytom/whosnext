import datetime
import time
from astropy.io import ascii
import os

# Set the working directory to the location of the script
# This makes sure the script can find the CSV file
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Read the CSV file into an astropy table
try:
    data = ascii.read('out.csv')
except FileNotFoundError:
    print("Error: out.csv not found. Please make sure the file is in the same directory as the script.")
    exit()

# Sort the data by time to ensure we process it chronologically
data.sort('time')

def generate_html():
    # Get the current time
    now = datetime.datetime.now()
    current_time = now.time()

    # Find the row that corresponds to the current time slot
    matching_row = None
    for row in data:
        # Convert the time string from the CSV into a time object
        slot_time = datetime.datetime.strptime(row['time'], '%H:%M').time()
        # If the slot time is before or at the current time, it's the current one
        if slot_time <= current_time:
            matching_row = row
        # Since the list is sorted, the first time we find that is *after*
        # the current time, we can stop looking.
        else:
            break

    # Generate the HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="1">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Current Information</title>
        <style>
            body { font-family: sans-serif; margin: 2em; }
            .container { border: 1px solid #ccc; padding: 2em; border-radius: 8px; }
            .dur_id { font-size: 4em; font-weight: bold; margin: 0; }
            .pref_name { font-size: 1.5em; margin-top: 0; }
            .info { margin-top: 1em; }
            .time { position: absolute; top: 1em; right: 1em; font-family: monospace; }
            p { margin-top: 1em; }
        </style>
    </head>
    <body>
    """

    html_content += f'<div class="time">Current Time: {now.strftime("%Y-%m-%d %H:%M:%S")}</div>'
    html_content += '<div class="container">'

    if matching_row:
        html_content += f'<h1 class="dur_id">{matching_row["dur_id"]}</h1>'
        html_content += f'<h2 class="pref_name">{matching_row["pref_name"]}</h2>'
        html_content += '<div class="info">'
        html_content += f'<b>Phone:</b> {matching_row["phone"]}<br>'
        html_content += f'<b>Instrument:</b> {matching_row["inst"]}<br>'
        html_content += f'<b>Double:</b> {matching_row["doub"]}<br>'
        html_content += '</div>'
        html_content += f'<p>{matching_row["resp"]}</p>'
        html_content += f'<p>{matching_row["accessib"]}</p>'
    else:
        html_content += '<h1>No information for the current time slot.</h1>'

    html_content += """
    </div>
    </body>
    </html>
    """

    # Write the HTML content to a file
    with open('index.html', 'w') as f:
        f.write(html_content)

    print(f"Successfully generated index.html at {datetime.datetime.now()}")

if __name__ == '__main__':
    while True:
        generate_html()
        time.sleep(1)