import numpy as np
import pickle
from ase.dft import kpoints
import pygrisb.gutz.gparam as gp
import pygrisb.gutz.atoms as gatoms
import pygrisb.model.tbASE as tb
import pygrisb.mbody.coulomb_matrix as cm
import pygrisb.symm.angular_momentum as am


def gutz_model_setup(u=0.5, v=.4, eta_f=0., eps_c=0., spindeg=True,
        iembeddiag=-3, kps_size = (20, 20, 20),
        dtype=np.float):
    '''Set up Gutzwiller calculations for periodic anderson model
    in simple cubic lattice in grand canonical ensemble.

    Parameters:

    * u: real number
      Hubbard U.
    * eta_f: real number
      eta_f := 1 + 2eps_f/U
    * spindeg: boolean number
      whether to keep spin degeneracy or not.
    * iembeddiag: integer
      flag for method to solve the embedding Hamiltonian.

      * -3: valence truncation ED with S=0 (spin-singlet) constraint;
      * -2: valence truncation ED with Sz symmetry;
      * -1: valence truncation ED;
      * 10: Hartree-Fock.

    Result:

    Create all the necessary input file of ``GBareH.h5`` and ``GParam.h5``
    for *CyGutz* calculation.
    '''

    # One pseudo "H" atoms in the square unit cell
    symbols=['H']
    scaled_positions=[(0, 0, 0)]
    cell = np.identity(3)
    a = tb.AtomsTB(symbols=symbols, scaled_positions=scaled_positions,
            cell=cell)

    # set spin degeneracy accordingly.
    a.set_orbitals_spindeg(orbitals=[("f","s")], spindeg=spindeg)

    # create a tight-binding model class given the AtomsTB.
    aTB = tb.TB(a)

    # set real space (nearest neighbour) hopping elements.
    # used convention in D. E. Logan, M. R. Galpin, and J. Mannouch, J.
    # Phys.: Condens. Matter 28, 455601 (2016).
    # t* = 1
    # t = t*/(2sqrt(Zc)), with Zc = 6 for simple cubic lattice.
    t = -1./(2*np.sqrt(6.))
    eps_f = (eta_f-1)*u/2.
    aTB.set_hop([
            (( 0, 0, 0),0, 0, eps_f),
            (( 0, 0, 0),1, 1, eps_c),
            (( 0, 0, 0),0, 1, v),
            (( 0, 0, 0),1, 0, v),
            ((-1, 0, 0),1, 1, t),
            (( 1, 0, 0),1, 1, t),
            (( 0,-1, 0),1, 1, t),
            (( 0, 1, 0),1, 1, t),
            (( 0, 0,-1),1, 1, t),
            (( 0, 0, 1),1, 1, t),
            ])

    # set 2d k-mesh
    kps = kpoints.monkhorst_pack(kps_size)

    # set uniform k-point weight
    num_k = len(kps)
    kps_wt = 1.0 / num_k * np.ones((num_k))
    if aTB.Atoms.spindeg:
        kps_wt *= 2

    # set maximal number of bands (here we have two bands.)
    num_band_max = 2

    # set list of one-body part of the local Hamiltonian (trivial here.)
    h1e_list = [np.array([[eps_f]], dtype=np.complex)
            for symbol in symbols]

    # create ``GBareH.h5`` file
    gbndinfo = gp.gparam_bnds(kps_wt, 0., num_band_max,
            h1e_list=h1e_list,
            ensemble=1,
            )
    gbndinfo.h5save()

    # adding bare Hamiltonian to ``GBareH.h5`` file.
    aTB.save_bareham(kps)

    # get ``GParam.h5`` file
    gatms = gatoms.cor_structure(symbols, scaled_positions, cell)
    gatms.update({
            "dc_mode": 0,
            "imap_list": [0],
            "na2_list": [2],
            "iso": 1,
            "ispin": 1,
            "db2sab_list": [np.eye(1, dtype=dtype)],
            "symbol_matrix_list": [np.arange(1,2).reshape(1,1)],
            "dc_u_avg_list": [0.],
            "dc_j_avg_list": [0.],
            "giembeddiag": iembeddiag,
            "nval_bot_list": [0],
            "nval_top_list": [2],
            })
    gatms.set_full_symm_adaptive_basis()
    # Coulomb matrix
    v2e_1 = np.zeros((1,1,1,1), dtype=dtype)
    v2e_1[0,0,0,0] = u
    v2e_2 = cm.add_spin_comp_to_coul_mat(v2e_1)
    v2e_2 = cm.apply_a4_unitary_trans(v2e_2, gatms.ps["db2sab_list"][0])
    v2e_2 = np.asarray(v2e_2, dtype=dtype)
    gatms.update({"v2e_list": [v2e_2]})
    # local single-particle matrix basis.
    gatms.set_matrix_basis_list(realhemb=dtype==np.float)
    # spin operator
    samop = am.samop_csh2(0.0)
    s_vec = samop.am_op
    gatms.set_s_vec_csh2_list([s_vec])
    gatms.set_sl_vector_sab_list(mode="sz_only")
    gpa = gp.gparam_atms(gatms.ps["na2_list"], gatms.ps)
    gpa.h5save()

    # save the aTB
    with open('aTB.pckl', 'wb') as f:
        pickle.dump([a, aTB], f)


def get_bard_bands():
    '''get bare band structure.
    '''
    # load aTB
    with open('aTB.pckl', 'rb') as f:
        a, aTB = pickle.load(f)

    # k-point path
    kG = [0.0, 0.0, 0]
    kX = [0.5, 0.0, 0]
    kM = [0.5, 0.5, 0]

    # set up a ase.dft.kpoints kpath object
    kps = kpoints.get_bandpath([kG, kX, kM, kG], a.cell)

    # get band structure of a square lattice
    aTB.get_bandstructure(kps, saveto="bare_bands.dat")


if __name__=='__main__':
    gutz_model_setup(eps_c=0)
    get_bard_bands()
