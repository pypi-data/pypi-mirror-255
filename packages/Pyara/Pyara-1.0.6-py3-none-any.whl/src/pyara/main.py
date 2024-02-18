"""Module for audio classification"""
from pyara import model_eval
from pyara import prediction, prepare_signal


def predict_audio(file_path):
    """
    Function for audio syntesized/real prediction

    :param file_path: path to the file
    :return: prediction about audio
    0: if real voice
    1: if syntesized voice
    """
    # Model to predict
    model = model_eval()
    signal = prepare_signal(file_path)

    pred = prediction(model, signal)
    return pred


def convert(my_name):
    """
    Print a line about converting a notebook.
    Args:
        my_name (str): person's name
    Returns:
        None
    """

    print(f"I'll convert a notebook for you some day, {my_name}.")


if __name__ == '__main__':
    print(predict_audio("mozila11_0.wav"))
