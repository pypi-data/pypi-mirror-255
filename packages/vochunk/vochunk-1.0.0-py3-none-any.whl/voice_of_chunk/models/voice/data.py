import os
import tempfile
import uuid
import soundfile as sf
from utils import is_audio_file, remove_silence, get_vgg_features

VOICE_CLASS = 0
NONVOICE_CLASS = 1
SPOKEN_CLASS = 2
NUM_CLASSES = 3

classification = dict()
classification[VOICE_CLASS] = "voice"
classification[NONVOICE_CLASS] = "nonvoice"
classification[SPOKEN_CLASS] = "spoken"


def process_sources(data_sources: dict):
    """
    Extract Features
    """

    data = list()

    for source in data_sources:
        dir = source["path"]
        files = os.listdir(dir)
        files = [file for file in files if is_audio_file(file)]
        for file in files:
            filepath = os.path.join(dir, file)

            with tempfile.TemporaryDirectory() as temp_dir:
                # remove silence
                sample_rate = 16000
                audio = remove_silence(filepath=filepath, sample_rate=sample_rate)

                if audio.size > 0:
                    # save new file in temp
                    nonsilent_filepath = os.path.join(temp_dir,
                                                      str(uuid.uuid4()) + ".mp3")
                    sf.write(nonsilent_filepath, audio, sample_rate)

                    features = get_vgg_features(nonsilent_filepath)

                    # store
                    datum = {
                        "path": filepath,
                        "class": source["class"],
                        "features": features
                    }
                    data.append(datum)

                    print(f"processed {filepath}")
                else:
                    print(f"file {filepath} is empty.")

    return data
