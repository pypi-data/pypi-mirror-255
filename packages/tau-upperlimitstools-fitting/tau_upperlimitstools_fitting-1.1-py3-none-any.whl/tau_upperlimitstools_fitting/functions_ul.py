"""
Set of functions to obtain fits and upper limits for the search of cLFV
Tau_upperlimitstools_fitting based on ROOT.
"""
import ROOT
from tau_upperlimitstools_fitting.utility import check_dictionary_upper_limit

def calculate_upperlimit_asymptotic_CLs(upper_limit_configuration):
    """
    Calculate the upper limit using the asymptotic CLs method.

    Parameters
    ----------
    upper_limit_configuration : dict
        Configuration dictionary for calculating upper limits using asymptotic CLs method. It should have the following structure:

        {
            'asymptotic_CLs': {
                'workspace': {
                    'filename': '<workspace_filename>',
                    'name': '<workspace_name>'
                },
                'upper_limit': {
                    'one_side': <bool>,
                    'confidence_level': <float>,
                    'points_to_scan': <int>,
                    'poi_min': <float or False>,
                    'poi_max': <float or False>,
                    'set_verbose': <bool>,
                    'set_print_level': <int>
                }
            }
        }

    Returns
    -------
    result_upper_limit :
        Confidence interval result of the upper limit calculation using the asymptotic CLs method.

    Notes
    -----
    - The 'poi_min' and 'poi_max' values can be set to False to use the minimum and maximum bounds of the parameter of interest (poi).
    - The 'confidence_level' specifies the confidence level for the upper limit calculation.
    - The 'set_verbose' option controls whether verbose output is printed during the calculation.
    - The 'set_print_level' option controls the RooFit print level during the calculation.

    Example
    -------
    >>> upper_limit_configuration = {
    ...     'asymptotic_CLs': {
    ...         'workspace': {
    ...             'filename': 'workspace_model_sb.root',
    ...             'name': 'myWorkSpace'
    ...         },
    ...         'upper_limit': {
    ...             'one_side': True,
    ...             'confidence_level': 0.90,
    ...             'points_to_scan': 30,
    ...             'poi_min': 0,
    ...             'poi_max': 100,
    ...             'set_verbose': False,
    ...             'set_print_level': -1
    ...         }
    ...     }
    ... }
    >>> result = calculate_upperlimit_asymptotic_CLs(upper_limit_configuration)
    """
        # Check if the input dictionary
    if not check_dictionary_upper_limit(upper_limit_configuration):
        print("Check your dictionay definition")
        return

    cls_configuration = upper_limit_configuration['asymptotic_CLs']
    infile = ROOT.TFile.Open(cls_configuration["workspace"]["filename"])
    myWorkSpace = infile.Get(cls_configuration["workspace"]["name"])
    print("Configurating S+B Model and B Model")
    #Get the S+B model
    sbModel = myWorkSpace.obj("ModelConfig")
    poi = sbModel.GetParametersOfInterest().first()
    sbModel.SetName("S+B Model")
    #Snapshot with the current value of the poi
    sbModel.SetSnapshot(ROOT.RooArgSet(poi))
    #Construc a modelConfig for the B only hypothesis
    #For a CLS-style limit calculation (hypothesis test inversion) we need an explicit specification of the background-only hypothesis
    bModel = sbModel.Clone()
    bModel.SetName("B Model")
    poi.setVal(0)
    #Configure bModel to encode current poi=0 scenario as its hypothesis
    bModel.SetSnapshot(ROOT.RooArgSet(poi))
    myWorkSpace.Import(bModel)
    data =myWorkSpace.data("pseudo_data")
    print("Cheking Workspace")
    myWorkSpace.Print()
    print("......................................")
    print("Creating Asymptotic Calculator with S+b and B Model")
    print("................................")
    ac = ROOT.RooStats.AsymptoticCalculator(data,bModel,sbModel)
    ac.SetOneSided(cls_configuration['upper_limit']['one_side'])
    ac.SetPrintLevel(cls_configuration['upper_limit']['set_print_level'])
    if cls_configuration['upper_limit']["poi_min"] is False:
        poi_min = poi.getMin()
    else:
        poi_min = cls_configuration['upper_limit']["poi_min"]

    if cls_configuration['upper_limit']["poi_max"] is False:
        poi_max = poi.getMax()
    else:
        poi_max = cls_configuration['upper_limit']["poi_max"]
    
    result_upper_limit = creating_hypothesis_test_inverter_for_CLS(ac, poi_max,poi_min, cls_configuration['upper_limit']["confidence_level"], cls_configuration['upper_limit']["points_to_scan"], cls_configuration['upper_limit']["set_verbose"])

    return result_upper_limit

def creating_hypothesis_test_inverter_for_CLS(ac, poi_max, poi_min, confidence_level, number_points, set_verbose):
    """
    Create a hypothesis test inverter for asymptotic CLs method.

    Parameters
    ----------
    ac : ROOT.RooStats.AsymptoticCalculator
        Asymptotic calculator object.

    poi_max : float
        Maximum value for the parameter of interest (poi) scan.

    poi_min : float
        Minimum value for the parameter of interest (poi) scan.

    confidence_level : float
        Confidence level for the calculation.

    number_points : int
        Number of points to scan during the calculation.

    set_verbose : bool
        Set to True for verbose output, False otherwise.

    Returns
    -------
    upper_limit : ROOT.RooStats.HypoTestInverterResult
        Result of the hypothesis test inverter for CLs method.
    """
    calc = ROOT.RooStats.HypoTestInverter(ac)
    calc.SetConfidenceLevel(confidence_level)
    calc.SetVerbose(set_verbose)
    calc.UseCLs(True)

    print("The hypothesis test for CLs will be between:\n")
    print("poi: ", poi_min, poi_max)
    print('The next number of points will be scanned:', number_points)
    print("................................")
    
    calc.SetFixedScan(number_points, poi_min, poi_max)
    upper_limit = calc.GetInterval()
    ac_results=ac.GetHypoTest()
    ac_results.Print()
    return upper_limit, ac_results

def print_save_results(ul_result, output_file=False):
    """
    Print and optionally save the results of upper limit calculation.

    Parameters
    ----------
    ul_result : ROOT.RooStats.HypoTestInverterResult
        Result of the upper limit calculation.

    output_file : str or False, optional
        If provided, the results will be saved to the specified file. Default is False.

    Returns
    -------
    None
    """
    print("The observed CLs upper limit is: ", ul_result.UpperLimit())
    #Compute expected limit
    print("Expected upper limits, using the B (alternate) model : ")
    print(" expected limit (median) ", ul_result.GetExpectedUpperLimit(0))
    print(" expected limit (-1 sig) ", ul_result.GetExpectedUpperLimit(-1))
    print(" expected limit (+1 sig) ", ul_result.GetExpectedUpperLimit(1))
    print(" expected limit (-2 sig) ", ul_result.GetExpectedUpperLimit(-2))
    print(" expected limit (+2 sig) ", ul_result.GetExpectedUpperLimit(+2))
    print("################")

    if output_file is not False:
        with open(output_file, 'w+') as fl:
            fl.write("Expected upper limits, using the B (alternate) model : "+ "\n")
            fl.write("expected limit (median)"+ "\n")
            fl.write(str(ul_result.GetExpectedUpperLimit(0))+ "\n")
            fl.write("expected limit (-1 sig)"+ "\n")
            fl.write(str(ul_result.GetExpectedUpperLimit(-1))+ "\n")
            fl.write("expected limit (+1 sig)"+ "\n")
            fl.write(str(ul_result.GetExpectedUpperLimit(1))+ "\n")
            fl.write("expected limit (-2 sig)"+ "\n")
            fl.write(str(ul_result.GetExpectedUpperLimit(-2))+ "\n")
            fl.write("expected limit (+2 sig)"+ "\n")
            fl.write(str(ul_result.GetExpectedUpperLimit(2))+ "\n")
            fl.write("--------------------------------------------"+ "\n")
            fl.write("The observed CLs upper limit is:"+ "\n")
            fl.write(str(ul_result.UpperLimit())+ "\n")

def make_brazil_band(ul_result, output_file=False):
    """
    Create and display the Brazil band plot from the HypoTestInverterResult.

    Parameters
    ----------
    ul_result : ROOT.RooStats.HypoTestInverterResult
        Result of the upper limit calculation.

    output_file : str or False, optional
        If provided and has a valid file extension (.png, .pdf, .jpg), the plot will be saved to the specified file.
        Default is False.

    Returns
    -------
    canvas : ROOT.TCanvas
        The TCanvas containing the Brazil band plot.
    """

    plot = ROOT.RooStats.HypoTestInverterPlot("HTI_Result_Plot","HypoTest Scan Result",ul_result)
    canvas = ROOT.TCanvas("HypoTestInverter Scan")
    canvas.SetLogy(False)
    plot.Draw("CLb 2CL")
    if output_file is not False:
        if isinstance(output_file, str) and output_file.lower().endswith((".png", ".pdf", ".jpg")):
            print(f"Saving the plot in {output_file}.")
            canvas.SaveAs(output_file)     
        else:
            print("The file is not valid; please provide a filename with a .png, .pdf, or .jpg extension.")
    return canvas

def calculate_upperlimit_toys_CLs(upper_limit_configuration):
    """
    Calculate the upper limit using the CLs method with toy experiments.

    Parameters
    ----------
    upperlimit_configuration : dict
        Configuration dictionary for calculating upper limits using CLs method with toy experiments.
        It should have the following structure:

        {
            'toys_CLs': {
                'workspace': {
                    'filename': '<workspace_filename>',
                    'name': '<workspace_name>'
                },
                'upper_limit': {
                    'one_side': <bool>,
                    'confidence_level': <float>,
                    'points_to_scan': <int>,
                    'toy_number': <int>,
                    'poi_min': <float or False>,
                    'poi_max': <float or False>,
                    'set_verbose': <bool>,
                    'set_print_level': <int>
                }
            }
        }

    Returns
    -------
    result_upper_limit :
        Confidence interval result of the upper limit calculation using the CLs method with toy experiments.

    Notes
    -----
    - The 'poi_min' and 'poi_max' values can be set to False to use the minimum and maximum bounds of the parameter of interest (poi).
    - The 'confidence_level' specifies the confidence level for the upper limit calculation.
    - The 'set_verbose' option controls whether verbose output is printed during the calculation.
    - The 'set_print_level' option controls the RooFit print level during the calculation.

    Example
    -------
    >>> upperlimit_configuration = {
    ...     'toys_CLs': {
    ...         'workspace': {
    ...             'filename': 'workspace_model_sb_2D.root',
    ...             'name': 'myWorkSpace'
    ...         },
    ...         'upper_limit': {
    ...             'one_side': True,
    ...             'confidence_level': 0.90,
    ...             'points_to_scan': 10,
    ...             'toy_number': 1000,
    ...             'poi_min': 0,
    ...             'poi_max': 35,
    ...             'set_verbose': False,
    ...             'set_print_level': -1
    ...         }
    ...     }
    ... }
    >>> result = calculate_upperlimit_toys_CLs(upperlimit_configuration)
    """
    cls_configuration = upper_limit_configuration['toys_CLs']
    infile = ROOT.TFile.Open(cls_configuration["workspace"]["filename"])
    myWorkSpace = infile.Get(cls_configuration["workspace"]["name"])
    print("Configurating S+B Model and B Model")
    sbModel = myWorkSpace.obj("ModelConfig")
    poi = sbModel.GetParametersOfInterest().first()
    sbModel.SetName("S+B Model")
    sbModel.SetSnapshot(ROOT.RooArgSet(poi))
    bModel = sbModel.Clone()
    bModel.SetName("B Model")
    poi.setVal(0)
    bModel.SetSnapshot(ROOT.RooArgSet(poi))
    myWorkSpace.Import(bModel)
    data =myWorkSpace.data("pseudo_data")
    fc = ROOT.RooStats.FrequentistCalculator(data, bModel, sbModel)
    fc.SetToys(cls_configuration['upper_limit']['toy_number'],cls_configuration['upper_limit']['toy_number'])
    if cls_configuration['upper_limit']["poi_min"] is False:
        poi_min = poi.getMin()
    else:
        poi_min = cls_configuration['upper_limit']["poi_min"]

    if cls_configuration['upper_limit']["poi_max"] is False:
        poi_max = poi.getMax()
    else:
        poi_max = cls_configuration['upper_limit']["poi_max"]

    result_upper_limit = creating_hypotesis_test_inverter_for_toys_CLS(fc,myWorkSpace, poi_max,poi_min, cls_configuration['upper_limit']["confidence_level"], cls_configuration['upper_limit']["points_to_scan"], cls_configuration['upper_limit']["set_verbose"])

    return result_upper_limit

def creating_hypotesis_test_inverter_for_toys_CLS(fc,myWorkSpace, poi_max,  poi_min, confidence_level, number_points, set_verbose):
    """
    Create a hypothesis test inverter for the CLs method with toy experiments.

    Parameters
    ----------
    fc : ROOT.RooStats.FrequentistCalculator
        FrequentistCalculator calculator object.

    myWorkSpace : ROOT.RooWorkspace
        RooFit workspace containing the S+B extended model.

    poi_max : float
        Maximum value for the parameter of interest (poi) scan.

    poi_min : float
        Minimum value for the parameter of interest (poi) scan.

    confidence_level : float
        Confidence level for the calculation.

    number_points : int
        Number of points to scan during the calculation.

    set_verbose : bool
        Set to True for verbose output, False otherwise.

    Returns
    -------
    upper_limit : ROOT.RooStats.HypoTestInverterResult
        Result of the hypothesis test inverter for CLs method with toy experiments.
    """
    #Proof takes the max number of cores availables in the machine
    #TO DO: change to "workers=number_cores"
    calc = ROOT.RooStats.HypoTestInverter(fc)
    calc.SetConfidenceLevel(confidence_level)
    calc.SetVerbose(set_verbose)
    calc.UseCLs(True)
    print("The hypotesis_test for CLS will be between:\n")
    print("poi: ", poi_min, poi_max)
    print('The next number of points will be scan:', number_points)
    print("................................")
    pc =ROOT.RooStats.ProofConfig(myWorkSpace, 0, "", False)
    toymcs = calc.GetHypoTestCalculator().GetTestStatSampler() 
    profll = ROOT.RooStats.ProfileLikelihoodTestStat(myWorkSpace.obj("B Model").GetPdf())
    profll.SetOneSided(True)
    toymcs.SetProofConfig(pc)
    toymcs.SetTestStatistic(profll)
    if not myWorkSpace.obj("B Model").GetPdf().canBeExtended():
        toymcs.SetNEventsPerToy(1)
        print('Can not be extended')
    calc.SetFixedScan(number_points,poi_min,poi_max)
    upper_limit = calc.GetInterval()
    #upper_limit = r.UpperLimit()
    fc_results=fc.GetHypoTest()
    fc_results.Print()
    return upper_limit, fc_results

def make_test_statistic(fc_result, output_file=False):

    plot = ROOT.RooStats.HypoTestPlot(fc_result)
    plot.SetLogYaxis(True)
    canvas = ROOT.TCanvas("Test statistic")
    plot.Draw(" ")
    if output_file is not False:
        if isinstance(output_file, str) and output_file.lower().endswith((".png", ".pdf", ".jpg")):
            print(f"Saving the plot in {output_file}.")
            canvas.SaveAs(output_file)     
        else:
            print("The file is not valid; please provide a filename with a .png, .pdf, or .jpg extension.")
    return canvas

