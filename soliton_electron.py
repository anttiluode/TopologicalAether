"""
The Clockfield Soliton Self-Energy Calculation
===============================================

Question: Does a Clockfield NLS soliton naturally produce a finite self-energy 
that matches the QED electron self-energy (specifically, the anomalous magnetic 
moment (g-2)/2)?

Approach:
---------
1. Set up the 3D NLS soliton (Townes profile for the radial part)
2. Compute its gradient energy (β profile)
3. Compute the Clockfield proper-time deficit (the "frozen time" integral)
4. Compare the structure to the QED self-energy corrections

The key insight: in QED, the electron self-energy is infinite for a point particle
and must be renormalized. For a soliton with finite width, the integral converges
naturally. The question is whether the FINITE PART matches what QED gives after
renormalization.

Physical constants (SI):
    m_e = 9.109e-31 kg          (electron mass)
    ℏ = 1.055e-34 J·s           (reduced Planck)
    c = 2.998e8 m/s             (speed of light)
    α_em = 1/137.036            (fine structure constant)
    λ_C = ℏ/(m_e·c) = 3.86e-13 m  (Compton wavelength)
    
QED target:
    (g-2)/2 = α/(2π) + O(α²) ≈ 0.001161...  (Schwinger term)
"""

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq
import json

# ============================================================
# PART 1: The 1D NLS Soliton (exact, as warmup)
# ============================================================

print("=" * 70)
print("PART 1: 1D NLS Soliton — Exact Solution")
print("=" * 70)

# The 1D focusing NLS: iℏₙ ∂φ/∂τ = -(ℏₙ²/2)∂²φ/∂v² - g|φ|²φ
# Soliton: φ(v) = A·sech(Av/ℏₙ)
# We work in natural units where ℏₙ = 1, g = 1

def soliton_1d(v, A=1.0):
    """1D NLS soliton profile"""
    return A / np.cosh(A * v)

def soliton_1d_deriv(v, A=1.0):
    """Derivative of 1D soliton"""
    return -A**2 * np.tanh(A * v) / np.cosh(A * v)

# Gradient energy (β profile) for 1D soliton
def beta_1d(v, A=1.0):
    """β ~ |∇φ|² for 1D soliton"""
    return soliton_1d_deriv(v, A)**2

# Total gradient energy
def total_gradient_energy_1d(A=1.0):
    """∫|∂φ/∂v|² dv for 1D soliton — should be 2A³/3"""
    result, _ = quad(lambda v: beta_1d(v, A), -50, 50)
    return result

# Analytical result: ∫|∂φ/∂v|² dv = 2A³/3
A = 1.0
numerical = total_gradient_energy_1d(A)
analytical = 2 * A**3 / 3
print(f"\n1D Soliton gradient energy (A={A}):")
print(f"  Numerical:  {numerical:.8f}")
print(f"  Analytical: {analytical:.8f}")
print(f"  Ratio:      {numerical/analytical:.8f}")

# Total field energy (kinetic + potential)
# E = ∫[(1/2)|∂φ/∂v|² - (1/2)|φ|⁴] dv = -A³/3
def total_energy_1d(A=1.0):
    integrand = lambda v: 0.5 * soliton_1d_deriv(v, A)**2 - 0.5 * soliton_1d(v, A)**4
    result, _ = quad(integrand, -50, 50)
    return result

E_num = total_energy_1d(A)
E_ana = -A**3 / 3
print(f"\n1D Soliton total energy:")
print(f"  Numerical:  {E_num:.8f}")
print(f"  Analytical: {E_ana:.8f}")

# Clockfield proper time deficit
# Δτ/T = (1/L)∫[1 - exp(-α·β(v))] dv
# For small α: Δτ/T ≈ (α/L)∫β(v) dv = α · (2A³/3) / L
def proper_time_deficit_1d(A=1.0, alpha=1.0, L=100.0):
    """Fraction of proper time frozen by the soliton"""
    integrand = lambda v: 1.0 - np.exp(-alpha * beta_1d(v, A))
    result, _ = quad(integrand, -L/2, L/2)
    return result / L

print(f"\n1D Proper time deficit (α=1):")
for alpha_val in [0.01, 0.1, 1.0, 10.0]:
    deficit = proper_time_deficit_1d(A, alpha_val)
    print(f"  α={alpha_val:5.2f}: Δτ/T = {deficit:.6f}")


# ============================================================
# PART 2: The 3D Radial NLS — Townes Profile
# ============================================================

print("\n" + "=" * 70)
print("PART 2: 3D Radial NLS — The Townes Soliton")
print("=" * 70)

# In 3D, the NLS is: i∂τφ = -(1/2)∇²φ - |φ|²φ
# Radial ansatz: φ(r,τ) = R(r)·exp(iμτ)
# Gives: R'' + (2/r)R' + 2(R³ - μR) = 0
# The Townes profile is the ground state: R(0) = R₀, R'(0) = 0, R(∞) = 0

# Actually, for the 3D focusing NLS, the critical soliton (Townes profile)
# exists only in 2D as the ground state. In 3D, the focusing NLS is
# supercritical — solitons are unstable (they either collapse or disperse).
#
# This is EXACTLY the point made in the paper: n > 2 gives finite-time collapse.
# The electron, if it's a soliton, must be stabilized by something — the 
# biharmonic term (AIS filter), or a saturable nonlinearity, or spin/topology.
#
# Let's work with two models:
# (a) 3D NLS with saturable nonlinearity (physically: the Clockfield can't 
#     freeze time below zero, so β is bounded)
# (b) 3D NLS with biharmonic stabilization (the AIS filter analogue)

print("\nModel A: 3D NLS with saturable nonlinearity")
print("  i∂τφ = -(1/2)∇²φ - |φ|²φ/(1 + σ|φ|²)")
print("  σ controls saturation — at large |φ|, the nonlinearity saturates")

# Radial equation: R'' + (2/r)R' + 2R³/(1+σR²) - 2μR = 0
# Boundary: R'(0) = 0, R(∞) = 0

def townes_ode(r, y, mu, sigma):
    """
    ODE for radial soliton profile in 3D with saturable nonlinearity.
    y = [R, R'], returns [R', R'']
    R'' = -2R'/r - 2R³/(1+σR²) + 2μR
    """
    R, Rp = y
    if r < 1e-12:
        # At r=0, use L'Hôpital: (2/r)R' → 2R''
        # So 3R'' = -2R³/(1+σR²) + 2μR
        Rpp = (-2*R**3/(1+sigma*R**2) + 2*mu*R) / 3.0
    else:
        Rpp = -2*Rp/r - 2*R**3/(1+sigma*R**2) + 2*mu*R
    return [Rp, Rpp]

def shoot_soliton(R0, mu=0.5, sigma=0.1, r_max=30.0):
    """
    Shoot from r=0 with R(0)=R0, R'(0)=0.
    Return R at r_max — want this to be 0 for a soliton.
    """
    sol = solve_ivp(
        townes_ode, [1e-6, r_max], [R0, 0.0],
        args=(mu, sigma), method='RK45',
        max_step=0.05, rtol=1e-10, atol=1e-12
    )
    if sol.success:
        return sol.y[0][-1]
    return 1e10  # Failed

def find_soliton(mu=0.5, sigma=0.1, R0_range=(0.1, 5.0), r_max=30.0):
    """Find R0 that gives R(r_max)=0 (bound state)"""
    # First scan to find sign change
    R0_values = np.linspace(R0_range[0], R0_range[1], 100)
    endpoints = []
    for R0 in R0_values:
        try:
            val = shoot_soliton(R0, mu, sigma, r_max)
            endpoints.append((R0, val))
        except:
            endpoints.append((R0, 1e10))
    
    # Find sign changes
    sign_changes = []
    for i in range(len(endpoints)-1):
        if endpoints[i][1] * endpoints[i+1][1] < 0:
            sign_changes.append((endpoints[i][0], endpoints[i+1][0]))
    
    if not sign_changes:
        return None, None
    
    # Refine the first sign change
    R0_lo, R0_hi = sign_changes[0]
    try:
        R0_sol = brentq(lambda R0: shoot_soliton(R0, mu, sigma, r_max), R0_lo, R0_hi, xtol=1e-8)
        sol = solve_ivp(
            townes_ode, [1e-6, r_max], [R0_sol, 0.0],
            args=(mu, sigma), method='RK45',
            max_step=0.02, rtol=1e-10, atol=1e-12,
            dense_output=True
        )
        return R0_sol, sol
    except:
        return None, None

# Solve for several saturation parameters
print("\nSearching for 3D soliton profiles...")
results = {}

for sigma in [0.01, 0.05, 0.1, 0.5]:
    R0, sol = find_soliton(mu=0.5, sigma=sigma)
    if R0 is not None:
        r = sol.t
        R = sol.y[0]
        Rp = sol.y[1]
        
        # Compute gradient energy: ∫|∇φ|² 4πr² dr = 4π ∫ R'² r² dr
        grad_energy, _ = quad(
            lambda rr: Rp_interp(rr, sol)**2 * rr**2 if rr > 1e-6 else 0,
            1e-6, sol.t[-1]
        ) if False else (0, 0)
        
        # Direct numerical integration using the solution arrays
        dr = np.diff(r)
        grad_e = 4 * np.pi * np.sum(Rp[:-1]**2 * r[:-1]**2 * dr)
        field_e = 4 * np.pi * np.sum(R[:-1]**4 / (1 + sigma*R[:-1]**2) * r[:-1]**2 * dr)
        mass_e = 4 * np.pi * np.sum(R[:-1]**2 * r[:-1]**2 * dr)
        
        results[sigma] = {
            'R0': R0,
            'gradient_energy': grad_e,
            'field_energy': field_e,
            'mass_integral': mass_e,
            'r': r,
            'R': R,
            'Rp': Rp
        }
        
        print(f"\n  σ = {sigma}:")
        print(f"    R(0) = {R0:.6f}")
        print(f"    Gradient energy (4π∫R'²r²dr) = {grad_e:.6f}")
        print(f"    Field energy (4π∫R⁴r²dr/(1+σR²)) = {field_e:.6f}")
        print(f"    Mass integral (4π∫R²r²dr) = {mass_e:.6f}")
    else:
        print(f"\n  σ = {sigma}: No soliton found")


# ============================================================
# PART 3: The Self-Energy Calculation
# ============================================================

print("\n" + "=" * 70)
print("PART 3: Soliton Self-Energy vs QED Self-Energy")
print("=" * 70)

# The QED electron self-energy:
# In QED, the electron interacts with its own electromagnetic field.
# The self-energy Σ(p) contributes to the mass renormalization and
# the anomalous magnetic moment.
#
# The key result (Schwinger, 1948):
#   (g-2)/2 = α/(2π) = 0.0011614...
#
# This comes from a single Feynman diagram: the electron emits and
# reabsorbs a virtual photon. The integral is:
#
#   δm/m = (3α/4π) ln(Λ/m) + finite    [mass renormalization, divergent]
#   (g-2)/2 = α/(2π)                      [anomalous moment, finite]
#
# In the Clockfield framework, the soliton has a natural cutoff:
# the soliton width ~ λ_C = ℏ/(mc). There is no UV divergence
# because the soliton has finite spatial extent.
#
# The question: does the soliton's β profile, when used to compute
# the Clockfield correction to proper time, give a finite answer
# that matches α/(2π)?

alpha_em = 1.0 / 137.036  # Fine structure constant
schwinger = alpha_em / (2 * np.pi)

print(f"\nQED target: (g-2)/2 = α/(2π) = {schwinger:.8f}")
print(f"This is the number we want from the soliton geometry.\n")

# The Clockfield proper-time correction to the soliton's self-interaction:
#
# A soliton of amplitude A and width w ~ 1/A has a β profile:
#   β(r) = |∇φ|²
#
# The proper time experienced by the soliton's own field at position r is:
#   dτ(r) = exp(-α_cf · β(r)) · dt
#
# The self-energy correction is the difference between the soliton's
# energy computed with and without the Clockfield metric:
#
#   δE/E = -⟨1 - Γ(r)⟩_weighted = -∫[1-exp(-α_cf·β(r))] |φ(r)|² d³r / ∫|φ(r)|² d³r
#
# This is the fraction of the soliton's energy that is "frozen" by
# its own Clockfield.

print("Computing self-energy correction for 1D soliton (analytical warmup)...")

# 1D case: φ = sech(v), β = tanh²(v)·sech²(v)
# The weighted proper-time deficit:
#   δE/E = ∫[1-exp(-α·tanh²sech²)] sech² dv / ∫sech² dv

def self_energy_correction_1d(alpha_cf):
    """
    Weighted proper-time deficit for 1D soliton.
    This is the self-energy correction in the Clockfield.
    """
    numerator, _ = quad(
        lambda v: (1.0 - np.exp(-alpha_cf * np.tanh(v)**2 / np.cosh(v)**2)) / np.cosh(v)**2,
        -20, 20
    )
    denominator, _ = quad(lambda v: 1.0/np.cosh(v)**2, -20, 20)  # = 2
    return numerator / denominator

# What value of α_cf gives δE/E = α/(2π)?
print(f"\nSearching for Clockfield coupling α_cf that matches Schwinger term...")
print(f"Target: δE/E = {schwinger:.8f}\n")

# Scan
alpha_cf_values = np.logspace(-3, 2, 1000)
corrections = [self_energy_correction_1d(a) for a in alpha_cf_values]

# Find the crossing
for i in range(len(corrections)-1):
    if corrections[i] <= schwinger <= corrections[i+1]:
        # Interpolate
        alpha_match = np.exp(np.interp(schwinger, 
                                        [corrections[i], corrections[i+1]], 
                                        [np.log(alpha_cf_values[i]), np.log(alpha_cf_values[i+1])]))
        break
else:
    alpha_match = None

if alpha_match:
    print(f"  1D soliton: α_cf = {alpha_match:.6f} gives δE/E = {schwinger:.8f}")
    print(f"  (The matched coupling constant is {alpha_match:.4f})")
else:
    print(f"  No match found in range [{alpha_cf_values[0]:.3f}, {alpha_cf_values[-1]:.3f}]")
    # Print what we get at various α
    for a in [0.001, 0.01, 0.1, 1.0, 10.0]:
        corr = self_energy_correction_1d(a)
        print(f"    α_cf = {a:6.3f}: δE/E = {corr:.8f}")


# ============================================================
# PART 4: The 3D Calculation (the real one)
# ============================================================

print("\n" + "=" * 70)
print("PART 4: 3D Soliton Self-Energy")
print("=" * 70)

# In 3D, we use a Gaussian-stabilized soliton as a model
# (since the pure focusing NLS has no stable 3D soliton).
#
# Model: φ(r) = A · exp(-r²/(2w²))
# This is not an exact NLS solution, but it IS the shape of a
# stabilized soliton (e.g., with saturable nonlinearity or biharmonic term).
#
# The key physical identification:
#   w = λ_C = ℏ/(mc)  (the soliton width is the Compton wavelength)
#   A² = m²c²/ℏ²     (from the mass-amplitude relation)

print("\nUsing Gaussian model soliton: φ(r) = A·exp(-r²/(2w²))")
print("Width w = Compton wavelength = ℏ/(mc)")

# Gradient of Gaussian: ∂φ/∂r = -Ar/w² · exp(-r²/(2w²))
# |∇φ|² = (Ar/w²)² · exp(-r²/w²)
# β(r) = A²r²/w⁴ · exp(-r²/w²)

def beta_3d_gaussian(r, A=1.0, w=1.0):
    """β profile for 3D Gaussian soliton"""
    return (A * r / w**2)**2 * np.exp(-r**2 / w**2)

def self_energy_3d_gaussian(alpha_cf, A=1.0, w=1.0):
    """
    Weighted proper-time deficit for 3D Gaussian soliton.
    δE/E = ∫[1-exp(-α·β(r))] |φ|² 4πr² dr / ∫|φ|² 4πr² dr
    """
    phi_sq = lambda r: A**2 * np.exp(-r**2/w**2)
    numerator, _ = quad(
        lambda r: (1.0 - np.exp(-alpha_cf * beta_3d_gaussian(r, A, w))) * phi_sq(r) * r**2,
        0, 20*w
    )
    denominator, _ = quad(
        lambda r: phi_sq(r) * r**2,
        0, 20*w
    )
    return numerator / denominator

# In natural units (w=1, A=1):
print(f"\n3D Gaussian soliton self-energy correction (natural units, A=w=1):")
for alpha_cf in [0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
    corr = self_energy_3d_gaussian(alpha_cf)
    print(f"  α_cf = {alpha_cf:6.3f}: δE/E = {corr:.8f}  (target: {schwinger:.8f})")

# Find the matching α_cf
alpha_scan = np.logspace(-4, 2, 5000)
corr_scan = [self_energy_3d_gaussian(a) for a in alpha_scan]

for i in range(len(corr_scan)-1):
    if corr_scan[i] <= schwinger <= corr_scan[i+1]:
        alpha_match_3d = np.exp(np.interp(schwinger,
                                           [corr_scan[i], corr_scan[i+1]],
                                           [np.log(alpha_scan[i]), np.log(alpha_scan[i+1])]))
        break
else:
    alpha_match_3d = None

if alpha_match_3d:
    corr_check = self_energy_3d_gaussian(alpha_match_3d)
    print(f"\n  *** Match found: α_cf = {alpha_match_3d:.8f} gives δE/E = {corr_check:.8f}")
    print(f"  *** Target was:  δE/E = {schwinger:.8f}")
    print(f"  *** Ratio α_cf to α_em: {alpha_match_3d / alpha_em:.4f}")


# ============================================================
# PART 5: Can α_cf = α_em work directly?
# ============================================================

print("\n" + "=" * 70)
print("PART 5: What if α_cf IS the fine structure constant?")
print("=" * 70)

# The most elegant result would be α_cf = α_em = 1/137.
# Does δE/E(α_em) give something meaningful?

corr_at_alpha = self_energy_3d_gaussian(alpha_em)
print(f"\n  α_cf = α_em = {alpha_em:.6f}")
print(f"  δE/E = {corr_at_alpha:.10f}")
print(f"  α/(2π) = {schwinger:.10f}")
print(f"  Ratio: δE/E / [α/(2π)] = {corr_at_alpha / schwinger:.6f}")

# Now try with amplitude A determined by the physical identification:
# The soliton amplitude in Compton units (w = λ_C = 1):
# A² = field energy density at center
# For the electron: A² ~ α_em (the electromagnetic coupling)
# This is because the electromagnetic self-energy is O(α_em)

print(f"\n  With A² = α_em (electromagnetic soliton amplitude):")
corr_em = self_energy_3d_gaussian(1.0, A=np.sqrt(alpha_em), w=1.0)
print(f"  δE/E = {corr_em:.10f}")
print(f"  Ratio to α/(2π): {corr_em / schwinger:.6f}")


# ============================================================
# PART 6: The Deeper Structure — Shape-Dependent Calculation
# ============================================================

print("\n" + "=" * 70)
print("PART 6: Shape Dependence — Different Soliton Profiles")
print("=" * 70)

# The result depends on the soliton shape. Let's try several:

def self_energy_general(alpha_cf, profile='gaussian', A=1.0, w=1.0):
    """
    Self-energy for different soliton profiles.
    All profiles are normalized to have the same total "mass" (∫|φ|²4πr²dr).
    """
    if profile == 'gaussian':
        phi = lambda r: A * np.exp(-r**2/(2*w**2))
        dphi = lambda r: -A * r/w**2 * np.exp(-r**2/(2*w**2))
    elif profile == 'sech':
        phi = lambda r: A / np.cosh(r/w) if r > 0 else A
        dphi = lambda r: -A/(w) * np.tanh(r/w) / np.cosh(r/w) if r > 0 else 0
    elif profile == 'exponential':
        phi = lambda r: A * np.exp(-r/w)
        dphi = lambda r: -A/w * np.exp(-r/w)
    elif profile == 'yukawa':
        # φ = A·exp(-r/w)/r — Yukawa-like, matches QED propagator
        phi = lambda r: A * np.exp(-r/w) / max(r, 0.01*w)
        dphi = lambda r: -A * np.exp(-r/w) * (1/max(r, 0.01*w)**2 + 1/(w*max(r, 0.01*w)))
    
    beta = lambda r: dphi(r)**2
    phi_sq = lambda r: phi(r)**2
    
    num, _ = quad(lambda r: (1.0 - np.exp(-alpha_cf * beta(r))) * phi_sq(r) * r**2,
                  0.001*w, 30*w, limit=200)
    den, _ = quad(lambda r: phi_sq(r) * r**2, 0.001*w, 30*w, limit=200)
    
    return num / den

print(f"\nSelf-energy correction for different profiles (α_cf=1, A=1, w=1):")
for profile in ['gaussian', 'sech', 'exponential']:
    try:
        corr = self_energy_general(1.0, profile)
        print(f"  {profile:15s}: δE/E = {corr:.8f}")
    except Exception as e:
        print(f"  {profile:15s}: Error — {e}")

# For each profile, find the α_cf that matches Schwinger
print(f"\nMatching α_cf for each profile to give δE/E = α/(2π):")
for profile in ['gaussian', 'sech', 'exponential']:
    try:
        # Binary search
        lo, hi = 1e-4, 100.0
        for _ in range(100):
            mid = np.sqrt(lo * hi)
            corr = self_energy_general(mid, profile)
            if corr < schwinger:
                lo = mid
            else:
                hi = mid
        print(f"  {profile:15s}: α_cf = {mid:.6f}, δE/E = {corr:.8f}")
    except Exception as e:
        print(f"  {profile:15s}: Error — {e}")


# ============================================================
# PART 7: The Key Test — Does the RATIO work?
# ============================================================

print("\n" + "=" * 70)
print("PART 7: The Ratio Test — Electron vs Muon")
print("=" * 70)

# If the framework is right, the SAME α_cf should work for both
# electron and muon, with only the soliton amplitude changing.
#
# m_μ/m_e = 206.768
# In the Clockfield: A_μ/A_e = √(m_μ/m_e) = √206.768 ≈ 14.38
#
# But (g-2)/2 for the muon includes the same Schwinger term α/(2π)
# PLUS a different set of higher-order corrections (because the
# muon's larger mass gives access to different virtual states).
#
# QED predicts: (g-2)_μ / (g-2)_e = 1 + (m_μ/m_e)² × (higher order stuff)
# But the leading term α/(2π) is UNIVERSAL — same for e and μ.
#
# In the Clockfield: the self-energy correction depends on α_cf AND on A and w.
# For universality, we need δE/E to be independent of A when α_cf and the
# physics are held fixed.

mass_ratio = 206.768
A_e = 1.0
A_mu = np.sqrt(mass_ratio)
w_e = 1.0  # Compton wavelength of electron (natural units)
w_mu = 1.0 / np.sqrt(mass_ratio)  # Compton wavelength of muon (smaller by √(m_μ/m_e))

# Wait — in natural units where w = ℏ/(mc), if m is larger, w is smaller.
# And A ∝ m, so A·w = ℏ/c = const.
# The β profile is β = (Ar/w²)²exp(-r²/w²) = (A/w)² · (r/w)² · exp(-(r/w)²)
# Since A·w = const, A/w = A²/const ∝ m², and the β profile scales as m⁴ 
# times a universal function of r/w.
# 
# Actually, let me think about this more carefully in physical units.

print("\nScaling analysis:")
print(f"  m_μ/m_e = {mass_ratio:.3f}")
print(f"  A_μ/A_e = √(m_μ/m_e) = {np.sqrt(mass_ratio):.3f}")
print(f"  w_μ/w_e = √(m_e/m_μ) = {1/np.sqrt(mass_ratio):.5f}")
print(f"  β_max(μ)/β_max(e) = (A_μ/w_μ²)² / (A_e/w_e²)² = (m_μ/m_e)^3 = {mass_ratio**3:.1f}")

# The self-energy correction for both particles
if alpha_match_3d:
    corr_e = self_energy_3d_gaussian(alpha_match_3d, A=A_e, w=w_e)
    corr_mu = self_energy_3d_gaussian(alpha_match_3d, A=A_mu, w=w_mu)
    print(f"\n  Using α_cf = {alpha_match_3d:.6f} (matched to electron):")
    print(f"    δE/E (electron) = {corr_e:.10f}")
    print(f"    δE/E (muon)     = {corr_mu:.10f}")
    print(f"    Ratio μ/e       = {corr_mu/corr_e:.6f}")
    print(f"    (Should be ~1 if the leading term is universal)")


# ============================================================
# PART 8: The Honest Assessment
# ============================================================

print("\n" + "=" * 70)
print("PART 8: Honest Assessment")
print("=" * 70)

print("""
WHAT THE CALCULATION SHOWS:
===========================

1. The soliton self-energy integral CONVERGES (no UV divergence).
   This is the key structural result: a soliton doesn't need 
   renormalization. The Clockfield's frozen-time mechanism provides 
   a natural cutoff at the soliton width ~ Compton wavelength.

2. The self-energy correction δE/E has the form:
   δE/E = f(α_cf, shape) 
   where f is a pure number determined by the Clockfield coupling 
   and the soliton profile.

3. There EXISTS a value of α_cf that matches α/(2π) for any given 
   profile. But this is not a prediction — it's curve-fitting with 
   one free parameter.

WHAT WOULD BE A GENUINE PREDICTION:
====================================

For the framework to predict (g-2)/2 = α/(2π), it would need:
(a) A derivation of the soliton profile from first principles
    (not a choice between Gaussian, sech, exponential, etc.)
(b) A derivation of α_cf from the framework's axioms
(c) The combination to give exactly α/(2π)

Currently, we can MATCH the answer but not DERIVE it.

THE STRUCTURAL INSIGHT THAT SURVIVES:
======================================

Even without deriving the exact value, the framework provides:
- A finite self-energy where QED has an infinite one
- A geometric interpretation: the self-energy is "frozen time"
- A natural cutoff: the soliton width (no arbitrary Λ)
- The FORM δE/E ~ α_cf × (geometric factor) matches QED's 
  structure δm/m ~ α × (log factor)

THE KEY OBSTRUCTION:
=====================

The soliton self-energy is NOT the anomalous magnetic moment.
The anomalous magnetic moment comes from the vertex correction 
(the electron's interaction with an EXTERNAL magnetic field, 
modified by virtual photon exchange). The self-energy is the 
mass renormalization (how the electron's own field modifies its 
mass).

These are different Feynman diagrams:
- Self-energy: electron → photon → electron (bubble on propagator)
- Vertex: electron + photon → electron (triangle diagram)

The Schwinger result α/(2π) comes from the vertex, not the 
self-energy. To get g-2 from the Clockfield, you'd need to 
compute how the soliton's β profile modifies its response to 
an external field — a DIFFERENT calculation from what we did.

HONEST BOTTOM LINE:
====================

The calculation demonstrates that the soliton framework eliminates 
UV divergences (a genuine structural advantage). But it does not 
derive the anomalous magnetic moment. The specific number α/(2π) 
requires the vertex correction, not the self-energy, and the 
Clockfield framework doesn't yet have the machinery for external 
field interactions at this level of detail.

The path forward would be:
1. Define what "external field" means for a Clockfield soliton
2. Compute the soliton's response (gyromagnetic ratio) in the 
   presence of an external Clockfield gradient
3. Show that the response differs from the naive value by α/(2π)

This is a well-defined calculation but requires extending the 
framework significantly.
""")


# ============================================================
# PART 9: What CAN we compute — the mass ratio prediction
# ============================================================

print("=" * 70)
print("PART 9: A Calculation That IS Within Reach — Mass Ratios")
print("=" * 70)

print("""
The framework makes a specific prediction about particle mass ratios.

If particles are NLS solitons stabilized by topological charge (Hopf 
fibration), then the available masses are determined by the allowed 
soliton amplitudes, which are set by the topology.

For a Hopf-fibered vortex in 3D:
- The fundamental (n=1) vortex has some base amplitude A₁
- Excited states (n=2, 3, ...) have amplitudes A_n = A₁ · f(n)
  where f(n) depends on the specific stabilization mechanism

For the simplest case (harmonic trap stabilization):
  E_n ∝ n + 3/2  (3D harmonic oscillator)
  m_n ∝ n + 3/2

For Coulomb-like stabilization:
  E_n ∝ 1/n²
  
For topological (Skyrme-like) stabilization:
  E_n ∝ n^(2/3)  (the Faddeev-Niemi scaling)
""")

# Test: do any simple power laws give the lepton mass ratios?
m_e = 0.511  # MeV
m_mu = 105.658
m_tau = 1776.86

print(f"Lepton masses: e={m_e}, μ={m_mu}, τ={m_tau} MeV")
print(f"Mass ratios: μ/e = {m_mu/m_e:.2f}, τ/e = {m_tau/m_e:.2f}, τ/μ = {m_tau/m_mu:.2f}")

# Koide formula (empirical, known since 1981)
koide = (m_e + m_mu + m_tau) / (np.sqrt(m_e) + np.sqrt(m_mu) + np.sqrt(m_tau))**2
print(f"\nKoide ratio: (m_e + m_μ + m_τ) / (√m_e + √m_μ + √m_τ)² = {koide:.6f}")
print(f"Koide prediction: 2/3 = {2/3:.6f}")
print(f"Difference: {abs(koide - 2/3):.6f} ({abs(koide - 2/3)/(2/3)*100:.3f}%)")

print("""
The Koide formula gives (m_e + m_μ + m_τ)/(√m_e + √m_μ + √m_τ)² = 2/3 
to within 0.03%. This has no explanation in the Standard Model.

In the Clockfield, if mass ∝ A² (soliton amplitude squared), then 
√m ∝ A, and the Koide formula becomes:

  (A_e² + A_μ² + A_τ²) / (A_e + A_μ + A_τ)² = 2/3

This is a constraint on the amplitude ratios. For three amplitudes 
(A₁, A₂, A₃), the quantity Σ(Aᵢ²)/(ΣAᵢ)² = 2/3 when the amplitudes 
are equally spaced on a circle of radius R centered at (R, 0) in the 
complex plane. That is:

  A_k = R(1 + cos(2πk/3 + δ))

for some phase offset δ. This is a GEOMETRIC constraint — it says the 
three lepton amplitudes lie on a circle in amplitude space.

In Clockfield language: the three generations of leptons correspond to 
three equally-spaced phase positions on the soliton's internal Hopf 
fiber. The mass hierarchy comes from the cosine modulation of the base 
amplitude by the topological phase.
""")

# Compute the Koide circle parameters
# If A_k = R(1 + cos(2πk/3 + δ)), then m_k = A_k² = R²(1 + cos(θ_k))²
# With √m_k = R(1 + cos(θ_k)), we need:
# √m_e = R(1 + cos(δ))
# √m_μ = R(1 + cos(2π/3 + δ))  
# √m_τ = R(1 + cos(4π/3 + δ))

sqrt_me = np.sqrt(m_e)
sqrt_mmu = np.sqrt(m_mu)
sqrt_mtau = np.sqrt(m_tau)

# Sum = R·Σ(1+cos(θ_k)) = 3R (since Σcos(2πk/3+δ) = 0)
R = (sqrt_me + sqrt_mmu + sqrt_mtau) / 3
print(f"Koide circle radius R = {R:.4f} √MeV")

# Individual phases
# 1 + cos(θ_k) = √m_k / R
cos_e = sqrt_me / R - 1
cos_mu = sqrt_mmu / R - 1
cos_tau = sqrt_mtau / R - 1

print(f"cos(θ_e) = {cos_e:.6f}")
print(f"cos(θ_μ) = {cos_mu:.6f}")
print(f"cos(θ_τ) = {cos_tau:.6f}")

# Check: these should satisfy cos(θ_e) + cos(θ_μ) + cos(θ_τ) = 0
print(f"Sum of cosines = {cos_e + cos_mu + cos_tau:.6f} (should be 0)")

# Find the phase offset δ
# cos(δ) = cos_e, so δ = arccos(cos_e)
if abs(cos_e) <= 1:
    delta = np.arccos(cos_e)
    print(f"\nPhase offset δ = {delta:.6f} rad = {np.degrees(delta):.2f}°")
    
    # Check the other phases
    theta_mu = 2*np.pi/3 + delta
    theta_tau = 4*np.pi/3 + delta
    pred_cos_mu = np.cos(theta_mu)
    pred_cos_tau = np.cos(theta_tau)
    print(f"Predicted cos(θ_μ) = {pred_cos_mu:.6f} (actual: {cos_mu:.6f})")
    print(f"Predicted cos(θ_τ) = {pred_cos_tau:.6f} (actual: {cos_tau:.6f})")
    
    # Predicted masses from the Koide circle
    pred_m_e = (R * (1 + np.cos(delta)))**2
    pred_m_mu = (R * (1 + np.cos(2*np.pi/3 + delta)))**2
    pred_m_tau = (R * (1 + np.cos(4*np.pi/3 + delta)))**2
    
    print(f"\nPredicted masses from Koide circle:")
    print(f"  m_e   = {pred_m_e:.4f} MeV (actual: {m_e})")
    print(f"  m_μ   = {pred_m_mu:.3f} MeV (actual: {m_mu})")
    print(f"  m_τ   = {pred_m_tau:.2f} MeV (actual: {m_tau})")


# Final summary
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
print(f"""
1. SOLITON SELF-ENERGY: Converges naturally (no renormalization needed).
   The Clockfield provides a built-in UV cutoff at the soliton width.
   This is a genuine structural advantage over point-particle QFT.

2. ANOMALOUS MAGNETIC MOMENT: Cannot be computed from self-energy alone.
   Would require vertex correction (soliton response to external field).
   The calculation is well-defined but not yet performed.

3. MASS RATIOS: The Koide formula has a natural interpretation as 
   three solitons with equally-spaced phases on a Hopf fiber circle.
   Phase offset δ ≈ {np.degrees(delta) if abs(cos_e) <= 1 else '?'}° determines all three lepton masses.
   
4. THE HONEST RESULT: We cannot derive α/(2π) from the Clockfield.
   We CAN show that:
   - Soliton self-energies are finite (structural improvement)
   - There exists a coupling that matches Schwinger (not predictive)
   - The Koide formula gets a geometric interpretation (suggestive)
   - The framework needs external-field response theory to go further
""")
