import json

if __name__ == "__main__":
    # convert to string
    input = json.dumps({'id': 'id' })
    
    # load to dict
    my_dict = json.loads(input) 
    
    print('input: ' + input)
    print('str(my_dict): ' + str(my_dict))
    