import pandas as pd
from pandas import DataFrame

#Ensure path below for tsv file is correct before running
redfin_data = pd.read_csv('county_market_tracker.tsv', sep='\t', header=0)

# Select only certin columns from original dataset to reduce size and complexity
redfin_data_selection = redfin_data[["period_begin", "period_end", "region", "table_id",
                                     "state", "median_sale_price", "median_list_price", "homes_sold",
                                     "pending_sales", "new_listings", "inventory", "avg_sale_to_list",
                                     "sold_above_list", "off_market_in_two_weeks"]]

#print("Original Datatypes", redfin_data_selection.dtypes)

redfin_data_selection[["period_begin", "period_end"]] = redfin_data_selection[["period_begin", "period_end"]].apply(pd.to_datetime)

#print("Converted Datatypes", redfin_data_selection.dtypes)

#  After team discussion, changed to only 2023 data
redfin_data_selection = redfin_data_selection[(redfin_data_selection["period_begin"] > "2023-01-01")]

redfin_data_selection["county"] = redfin_data_selection["region"].str.split(",").str[0]

redfin_data_selection["county"] = redfin_data_selection["county"].str.replace(" County", "")

#print(redfin_data_selection["county"][0:10])

redfin_data_selection_final = (redfin_data_selection.rename(columns={"state": "state_name", "county": "county_name"})
                               .reset_index(drop=True)).drop(columns=["region"])

# Ensure path is correct fow where to save csv file
redfin_data_selection_final.to_csv("redfin_filtered_data.csv", index=False, header=True)
