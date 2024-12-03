from flask import Flask, jsonify, render_template, request
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from filter_chloro_counties_by_state import filter_chloro_counties
from filter_chloro_states_by_state import filter_chloro_states
from convert_state_abbrev import get_state_name
from reset_map_on_reload import reset_nation

app = Flask(__name__)


# Read in redfin_merged_data, which was created on local computer using files in Redfin_Data_Clean folder
df_redfin = pd.read_csv("static/redfin_merged_data.csv")
df_redfin_2 = df_redfin[["state_name", "county_name", "fips","median_sale_price","inventory"]]


#unique_FIPS = pd.DataFrame(pd.unique(df_redfin["fips"]), columns=["fips"])
# Map economic median sale price to FIPS
unique_FIPS = df_redfin_2.drop_duplicates(subset=["fips"]).reset_index(drop=True)
unique_FIPS["fips"] = unique_FIPS["fips"].astype("str").apply(lambda x: x.zfill(5))
unique_FIPS=unique_FIPS.rename(columns={'median_sale_price':'median_price'})

# Calculate overall scores
score_df = pd.read_csv('static/scores_combined.csv')


#grouping factors from data into 7 groups
economic=['Economic_Capital_Investment_Score',
       'Economic_Consumption_Score', 'Economic_Employment_Score',
       'Economic_Finance_Score', 'Economic_Innovation_Score',
       'Economic_Production_Score', 'Economic_Re_Distribution_Score']
ecosystem=['Ecosystem_Air_Quality_Score',
       'Ecosystem_Food__Fiber_and_Fuel_Provisioning_Score',
       'Ecosystem_Greenspace_Score', 'Ecosystem_Water_Quality_Score',
       'Ecosystem_Water_Quantity_Score']
education=['EDU_BE_Score', 'EDU_PA_Score',
       'EDU_SED_Score']
health=['HEA_HC_Score', 'HEA_LEM_Score', 'HEA_LB_Score',
       'HEA_PWB_Score', 'HEA_PMHC_Score']
living_standards=['LST_BN_Score', 'LST_INC_Score',
       'LST_WEA_Score', 'LST_WRK_Score']
safety=['SAS_ACTS_Score', 'SAS_PERS_Score',
       'SAS_RISK_Score']
nature=['C2N_Bio_Score',
       'CF_AP_Score']

#calculate mean of these columns and insert into separtate factor columns (equivalent to overall scores calculated above)
score_df['economic_factors']=score_df[economic].mean(axis=1)
score_df['ecosystem_factors']=score_df[ecosystem].mean(axis=1)
score_df['education_factors']=score_df[education].mean(axis=1)
score_df['health_factors']=score_df[health].mean(axis=1)
score_df['living_standards_factors']=score_df[living_standards].mean(axis=1)
score_df['safety_factors']=score_df[safety].mean(axis=1)
score_df['nature_factors']=score_df[nature].mean(axis=1)
factor_cons_df=score_df[['FIPS','County','State','economic_factors','ecosystem_factors','education_factors','health_factors',
                        'living_standards_factors','safety_factors','nature_factors']]
factor_cons_df=factor_cons_df.rename(columns={"FIPS":"fips","County":"county_name","State":"state_name"})
factor_cons_df['fips']=factor_cons_df['fips'].astype("str").apply(lambda x: x.zfill(5))

#Kmeans clustering model
X=factor_cons_df[['economic_factors','ecosystem_factors','education_factors','health_factors',
                        'living_standards_factors','safety_factors','nature_factors']].to_numpy()
kmeans_final=KMeans(n_clusters=10,random_state=0)
kmeans_final.fit(X)
labels=kmeans_final.labels_
factor_cons_df["well_being"]=labels

#merge reduced factor and cluster dataframe with redfin data
factors=factor_cons_df.merge(unique_FIPS, how='left', on='fips',suffixes=('','_right'))
factors=factors.drop(columns=['county_name_right','state_name_right'])

#Merge with redfin data stats for average sale price for 2023 and average inventory for 2023
redfin_stats = pd.read_csv("static/redfin_stats.csv")
redfin_stats['fips']=redfin_stats['fips'].astype("str").apply(lambda x: x.zfill(5))

factors_2 = factors.merge(redfin_stats, how='left', on='fips')
factors_2.avg_med_sale_price = factors_2.avg_med_sale_price.round()
factors_2.avg_inventory = factors_2.avg_inventory.round()

@app.route('/')
def index():
    reset_nation()
    fips_test_data = factors_2.to_dict("records")
    return render_template('index.html', test_data = fips_test_data)


@app.route('/input', methods=['POST'])
def input():
    ''''This is where all the POST data is being collected from the drop downs and text field'''
    init_features = [x for x in request.form.values()]
    budget=float(init_features[7])

    # Place Clustering Algo Here using init_features input!!
    percentile_dict = {"1":0.0,"2":0.25,"3":0.5,"4":0.75,"5":1.0}


    # synthetic county scores for predicting user cluster
    q_health = percentile_dict[request.form["Health"]]
    q_livingstandards = percentile_dict[request.form["LivingStandards"]]
    q_education = percentile_dict[request.form["Education"]]
    q_safety = percentile_dict[request.form["Safety"]]
    q_economic = percentile_dict[request.form["Economic"]]
    q_ecosystem = percentile_dict[request.form["Ecosystem"]]
    q_nature = percentile_dict[request.form["Nature"]]
    syn_health_score = score_df['health_factors'].quantile(q_health)
    syn_livingstandards_score = score_df['living_standards_factors'].quantile(q_livingstandards)
    syn_education_score = score_df['education_factors'].quantile(q_education)
    syn_safety_score = score_df['safety_factors'].quantile(q_safety)
    syn_economic_score = score_df['economic_factors'].quantile(q_economic)
    syn_ecosystem_score = score_df['ecosystem_factors'].quantile(q_ecosystem)
    syn_nature_score = score_df['nature_factors'].quantile(q_nature)
    filt_state_abbrev = request.form["state"]
    filt_state = get_state_name(filt_state_abbrev)
    
    #Filter geojson files by selected states
    if filt_state:
        if filt_state != "optional":
            state_fips = set((score_df[score_df["State"]==filt_state]["FIPS"]))
        else:
            state_fips = "all"
        
        filter_chloro_states(filt_state)
        filter_chloro_counties(state_fips)

    #Predict Cluster Using Model
    pred_array=np.array([syn_economic_score,syn_ecosystem_score,syn_education_score,syn_health_score,syn_livingstandards_score,syn_safety_score,syn_nature_score]).reshape(1,-1)
    pred=kmeans_final.predict(pred_array)
    predicted_cluster=pred[0] 

    #filter counties based on cluster and budget
    clustered_df=factors_2[(factors_2['well_being']==predicted_cluster)&(factors_2['avg_med_sale_price']<=budget)]

    #filter counties if there is specified state
    if filt_state != "optional":
        clustered_df=clustered_df[clustered_df['state_name']==filt_state]


    #pass in new reduced dataset to ui
    fips_test_data_user = clustered_df.to_dict("records")


    return render_template('index.html', test_data=fips_test_data_user, previous_query = init_features)

if __name__ == '__main__':
    app.run(debug=True, port =5000)
