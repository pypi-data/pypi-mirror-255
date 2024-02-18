# distutils: language=c++

from libcpp.vector cimport vector
from libcpp cimport bool

cdef extern from "ctape.h":
    cdef struct ShotSetting:
        double meas_angle
        int k

    cdef struct GainPoint:
        double angle
        double gain

    cdef cppclass _PhaseDensity_ "PhaseDensity":
        _PhaseDensity_(int N_max, int K, int M, double phi0) except+
        void set_K(int K) except+
        int get_K() except+
        int get_M() except+
        int get_phi0() except+
        void setContrasts(const vector[double] &z) except+
        void setSymmetries(const vector[double] &lam) except+
        void setWeights(const vector[double] &w) except+
        void setDensity(const _PhaseDensity_ *density, int M) except+
        void contractDensity(const _PhaseDensity_ *density, int M) except+
        void contractDensity(int M) except+
        void expandDensity(const _PhaseDensity_ *density, int expansion_type) except+
        void update(int spin, double meas_angle, int k) except+
        complex getHarmonic(int n) except+
        void setHarmonic(int n, double mag, double phase, int n_max) except+
        double getDensity(double phase) except+
        double getScaledDensity(double phase) except+
        double getPhaseEst() except+
        double getPhaseEstPeak() except+
        void shift(double phase_shift) except+
        void spread(double r) except+
        void setUniform(bool reset_M) except+
        void setGaussian(double mean, double std) except+
        double getVariance() except+
        double getEntropyGain(double meas_angle, int k) except+
        double getVarianceGain(double meas_angle, int k) except+
        double getSharpnessGain(double meas_angle, int k) except+
        GainPoint findBestGainAngle(int k, int gain_type) except+
        GainPoint getMultiShotGain(const vector[int] &k_vals, int gain_type) except+
        ShotSetting findBestShotSetting(const vector[int] &k_vals,
                                        int gain_type, bool brute_force) except+
