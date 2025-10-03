from datetime import datetime
import time
from astropy.io import ascii
from astropy.table import Table
from astropy.time import Time
import os
import numpy as np
import re
import http.server
import socketserver

def safe_to_jd(date_str):
    if str(date_str).strip().lower() == 'not found':
        return np.nan
    try:
        dt_obj = datetime.strptime(str(date_str), '%m/%d/%y %H:%M')
        time_obj = Time(dt_obj, scale='utc')
        return time_obj.jd
    except ValueError:
        return np.nan

def initialise():
    data = Table(ascii.read('out.csv'))
    date_column = data['time'].copy()
    jd_column = np.array([safe_to_jd(d) for d in date_column], dtype=float)
    data['time'] = jd_column
    data = data[~np.isnan(data['time'].data)]
    data.sort('time')
    return data

def get_candidates(table):
    nt = (Time.now().jd+1/24)+0
    base_idx = np.sum(table['time'] < nt) - 1
    
    candidates = {
        "now": table[base_idx] if base_idx < len(table) else None,
        "nxt": table[base_idx + 1] if base_idx + 1 < len(table) else None,
        "queue1": table[base_idx + 2] if base_idx + 2 < len(table) else None,
        "queue2": table[base_idx + 3] if base_idx + 3 < len(table) else None,
    }
    return candidates

def process_name(dur_id:str, pref_name:str):
    surname = re.search(r" (\S+)\s*$", dur_id).group(1).lower().capitalize()
    firstname = pref_name.rstrip().capitalize()
    return firstname+' '+surname

def generate_html(candidates):
    now = candidates["now"]
    nxt = candidates["nxt"]
    queue1 = candidates["queue1"]
    queue2 = candidates["queue2"]

    # SVG icons for reliability
    icons = {
        "email": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>""",
        "phone": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>""",
        "ensemble": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>""",
        "leadership": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>""",
        "doubling": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>""",
        "accessibility": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.46 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>""",
        "response": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>"""
    }

    def format_candidate(candidate, title):
        if not candidate:
            return f"<div class='card'><h2>{title}</h2><p class='placeholder'>No candidate information available.</p></div>"

        doubling_info = ''
        if candidate['doub'] != 'No':
            doubling_info = f"""
            <div class="info-row highlight">
                <span>{icons['doubling']}</span>
                <div>
                    <strong>Doubling on</strong>
                    <p>{candidate['doub']}</p>
                </div>
            </div>"""

        accessibility_info = ''
        if len(candidate['accessib']) > 1:
            accessibility_info = f"""
            <div class="info-row highlight">
                <span>{icons['accessibility']}</span>
                <div>
                    <strong>Accessibility Notes</strong>
                    <p>{candidate['accessib']}</p>
                </div>
            </div>"""
        
        response_info = ''
        if len(candidate['resp']) > 1:
            response_info = f"""
            <div class="info-row">
                <span>{icons['response']}</span>
                <div>
                    <strong>Response</strong>
                    <p>{candidate['resp']}</p>
                </div>
            </div>"""

        return f"""
        <div class="card">
            <h2>{title}</h2>
            <div class="candidate-main">
                <p class="name">{process_name(candidate['\ufeffdur_id'], candidate['pref_name'])}</p>
                <p class="instrument">{candidate['inst']}</p>
            </div>
            <div class="info-grid">
                <div class="info-row"><span>{icons['email']}</span><div><strong>Email</strong><p>{candidate['cisid']}</p></div></div>
                <div class="info-row"><span>{icons['phone']}</span><div><strong>Phone</strong><p>{candidate['phone']}</p></div></div>
                <div class="info-row"><span>{icons['ensemble']}</span><div><strong>Ensemble Preference</strong><p>{candidate['pref']}</p></div></div>
                <div class="info-row"><span>{icons['leadership']}</span><div><strong>Section Leadership?</strong><p>{candidate['sl']}</p></div></div>
                {doubling_info}
                {accessibility_info}
                {response_info}
            </div>
        </div>"""

    main_cards_html = format_candidate(now, "Current Candidate") + format_candidate(nxt, "Next Candidate")

    queue_html = ""
    if queue1:
        queue_html += f"""
        <div class="queue-item">
            <p class="name">{process_name(queue1['\ufeffdur_id'], queue1['pref_name'])}</p>
            <p class="instrument">{queue1['inst']}</p>
        </div>"""
    if queue2:
        queue_html += f"""
        <div class="queue-item">
            <p class="name">{process_name(queue2['\ufeffdur_id'], queue2['pref_name'])}</p>
            <p class="instrument">{queue2['inst']}</p>
        </div>"""
    
    if not queue_html:
        queue_html = "<p class='placeholder'>No further candidates in the queue.</p>"


    html = f"""
    <html>
    <head>
        <title>Who's Next</title>
        <meta http-equiv="refresh" content="60">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-color: #f4f7f9;
                --card-bg: #ffffff;
                --primary-text: #2c3e50;
                --secondary-text: #7f8c8d;
                --accent-color: #3498db;
                --border-color: #ecf0f1;
                --shadow: 0 4px 12px rgba(0,0,0,0.08);
            }}
            body {{
                font-family: 'Roboto', sans-serif;
                margin: 0;
                background-color: var(--bg-color);
                color: var(--primary-text);
                padding-bottom: 120px; /* Space for the queue footer */
            }}
            .container {{
                display: flex;
                gap: 40px;
                padding: 40px;
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                box-sizing: border-box;
            }}
            .card {{
                flex: 1;
                background-color: var(--card-bg);
                border-radius: 12px;
                box-shadow: var(--shadow);
                padding: 30px;
                transition: transform 0.2s ease-in-out;
                display: flex;
                flex-direction: column;
            }}
            .card:hover {{
                transform: translateY(-5px);
            }}
            h2 {{
                text-align: center;
                color: var(--accent-color);
                font-weight: 500;
                margin-top: 0;
                margin-bottom: 25px;
                font-size: 1.5em;
            }}
            .candidate-main {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .name {{
                font-size: 2.2em;
                font-weight: 700;
                margin: 0;
            }}
            .instrument {{
                font-size: 1.4em;
                color: var(--secondary-text);
                margin: 5px 0 0 0;
            }}
            .info-grid {{
                display: grid;
                gap: 20px;
            }}
            .info-row {{
                display: flex;
                align-items: flex-start;
                background-color: #fdfdfd;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid var(--border-color);
            }}
            .info-row span {{
                margin-right: 15px;
                margin-top: 3px;
                color: var(--secondary-text);
            }}
            .info-row div {{ flex: 1; }}
            .info-row strong {{
                font-weight: 500;
                color: var(--primary-text);
            }}
            .info-row p {{
                margin: 4px 0 0 0;
                color: var(--secondary-text);
                font-weight: 300;
                white-space: pre-wrap;
            }}
            .highlight {{
                background-color: #fffbe6;
                border-color: #ffe58f;
            }}
            .placeholder {{
                text-align: center;
                color: var(--secondary-text);
                padding: 20px;
            }}
            .queue-container {{
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background-color: var(--card-bg);
                box-shadow: 0 -4px 12px rgba(0,0,0,0.05);
                padding: 15px 40px;
                box-sizing: border-box;
                border-top: 1px solid var(--border-color);
            }}
            .queue-header {{
                text-align: center;
                font-weight: 500;
                color: var(--secondary-text);
                margin: 0 0 10px 0;
                font-size: 1.1em;
            }}
            .queue-list {{
                display: flex;
                justify-content: center;
                gap: 40px;
            }}
            .queue-item .name {{
                font-size: 1.1em;
                font-weight: 500;
            }}
            .queue-item .instrument {{
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {main_cards_html}
        </div>
        <div class="queue-container">
            <p class="queue-header">Up Next</p>
            <div class="queue-list">
                {queue_html}
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    PORT = 8000
    table = initialise()

    class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            candidates = get_candidates(table)
            html = generate_html(candidates)
            
            self.wfile.write(bytes(html, "utf8"))
            return

    Handler = MyHttpRequestHandler
    with socketserver.TCPServer(("localhost", PORT), Handler) as httpd:
        print("serving at port", PORT)
        print("Open http://localhost:8000 in your browser")
        httpd.serve_forever()
    




