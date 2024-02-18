"""
Set of functions to obtain fits and upper limits for the search of cLFV
Tau_upperlimitstools_fitting based on ROOT.
"""
import numpy as np
import ROOT
from tau_upperlimitstools_fitting.utility import check_dictionary_model

def create_gauss_histogram_1D(gauss_mean, gauss_sigma, gauss_events, hist_ranges, hist_name="histogram_signal", hist_bins=100):
    """
    Create a 1D Gaussian Histogram for model definition examples.

    Parameters
    ----------
    gauss_mean : float
        Mean of the Gaussian distribution.

    gauss_sigma : float
        Standard deviation (sigma) of the Gaussian distribution.

    gauss_events : int
        Number of events (data points) to generate.

    hist_ranges : tuple(float, float)
        Tuple representing the histogram range (min, max).

    hist_name : str, optional
        Name of the histogram. Default is "histogram_signal".

    hist_bins : int, optional
        Number of bins in the histogram. Default is 100.

    Returns
    -------
    ROOT.TH1D
        1D Gaussian histogram.
    """
    data = np.random.normal(gauss_mean, gauss_sigma, gauss_events)
    h_gauss = ROOT.TH1D(hist_name, hist_name, hist_bins, hist_ranges[0], hist_ranges[1])

    for data_elem in data:
        h_gauss.Fill(data_elem)

    return h_gauss

def create_gauss_histogram_2D(gauss_mean, gauss_sigma, gauss_events, hist_ranges, hist_name="histogram_signal_2d", hist_bins=100):
    """
    Create a 2D Gaussian Histogram for model definition examples.

    Parameters
    ----------
    gauss_mean : float
        Mean of the Gaussian distribution.

    gauss_sigma : float
        Standard deviation (sigma) of the Gaussian distribution.

    gauss_events : int
        Number of events (data points) to generate.

    hist_ranges : tuple(tuple(float, float), tuple(float, float))
        Tuples representing the histogram ranges for x and y dimensions, respectively.

    hist_name : str, optional
        Name of the histogram. Default is "histogram_signal_2d".

    hist_bins : int, optional
        Number of bins in each dimension of the histogram. Default is 100.

    Returns
    -------
    ROOT.TH2D
        2D Gaussian histogram.
    """
    data = np.random.normal(gauss_mean, gauss_sigma, (2, gauss_events))
    h2d_gauss = ROOT.TH2D(hist_name, hist_name, hist_bins, hist_ranges[0][0], hist_ranges[0][1], hist_bins, hist_ranges[1][0], hist_ranges[1][1])

    for data_elem in range(gauss_events):
        h2d_gauss.Fill(data[0][data_elem], data[1][data_elem])

    return h2d_gauss

def create_exponential_histogram_1D(exp_scale, exp_events, hist_ranges, hist_name="histogram_background", hist_bins=100):
    """
    Create a 1D Exponential Histogram for model definition examples.

    Parameters
    ----------
    exp_scale : float
        Scale parameter of the exponential distribution.

    exp_events : int
        Number of events (data points) to generate.

    hist_ranges : tuple(float, float)
        Tuple representing the histogram range (min, max).

    hist_name : str, optional
        Name of the histogram. Default is "histogram_background".

    hist_bins : int, optional
        Number of bins in the histogram. Default is 100.

    Returns
    -------
    ROOT.TH1D
        1D Exponential histogram.
    """
    data = np.random.exponential(exp_scale, exp_events)
    h_exp = ROOT.TH1D(hist_name, hist_name, hist_bins, hist_ranges[0], hist_ranges[1])

    for data_elem in data:
        h_exp.Fill(data_elem)

    return h_exp

def create_exponential_histogram_2D(exp_scale, exp_events, hist_ranges, hist_name="histogram_background", hist_bins=100):
    """
    Create a 2D Exponential Histogram for model definition examples.

    Parameters
    ----------
    exp_scale : float
        Scale parameter of the exponential distribution.

    exp_events : int
        Number of events (data points) to generate.

    hist_ranges : tuple(tuple(float, float), tuple(float, float))
        Tuples representing the histogram ranges for x and y dimensions, respectively.

    hist_name : str, optional
        Name of the histogram. Default is "histogram_background".

    hist_bins : int, optional
        Number of bins in each dimension of the histogram. Default is 100.

    Returns
    -------
    ROOT.TH2D
        2D Exponential histogram.
    """
    data = np.random.exponential(exp_scale, (2, exp_events))
    h2d_exp = ROOT.TH2D(hist_name, hist_name, hist_bins, hist_ranges[0][0], hist_ranges[0][1], hist_bins, hist_ranges[1][0], hist_ranges[1][1])

    for data_elem in range(exp_events):
        h2d_exp.Fill(data[0][data_elem], data[1][data_elem])

    return h2d_exp

def create_workspace_extended(model_configuration):
    """
    Create and return the S+B extended model in a WorkSpace given the input configuration.
    Define the configuration for S+B extended model for the 1D or 2D case.
    Option to generate pseudo data from a pre-defined S+B model in myWorkSpace.


    Parameters
    ----------
    model_configuration : dict
        A dictionary containing the configuration for the S+B model. It should have the following structure:

        {
            'model_sb': {
                'signal': {
                    'histogram': <TH1D>,
                    'pdf_name': '<signal_pdf_name>',
                    'nsig_yield_range': '[<min>, <max>]'
                },
                'background': {
                    'histogram': <TH1D>,
                    'pdf_name': '<background_pdf_name>',
                    'nbkg_yield_range': '[<min>, <max>]'
                },
                'variables_names': ['<variable_name_1>', '<variable_name_2>', ...],
                'variables_ranges': ['[<min_1>, <max_1>]', '[<min_2>, <max_2>]', ...],
                'dimension': "<1D_or_2D>",
                'generate_data': <bool>,
                'include_binned_data':<bool>,
                'data_bins' : <int>, 
                'pseudo_data_yields':{'n_sig':<int>, 'n_bkg':<int>}
            }
        }

    Returns
    -------
    myWorkSpace : ROOT.RooWorkspace
        The RooWorkspace containing the S+B extended model.

    Notes
    -----
    - The 'nsig_yield_range' and 'nbkg_yield_range' values are expected to be in the form of a string representing a numeric range (e.g., '[-10, 1000]').
    - The 'variables_ranges' list should contain strings representing the variable ranges in the form of '[<min>, <max>]'.
    - The 'dimension' field should be a string indicating the dimension of the model, either "1D" or "2D".
    - Ensure that the histograms provided for signal and background are compatible with ROOT.RooDataHist.

    Example
    -------
    >>> model_configuration = {
    ...     'model_sb': {
    ...         'signal': {
    ...             'histogram': h1sig,
    ...             'pdf_name': 'signal_pdf',
    ...             'nsig_yield_range': '[-10, 1000]'
    ...         },
    ...         'background': {
    ...             'histogram': h1bkg,
    ...             'pdf_name': 'background_pdf',
    ...             'nbkg_yield_range': '[-10, 3000]'
    ...         },
    ...         'variables_names': ['x'],
    ...         'variables_ranges': ['[0, 10]'],
    ...         'dimension': "1D",
                'generate_data': True,
                'include_binned_data':True,
                'data_bins' : 100, 
                'pseudo_data_yields':{'n_sig':1, 'n_bkg':2000}
    ...     }
    ... }
    >>> workspace = create_workspace_extended(model_configuration)
    """
    # Check if the input dictionary
    if not check_dictionary_model(model_configuration):
        print("Check your dictionay definition")
        return

    variables_names = model_configuration['model_sb']['variables_names']
    variables_ranges = model_configuration['model_sb']['variables_ranges']
    
    # Create RooWorkspace
    myWorkSpace = ROOT.RooWorkspace("myWorkSpace")
    x = myWorkSpace.factory(f"{variables_names[0]}{variables_ranges[0]}")
    if model_configuration['model_sb']['dimension'] == "1D":
        variables_arglist = ROOT.RooArgList(x)
        variables_argset = ROOT.RooArgSet(x)
    elif model_configuration['model_sb']['dimension'] == "2D":
        y = myWorkSpace.factory(f"{variables_names[1]}{variables_ranges[1]}")
        variables_arglist = ROOT.RooArgList(x,y)
        variables_argset = ROOT.RooArgSet(x,y)
    
    # Create signal and background RooHistPdfs
    print("Creating HistPDFs")
    datahist_vars_signal= ROOT.RooDataHist("datahist_vars_signal", "datahist_vars_signal",variables_arglist, model_configuration['model_sb']['signal']['histogram'])
    pdf_signal = ROOT.RooHistPdf(model_configuration['model_sb']['signal']['pdf_name'],model_configuration['model_sb']['signal']['pdf_name'],variables_argset,datahist_vars_signal,0)
    datahist_vars_background= ROOT.RooDataHist("datahist_vars_background", "datahist_vars_background",variables_arglist, model_configuration['model_sb']['background']['histogram'])
    pdf_background = ROOT.RooHistPdf(model_configuration['model_sb']['background']['pdf_name'],model_configuration['model_sb']['background']['pdf_name'],variables_argset,datahist_vars_background,0)
    
    # Model definition in WorkSpace
    print("Creating model in WorkSpace")
    myWorkSpace.Import(pdf_signal)
    myWorkSpace.Import(pdf_background)
    myWorkSpace.factory(f"n_sig{model_configuration['model_sb']['signal']['nsig_yield_range']}")
    myWorkSpace.factory(f"n_bkg{model_configuration['model_sb']['background']['nbkg_yield_range']}")
    myWorkSpace.factory(f"SUM:model_sb(n_sig*{model_configuration['model_sb']['signal']['pdf_name']}, n_bkg*{model_configuration['model_sb']['background']['pdf_name']})")
    myWorkSpace = model_configuration_extended(myWorkSpace,variables_names, model_configuration['model_sb']['dimension'])
    if model_configuration['model_sb']['generate_data']:
        myWorkSpace = generate_pseudodata_fromW(myWorkSpace, variables_names, variables_argset, model_configuration['model_sb']['dimension'], 
                                                model_configuration['model_sb']['pseudo_data_yields'],model_configuration['model_sb']['include_binned_data'], 
                                                model_configuration['model_sb']['data_bins'])

    return myWorkSpace

def model_configuration_extended(myWorkSpace,variables_names, dimension):
    """
    Define the configuration for S+B extended model for the 1D or 2D case.

    This function sets up the configuration for a S+B extended model.
    The variables involved are n_bkg, n_sig, and, in the case of 2D, x and y.
    The parameter of interest is the signal yield (n_sig), while n_bkg is treated as a nuisance parameter.

    Parameters
    ----------
    myWorkSpace : ROOT.RooWorkspace
        RooFit workspace containing the necessary variables and models.
    
    variables_names: list

    dimension : str
        Dimensionality of the model, either "1D" or "2D".

    Returns
    -------
    ROOT.RooWorkspace
        Updated RooFit workspace with the configured model.
    """
    set_n_sig=ROOT.RooArgSet(myWorkSpace.var("n_sig"))
    set_n_bkg=ROOT.RooArgSet(myWorkSpace.var("n_bkg"))
    
    #Create model configuration
    mc = ROOT.RooStats.ModelConfig("ModelConfig",myWorkSpace)
    mc.SetPdf(myWorkSpace.pdf("model_sb"))
    mc.SetParametersOfInterest(set_n_sig)
    
    if dimension =="1D":
        mc.SetObservables(ROOT.RooArgSet(myWorkSpace.var(variables_names[0])))
    elif dimension == "2D":
        mc.SetObservables(ROOT.RooArgSet(myWorkSpace.var(variables_names[0]), myWorkSpace.var(variables_names[1])))
    
    mc.SetNuisanceParameters(set_n_bkg)
    
    #Import the mc to the WorkSpace
    myWorkSpace.Import(mc)
    return myWorkSpace

def generate_pseudodata_fromW(myWorkSpace, variables_names, variables_argset, dimension, yield_values, data_binned=False, data_bins=100):
    """
    Generate pseudo data from a pre-defined S+B model in myWorkSpace.

    Parameters
    ----------
    myWorkSpace : ROOT.RooWorkspace
        RooFit workspace containing the S+B model.
    
    variables_names: list
    
    variables_argset: RooArgSet


    dimension : str
        Dimensionality of the model, either "1D" or "2D".

    yield_values : dict
        Dictionary containing signal and background yield values.
        Should include 'n_sig' for signal yield and 'n_bkg' for background yield.

    data_binned : bool, optional
        If True, generates binned pseudo data. Default is False.

    data_bins : int, optional
        Number of bins for binned pseudo data. Default is 100.

    Returns
    -------
    ROOT.RooWorkspace
        Updated RooFit workspace with generated pseudo data.
    """

    myWorkSpace.var("n_sig").setVal(yield_values['n_sig'])
    myWorkSpace.var("n_bkg").setVal(yield_values['n_bkg'])

    pseudo_data = myWorkSpace.pdf("model_sb").generate(variables_argset)
    pseudo_data.SetName("pseudo_data")
    myWorkSpace.Import(pseudo_data)

    if data_binned:
        myWorkSpace.var(variables_names[0]).setBins(data_bins)
        if dimension == "2D":
            myWorkSpace.var(variables_names[1]).setBins(data_bins)
        pseudo_data_binned = ROOT.RooDataHist("pseudo_data_binned", "pseudo_data_binned", variables_argset, pseudo_data)
        pseudo_data_binned.SetName("pseudo_data_binned")
        myWorkSpace.Import(pseudo_data_binned)

    return myWorkSpace
    
def save_myworkspace_infile(myWorkSpace, workspace_filename="workspace_model_sb.root", workspace_name="myWorkSpace"):
    """
    Save the RooFit workspace to a ROOT file.

    Parameters
    ----------
    myWorkSpace : ROOT.RooWorkspace
        The RooFit workspace to be saved.

    workspace_filename : str, optional
        The name of the ROOT file to save the workspace. Default is "workspace_model_sb.root".

    workspace_name : str, optional
        The name to set for the RooFit workspace in the saved file. Default is "myWorkSpace".

    Returns
    -------
    None
        This function does not return any value.
    """
    if workspace_name != "myWorkSpace":
        myWorkSpace.SetName(workspace_name)

    myWorkSpace.writeToFile(workspace_filename, True)
    print(f"Workspace saved to {workspace_filename} with the name {workspace_name}")

def check_status_fit(fitResult):
    print('-------------------------------------------')
    print("A small edm value indicates effective convergence of the fit.")
    print('edm',fitResult.edm(), '\n')
    print("A low minNll value indicates a successful fit finding a good description for the data.")
    print('minNll',fitResult.minNll(), '\n')
    print("A value of 0 typically indicates a successful fit.")
    print('status',fitResult.status(), '\n')
    print("A high covQual value (3) indicates good quality of the covariance matrix.")
    print('covQual',fitResult.covQual(), '\n')
    print("A value of 0 suggests that all likelihood evaluations were valid.")
    print('numInvalidNll',fitResult.numInvalidNLL(), '\n')
    print('--------------------------------------------')

def create_workspace_extended_gausExp(model_configuration):
    #TO DO :  This can be generalized
    """
    Create and return a Workspace with a customized S+B extended model based on the input configuration.
    A simple 1D S+B model for the Gaussian &  Exponential functions, for signal and background, respectively.

    Parameters
    ----------
    model_configuration : dict
        A dictionary containing the configuration for the S+B model. It should have the following structure:

        {
            'model_sb': {
                'signal': {
                    'function': "<signal_gaussian_function>",
                    'mean': "<mean_expression>",
                    'sigma': "<sigma_expression>",
                    'pdf_name': '<signal_pdf_name>',
                    'nsig_yield_range': '[<min>, <max>]'
                },
                'background': {
                    'function': "<background_exponential_function>",
                    'coefficient': "<coefficient_expression>",
                    'pdf_name': '<background_pdf_name>',
                    'nbkg_yield_range': '[<min>, <max>]'
                },
                'variables_names': ['<variable_name_1>', '<variable_name_2>', ...],
                'variables_ranges': ['[<min_1>, <max_1>]', '[<min_2>, <max_2>]', ...],
                'dimension': "<1D_or_2D>",
                'generate_data': <True_or_False>,
                'include_binned_data': <True_or_False>,
                'data_bins': <number_of_bins>,
                'pseudo_data_yields': {
                    'n_sig': <signal_yield>,
                    'n_bkg': <background_yield>
                }
            }
        }

    Returns
    -------
    myWorkSpace : ROOT.RooWorkspace
        The RooWorkspace containing the customized S+B extended model.

    Notes
    -----
    - The 'nsig_yield_range' and 'nbkg_yield_range' values are expected to be in the form of a string representing a numeric range (e.g., '[-10, 1000]').
    - The 'variables_ranges' list should contain strings representing the variable ranges in the form of '[<min>, <max>]'.
    - The 'dimension' field should be a string indicating the dimension of the model, either "1D" or "2D".
    - Ensure that the functions provided for signal and background are compatible with ROOT.RooAbsPdf.
    - The 'generate_data' flag controls whether pseudo-data is generated.
    - The 'include_binned_data' flag controls whether binned data is included in the workspace.

    Example
    -------
    >>> model_configuration = {
    ...     'model_sb': {
    ...         'signal': {
    ...             'function': "gaussian",
    ...             'mean': "m[5]",
    ...             'sigma': "s[1]",
    ...             'pdf_name': 'signal_pdf',
    ...             'nsig_yield_range': '[-20, 1000]'
    ...         },
    ...         'background': {
    ...             'function': "exponential",
    ...             'coefficient': "c[-1/4]",
    ...             'pdf_name': 'background_pdf',
    ...             'nbkg_yield_range': '[-10, 3000]'
    ...         },
    ...         'variables_names': ['x'],
    ...         'variables_ranges': ['[0, 10]'],
    ...         'dimension': "1D",
    ...         'generate_data': True,
    ...         'include_binned_data': True,
    ...         'data_bins': 100,
    ...         'pseudo_data_yields': {'n_sig': 1, 'n_bkg': 2000}
    ...     }
    ... }
    >>> workspace = create_workspace_custom(model_configuration)
    """
    # Check the input dictionary TO DO

    variables_names = model_configuration['model_sb']['variables_names']
    variables_ranges = model_configuration['model_sb']['variables_ranges']
    
    # Create RooWorkspace
    myWorkSpace = ROOT.RooWorkspace("myWorkSpace")
    x = myWorkSpace.factory(f"{variables_names[0]}{variables_ranges[0]}")
    if model_configuration['model_sb']['dimension'] == "1D":
        variables_arglist = ROOT.RooArgList(x)
        variables_argset = ROOT.RooArgSet(x)
    elif model_configuration['model_sb']['dimension'] == "2D":
        print("TO DO")
        return
    myWorkSpace.factory(f"n_sig{model_configuration['model_sb']['signal']['nsig_yield_range']}")
    myWorkSpace.factory(f"n_bkg{model_configuration['model_sb']['background']['nbkg_yield_range']}")
    myWorkSpace.factory(f"Gaussian::{model_configuration['model_sb']['signal']['pdf_name']}({variables_names[0]}, {model_configuration['model_sb']['signal']['mean']}, {model_configuration['model_sb']['signal']['sigma']})")
    myWorkSpace.factory(f"Exponential::{model_configuration['model_sb']['background']['pdf_name']}({variables_names[0]}, {model_configuration['model_sb']['background']['coefficient']})")
    myWorkSpace.factory(f"SUM:model_sb(n_sig*{model_configuration['model_sb']['signal']['pdf_name']}, n_bkg*{model_configuration['model_sb']['background']['pdf_name']})")
    myWorkSpace = model_configuration_extended(myWorkSpace, variables_names, model_configuration['model_sb']['dimension'])
    if model_configuration['model_sb']['generate_data']:
        myWorkSpace = generate_pseudodata_fromW(myWorkSpace, variables_names, variables_argset, model_configuration['model_sb']['dimension'], 
                                                model_configuration['model_sb']['pseudo_data_yields'],model_configuration['model_sb']['include_binned_data'], 
                                                model_configuration['model_sb']['data_bins'])
    return myWorkSpace

def create_workspace_HistFactory(model_configuration):

    """
    Model definition via WorkSpace given the input configuration.
    The workspace is created via HistFactory
    """
    print("TO DO")