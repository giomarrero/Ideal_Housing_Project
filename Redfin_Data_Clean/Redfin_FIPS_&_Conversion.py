import pandas as pd

# Ensure paths for Redfin and FIPS data are correct
rf_data = pd.read_csv("redfin_filtered_data.csv", sep=",", header=0)
fips_data = pd.read_csv("county_fips_master.csv", sep=",", header=0, encoding = "ISO-8859-1")


fips_data["county_name"] = fips_data["county_name"].str.replace(" County", "")

fips_data = fips_data.drop(columns=["state_abbr", "long_name", "sumlev", "region",
                                    "division", "state", "county", "crosswalk", "region_name", "division_name"])
# Explore Data
#print(rf_data.head(10))
#print(fips_data.head(10))

merged_data = pd.merge(rf_data, fips_data, how="outer", on=["state_name", "county_name"])
merged_data = merged_data.drop(columns=["table_id"])
merged_data = merged_data[merged_data['fips'].notna()]
merged_data["fips"] = merged_data["fips"].astype("int")

merged_data["fips"] = merged_data["fips"].astype("str").apply(lambda x: x.zfill(5))

merged_data.to_csv("redfin_merged_data.csv", index=False, header=True)
