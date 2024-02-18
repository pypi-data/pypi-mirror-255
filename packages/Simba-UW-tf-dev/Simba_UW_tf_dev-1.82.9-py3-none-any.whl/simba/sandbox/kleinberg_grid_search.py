import os.path
from itertools import product
from simba.data_processors.kleinberg_calculator import KleinbergCalculator

#SPECIFY KLEINBERG PARAMETERS.
#Note: all the different 4-way combinations of values will be run. For example, the below values will results in
# 72 different combinations of Kleinberg smoothings, saved in 72 different output folders.
# You may want to remove some values, if you have a lot of data, and want to spare disk space.
# For information on the parameters see the [SimBA GitHub Repo](https://github.com/sgoldenlab/simba/blob/master/docs/kleinberg_filter.md)
SIGMAS = [1.5, 2.0, 3.0]
GAMMAS = [0.1, 0.2, 0.3, 0.5]
HIERARCHIES = [1, 2, 3]
HIERARCHY_SEARCH = [True, False]

#SPECIFY CLASSIFIERS AND PATHS
## NAMES OF THE BEHAVIORS IN YOUR SIMBA PROJECT YOU WANT TO PERFORM KLEINBERG SMOOTHING ON
CLASSIFIER_NAMES = ['Attack', 'Sniffing', 'Rear']
##THE FULL PATH TO YOUR SIMBA PROJECT CONFIG FILE
PROJECT_CONFIG_PATH = r'/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/project_config.ini'
##THE DIRECTORY HOLDING THE DATA FILES WITH BEHAVIOR COLUMNS THAT YOU WANT TO SMOOTH
INPUT_DIR = r'/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/csv/machine_results'
##THE OUTPUT DIRECTORY WHERE THE SMOOTHENED DATA SHOULD BE STORED. ONE SUB-DIRECTORY INSIDE THIS OUTPUT DIRECTORY WILL BE CREATED PER PARAMETER COMBINATION
OUTPUT_DIR = r'/Users/simon/Desktop/envs/troubleshooting/two_black_animals_14bp/project_folder/csv/kleinberg_gridsearch_test'


#RUN THE KLEINBERG ANALYSIS. ONCE COMPLETE, THE RESULTS CAN BE FOUND IN THE SPECIFIED OUTPUT_DIR.
#THE RESULTS WILL BE SAVED IN SUB-DIRECTORIES THAT INDICATE THE SPEFIFIC PARAMETERS USED.
#FOR EXAMPLE. A DIRECTORY CALLED s3.0_g0.2_h3_hsTrue TRANSLATED TO sigma = 3.0, gamma = 0.2, hierarchy = 3, hierarchy search = TRUE.
for cnt, param in enumerate(list(product(SIGMAS, GAMMAS, HIERARCHIES, HIERARCHY_SEARCH))):
    s, g, h, hs = param
    print(f'Running parameters ({cnt+1}/{len(list(product(SIGMAS, GAMMAS, HIERARCHIES, HIERARCHY_SEARCH)))}): sigma = {s}, gamma = {g}, hierarchy = {h}, hierarchy search = {hs}')
    save_dir = os.path.join(OUTPUT_DIR, f's{s}_g{g}_h{h}_hs{hs}')
    if not os.path.isdir(save_dir): os.makedirs(save_dir)
    kleinberg_runner = KleinbergCalculator(config_path=PROJECT_CONFIG_PATH,
                                           classifier_names=CLASSIFIER_NAMES,
                                           sigma=s,
                                           gamma=g,hierarchy=h,
                                           hierarchical_search=hs,
                                           input_dir=INPUT_DIR,
                                           output_dir=save_dir)
    kleinberg_runner.run()

