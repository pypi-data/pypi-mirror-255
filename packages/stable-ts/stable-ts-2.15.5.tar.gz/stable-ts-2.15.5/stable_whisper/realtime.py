import subprocess
import time
from typing import List

import numpy as np
import torch

import whisper
from whisper.audio import (
    SAMPLE_RATE, N_FRAMES, HOP_LENGTH, N_SAMPLES, N_SAMPLES_PER_TOKEN, TOKENS_PER_SECOND, FRAMES_PER_SECOND, N_FFT,
    pad_or_trim, log_mel_spectrogram
)
from whisper.decoding import DecodingOptions

from .audio import load_audio
from .utils import isolate_useful_options
from .whisper_compatibility import get_tokenizer
from .decode import decode_stable
from .timing import _split_tokens, add_word_timestamps_stable


def transcribe_live(
        model: whisper.Whisper,
        audio,
        chunk_duration: int = 0.25,
        language: str = 'en',
        no_speech_threshold: float = 0.6,
        **kwargs
):
    chunk_size = round(SAMPLE_RATE * chunk_duration)
    audio_file = audio if isinstance(audio, str) else None
    audio = load_audio(
        audio,
        sr=SAMPLE_RATE,
        chunk_size=chunk_size,
        **isolate_useful_options(kwargs, load_audio, pop=True)
    )
    dtype = torch.float16
    assert not isinstance(kwargs.get('temperature'), (list, tuple)), 'temperature can only be a single value'
    task = 'transcribe'
    tokenizer = get_tokenizer(model, language=language, task=task)
    mel = None
    max_mel_index = 3*100
    prev_mel_index = 0
    p = subprocess.Popen(f'ffplay -i "{audio_file}"', stderr=subprocess.DEVNULL)
    start_time = time.time()
    accum_time = 0
    all_words, temp_words = [], []
    curr_mel_count = 0
    time_offset = 0.0

    def timestamp_words(_words, _tokens) -> List[dict]:
        temp_segment = dict(
            seek=time_offset,
            tokens=(_words, _tokens)
        )

        add_word_timestamps_stable(
            segments=[temp_segment],
            model=model,
            tokenizer=tokenizer,
            mel=mel,
            audio_features=audio_feature,
            num_samples=segment_samples,
            split_callback=(lambda x, _: x),
            gap_padding=None
        )

        return temp_segment['words']

    for audio_chunk in audio:
        if (wait := (accum_time - (time.time()-start_time))) > 0:
            time.sleep(wait)
        mel_chunk = log_mel_spectrogram(audio_chunk, model.dims.n_mels)
        if mel is None:
            segment_samples = len(mel_chunk)
            mel = pad_or_trim(mel_chunk, N_FRAMES).to(device=model.device, dtype=dtype)[None]
        else:
            mel_len = mel_chunk.shape[-1]
            mel_index = prev_mel_index + mel_len
            if mel_index > max_mel_index:
                print('overflow')
            mel[0, :, prev_mel_index:mel_index] = mel_chunk
            prev_mel_index = mel_index
            segment_samples = round(mel_index / 100 * SAMPLE_RATE)

        # prefix = [t for w in prefix_words for t in w['tokens']]
        decoding_options = DecodingOptions(**kwargs, without_timestamps=True, language=language)
        result, audio_feature = decode_stable(model, mel, decoding_options)
        accum_time += (len(audio_chunk) / SAMPLE_RATE)

        # non-speech
        if result[0].no_speech_prob > no_speech_threshold or not result[0].tokens:
            temp_words = []
            mel[..., :prev_mel_index] = 0
            curr_mel_count += prev_mel_index / 100
            prev_mel_index = 0
            continue

        words = timestamp_words(*_split_tokens(result[0].tokens, tokenizer))
        if temp_words:
            for i in range(len(words)):
                if i < len(temp_words) and temp_words[i]['word'] == words[0]['word']:
                    word = words.pop(0)
                    print(word['word'])
                    all_words.append(word)
                    adjustment = round((word['end'] - time_offset) * 100)
                    curr_mel_count += adjustment
                    time_offset = round(curr_mel_count / 100, 3)
                    mel_index = prev_mel_index-adjustment
                    mel[..., :mel_index] = mel[..., adjustment:prev_mel_index]
                    mel[..., mel_index:prev_mel_index] = 0
                    prev_mel_index = mel_index
                else:
                    break
        temp_words = words
    p.terminate()
    return all_words, tokenizer
