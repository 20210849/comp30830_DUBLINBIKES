# engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, HOST, PORT, DATABASE), echo=True)
# connection = engine.connect()  

# sql = "SELECT number FROM dbbikes1.station " \
#    "ORDER BY number;"

# for row in engine.execute(sql):
    # print(row)
    # print(str(row)[1 : len(str(row)) - 2])
    # number = str(row)[1 : len(str(row)) - 2]
    # print('model_{}.pkl'.format(number))

    # station_number = int(number)
    # print(station_number)

import pickle


number = 2

with open('./static/model_{}.pkl'.format(number), 'rb') as handle:
    model = pickle.load(handle)
    result = model.predict([[9.0,56.0,283.67,79.0,1009.0,75.0,10000.0,9.26,0,0,0,0,0,1,0,0,1,0,0]])
    
    predict_list = result.tolist()   
    print(predict_list)

