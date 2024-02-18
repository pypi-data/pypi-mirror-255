# distutils: language=c++

import numpy as np
cimport numpy as np
import enum

ctypedef np.float_t FLOAT_t
ctypedef np.int_t INT_t
CPX = np.complex128
ctypedef np.complex128_t CPX_t

# cdef cppToNumpy1Dr(vector[double] &v):
#     cdef int N = v.size()
#     cdef np.ndarray[FLOAT_t, ndim=1] A = np.zeros(N, dtype=float)
#     cdef int n
#     for n in range(N):
#         A[n] = v[n]
#     return A

cdef numpyToCpp1Dr(np.ndarray[FLOAT_t, ndim=1] A, vector[double] &v):
    cdef int N = A.shape[0]
    cdef int n

    v.resize(N)
    for n in range(N):
        v[n] = A[n]

# cdef cppToNumpy1Di(vector[int] &v):
#     cdef int N = v.size()
#     cdef np.ndarray[INT_t, ndim=1] A = np.zeros(N, dtype=int)
#     cdef int n
#     for n in range(N):
#         A[n] = v[n]
#     return A

cdef numpyToCpp1Di(np.ndarray[INT_t, ndim=1] A, vector[int] &v):
    cdef int N = A.shape[0]
    cdef int n

    v.resize(N)
    for n in range(N):
        v[n] = A[n]

class GainType(enum.IntEnum):
    ENTROPY = 0
    VARIANCE = 1
    SHARPNESS = 2

class ExpansionType(enum.IntEnum):
    UNIFORM = 0
    GAUSSIAN = 1
    GAUSSIAN_SELF_MEAN = 2
    SELF_ENVELOPE = 3

cdef class PhaseDensity:
    cdef _PhaseDensity_* phase_density
    cdef int N_max
    def __cinit__(self, int N_max, int K=1, int M=1, double phi0=0.0):
        self.phase_density = new _PhaseDensity_(N_max, K, M, phi0)
        self.N_max = N_max
    def __dealloc__(self):
        del self.phase_density
    def set_K(self, int K):
        self.phase_density.set_K(K)
    def get_K(self):
        return self.phase_density.get_K()
    def get_M(self):
        return self.phase_density.get_M()
    def get_phi0(self):
        return self.phase_density.get_phi0()
    def setContrasts(self, np.ndarray[FLOAT_t, ndim=1] z):
        cdef vector[double] zv
        numpyToCpp1Dr(z, zv)
        self.phase_density.setContrasts(zv)
    def setSymmetries(self, np.ndarray[FLOAT_t, ndim=1] lam):
        cdef vector[double] lamv
        numpyToCpp1Dr(lam, lamv)
        self.phase_density.setSymmetries(lamv)
    def setWeights(self, np.ndarray[FLOAT_t, ndim=1] w):
        cdef vector[double] wv
        numpyToCpp1Dr(w, wv)
        self.phase_density.setWeights(wv)
    def setDensity(self, PhaseDensity density, int M):
        self.phase_density.setDensity(density.phase_density, M)
    def contractDensity(self, PhaseDensity density, int M):
        self.phase_density.contractDensity(density.phase_density, M)
    def contractSelf(self, int M):
        self.phase_density.contractDensity(M)
    def expandDensity(self, PhaseDensity density, int expansion_type):
        self.phase_density.expandDensity(density.phase_density, expansion_type)
    def update(self, int spin, double meas_angle, int k=1):
        self.phase_density.update(spin, meas_angle, k)
    def getHarmonic(self, int n):
        return self.phase_density.getHarmonic(n)
    def setHarmonic(self, int n, double mag, double phase, int n_max):
        self.phase_density.setHarmonic(n, mag, phase, n_max)
    def getDensity(self, double phase):
        return self.phase_density.getDensity(phase)
    def getScaledDensity(self, double phase):
        return self.phase_density.getScaledDensity(phase)
    def getPhaseEst(self):
        return self.phase_density.getPhaseEst()
    def getPhaseEstPeak(self):
        return self.phase_density.getPhaseEstPeak()
    def shift(self, double phase_shift):
        self.phase_density.shift(phase_shift)
    def spread(self, double r):
        self.phase_density.spread(r)
    def setUniform(self, bool reset_M=False):
        self.phase_density.setUniform(reset_M)
    def setGaussian(self, double mean, double std):
        self.phase_density.setGaussian(mean, std)
    def getVariance(self):
        return self.phase_density.getVariance()
    def getEntropyGain(self, double meas_angle, int k):
        return self.phase_density.getEntropyGain(meas_angle, k)
    def getVarianceGain(self, double meas_angle, int k):
        return self.phase_density.getVarianceGain(meas_angle, k)
    def getSharpnessGain(self, double meas_angle, int k):
        return self.phase_density.getSharpnessGain(meas_angle, k)
    def findBestGainAngle(self, int k, int gain_type=GainType.ENTROPY):
        cdef GainPoint gp = self.phase_density.findBestGainAngle(k, gain_type)
        return gp.angle, gp.gain
    def getMultiShotGain(self, np.ndarray[INT_t, ndim=1] k_vals, int gain_type=GainType.ENTROPY):
        cdef vector[int] k_vals_v
        numpyToCpp1Di(k_vals, k_vals_v)
        cdef GainPoint gp = self.phase_density.getMultiShotGain(k_vals_v, gain_type)
        return gp.angle, gp.gain
    def findBestShotSetting(self, np.ndarray[INT_t, ndim=1] k_vals,
                            int gain_type=GainType.ENTROPY, bool brute_force=False):
        cdef vector[int] k_vals_v
        numpyToCpp1Di(k_vals, k_vals_v)
        cdef ShotSetting ss = self.phase_density.findBestShotSetting(k_vals_v, gain_type, brute_force)
        return ss.meas_angle, ss.k
