import numpy as np
from angmom_suite.basis import extract_blocks, dissect_array, \
    print_sf_term_content, print_so_term_content, sf2ws, sf2ws_amfi, \
    make_angmom_ops_from_mult, unitary_transform
from angmom_suite.crystal import ProjectModelHamiltonian
from angmom_suite.utils import plot_op
from .extractor import make_extractor


def make_proj_evaluator(h_file, options):
    return ProjectModelHamiltonianMolcas(h_file, options)


class ProjectModelHamiltonianMolcas(ProjectModelHamiltonian):

    def __init__(self, h_file, options):

        angm = make_extractor(h_file, ("rassi", "SFS_angmom"))[()]
        ener = make_extractor(h_file, ("rassi", "SFS_energies"))[()]
        amfi = make_extractor(h_file, ("rassi", "SFS_AMFIint"))[()]

        spin_mult = make_extractor(h_file, ("rassi", "spin_mult"))[()]

        # spin-free energies; reference to ground state of lowest multiplicity
        sf_ener = list(extract_blocks(ener, spin_mult))

        ops = {
            'sf_angm': list(extract_blocks(angm, spin_mult, spin_mult)),
            'sf_mch': list(map(lambda e: np.diag(e - sf_ener[0][0]), sf_ener)),
            'sf_amfi': list(map(list, dissect_array(amfi, spin_mult, spin_mult)))
        }

        sf_mult = dict(zip(*np.unique(spin_mult, return_counts=True)))

        self.comp_thresh = options.pop("comp_thresh")
        self.field = options.pop("field")

        super().__init__(ops, sf_mult, **options)
