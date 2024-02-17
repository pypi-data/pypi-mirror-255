import numpy as np
import pyreprimand as pyr

sol_units = pyr.units.geom_solar()
ref_mg = 1.4
ref_eos = pyr.load_eos_barotr('/home/smeagol/repos/eos_framework/EOS/APR4_Read_PP.eos.h5', sol_units)

ref_seq_acc = pyr.tov_acc_simple(tov=1e-10, deform=1e-8)
ref_seq = pyr.make_tov_branch_stable(ref_eos, ref_seq_acc)

ref_gm1 = ref_seq.center_gm1_from_grav_mass(ref_mg)
ref_rho = ref_eos.rho_at_gm1(ref_gm1)

def mktovadpt(acc, eos=ref_eos, rhoc=ref_rho, tidal_facc=1.0, wdiv=1/1.1):
    acc_tidal = tidal_facc*acc
    tov = pyr.get_tov_star_properties_adaptive(eos, rhoc, acc, acc_tidal, wdiv, False, True, 1e-8)
    return acc, acc_tidal, tov
    
    
mktovadpt(1e-8)

