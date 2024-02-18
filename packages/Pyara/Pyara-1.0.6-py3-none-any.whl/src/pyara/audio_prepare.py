"""Module for audio prepare"""

import torch
import torchaudio

from pyara import CFG

# TODO __all__ во всех файлах чтобы в import опадали только написанные функции

def cut_if_necessary(signal):
    """cuts the audio signal to CFG.width samples """

    if signal.shape[2] > CFG.width:
        signal = signal[:, :, 0:CFG.width]
    return signal


def right_pad_if_necessary(signal):
    """
     Выполняет дополнение последнего измерения входного сигнала вправо, если необходимо.

     Параметры:
     - signal (torch.Tensor): Тензор сигнала, представляющий многомерные данные.
                              Должен быть трехмерным тензором
                              с размерностью [batch_size, num_channels, signal_length].

     Возвращает:
     - torch.Tensor: Дополненный сигнал с выполненным дополнением последнего измерения вправо.

     """
    length_signal = signal.shape[2]
    if length_signal < CFG.width:
        num_missing_samples = CFG.width - length_signal
        last_dim_padding = (0, num_missing_samples)
        signal = torch.nn.functional.pad(signal, last_dim_padding)
    return signal


def prepare_signal(voice_path):
    """
      Подготавливает аудиосигнал для обработки.

      Аргументы:
      - voice_path (str): Путь к аудиофайлу.

      Возвращает:
      - signal (torch.Tensor): Подготовленный сигнал для обработки.

      Шаги подготовки сигнала:
      1. Загрузка аудиофайла с помощью функции `torchaudio.load(voice_path)`.
      Возвращает сигнал `signal` и частоту дискретизации `sr`.
      2. Усреднение сигнала `signal` по первому измерению (каналам),
       используя функцию `signal.mean(dim=0)`.
      3. Добавление размерности пакета (batch) к сигналу `signal`,
      используя функцию `signal.unsqueeze(dim=0)`.
      4. Применение преобразования MFCC (Mel-frequency cepstral coefficients)
      к сигналу `signal` с помощью функции `MFCC_spectrogram(signal)`.
         В результате получается спектрограмма MFCC.
      5. Обрезка спектрограммы `signal`, если необходимо,
      с помощью функции `cut_if_necessary(signal)`.
      6. Дополнение спектрограммы `signal`, если необходимо,
      с помощью функции `right_pad_if_necessary(signal)`.
      7. Повторение спектрограммы `signal` 3 раза по первому измерению (пакету),
       используя функцию `signal.repeat(3, 1, 1)`.
      8. Добавление размерности пакета (batch) к спектрограмме `signal`,
       используя функцию `signal.unsqueeze(dim=0)`.
      9. Перемещение спектрограммы `signal` на устройство (например, GPU),
       указанное в `CFG.device`, с помощью функции `signal.to(CFG.device)`.
      10. Возврат подготовленного сигнала `signal`.
      """
    signal, sample_rate = torchaudio.load(voice_path)
    signal = signal.mean(dim=0)
    signal = signal.unsqueeze(dim=0)

    signal = MFCC_spectrogram(signal)

    signal = cut_if_necessary(signal)
    signal = right_pad_if_necessary(signal)

    signal = signal.repeat(3, 1, 1)
    signal = signal.unsqueeze(dim=0)
    signal = signal.to(CFG.device)
    return signal


def prediction(model, signal):
    """
    Функция prediction выполняет предсказание с использованием заданной модели для входного сигнала.

    Параметры:
    - model: Модель, которая будет использоваться для предсказания. Должна быть совместима с PyTorch
     и иметь метод forward для выполнения прямого прохода.
    - signal: Входной сигнал, для которого будет выполнено предсказание.
    Должен быть трехмерным тензором с размерностью [batch_size, num_channels, signal_length].

    Возвращает:
    - Предсказанную метку класса для входного сигнала.
    Возвращается значение 1, если модель предсказывает синтезированный голос, и 0,
     если модель предсказывает реальный голос.

    Пример использования:
    ```python
    import torch

    # Создать модель
    model = MyModel()

    # Создать входной сигнал
    signal = torch.randn(1, 3, 100)
    # Размерность сигнала: [batch_size=1, num_channels=3, signal_length=100]

    # Выполнить предсказание
    prediction = prediction(model, signal)

    print(prediction)  # Выводит: 1
    ```
    """
    model = model.to(CFG.device)
    signal = signal.squeeze()
    with torch.no_grad():
        output = model(signal)
        print(output)
        out = output.argmax(dim=-1).cpu().numpy()
    if out[0] == 1:
        return 1
    elif out[0] == 0:
        return 0

    return 0


# Audio to MFCC spectrogram
MFCC_spectrogram = torchaudio.transforms.MFCC(
    sample_rate=CFG.SAMPLE_RATE,
    n_mfcc=CFG.mels,
    melkwargs={
        "n_fft": 1024,
        "n_mels": CFG.mels,
        "hop_length": 256,
        "mel_scale": "htk",
        'win_length': 1024,
        'window_fn': torch.hann_window,
        'center': False
    },
)
