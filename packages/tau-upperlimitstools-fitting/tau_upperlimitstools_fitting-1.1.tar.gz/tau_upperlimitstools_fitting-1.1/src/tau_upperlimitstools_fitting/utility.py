"""
common functions for the module.
"""

def save_histogram_to_root_file(histogram, filename, histogram_name):
    """
    Save a ROOT histogram to a ROOT file.

    Parameters
    ----------
    histogram : ROOT.TH1
        The histogram to be saved.

    filename : str
        The name of the ROOT file to save the histogram.

    histogram_name : str
        The name to set for the histogram in the saved file.

    Returns
    -------
    None
        This function does not return any value.
    
    Raises
    ------
    Exception
        If there is an issue with writing the histogram or closing the file, an exception is raised.
    """
    try:
        root_file = ROOT.TFile(filename, "RECREATE")
        histogram.Write(histogram_name)
        root_file.Close()
    except Exception as e:
        print(f"Error: {e}")
        raise

def check_dictionary_model(model_dict):
    """
    Check the structure of the model dictionary.

    Parameters
    ----------
    model_dict : dict
        The dictionary representing the model structure.

    Returns
    -------
    bool
        Returns True if the dictionary has the expected structure, otherwise False.

    Notes
    -----
    The expected structure includes the keys 'model_sb', 'signal', 'background', 
    'variables_names', 'dimension' at various levels of the dictionary.
    """
    if 'model_sb' not in model_dict:
        print("Error: Key 'model_sb' not found in the dictionary.")
        return False
    model_sb_dict = model_dict['model_sb']
    if 'signal' not in model_sb_dict or 'background' not in model_sb_dict or 'variables_names' not in model_sb_dict or 'dimension' not in model_sb_dict or 'generate_data' not in model_sb_dict or 'include_binned_data' not in model_sb_dict or 'data_bins' not in model_sb_dict or 'pseudo_data_yields' not in model_sb_dict:
        print("Error: Incorrect internal structure of 'model_sb'.")
        return False
    signal_dict = model_sb_dict['signal']
    if 'histogram' not in signal_dict or 'pdf_name' not in signal_dict or 'nsig_yield_range' not in signal_dict:
        print("Error: Incorrect internal structure of 'signal'.")
        return False
    background_dict = model_sb_dict['background']
    if 'histogram' not in background_dict or 'pdf_name' not in background_dict or 'nbkg_yield_range' not in background_dict:
        print("Error: Incorrect internal structure of 'background'.")
        return False
    return True
    
def check_dictionary_upper_limit(ul_dictionary):
    """
    Check the structure of the dictionary for configuring upper limit calculations.

    Parameters
    ----------
    ul_dictionary : dict
        The dictionary representing the configuration for upper limit calculations.

    Returns
    -------
    bool
        Returns True if the dictionary has the expected structure, otherwise False.

    Notes
    -----
    - The dictionary is expected to have keys 'asymptotic_CLs', 'workspace', and 'upper_limit'.
    - The 'asymptotic_CLs' key should further contain keys 'workspace' and 'upper_limit'.
    - The 'workspace' key under 'asymptotic_CLs' should have keys 'filename' and 'name'.
    - The 'upper_limit' key under 'asymptotic_CLs' should have keys 
      'one_side', 'confidence_level', 'points_to_scan', 'poi_min', 'poi_max', 'set_verbose', 'set_print_level'.
    """
    expected_keys = ['asymptotic_CLs']
    
    if 'asymptotic_CLs' not in ul_dictionary:
        print("Error: Key 'asymptotic_CLs' not found in the dictionary.")
        return False
    asymptotic_CLs_keys = ul_dictionary['asymptotic_CLs'].keys()
    expected_asymptotic_keys = ['workspace', 'upper_limit']
    
    if not set(asymptotic_CLs_keys) == set(expected_asymptotic_keys):
        print("Error: Keys 'workspace' and 'upper_limit' not found in the asymptotic_CLs dictionary.")
        return False
    
    workspace_keys = ul_dictionary['asymptotic_CLs']['workspace'].keys()
    expected_workspace_keys = ['filename', 'name']
    
    if not set(workspace_keys) == set(expected_workspace_keys):
        print("Error: Keys 'filename' and 'name' not found in the workspace dictionary.")
        return False
    
    # Check the keys under 'upper_limit'
    upper_limit_keys = ul_dictionary['asymptotic_CLs']['upper_limit'].keys()
    expected_upper_limit_keys = ['one_side', 'confidence_level', 'points_to_scan', 'poi_min', 'poi_max', 'set_verbose', 'set_print_level']
    
    return set(upper_limit_keys) == set(expected_upper_limit_keys)

