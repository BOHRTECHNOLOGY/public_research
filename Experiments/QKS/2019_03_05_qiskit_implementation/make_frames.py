import numpy as np


def make_frames(train_size=200, test_size=50, outer_length=2, inner_length=1):
    """
    Generates pictures frames dataset.
    """

    def zip_arrays(d1, d2):
        return np.array(list(zip(d1, d2)))

    def shuffle(d1, d2):
        assert len(d1) == len(d2)
        p = np.random.permutation(len(d1))
        return d1[p], d2[p]

    def make_barriers(num, length):
        dist = 0.1 * length
        left = np.random.uniform((-length - dist), (-length + dist), num)
        right = np.random.uniform((length - dist), (length + dist), num)
        left_barrier = np.random.uniform(-length, length, num)
        right_barrier = np.random.uniform(-length, length, num)
        L = zip_arrays(left, left_barrier)
        R = zip_arrays(right, right_barrier)
        barriers = np.vstack((L, R))
        return barriers

    def make_squares(num, length):
        left_right, top_bottom = make_barriers(num, length), make_barriers(num, length)
        top_bottom[:, [0, 1]] = top_bottom[:, [1, 0]]  # swaps X and Y axis
        square = np.concatenate((left_right, top_bottom))
        return square

    def make_data(size, outer_length, inner_length):
        outer = make_squares(size, outer_length)
        inner = make_squares(size, inner_length)
        assert len(outer) == len(inner)

        frames = np.concatenate((outer, inner))
        target = np.concatenate((np.zeros(len(outer)), np.ones(len(inner))))

        X, y = shuffle(frames, target)
        return X, y

    X_train, y_train = make_data(train_size, outer_length, inner_length)
    X_test, y_test = make_data(test_size, outer_length, inner_length)
    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = make_frames()
