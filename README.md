# Grab Core Web Vitals - csv based

- Fresh Core Web Vitals data via Chrome User Experience Report API for a list of domains via csv
  - LCP, FID and CLS 75 percentiles
  - % of good experiences in % for LCP, FID and CLS
  - Did the origin pass the Core Web Vitals assessment = all 3 metrics above CWV threshold

## Example
python3 grab_cwv.py import.csv

## Output
cwvchecks.csv file, seperated by ";"

## About
Created this project to learn python
