import os
import tempfile
import uuid
import warnings
import statistics
import torch
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from utils import remove_silence, get_vgg_features
from .mlp import VoiceNonVoiceClassifierNetwork


class VoiceNonVoiceModel():

    def __init__(self):
        self.net = VoiceNonVoiceClassifierNetwork()
        self.net.load_state_dict(
            torch.load("VoiceNonVoiceClassifier_20240110184627.pt"))
        self.net.eval()

    def predict(self, filepath: str, plot=False):

        with tempfile.TemporaryDirectory() as temp_dir:
            # strip silences from audio
            sample_rate = 16000
            audio = remove_silence(filepath=filepath, sample_rate=sample_rate)
            if audio.size > 0:
                # resave
                temp_file = os.path.join(temp_dir, f"{str(uuid.uuid4())}.mp3")
                sf.write(temp_file, audio, sample_rate)
                # extract features
                features = get_vgg_features(temp_file)
                # pass features to model
                outputs = self.net(features)
                _, predictions = torch.max(outputs, 1)
                predictions = predictions.tolist()

                detected_class = statistics.mode(predictions)
                # print(f"in file {filepath} detected {classification[detected_class]}")

                if (plot):

                    dur = sample_rate / len(audio)
                    audio_t = np.linspace(0, dur, len(audio), False)
                    predictions_t = np.linspace(0, dur, len(predictions), False)

                    plt.plot(audio_t, audio)
                    plt.plot(predictions_t, predictions)

                    plt.show()

                return detected_class

            else:
                warnings.warn(f"file {filepath} contains only silence.")
                return -1
