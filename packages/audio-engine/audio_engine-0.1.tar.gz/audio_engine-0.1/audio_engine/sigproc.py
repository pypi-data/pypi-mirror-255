import numpy as np
import math

def round_half_up(number):
    """Rounds a number to the nearest integer with ties going away from zero."""
    return int(np.round(number))


def rolling_window(a, window, step=1):
    if a.size < window:  # Check if the window is larger than the array
        return np.array([]).reshape(0, window)  # Return an empty array with the correct shape
    shape = (a.size - window + 1, window)
    strides = (a.strides[0], a.strides[0])
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)[::step]



def framesig(sig, frame_len, frame_step, winfunc=lambda x: np.ones((x,))):
    slen = len(sig)
    frame_len = int(round_half_up(frame_len))
    frame_step = int(round_half_up(frame_step))
    
    # Ensure that we have at least one frame
    if slen < frame_len:
        numframes = 1
        padlen = frame_len - slen
        sig = np.append(sig, np.zeros(padlen))  # Pad the signal
    else:
        numframes = 1 + int(math.ceil((1.0 * slen - frame_len) / frame_step))

    padlen = int((numframes - 1) * frame_step + frame_len)
    zeros = np.zeros((padlen - slen,))
    padsignal = np.concatenate((sig, zeros))

    win = winfunc(frame_len)
    frames = rolling_window(padsignal, window=frame_len, step=frame_step)

    return frames * win



def deframesig(frames, siglen, frame_len, frame_step, winfunc=lambda x: np.ones((x,))):
    """Reconstruct a signal from framed data, using overlap-add method."""
    frame_len = round_half_up(frame_len)
    frame_step = round_half_up(frame_step)
    numframes = len(frames)
    assert frames.shape[1] == frame_len, 'Frame length mismatch.'

    padlen = (numframes - 1) * frame_step + frame_len
    rec_signal = np.zeros(padlen)
    window_correction = np.zeros(padlen)
    win = winfunc(frame_len)

    for i in range(numframes):
        start_index = i * frame_step
        end_index = start_index + frame_len
        window_correction[start_index:end_index] += win + 1e-15
        rec_signal[start_index:end_index] += frames[i]

    rec_signal /= window_correction
    return rec_signal[:siglen] if siglen > 0 else rec_signal


def magspec(frames, NFFT):
    """Compute the magnitude spectrum of each frame."""
    complex_spec = np.fft.rfft(frames, NFFT)
    return np.abs(complex_spec)


def powspec(frames, NFFT):
    """Compute the power spectrum of each frame."""
    return 1.0 / NFFT * np.square(magspec(frames, NFFT))


def logpowspec(frames, NFFT, norm=1):
    """Compute the log power spectrum of each frame, optionally normalizing."""
    ps = powspec(frames, NFFT)
    ps[ps <= 1e-30] = 1e-30
    lps = 10 * np.log10(ps)
    if norm:
        return lps - np.max(lps)
    else:
        return lps


def preemphasis(signal, coeff=0.95):
    if signal.size == 0:  # Check if the signal is empty
        return signal  # Return the empty signal
    return np.append(signal[0], signal[1:] - coeff * signal[:-1])

