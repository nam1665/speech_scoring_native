import numpy as np
import os
import sys


def main():
    random_state = 42
    np.random.seed(random_state)

    current_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(current_dir, '..'))
    current_dir = current_dir if current_dir is not '' else '.'

    output_dir_path = current_dir + '/models'
    data_file_path = current_dir + '/data/1002.txt'

    from library.lstm import training_processing
    from library.simple_data_loader import load_text_label_pairs
    from library.text_fit import fit_text

    text_data_model = fit_text(data_file_path)
    text_label_pairs = load_text_label_pairs(data_file_path)

    classifier = training_processing()
    batch_size = 128
    epochs = 100
    history = classifier.fit(text_data_model=text_data_model,
                             model_dir_path=output_dir_path,
                             text_label_pairs=text_label_pairs,
                             batch_size=batch_size, epochs=epochs,
                             test_size=0.3,
                             random_state=random_state)


if __name__ == '__main__':
    main()

