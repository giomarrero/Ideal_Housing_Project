import pandas as pd

# Ensure paths for redfin_merged_data.csv data is correct before running
merged_data = pd.read_csv("redfin_merged_data.csv", sep=",", header=0)

stats_data = (merged_data.groupby('fips', as_index=False)[['median_sale_price', 'inventory']].mean()
              .rename(columns={"median_sale_price": "avg_med_sale_price", "inventory": "avg_inventory"}))

# Drop null values for both columns
stats_data_clean = stats_data.dropna(subset=["avg_med_sale_price", "avg_inventory"])

# Ensure path is correct for where you would like to write your redfin_stats to
stats_data_clean.to_csv("redfin_stats.csv", index=False, header=True)