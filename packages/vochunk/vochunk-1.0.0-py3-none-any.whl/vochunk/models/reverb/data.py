import os
import tempfile
import random
import argparse
import uuid
import json

import numpy as np
import scipy.signal as signal
import scipy.stats as stats
import matplotlib.pyplot as plt

import librosa
import soundfile as sf

# importing within package
from utils import is_audio_file, remove_silence, get_vgg_features
"""
Reverb/Echo Data

Data to train a classifier to disambiguate dry acapella vocals vs. 
vocals processed by reverb or echo.

To do this we will process known dry vocals from our datasets with a 
large collection of FIR (reverberation) and IIR (echo) filters.
"""

DRY_CLASS = 0
REVERB_CLASS = 1
NUM_CLASSES = 2

classification = dict()
classification[DRY_CLASS] = "dry"
classification[REVERB_CLASS] = "reverb"


def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
    """
    return ((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]


def random_bool():
    return bool(random.getrandbits(1))


def measure_rt60(ir, sample_rate):
    # measure RT60
    ir_rms = librosa.feature.rms(y=ir, hop_length=256)[0]
    ir_rms_t = np.linspace(0, len(ir) / sample_rate, len(ir_rms), False)
    if max(np.abs(ir_rms)) > 0:
        ir_rms /= max(np.abs(ir_rms))
    ir_rms = 20 * np.log10(ir_rms)

    rt60_index = len(ir_rms) - 1
    for n, _ in enumerate(ir_rms[:-1]):
        if ir_rms[n] > -60 and ir_rms[n + 1] < -60:
            rt60_index = n
            break

    rt60 = ir_rms_t[rt60_index]
    return rt60


def apply_reverb(audio, ir, ratio):

    # apply ir
    wet = signal.convolve(audio, ir)
    audio = librosa.util.fix_length(audio, size=len(wet))

    theta = scale(ratio, [0, 1], [0, np.pi / 2])
    dry_level = np.cos(theta)
    wet_level = np.sin(theta)

    output = dry_level * audio + wet_level * wet
    return output


def process_sources(data_sources: dict, ir_dir: str, sample_rate=16000):
    """
    Extract Features
    """

    # get impulse response files
    ir_files = os.listdir(ir_dir)
    ir_files = [file for file in ir_files if is_audio_file(file)]
    ir_filepaths = [os.path.join(ir_dir, file) for file in ir_files]

    data = list()

    for source in data_sources:
        dir = source["path"]
        files = os.listdir(dir)
        files = [file for file in files if is_audio_file(file)]
        for file in files:
            filepath = os.path.join(dir, file)

            # remove silence
            dry_audio = remove_silence(filepath=filepath, sample_rate=sample_rate)

            # get impulse response
            ir_filepath = random.choice(ir_filepaths)
            ir, _ = librosa.load(ir_filepath, sr=sample_rate)
            ratio = stats.skewnorm(4.0, 0.1, 0.05).rvs()
            # ratio = 1.0

            reverb_audio = apply_reverb(dry_audio, ir, ratio)
            with tempfile.TemporaryDirectory() as temp_dir:
                tmp_file = os.path.join(temp_dir, str(uuid.uuid4()) + ".mp3")
                sf.write(tmp_file, reverb_audio, sample_rate)
                reverb_audio = remove_silence(filepath=tmp_file,
                                              sample_rate=sample_rate)

            with tempfile.TemporaryDirectory() as temp_dir:
                if dry_audio.size > 0:
                    # save new file in temp
                    nonsilent_filepath = os.path.join(temp_dir,
                                                      str(uuid.uuid4()) + ".mp3")
                    sf.write(nonsilent_filepath, dry_audio, sample_rate)

                    features = get_vgg_features(nonsilent_filepath)

                    # store
                    datum = {
                        "path": filepath,
                        "class": source["class"],
                        "features": features,
                        "ratio": 0
                    }
                    data.append(datum)

                    print(f"processed {filepath}")
                else:
                    print(f"file {filepath} is empty.")

            with tempfile.TemporaryDirectory() as temp_dir:
                if reverb_audio.size > 0:
                    # save new file in temp
                    nonsilent_filepath = os.path.join(temp_dir,
                                                      str(uuid.uuid4()) + ".mp3")
                    sf.write(nonsilent_filepath, reverb_audio, sample_rate)

                    features = get_vgg_features(nonsilent_filepath)

                    # store
                    datum = {
                        "path": filepath,
                        "class": REVERB_CLASS,
                        "features": features,
                        "ratio": ratio
                    }
                    data.append(datum)

                    print(f"processed {filepath} with reverb")
                else:
                    print(f"file {filepath} is empty.")

    return data
