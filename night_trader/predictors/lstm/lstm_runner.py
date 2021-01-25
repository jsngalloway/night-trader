from lstm_creator import createLstmModelFromDatasets
from predict_next_value import predict_next, load_x_from_file

if __name__ == "__main__":
    # execute only if run as a script

    # paths = ["../data/MorningTest.csv", "../data/MorningTest2.csv", "../data/MorningTest3.csv", "../data/MorningTest4.csv", "../data/MorningTest5.csv", "../data/MorningTest6.csv", "../data/MorningTest8.csv"]
    paths = ["data/MorningTest2.csv"]
    model = createLstmModelFromDatasets(paths)

    live_data = load_x_from_file("data/MorningTest4.csv", 90)

    next_value = predict_next(model, live_data)
    print(next_value)