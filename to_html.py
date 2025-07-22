#!/usr/bin/env python3
import sys
from datetime import datetime

# converts a text file generated from reconcile.py to an html file
# does not handle missing file/directory or ill-formatted file gracefully
def main():
    if len(sys.argv) != 4:
        print("Usage: to_html.py <source_file> <stat_file> <dest>")
        sys.exit(1)
    
    generate_html(sys.argv[1], sys.argv[2], sys.argv[3])
    

def generate_html(input_filename, stats, output_filename):
    # HTML header
    now = datetime.now()

    th_style = "pico-color-slate-500"
    html_output = """
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.colors.min.css">
        <title>Washington State Court of Appeals Opinions</title>
    </head>
    <body>
        <h1 id="top" style="text-align: center">Opinions from Washington State Court of Appeals, Division 1</h1>
        <h4 style="text-align: center">Since Jan 2024</h4>
        <a style="margin-left: .5rem; font-size: .75rem;" href="#stats">Go to stats</a><a style="margin-left: 1rem; font-size: .75rem;" href="./cases_waiting.html">Cases waiting opinion</a><br>
    """
    html_output += f"<span style='margin-left: .5rem; font-size: .75rem;'>Report ran on {now.strftime("%m/%d/%Y")} @ {now.strftime("%H:%M")}</span>"
    html_output += """
        <table border="1">
            <tr class="pico-background-slate-500">
                <th class="pico-background-slate-500">Case</th>
                <th class="pico-background-slate-500">Panel Date</th>
                <th class="pico-background-slate-500">Rel Date</th>
                <th class="pico-background-slate-500">Days</th>
                <th class="pico-background-slate-500">Orals</th>
                <th class="pico-background-slate-500">Opinion Type</th>
                <th class="pico-background-slate-500">Case Title</th>
            </tr>
    """
    
    elem_style = ""

    # Read the input file
    with open(input_filename, 'r') as file:
        for line in file:
            fields = line.strip().split('\t')
            case = fields[0]

            date_fields = fields[1].split('/')
            panel_date_link = f"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year={date_fields[2]}&file={date_fields[2]}{date_fields[0]}{date_fields[1]}"
            
            html_output += f"<tr>" 

            html_output += f'<td class="{elem_style}"><a href="https://www.courts.wa.gov/opinions/index.cfm?fa=opinions.showOpinion&filename={fields[0]}MAJ" target="_blank">{fields[0]}</a></td>'           
            html_output += f"<td class='{elem_style}'><a href='{panel_date_link}' target='_blank'>{fields[1]}</a></td>"
            html_output += f"<td class='{elem_style}'>{fields[2]}</td>"
            html_output += f"<td class='{elem_style}'>{fields[5]}</td>"
            html_output += f"<td class='{elem_style}'>{fields[3]}</td>"
            html_output += f"<td class='{elem_style}'>{fields[4]}</td>"
            html_output += f"<td class='{elem_style}'>{fields[6]}</td>"
            html_output += f"</tr>"
    
    # Close the HTML tags
    html_output += """
        </table>
        <h3 style="text-align: center">Some Stats</h2>
        <a style="margin-left: .5rem; font-size: .75rem;" href="#top">Go to top</a><br>
        <table id="stats" border="2">
    """

    with open(stats, 'r') as stats_file:
        for line in stats_file:
            fields = line.strip().split(':')
            html_output += f"<tr>"
            html_output += f"<td>{fields[0]}</td>"
            html_output += f"<td>{fields[1]}</td>"
            html_output += f"</tr>"
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
