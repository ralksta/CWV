# Grab Core Web Vitals

Takes a CSV file with domains as input, grabs via CRUX API the Core Web Vitals and writes them to an output.csv


## Example
python3 grab_cwv.py import.csv


## Output
cwvchecks.csv file, seperated by ";"

Content: Domain, Core Web Vitals passed, Date, LCP, FID, CLS
