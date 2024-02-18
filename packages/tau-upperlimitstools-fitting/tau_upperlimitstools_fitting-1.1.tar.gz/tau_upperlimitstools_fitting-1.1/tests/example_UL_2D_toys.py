#!/usr/bin/env python
# coding: utf-8

import ROOT

import tau_upperlimitstools_fitting as tau_tools

upperlimit_configuration={'toys_CLs':{ "workspace":{
                                                          "filename": "workspace_model_sb_2D.root", 
                                                          "name":"myWorkSpace"},
                                             "upper_limit":{
                                                             "one_side":True,
                                                             "confidence_level":0.90,
                                                             "points_to_scan":10,
                                                             "toy_number":200,
                                                             "poi_min":0,
                                                             "poi_max":35,
                                                             "set_verbose":False,
                                                             "set_print_level":-1}
                                           }
                    }

upper_limit_result, fc_result=tau_tools.calculate_upperlimit_toys_CLs(upperlimit_configuration)
tau_tools.print_save_results(upper_limit_result, "results_2D_toys.txt")
canvas_brazil_band=tau_tools.make_brazil_band(upper_limit_result, "brazil_band_2D_toys.png")
canvas_test_statistic=tau_tools.make_test_statistic(fc_result, "test_statistic.png")