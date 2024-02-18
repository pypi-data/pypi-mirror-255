import numpy as np
from scipy.stats import norm
import common_library as common_library
import unittest

class TestCommomLibrary(unittest.TestCase):
    """
        Commom library test class
    """

    def test_sampling_result_len(self):
        """
            Test the length of the sampling result
        """
        N_POP = 5
        DEAD_LOAD = ['NORMAL', 7.64, 7.64 * 0.1, 5, None]
        LIVE_LOAD = ['GUMBEL MAX', 1.43 * 0.93, 1.43 * 0.93 * 0.2, 1, None]
        VARS = [DEAD_LOAD, LIVE_LOAD]


        setup = {
                    'number of samples': N_POP, 
                    'number of dimensions': len(VARS), 
                    'numerical model': {'model sampling': 'mcs-time', 'time analysis': 5}, 
                    'variables settings': VARS
                    }

        n_samples = setup['number of samples']
        n_dimensions = setup['number of dimensions']
        model = setup['numerical model']
        variables_settings = setup['variables settings']

        RESULTS = common_library.sampling(n_samples=N_POP, d=len(VARS), model=model, variables_setup=VARS)
        
        self.assertEqual(len(RESULTS), 25, msg="The length of the sampling result must be 25")
        self.assertEqual(len(RESULTS[0]), 3, msg="The length of the sampling result must be 3")