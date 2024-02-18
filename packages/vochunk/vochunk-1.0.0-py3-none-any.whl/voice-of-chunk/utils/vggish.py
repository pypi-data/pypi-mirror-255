import torch
from utils import is_audio_file

vggish_audio_model = torch.hub.load('harritaylor/torchvggish', 'vggish')
vggish_audio_model.eval()


def get_vgg_features(filepath):
    """
    Wrapper for extracting VGGish features from audio file.
    """
    feature = torch.tensor

    if is_audio_file(filepath):
        feature = vggish_audio_model.forward(filepath)
        if feature.dim() < 2:
            feature = torch.unsqueeze(feature, 0)

    return feature.detach()
