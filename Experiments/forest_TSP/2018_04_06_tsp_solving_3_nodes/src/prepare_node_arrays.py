import numpy as np

def main():

    list_of_embeddings = []
    np.random.seed(78637)
    number_of_nodes = 3
    number_of_embeddings = 1000
    file_name = "embeddings_" + str(number_of_nodes) + ".csv"
    for i in range(number_of_embeddings):

        single_embedding = np.random.rand(2 * number_of_nodes) * 10
        list_of_embeddings.append(np.array(single_embedding))

    np.savetxt(file_name, np.array(list_of_embeddings))


if __name__ == '__main__':
    main()