DESCRIPTION - Describe the package in a few paragraphs

	The app.py file is where the flask app is initiated. It also reads in several datasets from the static folder including (redfin_merged_data.csv, redfin_stats.csv, scores_combined.csv), generates the clustering results and calls several functions from other python files to manage the data that is used in the rendering of the choropleth map. Four function files are called from the app.py file. These include:

	- convert_state_abbrev.py- This file contains the function to convert state abbreviations to state names
	- filter_chloro_counties_by_state.py- contains a function that filters the us_counties.json file on the FIPS ids that are within the specified state
	- filter_chloro_states_by_state.py- contains a function that filters the us_states.json file on the specified state
	- reset_map_on_reload.py- contains a function that resets the us_states and us_counties geojson files to the original files containing all states and counties
	
	The static folder contains all of the static files used in the flask app. The js subfolder contains choropleth_map.js which uses D3 to generate a map of the United States (or a particular state) and its counties along with a line chart that is generated on a click events on a county that displays a historical view of the median home sale price for the county for the last year. The counties on the map are colored based on the results of the well-being score clustering that occurs within the app.py file. The static folder contains all of the .csv files that contain the teams preprocessed data. These files include:
		
	- scores_combined.csv (obtained via the steps outlined in Dataset Requirements for EPA Wellbeing Data outlined below)
	- redfin_stats.csv (average median sale price and average inventory for 2023)
	- redfin_merged_data.csv (market data used when filtering counties and for providing median home prices and housing availability) 
	- unique_FIPS_data.csv (unique mapping of FIPS to county)
		
	It also contains 4 files (us-counties_original.json, us-states_original.json, us-counties.json and us-states.json). us-counties_original.json and us-states_original.json are geoJSON files containing the geometry for all US counties and states respectively, they can be used to revert the us_counties.json and us-states.json geoJSON files which contain the geometries that are rendered within the choropleth. These files are not truly static but rather change based on user-input and can contain all state/county geometries or a specific state and its counties geometries. Additionally, a styles.css file is include in this folder providing styling for the projects html. 
		
	The templates folder contains the index.html file which is used to construct our user interface and the styling is largely specified within the styles.css file. This file contains the user form and calls to 		choropleth.js to render the D3 graphics. It also contains all of the necessary imports for Bootstrap.

	Supplementary files have been included within the data-processing folder. These include:

	- Redfin_Data_Open.py  (reads in .TSV file downloaded from Redfin.com)
	- Redfin_FIPS_&_Conversion.py (@ NICK SEAGER county_fips_master.csv?)
	- parsewellbeingfiles.py (used to aggregate the JSON well-being data gathered from the EPA API into a singular csv file)
	

cluster_data.csv - supplementary file (REMOVE- Generated early on for clustering development)
zip_fip.csv - supplementary file (REMOVE- I don’t think this ended up getting used, had developed from USPS dataset)

		
INSTALLATION - How to install and setup your code

	The required folder structure is already provided in our submitted code. The following packages are required to be installed prior to moving on to the execution of a demo of our application.

	flask installation
		https://flask.palletsprojects.com/en/3.0.x/installation/
		
	pandas installation
		https://pandas.pydata.org/docs/getting_started/install.html

	simplejson installation
		https://pypi.org/project/simplejson/

	sci-kit learn installation
		https://scikit-learn.org/stable/install.html


EXECUTION - How to run a demo on your code

	Dataset requirements-
		
		Two datasets are required for this application to function. The first of which is a subset of the publicly available Redfin housing market dataset. The median monthly cost is required at a county level. The second dataset is a subset of EPA well-being data at a county level. This required dataset is only accessible via a series of web based API calls of restricted length resulting in JSON files that can be aggregated into a comprehensive dataset. Postman can be used to facilitate the API calls. 

		-Redfin Dataset 
			Downloadable (https://www.redfin.com/news/data-center/)
			Additional processing.
			Pass downloaded .tsv file through Redfin_Data_Open.py and Redfin_FIPS_&_Conversion.py (@NICK SEAGER)
				

		- EPA Wellbeing Dataset- 
			Series of manual API calls via postman (aggregated csv file included as part of submission) (https://gispub.epa.gov/arcgis/rest/services/ORD/HumanWellBeingIndex/MapServer)
			If it is desired to recreate the process of collecting the dataset.
				1. Go to https://gispub.epa.gov/arcgis/rest/services/ORD/HumanWellBeingIndex/MapServer
				2. Click on desired score metric/layer (ex. Health Overall Score)
				3. Scroll to the bottom of the page.
				4. Make note of available fields in the score page that you want included as output in your query (ex. Domain_Score, County, State)
				5. Select “Query” at the bottom of the page
				6. A query form will pop up allowing you to enter your desired criteria. (Ex. Where: Domain_Score > 0, Out Fields: Domain_Score, County, State)
				7. Set return geometry to False
				8. Set format to  JSON.
				9. Copy the url and go to Postman (https://www.postman.com/ - sign up for a free account if needed)
				10. Paste the url into the GET Rest API under “My Workspace -> Collections”
				11. Click Send. 
				12. View the json results in the Body at the bottom of the screen. 
				13. Click the three horizontal dots to the upper right of the displayed results and click “save response to file”, saving the results to a .txt file. Update the extension from .txt to .json. 
				14. Update the Params so that the resultOffset is 1000 and then click Send. This will allow the next 1000 counties to be included in the results and repeat step 13.
				15. Repeat step 14 for a result offset of 2000 and 3000 saving the file each time.
				16. Return to step 1 and repeat the process for the other desired metrics.
				17. Once all desired API calls have been completed, proceed to using the code included “parsewellbeingfiles.py” to read in the JSON files and aggregate them into a singular csv. 
				18. Save the file within the static folder in the provided file tree as scores_combined.csv. 

	
	Running the Flask application:
		Do not proceed unless all data is available locally to your machine and all package installations have been complete.
			1. Open up downloaded directory of files provided
			2. Open terminal in your IDE
			3. Navigate in terminal to the directory containing app.py within the downloaded directory
			4. Enter the command “flask run” in the terminal and a local web server will be spun up to render the application
			5. Once on the website, please note that the income and the stars are required fields for the form. Entering those should result in your input being assigned to a cluster that will be displayed on the 				choropleth map. If a state is also entered, the choropleth will only show the state after the choices have been submitted.



CODE CITATIONS: 

Star rating system modified from code found at https://codepen.io/facundocorradini/pen/MQmoLR. 
				 