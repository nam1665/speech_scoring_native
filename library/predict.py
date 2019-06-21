from random import shuffle
import numpy as np
import sys
import os


def main():
    random_state = 42
    np.random.seed(random_state)

    current_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(current_dir, '..'))
    current_dir = current_dir if current_dir is not '' else '.'

    model_dir_path = current_dir + '/models'
    data_file_path = current_dir + '/data/1000.txt'

    from library.lstm import training_processing
    from library.simple_data_loader import load_text_label_pairs

    text_label_pairs = load_text_label_pairs(data_file_path)

    classifier = training_processing()
    classifier.load_model(model_dir_path=model_dir_path)

    shuffle(text_label_pairs)

    for i in range(50):
        text, label = text_label_pairs[i]
        print('Output: ', classifier.predict(sentence=text))
        predicted_label = classifier.predict_class(text)
        print('Sentence: ', text)
        print('Predicted: ', predicted_label, 'Actual: ', label)


if __name__ == '__main__':
    main()

