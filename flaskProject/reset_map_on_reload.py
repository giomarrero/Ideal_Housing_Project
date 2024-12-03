def reset_nation():
    '''rewrites filtered geo-json files to the original national geo-json file'''

    import json

    with open('static/us-states_original.json', 'r', encoding='utf-8') as f:

        data = json.load(f)
        new_file = data
        with open("static/us-states.json", "w") as outfile:
            json.dump(new_file, outfile)
            f.close()
            
    with open('static/us-counties_original.json', 'r', encoding='utf-8') as f:

        data = json.load(f)
        new_file = data
        with open("static/us-counties.json", "w") as outfile:
            json.dump(new_file, outfile)
            f.close()
            