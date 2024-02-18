import pandas as pd
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from tqdm import tqdm
from cobra.flux_analysis import single_reaction_deletion
from cobra.flux_analysis import flux_variability_analysis
from QPAML import config

tol = config.non_zero_flux_threshold

def json2df(js):
    df = pd.DataFrame(js).transpose()
    df.columns = (i + 1 for i in range(10))
    return df

def get_line_eq(x, y):
    X = x.reshape(-1, 1)
    lin_model = LinearRegression()
    lin_model.fit(X, y)
    slope = lin_model.coef_[0]
    intercept = lin_model.intercept_
    return slope, intercept

def calc_diff_line(m, b, x, y):
    sds = 0
    for i in range(0, len(x)):
        y_pred = x[i]*m + b
        dif = y_pred - y[i]
        ds = dif**2
        sds += ds
    return sds

def calc_diff(y1, y2):
    return ((y2-y1)**2).sum()

def calc_slope(x, y):
    x = np.array(x).reshape(-1,1)
    regression_model = LinearRegression().fit(x, y)
    slope = regression_model.coef_[0]
    return slope

def normalize_data(vals):
    abs_rn = vals.abs()
    min = abs_rn.min()
    max = abs_rn.max() - min
    ori_vals = abs_rn - min
    if max == 0:
        norm_vals = ori_vals
    else:
        norm_vals = ori_vals/max
    return norm_vals, max

def invert_line(vals):
    max = vals.max()
    invert = max - vals
    return invert

def get_max_flux(model, rn):
    model.objective = model.reactions.get_by_id(rn)
    max_rn = model.slim_optimize()
    return max_rn


def get_bounded_model(model, bounds):
    b_model = model.copy()
    for rn, bounds in bounds.items():
        if rn not in model.reactions:
            raise ValueError('Model does not contain the reaction ' + rn)
        if 'lb' in bounds:
            b_model.reactions.get_by_id(rn).lower_bound = bounds['lb']
        if 'ub' in bounds:
            b_model.reactions.get_by_id(rn).upper_bound = bounds['ub']
        if b_model.reactions.get_by_id(rn).bounds[0] > b_model.reactions.get_by_id(rn).bounds[1]:
            raise ValueError('Lower bound is greater than upper bound for reaction ' + rn)
    return b_model


def get_essential(model, min_biomass=tol, reactions=None):
    if reactions == None:
        [rn.id for rn in model.reactions]
    progress_bar = tqdm(total=100, desc="Essential reactions", unit="%")
    model = model.copy()
    progress_bar.update(20)
    RxnRatio = single_reaction_deletion(model=model, reaction_list=reactions).fillna(0)
    progress_bar.update(60)
    rxns_essential = [list(id)[0] for id in RxnRatio[RxnRatio['growth'] < min_biomass]['ids'].to_list()]
    progress_bar.update(20)
    progress_bar.close()
    return rxns_essential

def get_flux_rn(model):
    progress_bar = tqdm(total=100, desc="Zero-flux reactions", unit="%")
    model = model.copy()
    progress_bar.update(5)
    df_fva = flux_variability_analysis(model, fraction_of_optimum=0.0)
    progress_bar.update(75)
    rxns_no_flux = list(df_fva[(abs(df_fva['minimum']) < tol) & (abs(df_fva['maximum']) < tol)].index)
    progress_bar.update(10)
    rxns_flux = list(set(df_fva.index) - set(rxns_no_flux))
    progress_bar.update(10)
    progress_bar.close()
    return (rxns_no_flux, rxns_flux)


def get_rn_optima(model, target, flux_rn=None):
    if flux_rn == None:
        flux_rn = [rn.id for rn in model.reactions]
    progress_bar = tqdm(total=100, desc="pFBA optima reactions", unit="%")
    max_target = get_max_flux(model.copy(), target)
    progress_bar.update(5)
    model = model.copy()
    progress_bar.update(10)
    model.reactions.get_by_id(target).lower_bound = max_target
    progress_bar.update(5)
    sol_optima = model.optimize(objective_sense='min')
    progress_bar.update(5)
    for f_rn in flux_rn:
        rn = model.reactions.get_by_id(f_rn)
        if rn.id in flux_rn:
            rn.lower_bound = sol_optima.fluxes[rn.id]
    progress_bar.update(65)
    df_fva2 = flux_variability_analysis(model, fraction_of_optimum=1, reaction_list=flux_rn)
    RxnOptima = list(df_fva2[((df_fva2['minimum'].abs() + df_fva2['maximum'].abs()) >= tol)
                            & (abs(df_fva2['minimum']) < 999) 
                            & (abs(df_fva2['maximum']) < 999) ].index)
    progress_bar.update(10)
    progress_bar.close()
    return RxnOptima

