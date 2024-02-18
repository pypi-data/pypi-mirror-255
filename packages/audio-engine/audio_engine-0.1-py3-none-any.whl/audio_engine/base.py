from __future__ import division, print_function
import numpy as np
from .sigproc import preemphasis, framesig, powspec
from scipy.fftpack import dct

def calculate_nfft(samplerate, winlen):
    """
    Calculate the FFT size as a power of two greater than or equal to
    the number of samples in a single window length.
    """
    window_length_samples = int(winlen * samplerate)
    nfft = 1
    while nfft < window_length_samples:
        nfft <<= 1
    return nfft

def mfcc(signal, samplerate=16000, winlen=0.025, winstep=0.01, numcep=13,
         nfilt=26, nfft=None, lowfreq=0, highfreq=None, preemph=0.97,
         ceplifter=22, appendEnergy=True, winfunc=lambda x: np.ones((x,))):
    """
    Compute MFCC features from an audio signal.
    """
    # Check if the input signal is empty
    if signal.size == 0:
        return np.empty((0, numcep))  # Adjust numcep to whatever your default or computed number of cepstral coefficients is

    nfft = nfft or calculate_nfft(samplerate, winlen)
    feat, energy = fbank(signal, samplerate, winlen, winstep, nfilt, nfft,
                         lowfreq, highfreq, preemph, winfunc)
    feat = np.log(feat)
    feat = dct(feat, type=2, axis=1, norm='ortho')[:, :numcep]
    feat = lifter(feat, ceplifter)
    if appendEnergy:
        feat[:, 0] = np.log(energy)  # Replace first cepstral coefficient with log of frame energy
    return feat

def fbank(signal, samplerate=16000, winlen=0.025, winstep=0.01, nfilt=26,
          nfft=512, lowfreq=0, highfreq=None, preemph=0.97, winfunc=lambda x: np.ones((x,))):
    """
    Compute Mel-filterbank energy features from an audio signal.
    """
    highfreq = highfreq or samplerate / 2
    signal = preemphasis(signal, preemph)
    frames = framesig(signal, winlen * samplerate, winstep * samplerate, winfunc)
    pspec = powspec(frames, nfft)
    energy = np.sum(pspec, 1)  # Total energy in each frame
    energy = np.where(energy == 0, np.finfo(float).eps, energy)  # Avoid log of zero

    fb = get_filterbanks(nfilt, nfft, samplerate, lowfreq, highfreq)
    feat = np.dot(pspec, fb.T)  # Filterbank energies
    feat = np.where(feat == 0, np.finfo(float).eps, feat)  # Avoid log of zero

    return feat, energy

def logfbank(signal, samplerate=16000, winlen=0.025, winstep=0.01,
             nfilt=26, nfft=512, lowfreq=0, highfreq=None, preemph=0.97,
             winfunc=lambda x: np.ones((x,))):
    if signal.size == 0:
        return np.empty((0, nfilt))
    
    feat, _ = fbank(signal, samplerate, winlen, winstep, nfilt, nfft,
                    lowfreq, highfreq, preemph, winfunc)
    return np.log(np.where(feat == 0, np.finfo(float).eps, feat))

def ssc(signal, samplerate=16000, winlen=0.025, winstep=0.01,
        nfilt=26, nfft=512, lowfreq=0, highfreq=None, preemph=0.97,
        winfunc=lambda x: np.ones((x,))):
    if signal.size == 0:
        return np.empty((0, nfilt))

    highfreq = highfreq or samplerate / 2
    signal = preemphasis(signal, preemph)
    frames = framesig(signal, winlen * samplerate, winstep * samplerate, winfunc)
    pspec = powspec(frames, nfft)
    pspec[pspec == 0] = np.finfo(float).eps  # Avoid log of zero

    fb = get_filterbanks(nfilt, nfft, samplerate, lowfreq, highfreq)
    feat = np.dot(pspec, fb.T)
    R = np.tile(np.linspace(1, samplerate / 2, np.size(pspec, 1)), (np.size(pspec, 0), 1))

    return np.dot(pspec * R, fb.T) / feat

def get_filterbanks(nfilt=20, nfft=512, samplerate=16000, lowfreq=0, highfreq=None):
    """
    Compute a Mel-filterbank.
    """
    highfreq = highfreq or samplerate / 2
    assert highfreq <= samplerate / 2, "highfreq is greater than samplerate/2"

    # Convert Hz to Mel
    lowmel = hz2mel(lowfreq)
    highmel = hz2mel(highfreq)
    melpoints = np.linspace(lowmel, highmel, nfilt + 2)
    bin = np.floor((nfft + 1) * mel2hz(melpoints) / samplerate)

    fbank = np.zeros([nfilt, nfft // 2 + 1])
    for j in range(0, nfilt):
        for i in range(int(bin[j]), int(bin[j+1])):
            fbank[j, i] = (i - bin[j]) / (bin[j+1] - bin[j])
        for i in range(int(bin[j+1]), int(bin[j+2])):
            fbank[j, i] = (bin[j+2] - i) / (bin[j+2] - bin[j+1])
    return fbank

def hz2mel(hz):
    """
    Convert a value in Hertz to Mels.
    """
    return 2595 * np.log10(1 + hz / 700.0)

def mel2hz(mel):
    """
    Convert a value in Mels to Hertz.
    """
    return 700 * (10**(mel / 2595.0) - 1)

def lifter(cepstra, L=22):
    """
    Apply a cepstral lifter to the matrix of cepstra.
    """
    if L > 0:
        nframes, ncoeff = np.shape(cepstra)
        n = np.arange(ncoeff)
        lift = 1 + (L / 2.) * np.sin(np.pi * n / L)
        return lift * cepstra
    else:
        return cepstra

def delta(feat, N):
    """
    Compute delta features from a feature vector sequence.
    """
    if N < 1:
        raise ValueError('N must be an integer >= 1')
    NUMFRAMES = len(feat)
    denominator = 2 * sum([i**2 for i in range(1, N + 1)])
    delta_feat = np.empty_like(feat)
    padded = np.pad(feat, ((N, N), (0, 0)), mode='edge')  # Pad feat for delta calculation
    for t in range(NUMFRAMES):
        delta_feat[t] = np.dot(np.arange(-N, N + 1), padded[t: t + 2 * N + 1]) / denominator
    return delta_feat
