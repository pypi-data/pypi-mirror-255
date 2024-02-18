/* Time Adaptive Phase Estimation (TAPE)
   Brennan de Neeve
   August 4, 2020. */

#include "ctape.h"
#include <boost/integer/common_factor.hpp>
#include <boost/math/tools/minima.hpp>
#include <limits>
#include <utility>
#include <cstdint>
#include <iostream>

double betweenZeroAndTwoPi(double phase) {
    const double twoPi {2*M_PI};
    phase = std::fmod(phase, twoPi);
    if (phase < 0.0) phase += twoPi;
    return phase;
}

std::complex<double>& CoeffSubset::operator[](int i) {
    auto res = binarySearch(idx, i);
    if (!res.second) {
        std::stringstream msg; msg << "CoeffSubset: invalid index: " << i;
        throw std::runtime_error(msg.str());
    }
    return cfs[res.first];
}

std::complex<double> CoeffSubset::operator[](int i) const {
    auto res = binarySearch(idx, i);
    if (!res.second) {
        std::stringstream msg; msg << "CoeffSubset: invalid index: " << i;
        throw std::runtime_error(msg.str());
    }
    return cfs[res.first];
}

// Calculate the indices of the coefficients in the prior (in four
// sets since that's more convenient for updating subsets) required to
// compute the posterior coefficients at the given indices. Vector
// 'post_idx' must be sorted in increasing order and contain no
// duplicates.
void getPriorIndexSets(int N, int N_new, int k, const std::vector<int> &post_idx,
                       std::vector<size_t> &i_mins, FourVector<int> &idx_sets) {
    auto getIndicesInRange = [&](size_t i_min, int n_max, std::vector<int> &idx, int offset) {
        auto res = binarySearch(post_idx, n_max);
        size_t i_max {res.first};
        if (res.second) i_max += 1;
        idx.clear();
        if (i_max > i_min) {
            idx.resize(i_max - i_min);
            size_t j {0};
            if (offset == 0) {
                for (size_t i = i_min; i < i_max; ++i)
                    idx[j++] = post_idx[i];
            } else {
                for (size_t i = i_min; i < i_max; ++i)
                    idx[j++] = post_idx[i] + offset;
            }
        }
    };

    i_mins.resize(4);

    auto result = binarySearch(post_idx, 1);
    i_mins[0] = result.first;
    getIndicesInRange(i_mins[0], N, idx_sets.v1, 0);

    i_mins[1] = i_mins[0];
    getIndicesInRange(i_mins[1], N - k, idx_sets.v2, k);

    if (k - N > 1) {
        result = binarySearch(post_idx, k - N);
        i_mins[2] = result.first;
    } else {
        i_mins[2] = i_mins[0];
    }
    std::vector<int> temp;
    getIndicesInRange(i_mins[2], (k - 1 < N_new) ? k - 1 : N_new, temp, -k);
    idx_sets.v3.resize(temp.size());
    size_t m {temp.size()};
    for (size_t j = 0; j < idx_sets.v3.size(); ++j)
        idx_sets.v3[j] = -temp[--m];

    result = binarySearch(post_idx, k);
    i_mins[3] = result.first;
    getIndicesInRange(i_mins[3], N_new, idx_sets.v4, -k);
}

void getPriorIndices(int N, int N_new, int k,
                     const std::vector<int> &post_idx, std::vector<int> &prior_idx) {
    std::vector<size_t> i_mins;
    FourVector<int> idx_sets;
    getPriorIndexSets(N, N_new, k, post_idx, i_mins, idx_sets);
    std::vector<int> temp1, temp2;
    mergeIndices(idx_sets.v1, idx_sets.v2, temp1);
    mergeIndices(idx_sets.v3, idx_sets.v4, temp2);
    mergeIndices(temp1, temp2, prior_idx);
}

PhaseDensity::PhaseDensity(int N_max, int K, int M, double phi0):
    N_max_{N_max}, N_{0}, M_{M}, phi0_{phi0}
{
    if (M_ < 1)
        throw std::runtime_error("M must be larger or equal to 1.");
    phi0_ = betweenZeroAndTwoPi(phi0_);
    set_K(K);
    coeffs_.resize(N_max_+1, 0.0);
    setUniform();
    setNDepConsts();
}

void PhaseDensity::set_K(int K) {
    if (K < 1)
        throw std::runtime_error("K must be larger or equal to 1.");
    if (K > N_max_)
        throw std::runtime_error("N_max must be larger or equal to K.");
    K_ = K;
    z_.assign(K_, 1.0);
    lam_.assign(K_, 1.0);
    w_.assign(K_, 1.0);
    setKDepConsts();
}

int PhaseDensity::get_K() {return K_;}
int PhaseDensity::get_M() {return M_;}
int PhaseDensity::get_phi0() {return phi0_;}

void PhaseDensity::setContrasts(const std::vector<double> &z) {
    if (static_cast<int>(z.size()) != K_)
        throw std::runtime_error("setContrasts: z.size() should be equal to K.");
    for (const auto &val : z)
        if (val < 0.0 || val > 1.0)
            throw std::runtime_error("Constrasts must be in [0,1].");

    z_ = z;
    setKDepConsts();
}

void PhaseDensity::setSymmetries(const std::vector<double> &lam) {
    if (static_cast<int>(lam.size()) != K_)
        throw std::runtime_error("setSymmetries: lam.size() should be equal to K.");
    for (const auto &val : lam)
        if (val < 0.0 || val > 1.0)
            throw std::runtime_error("Symmetries must be in [0,1].");

    lam_ = lam;
    setKDepConsts();
}

void PhaseDensity::setWeights(const std::vector<double> &w) {
    if (static_cast<int>(w.size()) != K_)
        throw std::runtime_error("setWeights: w.size() should be equal to K.");

    w_ = w;
}

void PhaseDensity::setDensity(const PhaseDensity &density, int M) {
    int M_expand {boost::integer::gcd(M_, density.M_)};
    M_expand = boost::integer::gcd(M_expand, M);

    int N_max_expand
        {
            ((N_max_ * M_ / M_expand) > (density.N_max_ * density.M_ / M_expand)) ?
            N_max_ * M_ / M_expand:
            density.N_max_ * density.M_ / M_expand
        };
    PhaseDensity pd(N_max_expand, M_expand, 0.0);

    if (M_ > density.M_) {
        if (M_expand > 1)
            pd.phi0_ = betweenZeroAndTwoPi(density.getPhaseEst() - M_PI/M_expand);
        pd.expandDensity(density, expansion::UNIFORM);
        pd.expandDensity(*this, expansion::SELF_ENVELOPE);
    } else {
        if (M_expand > 1)
            pd.phi0_ = betweenZeroAndTwoPi(getPhaseEst() - M_PI/M_expand);
        pd.expandDensity(*this, expansion::UNIFORM);
        pd.expandDensity(density, expansion::SELF_ENVELOPE);
    }
    if (M_expand == M) {
        copyConsts(density);
        if (pd.N_ > N_max_) {
            N_ = N_max_;
            std::cout << "Warning (setDensity): given density has too few coefficients." << std::endl;
        } else {
            N_ = pd.N_;
        }
        for (int n = 0; n <= N_; ++n)
            coeffs_[n] = pd.coeffs_[n];
        M_ = M;
        phi0_ = pd.phi0_;
    } else {
        contractDensity(pd, M);
        if (N_max_expand > density.N_max_)
            std::cout << "Warning (setDensity): given density has too few coefficients." << std::endl;
        copyConsts(density);
    }
}

void PhaseDensity::contractDensity(const PhaseDensity &density, int M) {
    if (M % density.M_ || M == density.M_)
        throw std::runtime_error("Invalid contraction.");

    M_ = M;
    const int M_rel {M_ / density.M_};
    phi0_ = density.getPhaseEst() - M_PI/M_;

    copyConsts(density);
    N_ = density.N_ / M_rel;

    int j {0};
    for (int n = 0; n <= N_; ++n) {
        coeffs_[n] = density.coeffs_[j];
        j += M_rel;
    }
    shift(M_PI - betweenZeroAndTwoPi(-std::arg(coeffs_.at(1))));
}

void PhaseDensity::contractDensity(int M) {
    if (M % M_ || M == M_)
        throw std::runtime_error("Invalid contraction.");

    const int M_rel {M / M_};
    phi0_ = getPhaseEst() - M_PI/M;
    M_ = M;

    N_ = N_ / M_rel;

    int j {0};
    for (int n = 0; n <= N_; ++n) {
        coeffs_[n] = coeffs_[j];
        j += M_rel;
    }
    shift(M_PI - betweenZeroAndTwoPi(-std::arg(coeffs_.at(1))));
}

void PhaseDensity::expandDensity(const PhaseDensity &density, expansion::Type type) {
    if (density.M_ % M_)
        throw std::runtime_error("Invalid expansion. The magnification of the given "
                                 "density must be a multiple of the magnification "
                                 "of this instance.");

    const double twoPi {2*M_PI};
    const int M_rel {density.M_ / M_};

    if (M_ > 1) {
        // We can check if the more magnefied density is in the range of this one using the
        // cross product of the phasors for the start and end of the range for each density.
        const std::complex<double> phase0_e {std::polar(1.0, phi0_)};
        const std::complex<double> phase1_e {std::polar(1.0, phi0_ + twoPi/M_)};
        const std::complex<double> phase0_c {std::polar(1.0, density.phi0_)};
        const std::complex<double> phase1_c {std::polar(1.0, density.phi0_ + twoPi/density.M_)};
        const double cross0 {std::real(phase0_e)*std::imag(phase0_c) -
                             std::imag(phase0_e)*std::real(phase0_c)};
        const double cross1 {std::real(phase1_c)*std::imag(phase1_e) -
                             std::imag(phase1_c)*std::real(phase1_e)};
        if (cross0 < 0.0 || cross1 < 0.0)
            throw std::runtime_error("Invalid expansion: other density out of range.");
    }

    int n_max = density.N_ * M_rel;
    if (n_max > N_max_) {
        n_max = N_max_;
        std::cout << "Warning: expanding into a density with too few coefficients." << std::endl;
    }

    // Shift the other density to be correctly aligned with this one.
    const double dphi0 {betweenZeroAndTwoPi(density.phi0_ - phi0_)};
    PhaseDensity shifted_density {density};
    shifted_density.shift(betweenZeroAndTwoPi(density.M_*dphi0));

    auto expand_to_this = [&]()
    {
        if (n_max < N_) n_max = N_;
        std::vector<std::complex<double>> c_copy(N_+1);
        for (int n = 0; n <= N_; ++n) c_copy[n] = coeffs_[n];
        for (int n = N_+1; n <= n_max; ++n) coeffs_[n] = 0.0;

        int j_min, j_max, v;
        for (int n = 0; n <= n_max; ++n) {
            j_max = ((N_ - n)/M_rel < shifted_density.N_) ? (N_ - n)/M_rel : shifted_density.N_;

            v = n;
            for (int j = 1; j <= j_max; ++j) {
                v += M_rel;
                coeffs_[n] += c_copy[v] * std::conj(shifted_density.coeffs_[j]);
            }

            j_min = (n / M_rel) + 1;
            j_max = (((N_ + n) / M_rel) < shifted_density.N_) ? (N_ + n) / M_rel : shifted_density.N_;

            v = M_rel*(j_min-1) - n;
            for (int j = j_min; j <= j_max; ++j) {
                v += M_rel;
                coeffs_[n] += std::conj(c_copy[v]) * shifted_density.coeffs_[j];
            }

            j_min = static_cast<int>(std::ceil(static_cast<double>(n - N_) / M_rel));
            if (j_min < 1) j_min = 1;
            j_max = ((n / M_rel) < shifted_density.N_) ? n / M_rel : shifted_density.N_;

            v = n - M_rel*(j_min-1);
            for (int j = j_min; j <= j_max; ++j) {
                v -= M_rel;
                coeffs_[n] += c_copy[v] * shifted_density.coeffs_[j];
            }
        }

        // Normalise.
        for (int n = 1; n <= n_max; ++n)
            coeffs_[n] /= coeffs_[0];
        coeffs_[0] = 1.0;
    };

    switch (type) {
    case expansion::UNIFORM:
        for (int n = 0; n <= n_max; ++n) {
            if (n % M_rel) {
                coeffs_[n] = 0.0;
            } else {
                coeffs_[n] = shifted_density.coeffs_[n / M_rel];
            }
        }
        break;
    case expansion::GAUSSIAN:
        // Set a gaussian with mean at the center of the range of the density to be
        // expanded. This will be used as an envelope in the next step. The standard
        // deviation of the gaussian is set to a sane value, but there's nothing
        // particularly special about this value; it could also be made an argument of the
        // method. Note that this method modifies N_ accordingly.
        setGaussian(M_*dphi0 + M_PI/M_rel, twoPi/(3*M_rel));
        expand_to_this();
        break;
    case expansion::GAUSSIAN_SELF_MEAN:
        setGaussian(betweenZeroAndTwoPi(-std::arg(coeffs_.at(1))), twoPi/(3*M_rel));
        expand_to_this();
        break;
    case expansion::SELF_ENVELOPE:
        expand_to_this();
        break;
    default:
        throw std::runtime_error("Invalid expansion type.");
    }

    N_ = n_max;
}

void PhaseDensity::update(int spin, double meas_angle, int k) {
    if (k < 1 || K_ < k) throw std::runtime_error("Invalid k-value.");
    if (spin != 0 && spin != 1) throw std::runtime_error("Invalid spin (must be 0 or 1).");
    const int k1 {k-1};
    if (z_[k1] <= EPSLN || lam_[k1] <= EPSLN)
        // We don't learn anything from the measurement.
        return;

    // spin = 0 (|0> state) : xi = +1
    // spin = 1 (|1> state) : xi = -1
    const double xi {1.0 - 2.0*static_cast<double>(spin)};
    const double xi_lz {xi*lam_[k1]*z_[k1]};
    const double xi_lz_half {xi_lz / 2.0};
    const double one_xi {1.0 + xi*(1.0 - lam_[k1])};

    if (M_ > 1) {
        check_k(k);
        meas_angle -= k*phi0_;
        k /= M_;
    }
    const std::complex<double> plusExpAngle {std::polar(1.0, meas_angle)};
    const std::complex<double> c_k {(k > N_) ? 0.0 : coeffs_[k]};

    const double a0 {one_xi + xi_lz*(std::real(c_k)*std::real(plusExpAngle) -
                                     std::imag(c_k)*std::imag(plusExpAngle))};

    const int N_new {(N_+k < N_max_) ? N_+k : N_max_};
    std::vector<std::complex<double>> c_norm(N_+1);
    for (int n = 0; n <= N_; ++n)
        c_norm[n] = coeffs_[n] / a0;
    coeffs_[0] = 1.0;
    for (int n = 1; n <= N_new; ++n)
        coeffs_[n] = 0.0;

    int n_min {1}, n_max {N_};

    for (int n = n_min; n <= n_max; ++n)
        coeffs_[n] += one_xi*c_norm[n];

    n_max = N_ - k;
    const std::complex<double> xi_lz_half_pExpA {xi_lz_half*plusExpAngle};
    int nk {n_min + k};
    for (int n = n_min; n <= n_max; ++n)
        coeffs_[n] += xi_lz_half_pExpA*c_norm[nk++];

    if (k-N_ > 1) n_min = k - N_;
    n_max = (k - 1 < N_new) ? k - 1 : N_new;
    const std::complex<double> xi_lz_half_mExpA {std::conj(xi_lz_half_pExpA)};
    int kn {k - n_min};
    for (int n = n_min; n <= n_max; ++n)
        coeffs_[n] += xi_lz_half_mExpA*std::conj(c_norm[kn--]);

    n_min = k; n_max = N_new;
    nk = 0; // n_min - k
    for (int n = n_min; n <= n_max; ++n)
        coeffs_[n] += xi_lz_half_mExpA*c_norm[nk++];

    // Update the number of coefficients used.
    N_ = N_new;
}

std::complex<double> PhaseDensity::getHarmonic(int n) {
    return coeffs_.at(n);
}

void PhaseDensity::setHarmonic(int n, double mag, double phase, int n_max) {
    if (mag > 1.0)
        throw std::runtime_error("Tried to set a coefficient magnitude to be larger than one.");

    coeffs_.at(n) = std::polar(mag, phase);

    if (n_max > N_max_)
        throw std::runtime_error("n_max larger than N_max_: cannot set N_ larger than N_max_.");
    N_ = n_max;
}

double PhaseDensity::getDensity(double phase) const {
    const std::complex<double> plusExpPhase {std::polar(1.0, phase)};
    std::complex<double> _2plusExpNphase {2.0};

    double prob_dens {coeffs_[0].real()};

    for (int n = 1; n <= N_; ++n) {
	_2plusExpNphase *= plusExpPhase;
        prob_dens += (coeffs_[n]*_2plusExpNphase).real();
    }
    return prob_dens;
}

double PhaseDensity::getScaledDensity(double phase) const {
    if (M_ == 1) return getDensity(phase);

    // We can use the cross product to see if the phase is in the domain of the contracted
    // density or not.
    phase = betweenZeroAndTwoPi(phase);
    const std::complex<double> p0 {std::polar(1.0, phi0_)};
    const std::complex<double> p {std::polar(1.0, phase)};
    const std::complex<double> p1 {std::polar(1.0, phi0_ + 2*M_PI/M_)};
    const double cross0 {std::real(p0)*std::imag(p) - std::imag(p0)*std::real(p)};
    const double cross1 {std::real(p)*std::imag(p1) - std::imag(p)*std::real(p1)};
    if (cross0 >= 0.0 && cross1 >= 0.0)
        return M_*getDensity(M_*betweenZeroAndTwoPi(phase - phi0_));
    else
        return 0.0;
}

double PhaseDensity::getPhaseEst() const {
    if (N_ < 1)
        throw std::runtime_error("The phase estimate is undefined for a uniform density.");
    return betweenZeroAndTwoPi(phi0_ + betweenZeroAndTwoPi(-std::arg(coeffs_[1]))/M_);
}

double PhaseDensity::getPhaseEstPeak() const {
    if (N_ < 1)
        throw std::runtime_error("The phase estimate is undefined for a uniform density.");
    const double phase_mean {-std::arg(coeffs_[1])};
    double phase_std;
    const double sharpness {std::norm(coeffs_[1])};
    if (sharpness < SMALL) phase_std = M_PI;
    phase_std = std::sqrt(1.0/sharpness - 1.0);
    if (phase_std > M_PI) phase_std = M_PI;
    auto get_density = [&](double phase) {return -getDensity(phase);};
    const int double_bits {std::numeric_limits<double>::digits / 2};
    // const int float_bits {std::numeric_limits<float>::digits / 2};
    // const int precision_bits {9};
    using boost::math::tools::brent_find_minima;
    std::pair<double, double> r = brent_find_minima(get_density,
                                                    phase_mean - phase_std,
                                                    phase_mean + phase_std, double_bits);
    return betweenZeroAndTwoPi(phi0_ + betweenZeroAndTwoPi(r.first)/M_);
}

void PhaseDensity::shift(double phase_shift) {
    const std::complex<double> expPhase {std::polar(1.0, -phase_shift)};
    std::complex<double> expNphase {1.0};
    for (int n = 1; n <= N_; ++n) {
	expNphase *= expPhase;
	coeffs_[n] *= expNphase;
    }
}

void PhaseDensity::spread(double r) {
    if (r <= 0.0)
        throw std::runtime_error("Tried to spread density with non-positive r value.");
    double mag_factor;
    for (int n = 1; n <= N_; ++n) {
	mag_factor = std::abs(coeffs_[n]);
	if (mag_factor > 1.0e-100) {
	    mag_factor = std::pow(mag_factor, r*r)/mag_factor;
	    coeffs_[n] *= mag_factor;
	} else {
            coeffs_[n] = 0.0;
        }
    }
}

void PhaseDensity::setUniform(bool reset_M) {
    N_ = 0;
    coeffs_[0] = 1.0;
    for (int n = 1; n <= N_max_; ++n)
        coeffs_[n] = 0.0;

    if (reset_M) {
        M_ = 1;
        phi0_ = 0.0;
    }
}

void PhaseDensity::setGaussian(double mean, double std) {
    const double mag {std::exp(-2.0*std*std)};
    const std::complex<double> expPhase {std::polar(1.0, -mean)};
    std::complex<double> expNphase {1.0};
    coeffs_[0] = 1.0;
    double magN {1.0}, magN_N {1.0}, magNm1_N {1.0};
    for (int n = 1; n <= N_max_; ++n) {
        // magN_N = std::pow(mag, n*n);
        // Probably faster implementation:
        magNm1_N = magN_N * magN;
        magN *= mag;
        magN_N = magNm1_N * magN;
        if (magN_N > SMALL) {
            expNphase *= expPhase;
            coeffs_[n] = magN_N*expNphase;
        } else {
            // not recording coefficients with such low magnitudes
            N_ = n-1;
            return;
        }
    }
    N_ = N_max_;
}

double PhaseDensity::getVariance() {
    if (N_ < 1) // i.e. uniform
        return std::numeric_limits<double>::max(); // largest positive value
    const double sharpness {std::norm(coeffs_[1])};
    if (sharpness < SMALL) // i.e. uniform
        return LARGE;
    return (1.0/sharpness - 1.0)/(M_*M_);
}

double PhaseDensity::getEntropyGain(double meas_angle, int k) {
    return getEntropyGain(meas_angle, k, N_, coeffs_);
}

double PhaseDensity::getVarianceGain(double meas_angle, int k) {
    return getVarianceGain(meas_angle, k, N_, coeffs_);
}

double PhaseDensity::getSharpnessGain(double meas_angle, int k) {
    return getSharpnessGain(meas_angle, k, N_, coeffs_);
}

GainPoint PhaseDensity::findBestGainAngle(int k, int gain_type) {
    return findBestGainAngle(k, static_cast<gain::Type>(gain_type), nullptr);
}

// This method returns with gain equal to the expected gain after all measurements
// specified by 'k_vals'. The angle returned is just the optimal angle for the 1st
// measurement and should match the value returned by method 'findBestGainAngle()' (The
// reason to return it is to not have to call the later method as well after this one when
// the angle is needed).
GainPoint PhaseDensity::getMultiShotGain(const std::vector<int> &k_vals, int gain_type) {
    if (k_vals.size() < 2)
        throw std::runtime_error("PhaseDensity method getMultiShotGain()"
                                 " requires at least 2 shots.");

    std::vector<int> km_vals(k_vals.size());
    for (size_t s = 0; s < k_vals.size(); ++s) {
        check_k(k_vals[s]);
        km_vals[s] = k_vals[s]/M_;
    }

    std::list<CoeffSubset> subsets;
    switch (gain_type) {
    case gain::ENTROPY:
        getSubsets(km_vals, &PhaseDensity::getEntropyGainIndices, subsets);
        break;
    case gain::VARIANCE:
    case gain::SHARPNESS:
        getSubsets(km_vals, &PhaseDensity::getVarianceGainIndices, subsets);
        break;
    default:
        throw std::runtime_error("Invalid 'gain_type'.");
    }

    const size_t s_subsets {k_vals.size() - 1 - subsets.size()};
    size_t s {0};
    GainPoint gp {findBestGainAngle(k_vals[s], gain_type)};
    gp.gain += getNextShotsGain(k_vals, s+1, gp.angle,
                                static_cast<gain::Type>(gain_type), s_subsets, subsets);
    return gp;
}

ShotSetting PhaseDensity::findBestShotSetting(const std::vector<int> &k_vals,
                                              int gain_type, bool brute_force) {
    if (k_vals.size() == 0)
        throw std::runtime_error("findBestShotSetting: no k-values.");
    for (auto k : k_vals)
        if (k < 1 || K_ < k)
            throw std::runtime_error("Invalid k-value found in 'k_vals'.");

    auto ss = ShotSetting();
    if (brute_force) {
        GainPoint gp {findBestGainAngle(k_vals[0], gain_type)};
        double max_gain {gp.gain};
        ss.meas_angle = gp.angle;
        ss.k = k_vals[0];
        for (size_t i = 1; i < k_vals.size(); ++i) {
            int k {k_vals[i]};
            gp = std::move(findBestGainAngle(k, gain_type));
            if (gp.gain/w_[k-1] > max_gain) {
                ss.meas_angle = gp.angle;
                ss.k = k;
                max_gain = gp.gain/w_[k-1];
            }
        }
    } else {
        std::function<GainPoint(int)> get_gain {[&](int k) {
            GainPoint gp {findBestGainAngle(k, gain_type)};
            gp.gain /= w_[k-1];
            return gp;
        }};
        std::pair<size_t,GainPoint> max;
        if (k_vals.size() <= MIN_BATCH_SIZE) {
            max = std::move(fibonacciSearchMax(k_vals, get_gain));
            ss.k = k_vals[max.first];
        } else {
            size_t batch_size {MIN_BATCH_SIZE};
            std::vector<int> k_vals_batch;
            k_vals_batch.reserve(k_vals.size()); k_vals_batch.resize(batch_size);
            size_t i {0};
            for (size_t j = 0; j < batch_size; ++j) k_vals_batch[j] = k_vals[i++];
            max = std::move(fibonacciSearchMax(k_vals_batch, get_gain));
            ss.k = k_vals_batch[max.first];
            while (i < k_vals.size()) {
                batch_size += BATCH_SIZE_STEP;
                const size_t num_left {k_vals.size() - i};
                if (batch_size > num_left) batch_size = num_left;
                k_vals_batch.resize(batch_size);
                for (size_t j = 0; j < batch_size; ++j) k_vals_batch[j] = k_vals[i++];
                auto batch_max = fibonacciSearchMax(k_vals_batch, get_gain);
                if (batch_max.second > max.second) {
                    max = std::move(batch_max);
                    ss.k = k_vals_batch[max.first];
                }
            }
        }
        ss.meas_angle = max.second.angle;
    }

    return ss;
}

void PhaseDensity::check_k(int k) {
    if (k % M_) {
        std::stringstream msg;
        msg << "Invalid k-value for a magnification of " << M_
            << ". " << k << " is not a multiple of " << M_ << ".";
        throw std::runtime_error(msg.str());
    }
}

void PhaseDensity::getSubsets(const std::vector<int> &km_vals,
                              void (PhaseDensity::*get_gain_indices)(int, int, std::vector<int> &),
                              std::list<CoeffSubset> &subsets) {
    std::vector<int> N_vals(km_vals.size() - 1);
    N_vals[0] = (N_ + km_vals[0] < N_max_) ? N_ + km_vals[0] : N_max_;
    for (size_t s = 1; s < N_vals.size(); ++s)
        N_vals[s] = (N_vals[s - 1] + km_vals[s] < N_max_) ? N_vals[s - 1] + km_vals[s] : N_max_;

    size_t s {km_vals.size() - 1};

    auto isSparse = [&]() {
        const double sparsity {1.0 - static_cast<double>(subsets.front().idx.size())/N_vals[s - 1]};
        if (sparsity < MIN_SPARSITY) {
            subsets.pop_front();
            return false;
        }
        return true;
    };

    subsets.push_front(CoeffSubset());
    (this->*get_gain_indices)(km_vals[s], N_vals[s - 1], subsets.front().idx);

    if (isSparse()) {
        subsets.front().N = N_vals[s - 1];
        --s;
        while (s > 0) {
            std::vector<int> idx_u, idx_e;
            if (subsets.front().idx.size())
                getPriorIndices(N_vals[s - 1], N_vals[s], km_vals[s], subsets.front().idx, idx_u);
            (this->*get_gain_indices)(km_vals[s], N_vals[s - 1], idx_e);
            subsets.push_front(CoeffSubset());
            mergeIndices(idx_u, idx_e, subsets.front().idx);
            if (!isSparse()) break;
            subsets.front().N = N_vals[s - 1];
            --s;
        }
    }
}

void PhaseDensity::getEntropyGainIndices(int km, int N, std::vector<int> &idx) {
    // Use 0.8*EPSLN to be sure we always have the odd coefficients when we need them. If
    // the comparisons are consistent this should not be scrictly necessary, but lacking
    // the odd coefficients when they're needed would cause the program to crash, and
    // having the coefficients when they're not needed isn't typically going to change the
    // performance significantly. (The point is rather pedantic in any case --
    // measurements with such low values of lamda would probably be absurd; nevertheless,
    // it's best if the code doesn't crash in these sorts of edge cases)
    const bool odd_cfs {lam_[km*M_-1] <= 1 - 0.8*EPSLN};
    const int step {(odd_cfs) ? km : 2*km};
    int num_indices {N/step};
    if (!odd_cfs && N/km > 0) ++num_indices;
    idx.resize(num_indices);
    // If lamda (the symmetry) is less than one, we need coefficients at multiples of km
    // (odd and even multiples), otherwise we only need those at multiples of 2km (only
    // even multiples). But we always need the km-th coefficient to compute the posterior
    // measurement probabilities.
    if (num_indices > 0) idx[0] = km;
    int m_step {(odd_cfs) ? step : 0};
    for (int m = 1; m < num_indices; ++m) {
        m_step += step;
        idx[m] = m_step;
    }
}

void PhaseDensity::getVarianceGainIndices(int km, int N, std::vector<int> &idx) {
    std::vector<int> all_idx((km < 3) ? 3 : 4);
    if (km < 3) {
        all_idx[0] = km-1; all_idx[1] = km; all_idx[2] = km+1;
    } else {
        all_idx[0] = 1; all_idx[1] = km-1; all_idx[2] = km; all_idx[3] = km+1;
    }
    idx.clear(); idx.reserve(4);
    for (const int i : all_idx) if (N >= i) idx.push_back(i);
}

double PhaseDensity::getNextShotsGain(const std::vector<int> &k_vals,
                                      size_t s, double meas_angle, gain::Type gain_type,
                                      size_t s_subsets, std::list<CoeffSubset> &subsets) {
    const int km {k_vals[s - 1]/M_};
    double gain0, gain1;
    int N_prior;
    std::complex<double> c_k {0.0};
    if (s > s_subsets) {
        auto it_post = subsets.begin();
        std::advance(it_post, s - 1 - s_subsets);
        std::function<void(int)> update_subset;
        if (s > s_subsets + 1) {
            update_subset = [&](int spin) {
                auto it_prior = it_post; --it_prior;
                updateSubset(spin, meas_angle, k_vals[s - 1], *it_prior, *it_post);
            };
            auto it_prior = it_post; --it_prior;
            N_prior = it_prior->N;
            if (km <= N_prior)
                c_k = (*it_prior)[km];
        } else {
            update_subset = [&](int spin) {
                updateSubset(spin, meas_angle, k_vals[s - 1], *it_post);
            };
            N_prior = N_;
            if (km <= N_prior)
                c_k = coeffs_[km];
        }
        auto getGain = [&](int spin) {
            update_subset(spin);
            GainPoint gp {findBestGainAngle(k_vals[s], gain_type, &*it_post)};
            if (s+1 < k_vals.size())
                gp.gain += getNextShotsGain(k_vals, s+1, gp.angle, gain_type, s_subsets, subsets);
            return gp.gain;
        };
        gain0 = getGain(0); gain1 = getGain(1);
    } else {
        N_prior = N_;
        if (km <= N_prior)
            c_k = coeffs_[km];
        const int initial_N {N_};
        const std::vector<std::complex<double>> initial_coeffs {coeffs_};
        auto getGain = [&](int spin) {
            update(spin, meas_angle, k_vals[s-1]);
            GainPoint gp {findBestGainAngle(k_vals[s], gain_type)};
            if (s+1 < k_vals.size())
                gp.gain += getNextShotsGain(k_vals, s+1, gp.angle, gain_type, s_subsets, subsets);
            N_ = initial_N;
            coeffs_ = initial_coeffs;
            return gp.gain;
        };
        gain0 = getGain(0); gain1 = getGain(1);
    }
    if (M_ > 1) meas_angle -= k_vals[s-1]*phi0_;
    const std::complex<double> expAngle {std::polar(1.0, meas_angle)};
    auto pi = getPostProbs(k_vals[s-1], N_prior, c_k, expAngle);
    return pi.first*gain0 + pi.second*gain1;
}

void PhaseDensity::updateSubset(int spin, double meas_angle, int k,
                                const CoeffSubset &prior, CoeffSubset &post) {
    updateSubset(spin, meas_angle, k, prior.N, prior, post);
}

void PhaseDensity::updateSubset(int spin, double meas_angle, int k, CoeffSubset &post) {
    updateSubset(spin, meas_angle, k, N_, coeffs_, post);
}

double PhaseDensity::getEntropyGain(double meas_angle, int k, const CoeffSubset &subset) {
    return getEntropyGain(meas_angle, k, subset.N, subset);
}

double PhaseDensity::getVarianceGain(double meas_angle, int k, const CoeffSubset &subset) {
    return getVarianceGain(meas_angle, k, subset.N, subset);
}

double PhaseDensity::getSharpnessGain(double meas_angle, int k, const CoeffSubset &subset) {
    return getSharpnessGain(meas_angle, k, subset.N, subset);
}

double PhaseDensity::getPostEntropy(int k, int N, const std::complex<double> &c_k,
                                    const std::complex<double> &expAngle) {
    auto pi = getPostProbs(k, N, c_k, expAngle);

    double H {0.0};
    if (pi.first > SMALL)
        H -= pi.first * std::log(pi.first);
    if (pi.second > SMALL)
        H -= pi.second * std::log(pi.second);
    return H;
}

std::pair<double,double> PhaseDensity::getPostProbs(int k, int N, const std::complex<double> &c_k,
                                                    const std::complex<double> &expAngle) {
    const int k1 {k-1};
    double z_k_half_cos {(1.0 - lam_[k1])/2};
    if (k/M_ <= N) {
        const double Re_c_exp {c_k.real() * expAngle.real() - c_k.imag() * expAngle.imag()};
        z_k_half_cos += lam_[k1] * z_[k1] * Re_c_exp / 2;
    }
    return std::pair<double,double>(0.5 + z_k_half_cos, 0.5 - z_k_half_cos);
}

GainPoint PhaseDensity::findBestGainAngle(int k, gain::Type gain_type, const CoeffSubset *subset) {
    if (k < 1 || K_ < k) throw std::runtime_error("Invalid k-value.");

    std::function<double(double)> get_gain_k;
    switch (gain_type) {
    case gain::ENTROPY:
        if (subset)
            get_gain_k = [&](double meas_angle) {return -getEntropyGain(meas_angle, k, *subset);};
        else
            get_gain_k = [&](double meas_angle) {return -getEntropyGain(meas_angle, k);};
        break;
    case gain::VARIANCE:
        if (subset)
            get_gain_k = [&](double meas_angle) {return -getVarianceGain(meas_angle, k, *subset);};
        else
            get_gain_k = [&](double meas_angle) {return -getVarianceGain(meas_angle, k);};
        break;
    case gain::SHARPNESS:
        if (subset)
            get_gain_k = [&](double meas_angle) {return -getSharpnessGain(meas_angle, k, *subset);};
        else
            get_gain_k = [&](double meas_angle) {return -getSharpnessGain(meas_angle, k);};
        break;
    default:
        throw std::runtime_error("Invalid gain_type.");
    }

    using boost::math::tools::brent_find_minima;

    // Note from boost website: "Note that in principle, the minima can not be located to
    // greater accuracy than the square root of machine epsilon (for 64-bit double,
    // sqrt(1e-16)≅1e-8), therefore the value of bits will be ignored if it's greater than
    // half the number of bits in the mantissa of T."
    // So double precision: (26 bits)
    // const int double_bits {std::numeric_limits<double>::digits / 2};
    // And float precision: (12 bits)
    // const int float_bits {std::numeric_limits<float>::digits / 2};
    // In practice knowing the angle withing 1 degree is probably good enough. This
    // corresponds to a precision in radians of 2pi/360 = 0.0174533 ~ 2^-6, so 6 bits.
    // const int one_deg_bits {6};
    const int two_deg_bits {5};

    std::pair<double, double> r = brent_find_minima(get_gain_k, 0.0, M_PI, two_deg_bits);
    if (std::abs(r.first - 0.0) < 1e-8 || std::abs(r.first - M_PI) < 1e-8)
        // It's likely that we didn't find the real peak and just got stuck at the boundary.
        r = brent_find_minima(get_gain_k, r.first - M_PI/2.0, r.first + M_PI/2.0, two_deg_bits);
    GainPoint gp; gp.angle = r.first; gp.gain = -r.second;
    if (gp.angle > M_PI) gp.angle -= M_PI;
    else if (gp.angle < 0.0) gp.angle += M_PI;
    return gp;
}

void PhaseDensity::setKDepConsts() {
    x_.resize(K_); y_.resize(K_); u_.resize(K_); v_.resize(K_);
    xu_.resize(K_); yv_.resize(K_); zu2_.resize(K_); dv2_.resize(K_);
    dH0_.resize(K_); B1_.resize(K_);
    int k1 {0}; // k - 1
    for (int k = 1; k <= K_; ++k) {
        const double _2_ml {2 - lam_[k1]};
        const double delta {lam_[k1]*z_[k1]/_2_ml};
        const double z2 {z_[k1]*z_[k1]};
        const double d2 {delta*delta};
        x_[k1] = std::sqrt(1 - z2);
        y_[k1] = std::sqrt(1 - d2);
        const double _1_px {1 + x_[k1]};
        const double _1_py {1 + y_[k1]};
        u_[k1] = 1/_1_px;
        v_[k1] = 1/_1_py;
        xu_[k1] = x_[k1]*u_[k1];
        yv_[k1] = y_[k1]*v_[k1];
        zu2_[k1] = z2*u_[k1]*u_[k1];
        dv2_[k1] = d2*v_[k1]*v_[k1];
        if (lam_[k1] <= EPSLN) {
            dH0_[k1] = 0;
            B1_[k1] = 0;
        } else {
            const double _1_ml {1 - lam_[k1]};
            const double ln_1_px {std::log(_1_px)};
            const double ln_1_py {std::log(_1_py)};
            const double ln_2_ml_l {std::log(_2_ml/lam_[k1])};
            dH0_[k1] = -_2log2_ + 0.5*std::log(1-_1_ml*_1_ml)
                + 0.5*_1_ml*ln_2_ml_l
                + 0.5*_2_ml*(d2*v_[k1] + ln_1_py)
                + 0.5*lam_[k1]*(z2*u_[k1] + ln_1_px);
            if (lam_[k1] >= 1 - EPSLN) {
                B1_[k1] = 0;
            } else {
                B1_[k1] = 0.5*lam_[k1]*z_[k1]
                    *(ln_2_ml_l + ln_1_py - ln_1_px + v_[k1] - u_[k1]);
            }
        }
        ++k1;
    }
}

void PhaseDensity::setNDepConsts() {
    // Maximum number of coefficients needed (for the k = 1 case).
    std::uint64_t n_max {static_cast<std::uint64_t>(N_max_) / 2};
    aI_.resize(n_max); aII_.resize(n_max);
    double _4n2_m1 {3};
    std::uint64_t _8n1_p4 {4};
    if (n_max > 0) {
        aI_[0]  = 1 / _4n2_m1;
        aII_[0] = 2 / _4n2_m1;
    }
    std::uint64_t n1 {1}; // n - 1
    for (std::uint64_t n = 2; n <= n_max; ++n) {
        _8n1_p4 += 8;
        _4n2_m1 += _8n1_p4;
        aI_[n1]  = 1 / (n * _4n2_m1);
        aII_[n1++] = 2 / _4n2_m1;
    }

    bI_.clear(); bII_.clear();
    n_max = static_cast<std::uint64_t>(N_max_ + 1) / 2;
    if (n_max > 1) {
        bI_.resize(n_max-1); bII_.resize(n_max-1);
        double bII_inv {2};
        std::uint64_t _2m {4};
        bI_[0] = 1 / 6.0;
        bII_[0] = 1 / bII_inv;
        std::uint64_t n2 {1}; // n - 2
        for (std::uint64_t n = 3; n <= n_max; ++n) {
            bII_inv += _2m++;
            bI_[n2] = 1 / (bII_inv * _2m++);
            bII_[n2++] = 1 / bII_inv;
        }
    }
}

void PhaseDensity::copyConsts(const PhaseDensity &density) {
    N_max_ = density.N_max_;
    coeffs_.resize(N_max_+1);
    aI_ = density.aI_;
    aII_ = density.aII_;
    bI_ = density.bI_;
    bII_ = density.bII_;

    K_ = density.K_;
    z_ = density.z_;
    lam_ = density.lam_;
    w_ = density.w_;
    K_ = density.K_;
    dH0_ = density.dH0_;
    x_ = density.x_;
    y_ = density.y_;
    u_ = density.u_;
    v_ = density.v_;
    xu_ = density.xu_;
    yv_ = density.yv_;
    zu2_ = density.zu2_;
    dv2_ = density.dv2_;
    B1_ = density.B1_;
}

PhaseDensity::PhaseDensity(int N_max, int M, double phi0) :
    N_max_{N_max}, N_{0}, M_{M}, phi0_{phi0}
{
    if (M_ < 1)
        throw std::runtime_error("M must be larger or equal to 1.");
    phi0_ = betweenZeroAndTwoPi(phi0_);
    set_K(1);
    coeffs_.resize(N_max_+1, 0.0);
    setUniform();
}
