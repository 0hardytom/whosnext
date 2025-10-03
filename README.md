# Who's Next

A simple tool to display the current and next candidates in a queue, either in a web browser or in the shell.

## Description

This project provides two Python scripts to manage and display a queue of candidates from a CSV file named `out.csv`. It's designed to be a simple solution for keeping track of who is currently up and who is next in line, for example, in an audition or interview setting.

The information is displayed in one of two ways:

1.  **Web Interface (`whosnext.py`):** A clean and auto-refreshing web page that shows the current and next candidates, along with a queue of the two candidates after that.
2.  **Shell Output (`whosnext_shell.py`):** A command-line interface that prints the information for the current and next candidates and refreshes every 60 seconds.

## Usage

### Prerequisites

- Python 3
- The following Python libraries: `astropy`, `numpy`. You can install them using pip:
  ```bash
  pip install astropy numpy
  ```

### Data File

Both scripts require a CSV file named `out.csv` to be present in the same directory. The CSV file should have the following columns:

- `time`: The date and time of the appointment (e.g., `10/27/24 14:30`).
- `dur_id`: A unique identifier for the candidate, which includes their surname.
- `pref_name`: The candidate's preferred first name.
- `cisid`: The candidate's email address.
- `phone`: The candidate's phone number.
- `inst`: The instrument or role they are auditioning for.
- `doub`: Any secondary instrument or role.
- `pref`: Ensemble preference.
- `sl`: Section leadership interest.
- `accessib`: Accessibility notes.
- `resp`: Additional responses or notes.

### Running the Web Interface

To start the web server, run the following command:

```bash
python whosnext.py
```

Then, open your web browser and navigate to `http://localhost:8000`. The page will automatically refresh every 60 seconds.

### Running the Shell Interface

To display the information in your shell, run the following command:

```bash
python whosnext_shell.py
```

The script will print the information for the current and next candidates to the console and will refresh every 60 seconds.