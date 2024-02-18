"""
This module contains functions for plotting barrier figures from molcas output
files
"""

from .extractor import make_extractor, read_elec_orb
import angmom_suite.multi_electron as me
import angmom_suite.crystal as crys
import angmom_suite.barrier as bar
import numpy as np
import numpy.linalg as la


def barrier(f_molcas, k_max=0, bz=25E-6, j=None, l=None, s=None,
            trans_colour="#ff0000", state_colour="black", show=False,
            save=True, save_name="barrier.svg",
            xlabel=r"$\langle \hat{J}_{z} \rangle$",
            ylabel=r"Energy (cm$^{-1}$)", yax2_label="Energy (K)",
            yax2=False, yax2_conv=1.4, print_datafile=True, verbose=True):
    """
    Creates barrier figure from CFPs in OpenMOLCAS output file

    Parameters
    ----------
        f_molcas : str
            Name of the MOLCAS output file to read from.
        k_max : int, optional
            Maximum (even) value of k to use in crystal field Hamiltonian
        bz : float, default=25 uT
            Magnetic field strength in z direction in Tesla (x and y are zero)
        j : int, optional
            J quantum number
        l : int, optional
            L quantum number
        s : int, optional
            S quantum number
        trans_colour : str, defualt "#ff0000" (red)
            Hex code or name specifying arrow colours
        state_colour: str, default "black"
            Hex code or name specifying state colours
        show : bool, default False
            If True, show plot on screen - disabled with `ax_in`
        save : bool, default True
            If True, save plot to file - disabled with `ax_in`
        save_name : str, default "barrier.svg"
            Filename for saved image
        yax2 : bool, default False
            If True use secondary y (energy) axis
        yax2_conv : float, default 1.4 (cm-1 --> Kelvin)
            Conversion factor from primary to secondary y axis
        yax2_label : str, default "Energy (K)"
            Label for secondary y axis (requires `yax2=True`)
        xlabel : str, default "$\langle \ \hat{J}_{z} \ \rangle$"
            x label
        ylabel : str, default "Energy (cm$^{-1}$)"
            x label
        print_datafile : bool, default True
            If True, save datafile containing energies, Bz, Jz, k_max
            to barrier_data.dat in execution directory
        verbose : bool, default True
            If True, print all saved filenames to screen
    Returns
    -------
        None
    """ # noqa

    # Calculate J, L, and S quantum numbers using number of active
    # electrons and orbitals, if they are not given
    # This is the Hund's rule ground term
    if not any([j, l, s]):
        _, n_act_elec, _, n_act_orb, _ = read_elec_orb(f_molcas)
        j, l, s = me.hunds_ground_term(n_act_elec, n_act_orb)

    # Check k_max vs specified value of J
    if k_max and k_max > 2*j:
        exit("Error: Inconsistency in k_max and J quantum number")
    # Set max value of k if not given
    elif not k_max:
        k_max = int(2*j)
        k_max -= k_max % 2
        # Set 12 as max possible value
        k_max = min(k_max, 12)

    # Calculate angular momentum, and Stevens, operators
    jx, jy, jz, jp, jm, j2 = crys.calc_ang_mom_ops(j)
    okq = crys.calc_stev_ops(k_max, j, jp, jm, jz)

    # Load CFPs from MOLCAS output file
    CFPs = make_extractor(f_molcas, ('cfp', 'j'))[1]

    # Check CFPs
    if CFPs is None:
        exit("Error: Cannot find CFPs in specified file")
    # Check number of CFPs matches that expected based on k_max
    elif CFPs.size < crys._even_kq_to_num(k_max, -k_max)+1:
        exit("Error: Inconsistency in number of CFPs and J quantum number")

    # Calculate and diagonalise crystal field Hamiltonian
    HCF, cf_val, _ = crys.calc_HCF(j, CFPs, okq[1::2, :, :, :], k_max=k_max)
    # Calculate zeeman Hamiltonian with very small z field
    # to quantise states
    Hzee, _, _ = me.calc_HZee_j(j, l, s, jx, jy, jz, B=[0., 0., bz])

    # Calculate and diagonalise total Hamiltonian
    Htot = HCF + Hzee
    tot_val, tot_vec = la.eigh(Htot)
    tot_val -= tot_val[0]

    # Get expectation values of Jz in CF+Zeeman eigenbasis
    jz_expect = np.diag(np.real(la.inv(tot_vec) @ jz @ tot_vec))

    # Calculate transition probabilities

    # Calculate expectation values of magnetic moment operators for
    # each direction in the eigenbasis of total Hamiltonian
    # ignoring hbar and muB as they are constants
    gJ = me.calc_lande_g(j, l, s)
    Mux = gJ * la.inv(tot_vec) @ jx @ tot_vec
    Muy = gJ * la.inv(tot_vec) @ jy @ tot_vec
    Muz = gJ * la.inv(tot_vec) @ jz @ tot_vec

    # Overall transition probabilties as average of each dipole moment squared
    trans = (np.abs(Mux) ** 2 + np.abs(Muy) ** 2 + np.abs(Muz) ** 2) * 1. / 3.

    # Create barrier figure
    bar.barrier_figure(
        j,
        tot_val,
        jz_expect,
        trans=trans,
        show=show,
        save=save,
        save_name=save_name,
        trans_colour=trans_colour,
        state_colour=state_colour,
        yax2=yax2,
        yax2_conv=yax2_conv,
        yax2_label=yax2_label,
        ylabel=ylabel,
        xlabel=xlabel
    )

    if save and verbose:
        print(
            "Barrier figure saved to {} in ".format(save_name) +
            "execution directory"
        )

    # Create output datafile

    if print_datafile:
        with open("barrier_data.dat", "w") as df:

            df.write("Barrier figure data for {}\n".format(f_molcas))
            df.write("\n")

            df.write("k_max = {:d}\n".format(k_max))

            df.write("Bz = {:.3e} Tesla\n".format(bz))
            df.write("\n")

            df.write("CF Energies with and without Zeeman term (cm^-1)\n")
            df.write("------------------------------------------------\n")
            for wizee, wozee in zip(tot_val, cf_val):
                df.write("{:14.7f}  {:14.7f}\n".format(wizee, wozee))

            df.write("\n")

            df.write("Jz expectation values with Zeeman term:\n")
            df.write("---------------------------------------\n")
            for val in jz_expect:
                df.write("{: .7f}\n".format(val))

    if verbose:
        print("Datafile saved to barrier_data.dat in execution directory")

    return
