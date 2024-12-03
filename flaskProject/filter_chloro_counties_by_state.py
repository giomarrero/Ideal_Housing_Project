
def filter_chloro_counties(state_fips):
    '''filters us-counties geojson file by state'''
    
    import json
    
    with open('static/us-counties_original.json', 'r', encoding='utf-8') as f:


        data = json.load(f)
        
        if state_fips == "all": 
            print("all of the fips")
            new_file = data
            with open("static/us-states.json", "w") as outfile:
                json.dump(new_file, outfile)
            f.close()
            return

        new_file = {
        "type": "FeatureCollection",
        "features": []}
        for i in data['features']:
            
            if int(i['id']) in state_fips:
                new_file['features'].append(i)
        

        with open("static/us-counties.json", "w") as outfile:
            json.dump(new_file, outfile)

        f.close()