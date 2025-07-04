
# This is the list of pages the get_argument_dates program traverses to get the Washington State Court of Appeals, 
# Division 1, hearing schedule for 2024 and 2025. It captures the information I'm interested in, and writes the 
# information to standard output. The link to the 2024 and 2025 docket archive is here:
#
# https://www.courts.wa.gov/appellate_trial_courts/appellateDockets/index.cfm?fa=appellateDockets.showDateList&courtId=a01&archive=y&yr1=2025&yr2=2024
#
# Since I am only interested in a subset of the docket, I did not write code to traverse all the links in the 
# docket. Instead, I pasted links to the specific days' dockets I am interested in. If I decide I want more days'
# worth, I'll copy them to the oral_arguments array.
#
# For each day's docket, I pull out:
# - Case Number (Anchor case and consolidated cases if relevant)
# - Date of Consideration (I refer to this as oral arguments, but not all cases have oral arguments)
# - Whether the case has Oral argument or not
# - The judicial panel hearing the case (or considering it if no oral argument)
# - The case title
#

# The three links below encapsulate the variety of html layouts I've seen, so use them as test cases when
panel_dates = [
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240109",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240110",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240111",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240112",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240117",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240118",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240119",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240123",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240124",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240125",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240227",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240228",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240229",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240301",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240305",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240306",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240307",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240308",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240312",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240313",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240321",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240409",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240410",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240411",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240412",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240416",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240417",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240418",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240419",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240423",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240424",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240529",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240530",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240531",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240604",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240605",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240606",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240607",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240611",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240612",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240613",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240709",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240710",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240711",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240712",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240716",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240717",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240718",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240719",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240723",
    "https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240724",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240910",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240911",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240912",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240913",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240917",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240918",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240919",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240920",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240924",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20240925",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20241029",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20241030",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20241031",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20241101",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20241105",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20241106",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20241107",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20241108",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20241113",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2024&file=20241114",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250108",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250109",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250110",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250114",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250115",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250116",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250117",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250122",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250123",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250226",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250227",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250228",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250304",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250305",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250306",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250307",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250311",
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250312"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250313"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250321"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250409"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250410"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250411"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250412"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250416"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250417"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250418"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250419"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250423"
	"https://www.courts.wa.gov/appellate_trial_courts/appellatedockets/index.cfm?fa=appellatedockets.showDocket&folder=a01&year=2025&file=20250424"
]
