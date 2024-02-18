/**
 * Time Adaptive Phase Estimation (TAPE)
 *  @author Brennan de Neeve
 *  August 4, 2020.
 *
 * @section DESCRIPTION
 *
 *   The PhaseDensity class represents a probability density function that describes the
 *   state of knowledge of a phase to be estimated by quantum measurements. The class
 *   offers methods that can be used to adaptively choose measurement settings.
 */

// #ifndef CTAPE_H
// #define CTAPE_H

#include <vector>
#include <complex>
#include <list>
#include <functional>
#include <stdexcept>

// vector 'v' must be sorted in increasing order and contain no
// duplicates. If value 'x' is in the vector 'v', returns the index of
// the value equal to 'x' and true. If the value 'x' is not in 'v'
// returns the index of the smallest value greater than 'x' and false.
// If the value 'x' is larger than the largest (i.e. the last) element
// of 'v' then returns the size of 'v' and false.
template <typename T>
std::pair<size_t,bool> binarySearch(const std::vector<T> &v, T x) {
    if (v.size() < 1)
        throw std::runtime_error("Cannot search an empty vector.");
    if (x < v.front())
        return std::pair<size_t,bool>(0, false);
    if (x > v.back())
        return std::pair<size_t,bool>(v.size(), false);
    if (v.size() == 1 && x == v[0])
        return std::pair<size_t,bool>(0, true);
    size_t n_min {0}, n_max {v.size()-1}, n;
    while (true) {
        if (n_max - n_min == 1) {
            if (x == v[n_min])
                return std::pair<size_t,bool>(n_min, true);
            if (x == v[n_max])
                return std::pair<size_t,bool>(n_max, true);
            return std::pair<size_t,bool>(n_max, false);
        }
        n = (n_min + n_max)/2;
        if (x < v[n])
            n_max = n;
        else if (x > v[n])
            n_min = n;
        else
            return std::pair<size_t,bool>(n, true);
    }
}

// Vectors 'v1' and 'v2' must be sorted in increasing order and
// contain no duplicates. 'v_merged' is returned in increasing order
// without duplicates.
template <typename T>
void mergeIndices(const std::vector<T> &v1,
                  const std::vector<T> &v2, std::vector<T> &v_merged) {
    if (v1.size() == 0) {
        v_merged = v2;
        return;
    }
    if (v2.size() == 0) {
        v_merged = v1;
        return;
    }
    v_merged.resize(v1.size() + v2.size());
    size_t i1 {0}, i2 {0}, i_m {0};
    while (true) {
        if (v1[i1] < v2[i2]) {
            v_merged[i_m++] = v1[i1++];
        } else if (v1[i1] > v2[i2]) {
            v_merged[i_m++] = v2[i2++];
        } else {
            v_merged[i_m++] = v1[i1++];
            ++i2;
        }
        if (i1 == v1.size()) {
            while (i2 < v2.size())
                v_merged[i_m++] = v2[i2++];
            v_merged.resize(i_m);
            return;
        }
        if (i2 == v2.size()) {
            while (i1 < v1.size())
                v_merged[i_m++] = v1[i1++];
            v_merged.resize(i_m);
            return;
        }
    }
}

template <typename T>
struct FourVector {
    std::vector<T> v1, v2, v3, v4;
};

struct CoeffSubset {
    int N; // Used number of coefficients (without counting c0) in the full set.
    std::vector<int> idx; // indices
    std::vector<std::complex<double>> cfs; // coefficients

    std::complex<double>& operator[](int i);
    std::complex<double> operator[](int i) const;
};

void getPriorIndexSets(int N, int N_new, int k, const std::vector<int> &post_idx,
                       std::vector<size_t> &i_mins, FourVector<int> &idx_sets);

// Standard Fibonacci search technique to find the maximum of a unimodal function from a
// discrete set of points. It is essentially an adaptation of the standard golden-section
// search method to the case where the domain is discretised. Given a function 'f' that
// maps from domain type X to range type Y, and a vector of domain points 'x', find the
// value in 'x' that 'f' maps to the highest value. If the function 'f' is unimodal on the
// interval that contains all values in 'x', then fibonacciSearchMax is guaranteed to find
// the value in 'x' that results in the highest value of 'f'. The return value is the
// index of 'x' that results in the highest value of 'f', and the corresponding value of
// 'f'.
template <typename X, typename Y>
std::pair<size_t,Y> fibonacciSearchMax(const std::vector<X> &x, const std::function<Y(X)> &f) {
    if (x.size() == 0) throw std::runtime_error("fibonacciSearchMax: no values to search.");
    if (x.size() < 4) { // If there are fewer that 4 values, simply check all.
        Y max {f(x[0])};
        size_t i_max {0};
        for (size_t i = 1; i < x.size(); ++i) {
            Y f_x {f(x[i])};
            if (f_x > max) {
                max = f_x;
                i_max = i;
            }
        }
        return std::pair<size_t,Y>(i_max, max);
    }

    size_t m {0}, n {x.size() - 1}; // min and max indices of 'x'.
    size_t j {0}, k {1}; // The first two Fibonacci numbers.
    size_t Fn; // A temporary value which will always be a Fibonacci number.
    while (k < n) {
        Fn = j + k;
        j = k;
        k = Fn;
    }
    size_t diff {k - j};
    k = j;
    j = diff;
    Y min, max, low, high;
    low = std::move(f(x[j]));
    high = std::move(f(x[k]));
    if (n == Fn) { // The last index of 'x' is a Fibonacci number.
        min = std::move(f(x[m]));
        max = std::move(f(x[n]));
    } else {
        if (high > low) {
            m = n - k;
            Fn = k - j;
            k = m + j;
            j = m + Fn;
            max = std::move(f(x[n]));
            high = std::move(f(x[k]));
        } else {
            n = k;
            k = j;
            j = n - k;
            max = high;
            high = low;
        }
        min = std::move(f(x[m]));
        low = std::move(f(x[j]));
    }
    while (true) {
        if (high > low) {
            if (n - k == 1)
                return (max > high) ? std::pair<size_t,Y>(n,max) : std::pair<size_t,Y>(k,high);
            Fn = j - m;
            m = j;
            j = k;
            k = m + Fn;
            min = low;
            low = high;
            high = std::move(f(x[k]));
        } else {
            if (j - m == 1)
                return (low > min) ? std::pair<size_t,Y>(j,low) : std::pair<size_t,Y>(m,min);
            Fn = k - j;
            n = k;
            k = j;
            j = m + Fn;
            max = high;
            high = low;
            low = std::move(f(x[j]));
        }
    }
}

struct ShotSetting {
    double meas_angle;
    int k;
};

struct GainPoint {
    double angle;
    double gain;

    friend bool operator==(const GainPoint &gp1,
                           const GainPoint &gp2) { return gp1.gain == gp2.gain; }
    friend bool operator!=(const GainPoint &gp1,
                           const GainPoint &gp2) { return !(gp1 == gp2); }
    friend bool operator<(const GainPoint &gp1,
                          const GainPoint &gp2) { return gp1.gain < gp2.gain; }
    friend bool operator>(const GainPoint &gp1,
                          const GainPoint &gp2) { return gp2 < gp1; }
    friend bool operator<=(const GainPoint &gp1,
                           const GainPoint &gp2) { return !(gp1 > gp2); }
    friend bool operator>=(const GainPoint &gp1,
                           const GainPoint &gp2) { return !(gp1 < gp2); }
};

namespace gain {
    /**
     * gain::Type
     *
     *   @see PhaseDensity::findBestGainAngle.
     */
    enum Type {
        ENTROPY,
        VARIANCE,
        SHARPNESS
    };
}

namespace expansion {
    /**
     * expansion::Type
     *
     *   @see PhaseDensity::expandDensity.
     */
    enum Type {
        UNIFORM,
        GAUSSIAN,
        GAUSSIAN_SELF_MEAN,
        SELF_ENVELOPE
    };
}

class PhaseDensity {
public:
    /**
     * PhaseDensity
     *
     *   Constructor.
     *
     *   @param N_max is the maximum number of coefficients that can be used for the
     *     truncated Fourier series representing the probability density function. This
     *     parameter cannot be changed after construction of the class.
     *
     *   @param K is the maximum value of k that can be used for a measurement, where k is
     *     the number of applications of the coherent evolution of the phase in a given
     *     measurement.
     *
     *   @param M is the magnification. M = 1 corresponds to no magnification; in that
     *     case the truncated Fourier series represents the phase on the full range of
     *     angles between zero and two pi. If M > 1, the truncated Fourier series
     *     represents the phase on a reduced range of 2*pi/M. We refer to a representation
     *     with M > 1 as a contraction. Contractions are useful since they reduce
     *     computational overhead.
     *
     *   @param phi0 is the offset phase of a contraction (M > 1). In general the phase on
     *     the full range from zero to two pi, call it phi, is equal to phi0 + theta/M,
     *     where theta is the phase represented by the truncated Fourier series and M is
     *     the magnification.
     */
    PhaseDensity(int N_max, int K=1, int M=1, double phi0=0.0);

    ~PhaseDensity() {}

    /**
     * set_K
     *
     *   Sets the maximum allowed k-value: the number of applications of the quantum
     *   evolution (for which the phase is being estimated). Calling this method resets
     *   all contrasts, symmetries, and weights to 1.0; @see setContrasts(), @see
     *   setSymmetries(), @see setWeights(). When this value is set some internal
     *   parameters used for gain computation are recalculated for all allowed k-values.
     *
     *   @param K is the maximum allowed k-value to be set. The value must be greater than
     *   or equal to one.
     */
    void set_K(int K);

    /**
     * get_K
     *
     *   @return returns K, the maximum allowed k-value. @see set_K().
     */
    int get_K();

    /**
     * get_M
     *
     *   @return returns the current magnification, M. If M > 1, the current probability
     *   density is represented as a contraction on a reduced range of 2*pi/M.
     */
    int get_M();

    /**
     * get_phi0
     *
     *   @return returns the current phase offset phi0 used to represent the probability
     *   density as a contraction on a reduced range. The phase to be estimated phi is
     *   then equal to phi0 + theta/M, where theta is the phase represented by a Fourier
     *   series, and M is the magnification.
     */
    int get_phi0();

    /**
     * setContrasts
     *
     *   Sets the contrasts of the measurement probability as a function of k. When this
     *   method is called some internal parameters used for gain computation are
     *   recalculated for all allowed k-values.
     *
     *   @param z is a vector (of length K) of contrasts in [0,1].
     */
    void setContrasts(const std::vector<double> &z);

    /**
     * setSymmetries
     *
     *   Sets the symmetry of the measurement probability as a function of k. When this
     *   method is called some internal parameters used for gain computation are
     *   recalculated for all allowed k-values.
     *
     *   @param lam is a vector (of length K) of symmetries in [0,1]. A value of 1
     *     corresponds to a symmetric measurement, i.e. the probability of each outcome
     *     averaged over all phase angles is equal to 1/2. A value of 0 corresponds to a
     *     measurement for which the outcome is deterministically 0.
     */
    void setSymmetries(const std::vector<double> &lam);

    /**
     * setWeights
     *
     *   Sets some weights as a function of k that are used to scale the expected
     *   knowledge gain in the method findBestShotSetting(). In particular the method
     *   findBestShotSetting maximises the gain divided by the weight for the k-value used
     *   to compute that gain. In this way the optimal value of k will be modified. @see
     *   findBestShotSetting().
     *
     *   @param w is a vector (of length K) of weights. The weights have any non-zero
     *     value.
     */
    void setWeights(const std::vector<double> &w);

    /**
     * setDensity
     *
     *   This method sets the probability density of this instance of PhaseDensity using
     *   the given instance and sets the magnification of this instance to the given
     *   value. Internally, a temporary density is created with a magnification that is
     *   equal to the greatest common divisor of the magnification of this and the given
     *   instance. The instance with a smaller magnification between this and the given
     *   instance is first expanded uniformly (expansion::Type UNIFORM) to the temporary
     *   density, and then the density with the larger magnification is expanded to the
     *   temporary afterwards using the envelope of the uniform expansion (expansion::Type
     *   SELF_ENVELOPE). Finally, the temporary density is contracted into this instance
     *   using the given magnification. The end result is that the most magnified
     *   contraction is combined with the other using it as an envelope and then the
     *   result is contracted to a specified magnification. K, contrasts, symmetries, and
     *   weights and all internal parameters are copied from the given density to this
     *   one.
     *
     *   @see contractDensity
     *   @see expandDensity
     *
     *   @param density is the given instance of PhaseDensity that is to be combined with
     *     this one.
     *
     *   @param M is the final value of magnification to contract to after combininig this
     *     and the given densities. There is no restriction on the value of M so long as
     *     it is a valid magnification (M >= 1). If M is larger than both the
     *     magnification of this and the given density only expansion will be performed
     *     and no contraction.
     */
    void setDensity(const PhaseDensity &density, int M);

    /**
     * contractDensity
     *
     *   Sets this instance of PhaseDensity to a contraction of the given density with the
     *   given magnification. The former state of this instance is lost by invoking this
     *   method. K, contrasts, symmetries, and weights and all internal parameters are
     *   copied from the given density to this one.
     *
     *   @param density is the given instance of PhaseDensity that is to be contracted.
     *
     *   @param M is the value of magnification to contract the given density to. M must
     *     be larger than and a multiple of the magnification of the given density.
     */
    void contractDensity(const PhaseDensity &density, int M);

    /**
     * contractDensity
     *
     *   Same as the other overload, except that instead of setting this density to a
     *   contraction of a given density, it is set to a contraction of itself. This is
     *   faster.
     *
     *   @param M is the value of magnification to contract the current density to. M must
     *     be larger than and a multiple of the current magnification.
     */
    void contractDensity(int M);

    /**
     * expandDensity
     *
     *   Sets this instance of PhaseDensity to an expansion of the given density. The
     *   magnification of this instance remains the same. The magnification of the given
     *   density must be a multiple of that of this instance. Different envelopes are
     *   applied depending on the type of expansion. Only sets coefficients and
     *   magnefication parameters. K, contrasts, symmetries, weights and k-dependent
     *   internal parameters are left unchanged.
     *
     *   @param density is the given instance of PhaseDensity that is to be expanded into
     *     this instance. The magnification of the given density must be a multiple of
     *     that of this instance. The range of the given density must be fully contained
     *     within the range of this instance.
     *
     *   @param type determines the envelope that will be applied to the expansion.
     *   @see expansion::Type
     *
     *     - UNIFORM: The envelope applied is flat (that of a uniform probability
     *         density). In this case the resulting probability density after expansion
     *         will contain multiple peaks of the same height.
     *
     *     - GAUSSIAN: Set a gaussian envelope with mean at the center of the range of the
     *         density to be expanded. The standard deviation of the gaussian is set to
     *         2*pi/(3*M/m), where m is the magnification of this instance and M is that
     *         of the given density.
     *
     *     - GAUSSIAN_SELF_MEAN: Set a gaussian envelope with mean at mean of this
     *         instance before expansion. The standard deviation of the gaussian is set to
     *         2*pi/(3*M/m), where m is the magnification of this instance and M is that
     *         of the given density.
     *
     *     - SELF_ENVELOPE: The density of this instance before expansion is used as an
     *         envelope.
     */
    void expandDensity(const PhaseDensity &density, expansion::Type type);

    // Some overloads for cython
    void setDensity(const PhaseDensity *density, int M)
    {setDensity(*density, M);}
    void contractDensity(const PhaseDensity *density, int M)
    {contractDensity(*density, M);}
    void expandDensity(const PhaseDensity *density, int expansion_type)
    {expandDensity(*density, static_cast<expansion::Type>(expansion_type));}

    /**
     * update
     *
     *   Apply Bayes' theorem to update the probability density given the new measurement
     *   result and control parameters used to perform the measurement.
     *
     *   @param spin is the result of the measurement. It must be 0 or 1; other values are
     *     invalid.
     *
     *   @param meas_angle is the value of the controllable feedback phase used for the
     *     measurement.
     *
     *   @param k is the number of applications of the quantum evolution (for which the
     *     phase is being estimated) that were used for the last measurement.
     */
    void update(int spin, double meas_angle, int k=1);

    /**
     * getHarmonic
     *
     *   Returns the value of a coefficient in the Fourier series representing the
     *   probability density for the phase. This method is mainly for testing purposes.
     *
     *   @param n is the index of the coefficient to be returned. Only non-negative values
     *     are valid (negative coefficents are just the complex conjugate of positive
     *     ones).
     *
     *   @return The complex value of the specified coefficient.
     */
    std::complex<double> getHarmonic(int n);

    /**
     * setHarmonic
     *
     *   Sets the value of a coefficient in the Fourier series representing the
     *   probability density of the phase. This method is mainly for testing purposes.
     *
     *   @param n is the index of the coefficient to be set. Only non-negative values are
     *     valid (negative coefficents are just the complex conjugate of positive ones).
     *
     *   @param mag is the magnitude of the complex coefficient to be set.
     *
     *   @param phase is the phase of the complex coefficient to be set.
     *
     *   @param n_max sets the current maximum index of valid coefficients (N_).
     */
    void setHarmonic(int n, double mag, double phase, int n_max);

    /**
     * getDensity
     *
     *   Returns the value of the probability density at a given phase. The method does
     *   not take the magnification into account; if the current density is contracted,
     *   then the value returned will correspond to the value of the un-contracted (M_=1)
     *   density at phi0_ + (phase mod 2*pi)/M_.
     *
     *   @param phase is the angle in radians at which the probability density is to be
     *     returned.
     *
     *   @return The value of the probability density at the given phase.
     */
    double getDensity(double phase) const;

    /**
     * getScaledDensity
     *
     *   Returns the value of the probability density at a given phase with the
     *   magnification taken into account; the value returned will correspond to the value
     *   of the un-contracted (M_=1) density at phase, even if the current density is
     *   contracted.
     *
     *   @param phase is the angle in radians at which the probability density is to be
     *     returned.
     *
     *   @return The value of the probability density at the given phase.
     */
    double getScaledDensity(double phase) const;

    /**
     * getPhaseEst
     *
     *   @return This method returns the current estimate of the phase, given by the mean
     *   of the current probability density. The returned value will still correspond to
     *   the full range estimate even when the probability density is contracted (M_ > 1),
     *   i.e. if theta_hat is the estimate given by the mean of the contracted density,
     *   then the returned value is (phi0_ + (theta_hat mod 2*pi)/M_) mod 2*pi.
     */
    double getPhaseEst() const;

    /**
     * getPhaseEstPeak
     *
     *   This method is the same as getPhaseEst except that the returned value corresponds
     *   to the location peak of the probability density rather than the mean.
     */
    double getPhaseEstPeak() const;

    /**
     * shift
     *
     *   Shifts the (contracted) probability density function by a given angle. Since this
     *   shifts the contracted density, the corresponding shift in the phase estimate will
     *   be M_ times smaller (at most, but could be less if the phase wraps), where M_ is
     *   the current magnification.
     *
     *   @param phase_shift is the angle by which the probability density is to be shifted
     *     in radians.
     */
    void shift(double phase_shift);

    /**
     * spread
     *
     *   This method spreads the (contracted) probability density function by a given
     *   factor. It does not modify the magnification.
     *
     *   @param r is the factor by which the probability density is to be spread. r must
     *    be positive. A value less(greater) than 1.0 will result in a
     *    decreased(increased) variance.
     */
    void spread(double r);

    /**
     * setUniform
     *
     *   Sets a uniform probability density.
     *
     *   @param reset_M determines if the magnification is changed. If reset_M is true the
     *     magnification is set back to M = 1, otherwise it is left unchanged.
     */
    void setUniform(bool reset_M=false);

    /**
     * setGaussian
     *
     *   Sets the probability density to a Gaussian (normal distribution) with the
     *   specified mean and standard deviation. This method does not change the
     *   magnification and the given mean and standard deviation are interpreted as the
     *   given values divided by the current magnification value.
     *
     *   @param mean is the mean of the Gaussian within the current range. Upon return the
     *     phase estimate will therefore be equal to phi0_ + mean/M_.
     *
     *   @param std is the standard deviation of the Gaussian to be set in the contracted
     *   (i.e. magnefied) probability density. This means the standard deviation in the
     *   full range of the phase will be std/M_.
     */
    void setGaussian(double mean, double std);

    /**
     * getVariance
     *
     *   @return Returns the variance of the current probability density. If the density
     *     is contracted (i.e. magnification M_ > 1) then the effect of the magnification
     *     is taken into account: the returned variance is that of the contracted density
     *     divided by the square of the magnification, M_.
     */
    double getVariance();

    /**
     * getEntropyGain
     *
     *   Returns the expected entropy gain for performing a measurement with the specified
     *   control parameters. If the current density is a contraction (magnification > 1)
     *   this will be taken into account; the given parameters correspond to the
     *   equivalent uncontracted density.
     *
     *   @param meas_angle is the value in radians of the contollable feedback phase that
     *     would be used for the measurement.
     *
     *   @param k is the number of applications of the quantum evolution (for which the
     *     phase is being estimated) that would be used for the next measurement.
     *
     *   @return is the value of the expected entropy gain. If the current density is
     *     contracted then this corresponds to the entropy gain of the contracted part,
     *     i.e. the value is not adjusted to the different scale of the phase used in the
     *     contraction (while this changes the differential entropy it may not affect the
     *     entropy gain).
     */
    double getEntropyGain(double meas_angle, int k);

    /**
     * getVarianceGain
     *
     *   Returns the expected variance gain for performing a measurement with the
     *   specified control parameters. If the current density is a contraction
     *   (magnification > 1) this will be taken into account for the input control
     *   parameters; the given parameters correspond to the equivalent uncontracted
     *   density.
     *
     *   @param meas_angle is the value in radians of the contollable feedback phase that
     *     would be used for the measurement.
     *
     *   @param k is the number of applications of the quantum evolution (for which the
     *     phase is being estimated) that would be used for the next measurement.
     *
     *   @return is the value of the expected variance gain. If the current density is
     *     contracted then this corresponds to the variance gain of the contracted part,
     *     i.e. the value is not adjusted to the different scale of the phase used in the
     *     contraction (for the variance gain the value will be approximately a factor of
     *     M squared larger, where M is the magnification, than the correct value for the
     *     full probability density).
     */
    double getVarianceGain(double meas_angle, int k);

    /**
     * getSharpnessGain
     *
     *   Returns the expected sharpness gain for performing a measurement with the
     *   specified control parameters. If the current density is a contraction
     *   (magnification > 1) this will be taken into account for the input control
     *   parameters; the given parameters correspond to the equivalent uncontracted
     *   density.
     *
     *   @param meas_angle is the value in radians of the contollable feedback phase that
     *     would be used for the measurement.
     *
     *   @param k is the number of applications of the quantum evolution (for which the
     *     phase is being estimated) that would be used for the next measurement.
     *
     *   @return is the value of the expected sharpness gain. If the current density is
     *     contracted then this corresponds to the sharpness gain of the contracted part,
     *     i.e. the value is not adjusted to the different scale of the phase used in the
     *     contraction (for the sharpness gain the value will be larger than the correct
     *     value for the full probability density).
     */
    double getSharpnessGain(double meas_angle, int k);

    /**
     * findBestGainAngle
     *
     *   Finds the approximate feedback phase angle at which the expected gain of the type
     *   specified is maximised.
     *
     *   @param k is the number of applications of the quantum evolution (for which the
     *     phase is being estimated) that would be used for the next measurement.
     *
     *   @param gain_type is an integer that must take on one of the values of the enum
     *     gain::Type. @see gain::Type. The value can be ENTROPY, VARIANCE, or SHARPNESS
     *     which will determine the function to be maximised: respectively @see
     *     getEntropyGain, @see getVarianceGain, @see getSharpnessGain.
     *
     *   @return The return value is a struct of type GainPoint that has two members,
     *     angle, and gain, corresponding to the approximate angle that maximises the
     *     gain, and the value of the gain at that point. @see GainPoint. If this is a
     *     contraction, then the returned angle corresponds to the one for the full range
     *     probability density without contraction, i.e. the one to be used in the
     *     experiment (this follows from the fact that the underlying functions being
     *     maximised always take the full range feedback phase angle as input, @see
     *     getEntropyGain, @see getVarianceGain, @see getSharpnessGain).
     */
    GainPoint findBestGainAngle(int k, int gain_type=gain::Type::ENTROPY);

    /**
     * getMultiShotGain
     *
     *   This method returns with gain equal to the expected gain after all measurements
     *   specified by 'k_vals'. The angle returned is just the optimal angle for the first
     *   measurement and should match the value returned by method findBestGainAngle()
     *   (The reason to return it is to not have to call the later method as well after
     *   this one when the angle is needed). The value of the gain returned is the the
     *   expected gain for all measurements where each measurement feedback phase angle is
     *   optimised for a phase density conditioned on a particular measurement
     *   record. Since the possible number of measurement records grows exponentially in
     *   the number of measurements, the computational complexity of this method is
     *   exponential in the size of 'k_vals'.
     *
     *   @param k_vals is a vector containing the number of applications of the quantum
     *     evolution (for which the phase is being estimated) that would be used for each
     *     of the next measurements.
     *
     *   @param gain_type is an integer that must take on one of the values of the enum
     *     gain::Type. @see gain::Type. The value can be ENTROPY, VARIANCE, or SHARPNESS
     *     which will determine the function to be maximised at each measurement:
     *     respectively @see getEntropyGain, @see getVarianceGain, @see getSharpnessGain.
     *
     *   @return The return value is a struct of type GainPoint that has two members,
     *     angle, and gain, corresponding to the approximate angle that maximises the
     *     gain, and the value of the gain at that point. @see GainPoint. If this is a
     *     contraction, then the returned angle corresponds to the one for the full range
     *     probability density without contraction, i.e. the one to be used in the
     *     experiment (this follows from the fact that the underlying functions being
     *     maximised always take the full range feedback phase angle as input, @see
     *     getEntropyGain, @see getVarianceGain, @see getSharpnessGain). The angle
     *     returned is the one for the first measurement. The gain returned is the total
     *     gain for all measurements.
     */
    GainPoint getMultiShotGain(const std::vector<int> &k_vals, int gain_type=gain::Type::ENTROPY);

    /**
     * findBestShotSetting
     *
     *   This method finds the value in the input 'k_vals' that maximises the expected
     *   gain (of the type specified) for the next measurement. The optimal feedback phase
     *   angle for the optimal k-value is also returned and should match the value
     *   returned by method findBestGainAngle() for that k-value. The expected gain
     *   maximised by this method is the one returned by findBestGainAngle() divided by
     *   the weight for that k-value, @see setWeights().
     *
     *   @param k_vals is a vector containing the possible number of applications of the
     *     quantum evolution (for which the phase is being estimated) that would be used
     *     for the next measurement.
     *
     *   @param gain_type is an integer that must take on one of the values of the enum
     *     gain::Type. @see gain::Type. The value can be ENTROPY, VARIANCE, or SHARPNESS
     *     which will determine the function to be maximised: respectively @see
     *     getEntropyGain, @see getVarianceGain, @see getSharpnessGain. The maximum for a
     *     given k-value will be computed using findBestGainAngle(), and the gain to be
     *     optimised over k-values will be this one divided by the corresponding weight
     *     for that k-value @see setWeights().
     *
     *   @param brute_force determines how the optimial k-value is found. If brute_force
     *     is true, a brute force search will be performed: the gain divided by the
     *     corresponding weight for that k-value will be computed for all k-values in
     *     k_vals, and the k-value achieving the maximum will be returned. If brute_force
     *     is false, the k-value returned will be determined by at least one Fibonacci
     *     search over the input k_vals. The number of elements per Fibonacci search is
     *     determined by the memeber parameters MIN_BATCH_SIZE and BATCH_SIZE_STEP as
     *     MIN_BATCH_SIZE + n*BATCH_SIZE_STEP for the n-th search.
     *
     *   @return The return value is a struct of type ShotSetting that has two members,
     *     meas_angle, and k, corresponding to the approximate feedback phase angle and
     *     k-value that maximise the gain divided by the weight. @see ShotSetting. If this
     *     is a contraction, then the returned angle corresponds to the one for the full
     *     range probability density without contraction, i.e. the one to be used in the
     *     experiment (this follows from the fact that the underlying functions being
     *     maximised always take the full range feedback phase angle as input, @see
     *     getEntropyGain, @see getVarianceGain, @see getSharpnessGain).
     */
    ShotSetting findBestShotSetting(const std::vector<int> &k_vals,
                                    int gain_type=gain::Type::ENTROPY, bool brute_force=false);
private:
    void check_k(int k);
    void getSubsets(const std::vector<int> &k_vals,
                    void (PhaseDensity::*get_gain_indices)(int, int, std::vector<int> &),
                    std::list<CoeffSubset> &subsets);
    void getEntropyGainIndices(int k, int N, std::vector<int> &idx);
    void getVarianceGainIndices(int k, int N, std::vector<int> &idx);
    double getNextShotsGain(const std::vector<int> &k_vals,
                            size_t s, double meas_angle, gain::Type gain_type,
                            size_t s_subsets, std::list<CoeffSubset> &subsets);
    void updateSubset(int spin, double meas_angle, int k,
                      const CoeffSubset &prior, CoeffSubset &post);
    void updateSubset(int spin, double meas_angle, int k, CoeffSubset &post);
    double getEntropyGain(double meas_angle, int k, const CoeffSubset &subset);
    double getVarianceGain(double meas_angle, int k, const CoeffSubset &subset);
    double getSharpnessGain(double meas_angle, int k, const CoeffSubset &subset);
    double getPostEntropy(int k, int N, const std::complex<double> &c_k,
                          const std::complex<double> &expAngle);
    std::pair<double,double> getPostProbs(int k, int N, const std::complex<double> &c_k,
                                          const std::complex<double> &expAngle);

    template <typename T>
    void updateSubset(int spin, double meas_angle, int k,
                      int N_prior, const T &prior, CoeffSubset &post);
    template <typename T>
    double getEntropyGain(double meas_angle, int k, int N, const T &cfs);
    template <typename T>
    std::pair<std::complex<double>, std::complex<double>>
    getPostSharpnessTerms(double meas_angle, int k, int N, const T &cfs);
    template <typename T>
    double getVarianceGain(double meas_angle, int k, int N, const T &cfs);
    template <typename T>
    double getSharpnessGain(double meas_angle, int k, int N, const T &cfs);

    GainPoint findBestGainAngle(int k, gain::Type gain_type, const CoeffSubset *subset);

    // Precompute some coefficients for entropy gain calculation.
    void setKDepConsts();
    void setNDepConsts();

    void copyConsts(const PhaseDensity &density);

    // A private constructor that doesn't compute internal constants required for update
    // and gain computation. This saves computation when a temporary instance is used and
    // the update and gain methods are not needed. See setDensity.
    PhaseDensity(int N_max, int M, double phi0);

    int N_max_; // Max number of coefficients.
    int N_; // Used number of coefficients (without counting c0).
    std::vector<std::complex<double>> coeffs_;
    std::vector<double> z_; // Measurement contrasts.
    std::vector<double> lam_; // Measurement symmetries.
    std::vector<double> w_; // Weights of different experiments.
    int K_; // Max repetitions.
    int M_; double phi0_; // Magnification.

    // Some constants for entropy gain computation.
    static constexpr double _2log2_ {2.0 * std::log(2.0)};
    // k-dependent
    std::vector<double> dH0_, x_, y_, u_, v_, xu_, yv_, zu2_, dv2_, B1_;
    // n-dependent
    std::vector<double> aI_, aII_, bI_, bII_;

    static const size_t MIN_BATCH_SIZE {1};
    static const size_t BATCH_SIZE_STEP {1};

    static constexpr double MIN_SPARSITY {0.15};

    static constexpr double LARGE {std::sqrt(std::numeric_limits<double>::max())};
    static constexpr double SMALL {std::sqrt(std::numeric_limits<double>::min())};
    // 10 x (double machine precision: 2.22044604926e-16)
    static constexpr double EPSLN {10*std::numeric_limits<double>::epsilon()};
};

template <typename T>
void PhaseDensity::updateSubset(int spin, double meas_angle, int k,
                                int N_prior, const T &prior, CoeffSubset &post) {
    if (k < 1 || K_ < k) throw std::runtime_error("Invalid k-value.");
    if (post.idx.size() == 0) return; // There is nothing to do.

    if (M_ > 1) {
        check_k(k);
        meas_angle -= k*phi0_;
    }
    const int km {k/M_};

    const int N_post {post.N};
    std::vector<size_t> i_mins;
    FourVector<int> idx_sets;
    getPriorIndexSets(N_prior, N_post, km, post.idx, i_mins, idx_sets);

    post.cfs.resize(post.idx.size());
    size_t j {0};
    if (post.idx[j] == 0) post.cfs[j++] = 1.0;
    while (j < post.cfs.size()) post.cfs[j++] = 0.0;

    const int k1 {k-1};
    if (lam_[k1] <= EPSLN || z_[k1] <= EPSLN) {
        // The measurement gives no information about the phase so the
        // posterior is the same as the prior.
        j = i_mins[0];
        for (int n : idx_sets.v1) post.cfs[j++] += prior[n];
        return;
    }

    // spin = 0 (|0> state) : xi = +1
    // spin = 1 (|1> state) : xi = -1
    const double xi {1.0 - 2.0*static_cast<double>(spin)};
    const double xi_lz {xi*lam_[k1]*z_[k1]};
    const double xi_lz_half {xi_lz / 2.0};
    const double one_xi {1.0 + xi*(1.0 - lam_[k1])};

    const std::complex<double> plusExpAngle {std::polar(1.0, meas_angle)};
    const std::complex<double> xi_lz_half_pExpA {xi_lz_half*plusExpAngle};
    const std::complex<double> xi_lz_half_mExpA {std::conj(xi_lz_half_pExpA)};

    j = i_mins[0];
    for (int n : idx_sets.v1) post.cfs[j++] += one_xi*prior[n];
    j = i_mins[1];
    for (int n : idx_sets.v2) post.cfs[j++] += xi_lz_half_pExpA*prior[n];
    j = i_mins[2];
    // For this set the indices run in oposite order.
    for (int u = static_cast<int>(idx_sets.v3.size()) - 1; u >= 0; --u)
        post.cfs[j++] += xi_lz_half_mExpA*std::conj(prior[idx_sets.v3[u]]);
    j = i_mins[3];
    for (int n : idx_sets.v4) post.cfs[j++] += xi_lz_half_mExpA*prior[n];

    // Unlike the full update, here we don't necessarily have more coefficients in the
    // posterior subset than the prior ones needed to compute them, so there's no
    // particular computational advantage to normalising before adding values to the
    // posterior coefficients. In this case normalising at the end is simpler since we
    // don't need to search for coefficients, even if the prior is a subset.
    double a0 {one_xi};
    if (km <= N_prior)
        a0 += xi_lz*(std::real(prior[km])*std::real(plusExpAngle) -
                     std::imag(prior[km])*std::imag(plusExpAngle));
    j = 0;
    if (post.idx.size())
        if (post.idx[j] == 0) ++j;
    while (j < post.cfs.size()) post.cfs[j++] /= a0;
}

template <typename T>
double PhaseDensity::getEntropyGain(double meas_angle, int k, int N, const T &cfs) {
    if (k < 1 || K_ < k) throw std::runtime_error("Invalid k-value.");
    const int k1 {k-1};
    if (lam_[k1] <= EPSLN || z_[k1] <= EPSLN)
        // Measurement gives no information about the phase.
        return 0;

    double dH {dH0_[k1]};

    if (M_ > 1) {
        check_k(k);
        meas_angle -= k*phi0_;
        k /= M_;
    }

    const std::complex<double> expAngle {std::polar(1.0, meas_angle)};
    const std::complex<double> exp2Angle {expAngle * expAngle};
    std::complex<double> exp2nAngle {1};
    const int _2k {2*k};
    int n_max {N / _2k};

    std::vector<double> Re_c_exp_v(n_max);
    int _2kn {0}, n1 {0} /* n - 1 */;
    for (int n = 1; n <= n_max; ++n) {
        _2kn += _2k;
        exp2nAngle *= exp2Angle;
        Re_c_exp_v[n1++] = (cfs[_2kn]).real() * exp2nAngle.real() -
            (cfs[_2kn]).imag() * exp2nAngle.imag();
    }

    double sumAx {0};
    double zu2n {1};
    n1 = 0;
    for (int n = 1; n <= n_max; ++n) {
        zu2n *= zu2_[k1];
        sumAx += (aI_[n1] + aII_[n1]*x_[k1])*zu2n*Re_c_exp_v[n1];
        ++n1;
    }
    if (lam_[k1] >= 1 - EPSLN) {
        dH += sumAx;
    } else {
        double sumAy {0};
        double dv2n {1};
        n1 = 0;
        for (int n = 1; n <= n_max; ++n) {
            dv2n *= dv2_[k1];
            sumAy += (aI_[n1] + aII_[n1]*y_[k1])*dv2n*Re_c_exp_v[n1];
            ++n1;
        }
        dH += ((2 - lam_[k1])*sumAy + lam_[k1]*sumAx)/2;

        n_max = (N + k) / _2k;
        if (n_max > 0) {
            double Re_c_exp {(cfs[k]).real() * expAngle.real() -
                             (cfs[k]).imag() * expAngle.imag()};
            dH += B1_[k1] * Re_c_exp;
        }
        if (n_max > 1) {
            double sumB {0};
            exp2nAngle = expAngle;
            zu2n = 1; dv2n = 1;
            _2kn = k;
            int n2 {0}; // n - 2
            for (int n = 2; n <= n_max; ++n) {
                _2kn += _2k;
                zu2n *= zu2_[k1];
                const double Bx {(bI_[n2]*u_[k1] + bII_[n2]*xu_[k1]) * zu2n};
                dv2n *= dv2_[k1];
                const double By {(bI_[n2]*v_[k1] + bII_[n2]*yv_[k1]) * dv2n};
                exp2nAngle *= exp2Angle;
                const double Re_c_exp {(cfs[_2kn]).real() * exp2nAngle.real() -
                                       (cfs[_2kn]).imag() * exp2nAngle.imag()};
                sumB += (Bx - By)*Re_c_exp;
                ++n2;
            }
            dH += lam_[k1]*z_[k1]*sumB/4;
        }
    }

    const std::complex<double> c_k {(k <= N) ? cfs[k] : 0.0};
    dH += getPostEntropy(k*M_, N, c_k, expAngle);
    return dH;
}

template <typename T>
std::pair<std::complex<double>, std::complex<double>>
PhaseDensity::getPostSharpnessTerms(double meas_angle_m, int km, int N, const T &cfs) {
    const int k1 {km*M_-1};
    std::pair<std::complex<double>, std::complex<double>> c1_terms(0.0, 0.0);
    if (N > 0) {
        c1_terms.first += (2.0 - lam_[k1])*std::conj(cfs[1]) / 2.0;
        c1_terms.second += lam_[k1]*std::conj(cfs[1]) / 2.0;
    } else {
        throw std::runtime_error("The expected variance or sharpness gain is not well "
                                 "defined for N = 0 (i.e. a uniform distribution). But in "
                                 "any case the optimal parameters for maximising gain with "
                                 "a uniform prior are k = 1 and any measurement angle.");
    }

    const std::complex<double> expAngle {std::polar(1.0, meas_angle_m)};
    if (km < N+2) {
        std::complex<double> coslike_term {expAngle*cfs[km-1]};
        if (km < N)
            coslike_term += std::conj(expAngle*cfs[km+1]);
        coslike_term *= lam_[k1] * z_[k1] / 4.0;
        c1_terms.first += coslike_term;
        c1_terms.second -= coslike_term;
    }
    return c1_terms;
}

template <typename T>
double PhaseDensity::getVarianceGain(double meas_angle, int k, int N, const T &cfs) {
    if (k < 1 || K_ < k) throw std::runtime_error("Invalid k-value.");
    const int k1 {k-1};
    if (lam_[k1] <= EPSLN || z_[k1] <= EPSLN)
        // Measurement gives no information about the phase.
        return 0;

    double dV {0.0};
    if (N > 0)  {
        const double prior_norm {std::norm(cfs[1])};
        if (prior_norm < SMALL)
            dV += LARGE;
        else
            dV += 1.0 / prior_norm;
    }

    if (M_ > 1) {
        check_k(k);
        meas_angle -= k*phi0_;
        k /= M_;
    }
    const std::complex<double> expAngle {std::polar(1.0, meas_angle)};
    const std::complex<double> c_k {(k <= N) ? cfs[k] : 0.0};
    auto pi = getPostProbs(k*M_, N, c_k, expAngle);
    std::pair<std::complex<double>, std::complex<double>> c1_terms
        {getPostSharpnessTerms(meas_angle, k, N, cfs)};
    const double p_norm {std::norm(c1_terms.first)};
    const double m_norm {std::norm(c1_terms.second)};

    if (pi.first > 0.0) {
        if (p_norm <= 0.0) {
            if (dV > std::sqrt(LARGE))
                throw std::range_error("Numeric limits reached: "
                                       "expected variance gain cannot be computed accurately.");
            return -LARGE;
        }
        dV -= std::pow(pi.first, 3.0)/p_norm;
    }
    if (pi.second > 0.0) {
        if (m_norm <= 0.0) {
            if (dV > std::sqrt(LARGE))
                throw std::range_error("Numeric limits reached: "
                                       "expected variance gain cannot be computed accurately.");
            return -LARGE;
        }
        dV -= std::pow(pi.second, 3.0)/m_norm;
    }
    return dV;
}

template <typename T>
double PhaseDensity::getSharpnessGain(double meas_angle, int k, int N, const T &cfs) {
    if (k < 1 || K_ < k) throw std::runtime_error("Invalid k-value.");
    const int k1 {k-1};
    if (lam_[k1] <= EPSLN || z_[k1] <= EPSLN)
        // Measurement gives no information about the phase.
        return 0;

    double dS {0.0};
    if (N > 0)  dS -= std::abs(cfs[1]);

    if (M_ > 1) {
        check_k(k);
        meas_angle -= k*phi0_;
        k /= M_;
    }
    std::pair<std::complex<double>, std::complex<double>> c1_terms
        {getPostSharpnessTerms(meas_angle, k, N, cfs)};
    dS += std::abs(c1_terms.first) + std::abs(c1_terms.second);
    return dS;
}

// #endif /* CTAPE_H */
