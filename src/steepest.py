import wave
import numpy as np
import matplotlib.pyplot as plt

overlap_factor = 0.5
frame_size = 1024
p_order = 512
window = np.hanning(frame_size)
# Open the audio file named 'example.wav'

def audio_read(file) : 
    with wave.open(file, 'rb') as wav_file:
        # Get the number of frames in the audio file
        num_frames = wav_file.getnframes()
        # Read all the frames in the audio file as bytes
        raw_audio = wav_file.readframes(num_frames)
    return np.frombuffer(raw_audio, dtype=np.int16)
     
def divide_into_frames(signal, frame_size, overlap_factor):
    step_size = int(frame_size * (1 - overlap_factor))
    num_frames = (len(signal) - frame_size) // step_size + 1
    frames = np.zeros((num_frames, frame_size))
    for i in range(num_frames):
        frames[i, :] = signal[i * step_size : i * step_size + frame_size]
    return frames

def apply_window(frames, window_function):
    return frames * window_function

def compute_correlation(x,y,p_order): 
    r = np.correlate(x,y,'full')
    var = np.var(x)
    N = len(x)
    R = np.zeros((N, N))
    for i in range(N):
        R[i,:] = r[N-1-i:2*N-1-i]
    return  r[:p_order] , R[:p_order,:p_order]

def rec_find_weights(w,r,R,frame,mu,iter) : 
    grad = R@w -r
    w -= mu*grad
    iter +=1
    if iter > 100: 
        return w
    else : 
        return rec_find_weights(w,r,R,frame,mu,iter)

def steepest(frames , init) : 
    for idx,frame in enumerate(frames): 
        mu = 0.02
        r, R = compute_correlation(frame,frame,p_order)
        R_norm = np.max(np.abs(R))  # normalization factor
        R /= R_norm  # normalize R
        w = rec_find_weights(init,r,R,frame,mu,0)
        w_whitening = np.zeros(len(w)+1)
        w_whitening[0] = 1
        w_whitening[1:] = -w

        W = np.fft.fft(w_whitening)
        Wf = np.fft.fftfreq(len(W))[:len(W)//2]
        plt.clf()
        plt.semilogx( Wf ,2.0/len(W) * np.abs(W[:len(W)//2]) )
        #plt.plot(Wf,2.0/len(W) * np.abs(W[:len(W)//2]))
        plt.show()


if __name__ == '__main__':
    samples = audio_read('res/piano.wav')
    frames = divide_into_frames(samples, frame_size, overlap_factor)
    w_frames = apply_window(frames, window)
    w_init = np.zeros(p_order)
    predictors = steepest(w_frames,w_init)
    plt.plot(w_frames[0])
    plt.show()