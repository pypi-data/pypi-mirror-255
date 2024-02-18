import csv
import ast
import pandas as pd
import numpy as np
from cobra import Reaction
from cobra.flux_analysis import flux_variability_analysis
from cobra.flux_analysis import single_reaction_deletion
from cameo import load_model
from functions import *
from flux_variability_based import FSEOF as cFSEOF
from sklearn import preprocessing
import pickle
import math
import networkx as nx
import os
from biocyc import *

tmodel = load_model("iML1515a_QPAML.xml") 

# if not exchange reaction exist for metabolite you can create a demand reaction
#tmodel.add_boundary(tmodel.metabolites.get_by_id("trp__L_e"), type="demand") 
# Target reaction
target = 'EX_trp__L_e' 

# Name of biomass reaction
biomass = 'BIOMASS_Ec_iML1515_core_75p37M' 

# Carbon source
substrate = 'EX_glc__D_e'

# Tolerance for values, lower is considered zero
tol = 1e-6

# Directory for results
dir = './opt_disturb_random/'


if not os.path.exists(dir):
    try:
        os.mkdir(dir)
        print(f"The directory {dir} has been created.")
    except FileExistsError:
        print(f"The directory {dir} already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")



def model_base_nr():
    model = tmodel.copy()
    # Bound for substrate uptake
    model.reactions.get_by_id(substrate).lower_bound = -18
    return model

model = model_base_nr()
RxnRatio = single_reaction_deletion(model).fillna(0)
rxns_essential = [list(id)[0] for id in RxnRatio[RxnRatio['growth'] < tol]['ids'].to_list()]

model = model_base_nr()
df_fva = flux_variability_analysis(model, fraction_of_optimum=0.0)
rxns_no_flux = list(df_fva[(abs(df_fva['minimum']) < tol) & (abs(df_fva['maximum']) < tol)].index)
rxns_flux = list(set(df_fva.index) - set(rxns_no_flux))

max_target = get_max_flux(model_base_nr(), target)
model = model_base_nr()
model.reactions.get_by_id(target).lower_bound = max_target
sol_optima = model.optimize(objective_sense='min')
for rn in model.reactions:
    if rn.id in rxns_flux:
        rn.lower_bound = sol_optima.fluxes[rn.id]


df_fva2 = flux_variability_analysis(model, fraction_of_optimum=1, reaction_list=rxns_flux)


RxnOptimaEx = list(df_fva2[((df_fva2['minimum'].abs() + df_fva2['maximum'].abs()) >= tol)
                         & (abs(df_fva2['minimum']) < 999) 
                         & (abs(df_fva2['maximum']) < 999) ].index)

##################################################################################################################################
#####################################################            Perturbations           #########################################
##################################################################################################################################

def model_base():
    model = tmodel.copy()
    ############### Media conditions start ##################
    model.reactions.EX_o2_e.lower_bound=-7.5
    model.reactions.EX_glc__D_e.lower_bound=-16.0
    model.reactions.EX_co2_e.lower_bound=7.0
    model.reactions.EX_co2_e.upper_bound=1000.0  
    ############### Media conditions end ####################
    # Minimal biomass target
    model.reactions.get_by_id(biomass).lower_bound = 0.05
    return model


max_target = get_max_flux(model_base(), target)
if math.isnan(max_target) or abs(max_target) < tol:
    print("The target reaction is not reachable.")
    quit()


b_model = model_base()
b_model.reactions.get_by_id(target).lower_bound = max_target*0.95
sol = b_model.optimize()
sol.fluxes[target] = max_target*0.95


strains = []
hm_df_fluxes = {}
factor = 1.5
for rxn in RxnOptimaEx + ['wt']:
    cur_model = model_base()
    rxn
    if rxn != 'wt':
        max_i = get_max_flux(model_base(), rxn)
        max_i = max_i if abs(max_i) < abs(sol.fluxes[rxn]*factor) else (sol.fluxes[rxn]*factor)
        if max_i > tol:
            print(rxn + ' - lb = ' + str(max_i*0.95))
            cur_model.reactions.get_by_id(rxn).lower_bound = max_i*0.95
        elif max_i < -tol:
            print(rxn + ' - ub = ' + str(max_i*0.95))
            cur_model.reactions.get_by_id(rxn).upper_bound = max_i*0.95
        else:
            print(rxn + ' - no changed = ' + str(max_i*0.95))
            continue
    fseof = cFSEOF(cur_model)
    try:
        fseof_result = fseof.run(target=cur_model.reactions.get_by_id(target), exclude=rxns_no_flux)
    except Exception as ex:
        print('Error en ' + rxn)
        print(ex)
        continue
    df_cur_all_fluxes = json2df(fseof_result.all_fluxes)
    df_cur_all_fluxes.columns = [rxn + ' ' + str(col) for col in df_cur_all_fluxes.columns]
    hm_df_fluxes[rxn + '_strain'] = df_cur_all_fluxes
    strains.append(rxn)


all_df_fluxes = pd.concat([df.T for df in hm_df_fluxes.values()])
all_df_fluxes.fillna(0, inplace=True)

all_df_fluxes.to_csv(dir + 'all_fluxes' + target + '.csv')


all_df_fluxes_T = all_df_fluxes.T




df_compare = pd.DataFrame(index=all_df_fluxes_T.index)
count_corr = {}
for strain in strains:
    df_compare[strain] = ''
    cols = [strain + ' ' + str(i) for i in range(10) if (strain + ' ' + str(i)) in all_df_fluxes_T.columns]
    if len(cols) == 0:
        continue
    cdf = all_df_fluxes_T[cols].T
    x_val = cdf[biomass]
    y_target_val, max1 = normalize_data(cdf[target])
    s1 = calc_slope(x_val.values, y_target_val.values)
    for rn in cdf.columns:
        if rn not in count_corr:
            count_corr[rn] = [0, 0, 0, 0] 
        if cdf[rn].abs().sum() == 0:
            df_compare.at[rn, strain] = 'zero'
        else:
            y_rn_real = cdf[rn]
            y_rn_val, max2 = normalize_data(y_rn_real)
            s2 = calc_slope(x_val.values, y_rn_val.values)
            s_real, b_real = get_line_eq(x_val.values, cdf[rn].values)
            if s2 == 0:
                count_corr[rn][2] += 1
            elif s1*s2 < 0:
                y_rn_val = invert_line(y_rn_val)
                if abs(b_real) < 0.05:
                    count_corr[rn][3] += 1
                else:
                    count_corr[rn][0] += 1
            else:
                count_corr[rn][1] += 1
            df_compare.at[rn, strain] = str(calc_diff(y_target_val, y_rn_val))



t_compare = df_compare.copy()

df_compare['rel_biomass'] = '0'

bio_fluxes = pd.DataFrame(all_df_fluxes[biomass], columns=[biomass]).T
for rn in all_df_fluxes_T.index:
    if rn in rxns_no_flux:
        continue
    rn_fluxes = all_df_fluxes[rn]
    rn_fluxes = pd.DataFrame(rn_fluxes, columns=[rn]).T
    data_rn_flux = np.array([])
    data_bio_flux = np.array([])
    for strain in strains:
        cols = []
        for i in range(10):
            col = strain + ' '  + str(i)
            if col in all_df_fluxes_T.columns:
                cols.append(col)
        cdf_bio = bio_fluxes[cols].values[0]
        cdf_rn = rn_fluxes[cols].values[0]
        if sum(cdf_rn) == 0:
            continue
        data_bio_flux = np.concatenate((data_bio_flux, cdf_bio))
        data_rn_flux = np.concatenate((data_rn_flux, cdf_rn))
    if len(data_bio_flux) == 0:
        continue
    s, i = get_line_eq(data_bio_flux, data_rn_flux)
    diff = calc_diff_line(s, i, data_bio_flux, data_rn_flux)
    if diff < 0.1:
        if abs(i) < 0.05:
            df_compare.at[rn, 'rel_biomass'] = '1'
        



df_compare['count'] = 0
df_compare['used'] = 0
t_df = t_compare.T
l_threshold = 0.01
for rn in t_df.columns:
    vals = pd.to_numeric(t_df[rn].values, errors='coerce')
    arr_vals = vals[vals < l_threshold].tolist()
    if len(arr_vals) > 0:
        df_compare.at[rn, 'count'] = len(arr_vals)
        df_compare.at[rn, 'used'] = 1
    


df_compare['essential'] = '0'
df_compare.loc[rxns_essential, 'essential'] = 1

df_compare['optima'] = 0
df_compare.loc[RxnOptimaEx, 'optima'] = 1


df_compare['invert'] = 0
df_compare['no_invert'] = 0
for rn, val in count_corr.items():
    df_compare.at[rn, 'invert'] = val[0]
    df_compare.at[rn, 'no_invert'] = val[1]



df_compare.to_csv(dir + 'compare_' + target + '.csv')







########################################################################################################################################
#####################################################   Machine Learning    ############################################################
########################################################################################################################################



df_random = pd.DataFrame()
df_random['flux_total'] = (all_df_fluxes_T.abs().sum(axis=1))
df_random['any_flux'] = (df_random['flux_total'] > 0).astype(int)
df_random = pd.concat([df_random, df_compare[['rel_biomass', 'count', 'invert', 'no_invert', 'used', 'essential', 'optima']]], axis=1)



df_random['corr'] = 0
df_random['icorr'] = 0
len_strain = len(strains)
for rn in df_random.index:
    df_random.at[rn, 'corr'] = 1 if (df_random.at[rn, 'no_invert'] - df_random.at[rn, 'invert'] > (len_strain/4)) else 0
    df_random.at[rn, 'icorr'] = 1 if (df_random.at[rn, 'invert'] > (len_strain/2)) else 0


df_random['no_flux'] = 0
df_random.loc[rxns_no_flux, 'no_flux'] = 1



df_random['genes_keio'] = ''
df_random['strain_keio'] = ''

csv_keio = './keio_parsed.csv'
with open(csv_keio, 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        rns = ast.literal_eval(row[3])
        for rn in rns:
            if rn not in df_random.index:
                print(rn + ' no encontrado')
                continue
            c_g = df_random.at[rn, 'genes_keio']
            if c_g != '':
                df_random.at[rn, 'genes_keio'] += ', '
            df_random.at[rn, 'genes_keio'] += row[2]
            c_s = df_random.at[rn, 'strain_keio']
            if c_s != '':
                df_random.at[rn, 'strain_keio'] += ', '
            df_random.at[rn, 'strain_keio'] += row[1]



df_random.to_csv(dir + 'df_random_' + target + '.csv')



df_all = df_random[['any_flux', 'essential', 'optima', 'rel_biomass', 'used', 'corr']]
df_all['essential'] = df_all['essential'].astype('category').cat.codes
df_all['optima'] = df_all['optima'].astype('category').cat.codes
df_all['rel_biomass'] = df_all['rel_biomass'].astype('category').cat.codes
df_all['used'] = df_all['used'].astype('category').cat.codes
df_all['corr'] = df_all['corr'].astype('category').cat.codes
df_all['any_flux'] = df_all['any_flux'].astype('category').cat.codes
scaler = preprocessing.MinMaxScaler(feature_range=(0,1))
X = scaler.fit_transform(df_all)
df_scaled= pd.DataFrame(X, columns=df_all.columns, index=df_all.index)
df_scaled.head()


hm_code2cat = {0:'0', 1:'Biomass', 2:'KD', 3:'KO', 4:'Low flux', 5:'Over'}


with open('./model/GBDT/model_rf.dat', 'rb') as file:
    model = pickle.load(file)

X_names = []
col_avoid = []
for col_name in df_all.columns:
    if col_name in col_avoid:
        continue
    X_names.append(col_name)


X_pred = df_all[X_names].values
predicted_prob_all = model.predict_proba(X_pred)[:,1]
predicted_all = model.predict(X_pred)

df_predicted = pd.DataFrame(columns=['Predicted', 'Distance'], index=list(df_all.index))
df_predicted['Predicted'] = predicted_all
df_predicted['Distance'] = 0

for idx in df_predicted.index:
    df_predicted.at[idx, 'Predicted'] = hm_code2cat[df_predicted.at[idx, 'Predicted']] 





##########################################################################################################
###################################### Distances #########################################################
##########################################################################################################

over = RxnOptimaEx
ko = list(df_predicted[df_predicted['Predicted'] == 'KO'].index)
kd = list(df_predicted[df_predicted['Predicted'] == 'KD'].index)

relevant = list(set(over) | set(ko) | set(kd))

G = nx.DiGraph()
for reaction in relevant:
    reaction = tmodel.reactions.get_by_id(reaction)
    for metabolite, coeff in reaction.metabolites.items():
        if reaction.lower_bound < 0:
            if coeff > 0:
                G.add_edge(metabolite.id, reaction.id)  # Metabolite -> Reaction
            elif coeff < 0:
                G.add_edge(reaction.id, metabolite.id)  # Reaction -> Metabolite
        if reaction.upper_bound > 0:
            if coeff < 0:
                G.add_edge(metabolite.id, reaction.id)  # Metabolite -> Reaction
            elif coeff > 0:
                G.add_edge(reaction.id, metabolite.id)  # Reaction -> Metabolite

levels = {}
all_neighbors = []
all_neighbors_temp = over.copy()
count = 0
avoid = ['h', 'h2o', 'nadp', 'nad', 'atp', 'pi', 'ppi', 'nadph', 'nadh', 'coa', 'co2', 'amp', 'adp', 'nh4', 'o2', 'so4', 'gdp', 'gtp', 'utp', 'udp', 'ump']
while all_neighbors != all_neighbors_temp:
    count += 1
    print(count)
    all_neighbors = all_neighbors_temp.copy()
    for node in all_neighbors_temp:
        if node in tmodel.metabolites:
            if node[:-3] in avoid:
                continue
        successors = list(G.successors(node))  # Neighbors that can be reached by a directed edge starting from the node
        for s in successors:
            if s not in all_neighbors:
                all_neighbors.append(s)
    if count % 2 == 0:
        levels[count/2] = list(set(all_neighbors) - set(all_neighbors_temp))
    if all_neighbors != all_neighbors_temp:
        all_neighbors_temp = all_neighbors.copy()
        all_neighbors = []
    



for i in range(1,len(levels)):
    print('Distance ' + str(i) + ': KO(' + str(len(list(set(levels[i]) - set(kd)))) + '), KD(' + str((len(levels[i]) - len(list(set(levels[i]) - set(kd))))) + ')')
    for rn in levels[i]:
        df_predicted.at[rn, 'Distance'] = i



df_predicted.to_csv(dir + 'predicted_' + target +  '.csv')






adapter = Adapter(tmodel)

hm_promoter = get_promoters()
hm_TU = get_TU(hm_promoter)
hm_complex = get_complex()
hm_gene = get_gene(hm_promoter, hm_TU)
hm_gene_tu = get_hm_gene_tu(hm_TU, hm_gene)
hm_protein = get_protein(hm_gene)
update_promoters(hm_protein)
hm_regulation = get_regulation()
hm_types_cpd, hm_compound = get_compounds()
hm_enzrxns = get_enzrxns(hm_regulation, hm_protein, hm_gene, hm_TU)
hm_reaction, nodes, att_reactions, metabolites, cpd_transported = get_reactions(hm_enzrxns, hm_protein, hm_gene, hm_gene_tu, hm_TU, hm_promoter, hm_complex, hm_regulation)
met_in_reactions = get_cpd_in_rn(hm_reaction)
update_regulation(hm_enzrxns, met_in_reactions)
hm_pathway, hm_rn_pathway = get_pathways()


metOptima = []

for rn in RxnOptimaEx:
    for met in tmodel.reactions.get_by_id(rn).metabolites.keys():
        try:
            met_bio = adapter.get_cpd_biocyc(met.id)
        except:
            continue
        
        for met_syn in met_bio:
            if met_syn not in metOptima:
                metOptima.append(met_syn)



cofactors = ['ATP', 'ADP', 'AMP', 'NAD', 'NADH', 'NADP', 'NADPH', 'Pi']

RegEnz = {}
for name, reg in hm_regulation.items():
    if 'Regulation-of-Enzyme-Activity' in reg.type:
        if '-' in reg.mode:
            for regulator in reg.regulator:
                if regulator in metOptima and regulator not in cofactors:
                    #print(reg.regulated_entity[0])
                    enzyme = reg.regulated_entity[0]
                    reaction_bc = hm_enzrxns[enzyme].reaction[0]
                    try:
                        rns_bigg = adapter.get_rn_bigg(reaction_bc)
                        if len(set.intersection(set(rns_bigg), set(RxnOptimaEx))):   
                            print(regulator + '   ' + str(adapter.get_rn_bigg(reaction_bc)))
                            crn = adapter.get_rn_bigg(reaction_bc)[0]
                            if crn not in RegEnz:
                                RegEnz[crn] = []
                            if regulator not in RegEnz[crn]:
                                RegEnz[crn].append(regulator)
                    except:
                        pass