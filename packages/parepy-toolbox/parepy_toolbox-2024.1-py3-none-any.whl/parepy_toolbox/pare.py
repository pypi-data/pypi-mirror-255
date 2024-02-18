"""Parepy toolbox: Probabilistic Approach Reliability Engineering"""
import time
from datetime import datetime
from multiprocessing import Pool

import numpy as np
import pandas as pd

import parepy_toolbox.common_library as parepyco


def sampling_algorithm_structural_analysis(setup):
    """
    This function creates the samples and evaluates the limit state functions for
    structural analysis problems.
    
    See documentation in https://wmpjrufg.github.io/PAREPY/

    Args:
        setup (dict): Setup settings.
        setup keys:
            'objective function' (def): Objective function.
            'number of samples' (int): Number of samples.
            'imension' (int): Number of dimensions.
            'numerical model' (dict): Numerical model settings.
            'variables settings' (list): Variables settings.
            'number of state limit functions or constraints' (int): 
                            Number of state limit functions or constraints.
            'none_variable' (Object or None): None variable. Default is None. 
                            Use in objective function.
            'name simulation' (str): Name simulation.
    
    Returns:    
        results_about_data (dataframe): Results about data.
        failure_prob_list (list): Failure probability list.
        beta_list (list): Beta list.
    """

    try:
        if not isinstance(setup, dict):
            raise TypeError('The setup parameter must be a dictionary.')

        # Keys verification
        for key in setup.keys():
            if key not in ['objective function', 'number of samples', 'number of dimensions', 'numerical model', 'variables settings', 'number of state limit functions or constraints', 'none variable', 'type process', 'name simulation']:
                raise ValueError('The setup parameter must have the following keys:\n- objective function;\n- number of samples;\n- number of dimensions;\n- numerical model;\n- variables settings;\n- number of state limit functions or constraints;\n- none variable;\n - type process;\n- name simulation.') 

        # Objective function verification
        if not callable(setup['objective function']):
            raise TypeError('The objective function parameter must be a function (def).')

        # Number of samples verification
        if not isinstance(setup['number of samples'], int):
            raise TypeError('The Number of samples parameter must be an integer.')

        # Dimension verification
        if not isinstance(setup['number of dimensions'], int):
            raise TypeError('The Dimension parameter must be an integer.')

        # Numerical model verification
        if not isinstance(setup['numerical model'], dict):
            raise TypeError('The Numerical model parameter must be a dictionary.')

        # Variables settings verification
        if not isinstance(setup['variables settings'], list):
            raise TypeError('The Variables settings parameter must be a list.')

        # Number of state limit functions or constraints verification
        if not isinstance(setup['number of state limit functions or constraints'], int):
            raise TypeError('The Number of state limit functions or constraints parameter must be an integer.')

        # General settings
        initial_time = time.time()
        obj = setup['objective function']
        n_samples = setup['number of samples']
        n_dimensions = setup['number of dimensions']
        variables_settings = setup['variables settings']
        n_constraints = setup['number of state limit functions or constraints']
        none_variable = setup['none variable']
        type_process = setup['type process']
        name_simulation = setup['name simulation']

        # Algorithm settings
        model = setup['numerical model']
        algorithm = model['model sampling']
        time_analysis = model['time analysis']

        # Creating samples
        dataset_x = parepyco.sampling(n_samples=n_samples,
                                        d=n_dimensions,
                                        model=model,
                                        variables_setup=variables_settings)

        # Starting variables
        capacity = np.zeros((len(dataset_x), n_constraints))
        demand = np.zeros((len(dataset_x), n_constraints))
        state_limit = np.zeros((len(dataset_x), n_constraints))
        indicator_function = np.zeros((len(dataset_x), n_constraints))

        # Selecting algorithm architecture
        # type_process, FO_TIME = PARE_LIB.GET_type_process(setup, obj, PARE_LIB.SAMPLING, PARE_LIB.EVALUATION_MODEL)

        # Multiprocess Objective Function evaluation
        if type_process.upper() == 'PARALLEL':
            information_model = [[list(i), obj, none_variable] for i in dataset_x]
            with Pool() as pool:
                results = pool.map_async(func=parepyco.evaluation_model, iterable=information_model)
            k = 0
            for result in results.get():
                capacity[k, :] = result[0].copy()
                demand[k, :] = result[1].copy()
                state_limit[k, :] = result[2].copy()
                indicator_function[k, :] = [0 if value <= 0 else 1 for value in result[2]]
                k += 1
        # Singleprocess Objective Function evaluation
        elif type_process.upper() == 'SERIAL':
            for id, sample in enumerate(dataset_x):
                sample_id = sample.copy()
                information_model = [sample_id, obj, none_variable]
                capacity_i, demand_i, state_limit_i = parepyco.evaluation_model(information_model)
                capacity[id, :] = capacity_i.copy()
                demand[id, :] = demand_i.copy()
                state_limit[id, :] = state_limit_i.copy()
                indicator_function[id, :] = [0 if value <= 0 else 1 for value in state_limit_i]

        # Storage all results (horizontal stacking)
        results = np.hstack((dataset_x, capacity, demand, state_limit, indicator_function))

        # Transforming time results in dataframe X_i T_i R_i S_i G_i I_i
        if algorithm.upper() == 'MCS-TIME' or  \
                        algorithm.upper() == 'MCS_TIME' or \
                        algorithm.upper() == 'MCS TIME':
            tam = int(len(results) / n_samples)
            line_i = 0
            line_j = tam
            result_all = []
            for i in range(n_samples):
                i_sample_in_temp = results[line_i:line_j, :]
                i_sample_in_temp = i_sample_in_temp.T
                line_i += tam
                line_j += tam
                i_sample_in_temp = i_sample_in_temp.flatten().tolist()
                result_all.append(i_sample_in_temp)
            results_about_data = pd.DataFrame(result_all)
        else:
            results_about_data = pd.DataFrame(result_all)

        # Rename columns in dataframe
        column_names = []
        for i in range(n_dimensions):
            if algorithm.upper() == 'MCS-TIME' or  \
                                        algorithm.upper() == 'MCS_TIME' or \
                                        algorithm.upper() == 'MCS TIME':
                for j in range(time_analysis):
                    column_names.append('X_' + str(i) + '_t=' + str(j))
            else:
                column_names.append('X_' + str(i))
        if algorithm.upper() == 'MCS-TIME' or \
                                        algorithm.upper() == 'MCS_TIME' or \
                                        algorithm.upper() == 'MCS TIME':
            for i in range(time_analysis):
                column_names.append('STEP_t_' + str(i))
        for i in range(n_constraints):
            if algorithm.upper() == 'MCS-TIME' or \
                                        algorithm.upper() == 'MCS_TIME' or \
                                        algorithm.upper() == 'MCS TIME':
                for j in range(time_analysis):
                    column_names.append('R_' + str(i) + '_t=' + str(j))
            else:
                column_names.append('R_' + str(i))
        for i in range(n_constraints):
            if algorithm.upper() == 'MCS-TIME' or \
                                        algorithm.upper() == 'MCS_TIME' or \
                                        algorithm.upper() == 'MCS TIME':
                for j in range(time_analysis):
                    column_names.append('S_' + str(i) + '_t=' + str(j))
            else:
                column_names.append('S_' + str(i))
        for i in range(n_constraints):
            if algorithm.upper() == 'MCS-TIME' or \
                                        algorithm.upper() == 'MCS_TIME' or \
                                        algorithm.upper() == 'MCS TIME':
                for j in range(time_analysis):
                    column_names.append('G_' + str(i) + '_t=' + str(j))
            else:
                column_names.append('G_' + str(i)) 
        for i in range(n_constraints):
            if algorithm.upper() == 'MCS-TIME' or \
                                        algorithm.upper() == 'MCS_TIME' or \
                                        algorithm.upper() == 'MCS TIME':
                for j in range(time_analysis):
                    column_names.append('I_' + str(i) + '_t=' + str(j))
            else:
                column_names.append('I_' + str(i))
        results_about_data.columns = column_names

        # First Barrier Failure (FBF)
        if algorithm.upper() == 'MCS-TIME' or \
                                        algorithm.upper() == 'MCS_TIME' or \
                                        algorithm.upper() == 'MCS TIME':
            i_columns = []
            for i in range(n_constraints):
                aux_column_names = []
                for j in range(time_analysis):
                    aux_column_names.append('I_' + str(i) + '_t=' + str(j))
                i_columns.append(aux_column_names)

            for i in i_columns:
                matrixx = results_about_data[i].values
                for id, linha in enumerate(matrixx):
                    indice_primeiro_1 = np.argmax(linha == 1)
                    if linha[indice_primeiro_1] == 1:
                        matrixx[id, indice_primeiro_1:] = 1
                results_about_data = pd.concat([results_about_data.drop(columns=i),
                                                pd.DataFrame(matrixx, columns=i)], axis=1)
        else:
            pass

        # Probability of failure and beta index
        if algorithm.upper() == 'MCS-TIME' or \
                                        algorithm.upper() == 'MCS_TIME' or \
                                        algorithm.upper() == 'MCS TIME':
            failure_prob_list = []
            beta_list = []

            for indicator_function_time_step_i in i_columns:
                pf_time = []
                beta_time = []
                for j in indicator_function_time_step_i:
                    n_failure = results_about_data[j].sum()
                    pf_value = n_failure / n_samples
                    beta_value = parepyco.beta_equation(pf_value)
                    pf_time.append(pf_value)
                    beta_time.append(beta_value)
                failure_prob_list.append(pf_time)
                beta_list.append(beta_time)
        else:
            pass

        # Save results in .txt file
        file_name = str(datetime.now().strftime('%Y%m%d-%H%M%S'))
        file_name_txt = name_simulation + '_' + algorithm.upper() + '_' + file_name + ".txt"
        parepyco.export_to_txt(results_about_data, file_name_txt)
        end_time = time.time()
        processing_time = end_time - initial_time

        # Report in command window
        print("PARE^py Report: \n")
        print(f"- Output file name: {file_name_txt}")
        print(f"- Processing time (s): {processing_time}")

        return results_about_data, failure_prob_list, beta_list

    except TypeError as te:
        print(f'Error: {te}')

    except ValueError as ve:
        print(f'Error: {ve}')

    return None, None, None


def concatenates_txt_files_sampling_algorithm_01(files_path, n_constraints, model, name_simulation):

    # set the model
    algorithm = model['model sampling']
    time_analysis = model['time analysis']

    # Start time
    initial_time = time.time()

    # Read txt files and concatenate
    results_about_data = pd.DataFrame()
    for txt_file in files_path:
        temp_df = pd.read_csv(txt_file, delimiter='\t')
        results_about_data = pd.concat([results_about_data, temp_df], ignore_index=True)
    n_samples = results_about_data.shape[0]

    if algorithm.upper() == 'MCS-TIME' or \
                                    algorithm.upper() == 'MCS_TIME' or \
                                    algorithm.upper() == 'MCS TIME':
        i_columns = []
        for i in range(n_constraints):
            aux_column_names = []
            for j in range(time_analysis):
                aux_column_names.append('I_' + str(i) + '_t=' + str(j))
            i_columns.append(aux_column_names)

    # Probability of failure and beta index
    if algorithm.upper() == 'MCS-TIME' or \
                                    algorithm.upper() == 'MCS_TIME' or \
                                    algorithm.upper() == 'MCS TIME':
        failure_prob_list = []
        beta_list = []

        for indicator_function_time_step_i in i_columns:
            pf_time = []
            beta_time = []
            for j in indicator_function_time_step_i:
                n_failure = results_about_data[j].sum()
                pf_value = n_failure / n_samples
                beta_value = parepyco.beta_equation(pf_value)
                pf_time.append(pf_value)
                beta_time.append(beta_value)
            failure_prob_list.append(pf_time)
            beta_list.append(beta_time)
    else:
        pass

    # Save results in .txt file
    file_name = str(datetime.now().strftime('%Y%m%d-%H%M%S'))
    file_name_txt = name_simulation + '_' + algorithm.upper() + '_' + file_name + ".txt"
    parepyco.export_to_txt(results_about_data, file_name_txt)
    end_time = time.time()
    processing_time = end_time - initial_time

    # Report in command window
    print("PARE^py Report: \n")
    print(f"- Output file name: {file_name_txt}")
    print(f"- Processing time (s): {processing_time}")

    return results_about_data, failure_prob_list, beta_list


    """   
    #EASY PLOT LIB
        pf_over_time_df = pd.DataFrame({
            'x0': range(time_analysis),
            'y0': pf_list[0]
        })

        beta_over_time_df = pd.DataFrame({
            'x0': range(time_analysis),
            'y0': beta_list[0]
        })

    CHART_CONFIG_PF = {
        'NAME': 'Pf values over time',
        'WIDTH': 15.,
        'HEIGHT': 7.5,
        'MARKER': ['s'],
        'MARKER SIZE': 3,
        'LINE WIDTH': 4,
        'LINE STYLE': ['--'],
        'X AXIS LABEL': 'Years',
        'X AXIS SIZE': 10,
        'Y AXIS LABEL': 'Failury Probability',
        'Y AXIS SIZE': 10,
        'AXISES COLOR': '#000000',
        'LABELS SIZE': 14,
        'LABELS COLOR': '#000000',
        'CHART COLOR': ['#000000'],
        'ON GRID?': True,
        'LEGEND': ['Failury Probability'],  # or without legend 'LEGEND': [None]
        'LOC LEGEND': 'upper left',
        'SIZE LEGEND': 12,
        'Y LOG': False,
        'X LOG': False,
        'DPI': 200,
        'EXTENSION': 'svg'
    }

    CHART_CONFIG_BETA = {
    'NAME': 'Beta values over time',
    'WIDTH': 15.,
    'HEIGHT': 7.5,
    'MARKER': ['s'],
    'MARKER SIZE': 3,
    'LINE WIDTH': 4,
    'LINE STYLE': ['--'],
    'X AXIS LABEL': 'Years',
    'X AXIS SIZE': 10,
    'Y AXIS LABEL': 'Beta',
    'Y AXIS SIZE': 10,
    'AXISES COLOR': '#000000',
    'LABELS SIZE': 14,
    'LABELS COLOR': '#000000',
    'CHART COLOR': ['#000000'],
    'ON GRID?': True,
    'LEGEND': ['Beta value'],  # or without legend 'LEGEND': [None]
    'LOC LEGEND': 'upper left',
    'SIZE LEGEND': 12,
    'Y LOG': False,
    'X LOG': False,
    'DPI': 200,
    'EXTENSION': 'svg'
    }

    DATA_PF = {'DATASET': pf_over_time_df}
    DATA_BETA = {'DATASET': beta_over_time_df}

    #LINE_CHART(DATASET=DATA_PF, PLOT_SETUP=CHART_CONFIG_PF)
    #LINE_CHART(DATASET=DATA_BETA, PLOT_SETUP=CHART_CONFIG_BETA)

    print(f'Output file name: {output_file_name}\nProcessing time (s): {processing_time}'
          f'\nNumber of samples: {total_rows}\n')
    
    return result_df, pf_over_time_df, beta_over_time_df
    

     
    #results_about_data.columns = column_names

    # Resume data (n_fails, p_f, beta)
    RESUME_DATA = PARE_LIB.DATA_RESUME(random_seed, n_constraints, results_about_data)

    # Resume process (Time and outputs)
    END = time.time()
    print('PAREpy report: \n') 
    NAME = MODEL_NAME + '_' + str(datetime.now().strftime('%Y%m%d-%H%M%S'))
    print(f' \U0001F202 ID report: {NAME} \n') 
    print(' \U0001F680' + f' Process Time ({type_process} version) ' + '\U000023F0' + ' %.2f' % (END - INIT), 'seconds \n') 
    print(' \U0001F550' + ' Objective function time evaluation per sample: ' + ' %.4f' % FO_TIME + ' milliseconds') 
    PARE_LIB.JSON_FILE(NAME, RESUME_DATA)
    PARE_LIB.TXT_FILE(NAME, results_about_data)
    PARE_LIB.ZIP_FILE(NAME)
    

    return results_about_data

def sampling_algorithm_PARALLEL_CONCAT(PATH = './'):
    
    # Unzip all files
    TAM = PARE_LIB.UNZIP_ALL_FILES(PATH)
        
    # Concatenating datasets
    results_about_data = PARE_LIB.CONCAT_RESULTS(PATH)
       
    # Counting number of limit state functions
    HEADER = []
    for COLUMN in results_about_data.columns:
        HEADER.append(COLUMN)
    n_constraints = 0
    for ELEMENT in HEADER:
        if ELEMENT[0] == 'I':
            n_constraints += 1

    # Delete all folders (unzip procedure)
    FOLDERS = PARE_LIB.READ_indicator_functionN_CURRENT_FOLDER(PATH)
    for FOLDER in FOLDERS:
        PARE_LIB.FOLDER_REMOVER(FOLDER, PATH)
 
    # Resume data in dataframe format
    RESUME_DATA = PARE_LIB.DATA_RESUME(None, n_constraints, results_about_data)

    # Command window report
    print('PAREpy report: \n') 
    MODEL_NAME = 'MCS_LHS'
    NAME = MODEL_NAME + '_' + str(datetime.now().strftime('%Y%m%d-%H%M%S'))
    print(f' \U0001F202 ID report: {NAME} \n') 
    print(f' \U00002705 jointing {TAM} .txt files totalizing {len(results_about_data)} samples') 
    PARE_LIB.JSON_FILE(NAME, RESUME_DATA)
    PARE_LIB.TXT_FILE(NAME, results_about_data)
    PARE_LIB.ZIP_FILE(NAME)
    """
