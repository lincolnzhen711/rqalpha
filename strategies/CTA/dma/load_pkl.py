import pickle

pkl_file = open('dma.pkl', 'rb')

data = pickle.load(pkl_file)

print(data)