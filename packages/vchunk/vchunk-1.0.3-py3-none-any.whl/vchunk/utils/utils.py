import os
import numpy as np
import soundfile as sf
import librosa

AUDIO_FILETYPES = tuple(
    ["." + filetype.lower() for filetype in list(sf._formats.keys())] + ['.mp3'])


def is_audio_file(file):
    """Is file an audio file?"""
    return os.path.splitext(file)[-1].lower() in AUDIO_FILETYPES


def remove_silence(filepath,
                   threshold_of_silence=0.0001,
                   minimum_interval_duration=0.1,
                   sample_rate=16000):
    """Strip Silence"""

    # load audio
    audio, sample_rate = librosa.load(filepath, sr=16000)
    audio = librosa.to_mono(audio)

    window_size = 2048
    hop_size = 512
    rms = librosa.feature.rms(y=audio, frame_length=window_size, hop_length=hop_size)
    rms = np.squeeze(rms)
    rms_t = librosa.times_like(rms, sr=sample_rate, hop_length=hop_size)

    nonsilent_indxs = [i for i, v in enumerate(rms) if v > threshold_of_silence]

    # find contiguous intervals on nonsilent indices
    contiguous_intervals = []
    buffer = []
    j = 0
    for i, _ in enumerate(nonsilent_indxs[:-1]):
        buffer.append(nonsilent_indxs[i])
        if (np.abs(nonsilent_indxs[i] - nonsilent_indxs[i + 1]) >
                1) or (i == len(nonsilent_indxs) - 2):
            contiguous_intervals.append(buffer)
            buffer = []
            j += 1

    # discard intervals below minimum
    minimum_num_frames = librosa.time_to_frames(times=minimum_interval_duration,
                                                hop_length=hop_size).item()
    contiguous_intervals = [
        interval for interval in contiguous_intervals
        if len(interval) > minimum_num_frames
    ]

    # get times corresponding to start and end of indices
    start_times = []
    end_times = []
    for interval in contiguous_intervals:
        start_times.append(rms_t[interval[0]])
        end_times.append(rms_t[interval[-1]])

    start_samples = [int(time * sample_rate) for time in start_times]
    end_samples = [int(time * sample_rate) for time in end_times]

    # calculate total nonsilent time in samples
    num_nonsilent_samples = 0
    for start_sample, end_sample in zip(start_samples, end_samples):
        num_nonsilent_samples += end_sample - start_sample

    # create new audio vector
    nonsilent_audio = np.zeros(num_nonsilent_samples)
    write_start = 0
    write_end = 0
    for start_sample, end_sample in zip(start_samples, end_samples):
        interval_num_samples = end_sample - start_sample
        write_end += interval_num_samples
        nonsilent_audio[write_start:write_end] = audio[start_sample:end_sample]
        write_start += interval_num_samples

    return nonsilent_audio
