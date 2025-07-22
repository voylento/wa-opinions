#!/usr/bin/env python3
import sys
from datetime import datetime, date
from dat import settledcases

# converts a text file generated from reconcile.py to an html file
# does not handle missing file/directory or ill-formatted file gracefully
def main():
    if len(sys.argv) != 3:
        print("Usage: to_html.py <sourcefile> <dest>")
        sys.exit(1)
    
    generate_html(sys.argv[1], sys.argv[2])
    

def generate_html(input_filename, output_filename):
    now = datetime.now()
   # HTML header
    th_style = "pico-color-slate-500"
    html_output = """
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.colors.min.css">
        <title>Cases Awaiting Opinion</title>
    </head>
    <body>
        <h1 style="text-align: center">Awaiting Opinion, WA State Court of Appeals, Div 1</h1>
        <a style="margin-left: .5rem; font-size: .75rem;" href="./cases_decided.html">Cases decided</a><br>
    """
    html_output += f"<span style='margin-left: .5rem;'><small>Report ran on {now.strftime('%m/%d/%Y')} @ {now.strftime('%H:%M')}</small></span>"
    html_output += """
            <table border="1">
            <tr class="pico-background-slate-500">
                <th class="pico-background-slate-500">Case</th>
                <th class="pico-background-slate-500">Panel Date</th>
                <th class="pico-background-slate-500">Days</th>
                <th class="pico-background-slate-500">Orals</th>
                <th class="pico-background-slate-500">Panel</th>
                <th class="pico-background-slate-500">Case Title</th>
            </tr>
    """
    
    elem_style = ""

    # Read the input file
    with open(input_filename, 'r') as file:
        for line in file:
            fields = line.strip().split('\t')
            # don't include cases that were settled after consideration, or disposed of for other reasons
            if fields[0] in settledcases.settled_cases:
                continue
            date_format = "%m/%d/%Y"
            date = datetime.strptime(fields[1], date_format)
            today = date.today()
            
            # schedule includes dates in the future
            if date > today:
                continue
            days = abs((today - date).days)
            elem_style = ""

            date_fields = fields[1].split('/')
            panel_date_link = f"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year={date_fields[2]}&file={date_fields[2]}{date_fields[0]}{date_fields[1]}"
            
            html_output += f"<tr>" 

            html_output += f'<td class="{elem_style}">{fields[0]}</td>'
            html_output += f"<td class='{elem_style}'><a href='{panel_date_link}' target='_blank'>{fields[1]}</a></td>"
            html_output += f"<td class='{elem_style}'>{days}</td>"
            html_output += f"<td class='{elem_style}'>{fields[2]}</td>"
            html_output += f"<td class='{elem_style}'>{fields[3]}</td>"
            html_output += f"<td class='{elem_style}'>{fields[4]}</td>"
            html_output += f"</tr>"
    
    # Close the HTML tags
    html_output += """
        </table>
    </body>
    </html>
    """
    
    # Write the output to an HTML file
    with open(output_filename, 'w') as output_file:
        output_file.write(html_output)


if __name__ == "__main__":
    main()
