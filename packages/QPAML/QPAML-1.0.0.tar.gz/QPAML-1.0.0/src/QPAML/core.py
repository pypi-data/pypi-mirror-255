import pandas as pd
import numpy as np
from QPAML.functions import *
from QPAML.flux_variability_based import FSEOF as cFSEOF
from QPAML import config
from sklearn import preprocessing
import pickle
import math
import networkx as nx
import os
from QPAML.biocyc import *
from tqdm import tqdm


tol = config.non_zero_flux_threshold

cdir = current_directory = os.path.dirname(os.path.abspath(__file__))


class QPAMLResult:
    def __init__(self, essential, no_flux, flux, optima, predicted, all_fluxes, ml_df, ur_model, r_model) -> None:
        self.rn_essentials = essential
        self.rn_no_flux = no_flux
        self.rn_flux = flux
        self.rn_optima = optima
        self.predicted = predicted
        self.all_fluxes = all_fluxes
        self.ml_df = ml_df
        self.ur_model = ur_model
        self.r_model = r_model
        self.disruption_distance = pd.DataFrame()
        self.graph = None
        self.feedback_reg = None

    def get_graph_reactions(self, rns, model):
        G = nx.DiGraph()
        for reaction in rns:
            reaction = model.reactions.get_by_id(reaction)
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
        self.graph = G
        return G

    def update_distances(self, avoid = []):
        self.disruption_distance = pd.DataFrame()
        tmodel = self.ur_model.copy()
        over = self.rn_optima
        ko = list(self.predicted[self.predicted['Predicted'] == 'KO'].index)
        kd = list(self.predicted[self.predicted['Predicted'] == 'KD'].index)
        relevant = list(set(over) | set(ko) | set(kd))
        G = self.get_graph_reactions(relevant, tmodel)
        levels = {}
        all_neighbors = []
        all_neighbors_temp = over.copy()
        count = 0
        while all_neighbors != all_neighbors_temp:
            count += 1
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
                self.disruption_distance.at[rn, 'Distance'] = i


    def find_fb_rn(self, model, avoid_regulators = [], reg_dir = None):
        """
        Identify reactions subject to negative feedback regulation.

        Parameters:
        - model (cobra.Model): Cobra Metabolic Model.
        - avoid_regulators (list): List of metabolites serving as global regulators, for instance ['ATP', 'ADP', 'AMP', 'NAD', 'NADH', 'NADP', 'NADPH', 'Pi'].
        - reg_dir (str): Directory where regulatory information is obtained. The algorithm uses BioCyc flat files. All files must be in the same folder; if no directory is specified, the EcoCyc (E. coli) files are used. The directory must contain the following files: transunits.dat, compounds.dat, enzrxns.dat, genes.dat, pathways.dat, promoters.dat, proteins.dat, protligandcplxes.dat, reactions.dat, regulation.dat.

        Returns:
        - Union[dict, None]: A dictionary with negative feedback regulatory relationships is returned. If any errors occur during the process, None is returned.
        """

        if reg_dir == None:
            reg_dir = cdir + '/biocyc/'
        else:
            if not os.path.exists(reg_dir):
                print(reg_dir + ' directory does\'t exists')
                return None
            files = ['transunits.dat', 'compounds.dat', 'enzrxns.dat', 'genes.dat', 'pathways.dat', 'promoters.dat', 'proteins.dat', 'protligandcplxes.dat', 'reactions.dat', 'regulation.dat']
            missing = []
            for file in files:
                if not os.path.exists(reg_dir + file):
                    missing.append(file)
            if len(missing) > 0:
                print('Missing files: ' + str(missing))
                return None

        tmodel = model.copy()
        adapter = Adapter(tmodel)

        hm_promoter = get_promoters(reg_dir)
        hm_TU = get_TU(hm_promoter, reg_dir)
        hm_complex = get_complex(reg_dir)
        hm_gene = get_gene(hm_promoter, hm_TU, reg_dir)
        hm_gene_tu = get_hm_gene_tu(hm_TU, hm_gene)
        hm_protein = get_protein(hm_gene, reg_dir)
        update_promoters(hm_protein)
        hm_regulation = get_regulation(reg_dir)
        hm_types_cpd, hm_compound = get_compounds(reg_dir)
        hm_enzrxns = get_enzrxns(hm_regulation, hm_protein, hm_gene, hm_TU, reg_dir)
        hm_reaction, nodes, att_reactions, metabolites, cpd_transported = get_reactions(hm_enzrxns, hm_protein, hm_gene, hm_gene_tu, hm_TU, reg_dir)
        met_in_reactions = get_cpd_in_rn(hm_reaction)
        update_regulation(hm_enzrxns, met_in_reactions)
        hm_pathway, hm_rn_pathway = get_pathways(reg_dir)

        metOptima = []
        for rn in self.rn_optima:
            for met in tmodel.reactions.get_by_id(rn).metabolites.keys():
                try:
                    met_bio = adapter.get_cpd_biocyc(met.id)
                except:
                    continue
                for met_syn in met_bio:
                    if met_syn not in metOptima:
                        metOptima.append(met_syn)

        cofactors = avoid_regulators # ['ATP', 'ADP', 'AMP', 'NAD', 'NADH', 'NADP', 'NADPH', 'Pi']
        RegEnz = {}
        for name, reg in hm_regulation.items():
            if 'Regulation-of-Enzyme-Activity' in reg.type:
                if '-' in reg.mode:
                    for regulator in reg.regulator:
                        if regulator in metOptima and regulator not in cofactors:
                            enzyme = reg.regulated_entity[0]
                            reaction_bc = hm_enzrxns[enzyme].reaction[0]
                            try:
                                rns_bigg = adapter.get_rn_bigg(reaction_bc)
                                if len(set.intersection(set(rns_bigg), set(self.rn_optima))):   
                                    print(regulator + '   ' + str(adapter.get_rn_bigg(reaction_bc)))
                                    crn = adapter.get_rn_bigg(reaction_bc)[0]
                                    if crn not in RegEnz:
                                        RegEnz[crn] = []
                                    if regulator not in RegEnz[crn]:
                                        RegEnz[crn].append(regulator)
                            except:
                                pass
        self.feedback_reg = RegEnz
        return RegEnz
        

class QPAML:
    '''
    from cameo import load_model
    import QPAML
    from QPAML.core import QPAML
    tmodel = load_model("iML1515") 
    tmodel.reactions.TRPAS2.lower_bound = 0.0
    ur_media = {'EX_glc__D_e': {'lb':-18.0}}
    r_media = {'EX_o2_e':{'lb':-7.5},
            'EX_glc__D_e': {'lb':-16.0},
            'EX_co2_e':{'lb':7.0, 'ub':1000},
            'BIOMASS_Ec_iML1515_core_75p37M':{'lb':0.05}}

    qpaml = QPAML(tmodel)

    qpaml_res = qpaml.run(target='EX_trp__L_e',
            biomass='BIOMASS_Ec_iML1515_core_75p37M',
            ur_media=ur_media,
            r_media=r_media)

    avoid = ['h', 'h2o', 'nadp', 'nad', 'atp', 'pi', 'ppi', 'nadph', 'nadh', 'coa', 'co2', 'amp', 'adp', 'nh4', 'o2', 'so4', 'gdp', 'gtp', 'utp', 'udp', 'ump']
    qpaml_res.update_distances(avoid)
    '''
    def __init__(self, model, *args, **kwargs) -> None:
        super(QPAML, self).__init__(*args, **kwargs)
        self.cbmodel = model
        self.r_media = {}
        self.ur_media = {}
        
    def  reset_restricted_media(self):
        self.r_media = {}

    def reset_unrestricted_media(self):
        self.ur_media = {}


    def _add_constrain(self, media, rn, lb, ub):
        if rn not in self.cbmodel.reactions:
            raise ValueError('Model does not contain the reaction ' + rn)
        
        if lb == None and ub == None:
            print('No bounds used in parameters.')
            return

        if lb != None:
            try:
                lb = float(lb)
            except ValueError:
                print(str(lb) + ' is not a numerical value')
                return
            
        if ub != None:
            try:
                ub = float(ub)
            except ValueError:
                print(str(ub) + ' is not a numerical value')
                return

        if rn not in media:
            media[rn] = {}

        if lb != None:
            media[rn]['lb'] = lb

        if ub != None:
            media[rn]['ub'] = ub


    def constrain_restricted_media(self, rn, lb = None, ub = None):
        self._add_constrain(self.r_media, rn, lb, ub)
    
    def constrain_unrestricted_media(self, rn, lb = None, ub = None):
        self._add_constrain(self.ur_media, rn, lb, ub)

    
    def run(self, target=None, biomass=None):
        print('\n')
        try:
            r_model = get_bounded_model(self.cbmodel, self.r_media)
            ur_model = get_bounded_model(self.cbmodel, self.ur_media)
        except ValueError as ex:
            print(ex)
            return QPAMLResult([], [], [], [], pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
            

        rxns_no_flux, rxns_flux = get_flux_rn(ur_model)

        rxns_essential = get_essential(ur_model, tol, rxns_flux)
        
        RxnOptimaEx = get_rn_optima(ur_model, target, rxns_flux)        
                
        max_target = get_max_flux(r_model.copy(), target)
        if math.isnan(max_target) or abs(max_target) < tol:
            print("The target reaction is not reachable.")
            return QPAMLResult(rxns_essential, rxns_no_flux, rxns_flux, [], pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
        
        b_model = r_model.copy()
        b_model.reactions.get_by_id(target).lower_bound = max_target*0.95
        sol = b_model.optimize()
        sol.fluxes[target] = max_target*0.95
        strains = []
        hm_df_fluxes = {}
        factor = 1.5
        progress_bar = tqdm(total=len(RxnOptimaEx) + 1, desc="Getting fluxes", unit="Perturbation")
        for rxn in RxnOptimaEx + ['wt']:
            progress_bar.update(1)
            cur_model = r_model.copy()
            if rxn != 'wt':
                max_i = get_max_flux(r_model.copy(), rxn)
                max_i = max_i if abs(max_i) < abs(sol.fluxes[rxn]*factor) else (sol.fluxes[rxn]*factor)
                if max_i > tol:
                    cur_model.reactions.get_by_id(rxn).lower_bound = max_i*0.95
                elif max_i < -tol:
                    cur_model.reactions.get_by_id(rxn).upper_bound = max_i*0.95
                else:
                    continue
            fseof = cFSEOF(cur_model)
            try:
                fseof_result = fseof.run(target=cur_model.reactions.get_by_id(target), exclude=rxns_no_flux)
            except Exception as ex:
                continue
            df_cur_all_fluxes = json2df(fseof_result.all_fluxes)
            df_cur_all_fluxes.columns = [rxn + ' ' + str(col) for col in df_cur_all_fluxes.columns]
            hm_df_fluxes[rxn + '_strain'] = df_cur_all_fluxes
            strains.append(rxn)
        progress_bar.close()
        all_df_fluxes = pd.concat([df.T for df in hm_df_fluxes.values()])
        all_df_fluxes.fillna(0, inplace=True)
        all_df_fluxes_T = all_df_fluxes.T
        df_compare = pd.DataFrame(index=all_df_fluxes_T.index)
        count_corr = {}
        progress_bar = tqdm(total=len(strains), desc="Normalizing fluxes", unit="Perturbation")
        for strain in strains:
            progress_bar.update(1)
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
        progress_bar.close()
        t_compare = df_compare.copy()
        df_compare['rel_biomass'] = '0'
        bio_fluxes = pd.DataFrame(all_df_fluxes[biomass], columns=[biomass]).T
        progress_bar = tqdm(total=len(all_df_fluxes_T.index), desc="Biomass fluxes", unit="Reaction")
        for rn in all_df_fluxes_T.index:
            progress_bar.update(1)
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
        progress_bar.close()
        
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
        df_all = pd.DataFrame()
        df_all['any_flux'] = df_random['any_flux'].astype('category').cat.codes
        df_all['essential'] = df_random['essential'].astype('category').cat.codes
        df_all['optima'] = df_random['optima'].astype('category').cat.codes
        df_all['rel_biomass'] = df_random['rel_biomass'].astype('category').cat.codes
        df_all['used'] = df_random['used'].astype('category').cat.codes
        df_all['corr'] = df_random['corr'].astype('category').cat.codes
        scaler = preprocessing.MinMaxScaler(feature_range=(0,1))
        X = scaler.fit_transform(df_all)
        df_scaled= pd.DataFrame(X, columns=df_all.columns, index=df_all.index)
        df_scaled.head()
        hm_code2cat = {0:'0', 1:'Biomass', 2:'KD', 3:'KO', 4:'Low flux', 5:'Over'}
        with open(cdir + '/model/GBDT/model_rf.dat', 'rb') as file:
            model = pickle.load(file)
        X_names = []
        col_avoid = []
        for col_name in df_all.columns:
            if col_name in col_avoid:
                continue
            X_names.append(col_name)
        X_pred = df_all[X_names].values
        #predicted_prob_all = model.predict_proba(X_pred)[:,1]
        predicted_all = model.predict(X_pred)
        df_predicted = pd.DataFrame(columns=['Predicted'], index=list(df_all.index))
        df_predicted['Predicted'] = predicted_all
        for idx in df_predicted.index:
            df_predicted.at[idx, 'Predicted'] = hm_code2cat[df_predicted.at[idx, 'Predicted']] 

        result = QPAMLResult(rxns_essential, rxns_no_flux, rxns_flux, RxnOptimaEx, df_predicted, all_df_fluxes_T, df_compare, ur_model, r_model)
        return result







