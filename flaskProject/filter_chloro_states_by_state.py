def filter_chloro_states(state):
    '''filters us-states geojson file by state'''
    import json

    with open('static/us-states_original.json', 'r', encoding='utf-8') as f:

        data = json.load(f)
        new_file = {
        "type": "FeatureCollection",
        "features": []}

        if state == "optional": 
            print("all of the states")
            new_file = data
            with open("static/us-states.json", "w") as outfile:
                json.dump(new_file, outfile)

            f.close()
            return


        for i in data['features']:
            if (i['properties']["name"]) == state:
                new_file['features'].append(i)
        

        with open("static/us-states.json", "w") as outfile:
            json.dump(new_file, outfile)

        f.close()

