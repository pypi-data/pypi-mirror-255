import csv
import ast
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from cobra.flux_analysis import flux_variability_analysis
from cobra.flux_analysis import single_reaction_deletion
from cameo import load_model
#from cameo.strain_design.deterministic.flux_variability_based import FSEOF
from flux_variability_based import FSEOF as cFSEOF
from sklearn import model_selection, preprocessing, feature_selection, ensemble, linear_model, metrics
from sklearn.linear_model import LinearRegression
from lime import lime_tabular
import networkx as nx
import pickle


tol = 1e-6 # Tolerancia, valores menores se consideran 0
dir = './opt_disturb_random/'
biomass = 'BIOMASS_Ec_iML1515_core_75p37M'
tmodel = load_model("iML1515a.xml")
target = 'EX_trp__L_e'

###########################################################################################################
###########################################  Funciones    #################################################
###########################################################################################################

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

def plot_rn_bio_real(rn):
    x_val = (all_TRP_fluxes.T.loc[biomass].values)
    y1_val = all_TRP_fluxes.T.loc[target].values
    y2_val = all_TRP_fluxes.T.loc[rn].values
    plt.scatter(x_val, y1_val, label=target, color='blue', marker='+')
    plt.scatter(x_val, y2_val, label=rn, color='red', marker='x')
    plt.xlabel('Flux of biomass')
    plt.ylabel('Flux of ' + target + '/' + rn)
    plt.title('Comparation of fluxes')
    plt.legend()
    plt.show()


def get_max_flux(model, rn):
    model.objective = model.reactions.get_by_id(rn)
    max_rn = model.slim_optimize()
    return max_rn

###########################################################################################################
####################################### Carga de datos ####################################################
###########################################################################################################

cur_mods = {}
with open('./gen_mods_trp.csv') as f:
    reader_obj = csv.reader(f)
    header = next(reader_obj)
    for row in reader_obj:
        if len(row) > 2:
            c_gene, c_rn, c_type = row[0], row[1], row[2]
            if c_rn != '':
                cur_mods[c_rn] = [c_gene, c_type]


###########################################################################################################
###########################################  Reacciones   #################################################
###########################################################################################################

def model_base():
    model = tmodel.copy()
    model.reactions.EX_glc__D_e.lower_bound = -18
    #model.reactions.GHMT2r.lower_bound = 0
    model.reactions.TRPS1.delete()
    model.reactions.TRPAS2.lower_bound = 0
    model.reactions.PPM.lower_bound = 0
    model.reactions.PRPPS.lower_bound = 0
    model.reactions.TRPt2rpp.lower_bound = 0 # BioCyc reporta las enzimas como de protoplasma a citosol
    return model

# Se encuentran cuales son las reacciones esenciales para crecimiento y produccion del metabolito objetivo
model = model_base()
model.reactions.get_by_id(target).lower_bound = 0.005 # Agrego las reacciones esenciales para producir el metabolito objetivo
RxnRatio = single_reaction_deletion(model).fillna(0)
ids_essential = RxnRatio[RxnRatio['growth'] < tol]['ids'].to_list()
rxns_essential = [list(id)[0] for id in ids_essential]


#Busca que reacciones nunca son utilizadas
model = model_base()
df_fva = flux_variability_analysis(model, fraction_of_optimum=0.0)
rxns_no_flux = [] # Reacciones que no llevan flujo nunca
rxns_flux = []
df_fva['amin'] = abs(df_fva['minimum'])
df_fva['amax'] = abs(df_fva['maximum'])
for rn, data_mm in df_fva.iterrows():
    if ((data_mm['amin'] < tol) and (data_mm['amax'] < tol)):
        rxns_no_flux.append(rn)
    else:
        rxns_flux.append(rn)



#tmodel.remove_reactions(rxns_no_flux)



# Busca cuales son las reacciones optimas para producir el metabolito objetivo sin restricciones de flujo
max_target = get_max_flux(model_base(), target)
model = model_base()
model.reactions.get_by_id(target).lower_bound = max_target
sol_optima = model.optimize(objective_sense='min')
for rn in model.reactions:
    if rn.id in rxns_flux:
        rn.lower_bound = sol_optima.fluxes[rn.id]


df_fva2 = flux_variability_analysis(model, fraction_of_optimum=1, reaction_list=rxns_flux)
#df_fva2 = flux_variability_analysis(model, fraction_of_optimum=1)
df_sum = abs(df_fva2['minimum']) + abs(df_fva2['maximum'])
RxnOptima = list(df_sum[df_sum >= tol].index)

RxnOptimaEx = []
for rn in RxnOptima:
    max = df_fva2.at[rn, 'maximum']
    min = df_fva2.at[rn, 'minimum']
    if abs(max) < 999 and abs(min) < 999: # Elimino reacciones que forman loops y los valores suben cerca del limite
        RxnOptimaEx.append(rn)

##################################################################################################################################
#####################################################    Empieza parte de perturbacion   #########################################
##################################################################################################################################

def model_base():
    model = tmodel.copy()
    model.reactions.EX_o2_e.lower_bound=-7.5
    model.reactions.EX_glc__D_e.lower_bound=-16.0
    model.reactions.EX_co2_e.lower_bound=7.0
    model.reactions.EX_co2_e.upper_bound=1000.0  
    model.reactions.get_by_id(biomass).lower_bound = 0.05
    model.reactions.TRPAS2.lower_bound = 0 # La reaccion reversa ocurre en condiciones muy controladas
    model.reactions.TRPS1.delete() # Es la suma de las reacciones TRPS2 y TRPS3
    model.reactions.PPM.lower_bound = 0
    model.reactions.PRPPS.lower_bound = 0
    model.reactions.TRPt2rpp.lower_bound = 0 # BioCyc reporta las enzimas como de protoplasma a citosol
    ####################### Start simulation that classify NADTRHD as overexpression
    #model.reactions.THD2pp.lower_bound = 45
    #model.reactions.GLNS.lower_bound = 3
    #model.reactions.GLUDy.upper_bound = -3
    #model.reactions.ICDHyr.lower_bound = 0.05
    #model.reactions.PRPPS.lower_bound = 3
    #model.reactions.PGCD.lower_bound = 3
    ####################### End simulation
    return model


max_target = get_max_flux(model_base(), target)
b_model = model_base()
b_model.reactions.get_by_id(target).lower_bound = max_target*0.95
sol = b_model.optimize()
sol.fluxes[target] = max_target*0.95


strains = []
all_fluxes_df = {}
perturbation = RxnOptimaEx.copy()
perturbation.append('wt')
factor = 1.3
for rxn in perturbation:
    cur_model = model_base()
    rxn
    if rxn != 'wt':
        max_i = get_max_flux(model_base(), rxn)
        max_i = max_i if abs(max_i) < abs((sol.fluxes[rxn]*factor)) else (sol.fluxes[rxn]*factor)
        flux = sol.fluxes[rxn] if abs(sol.fluxes[rxn]) > tol else 0
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
        #fseof_result = fseof.run(target=cur_model.reactions.get_by_id(target))
    except Exception as ex:
        print('Error en ' + rxn)
        print(ex)
        continue
    cur_all_fluxes = fseof_result.all_fluxes
    json2df(cur_all_fluxes).T.to_csv(dir + rxn + '_strain.csv')
    df_cur_all_fluxes = json2df(cur_all_fluxes)
    df_cur_all_fluxes.columns = [rxn + ' ' + str(col) for col in df_cur_all_fluxes.columns]
    all_fluxes_df[rxn + '_strain'] = df_cur_all_fluxes
    strains.append(rxn)


all_TRP_fluxes = pd.concat([df.T for df in all_fluxes_df.values()])
all_TRP_fluxes.fillna(0, inplace=True)
all_TRP_fluxes.to_csv(dir + 'all_fluxes.csv')


conserv_reactions_TRP_fluxes = all_TRP_fluxes.T
conserv_reactions_TRP_fluxes.to_csv(dir + 'all_strain_all_rn_fluxes.csv')

df_random = conserv_reactions_TRP_fluxes[[]]
df_random['flux_total'] = 0
df_random['any_flux'] = 0


for rn in conserv_reactions_TRP_fluxes.T.columns:
    if rn in rxns_flux:
        total_flux = float(abs(conserv_reactions_TRP_fluxes.T[rn]).sum())
        df_random.at[rn, 'flux_total'] = total_flux
        if total_flux > tol:
            df_random.at[rn, 'any_flux'] = 1


df_random['modification'] = ''
for cm, val in cur_mods.items():
    df_random.at[cm, 'modification'] = val[1]
    

df_compare = pd.DataFrame(index=all_TRP_fluxes.columns)
t_all_fluxes = all_TRP_fluxes.T
count_invert = {}
for strain in strains:
    df_compare[strain] = ''
    cols = []
    for i in range(0, 10):
        col = strain + ' ' + str(i)
        if col not in t_all_fluxes.columns:
            continue
        cols.append(col)
    if len(cols) == 0:
        continue
    cdf = t_all_fluxes[cols].T
    x_val = cdf[biomass]
    y_target_val, max1 = normalize_data(cdf[target])
    s1 = calc_slope(x_val.values, y_target_val.values)
    for rn in cdf.columns:
        if rn not in count_invert:
            count_invert[rn] = [0, 0, 0, 0] # [invertido, no invertido, horizontal, biomasa]
        if cdf[rn].abs().sum() == 0:
            df_compare.at[rn, strain] = 'zero'
        else:
            y_rn_real = cdf[rn]
            y_rn_val, max2 = normalize_data(y_rn_real)
            s2 = calc_slope(x_val.values, y_rn_val.values)
            s_real, b_real = get_line_eq(x_val.values, cdf[rn].values)
            #print(str(s2) + '  - ' + str(b))
            if s2 == 0:
                count_invert[rn][2] += 1
            elif s1*s2 < 0:
                y_rn_val = invert_line(y_rn_val)
                if abs(b_real) < tol:
                    count_invert[rn][3] += 1
                    #print(rn + ' biomass')
                else:
                    count_invert[rn][0] += 1
            else:
                count_invert[rn][1] += 1
            df_compare.at[rn, strain] = str((calc_diff(y_target_val, y_rn_val)))



t_compare = df_compare.copy()


df_compare['rel_biomass'] = '0'
bio_fluxes = all_TRP_fluxes[biomass]
bio_fluxes = pd.DataFrame(bio_fluxes, columns=[biomass]).T
for rn in t_all_fluxes.index:
    if rn in rxns_no_flux:
        continue
    rn_fluxes = all_TRP_fluxes[rn]
    rn_fluxes = pd.DataFrame(rn_fluxes, columns=[rn]).T
    data_rn_flux = np.array([])
    data_bio_flux = np.array([])
    for strain in strains:
        cols = []
        for i in range(0, 10):
            col = strain + ' '  + str(i)
            if col in t_all_fluxes.columns:
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
        



df_compare['count'] = ''
df_compare['used'] = ''
t_df = t_compare.T
l_threshold = 0.01
for col in t_df.columns:
    vals = t_df[col].values
    arr_vals = []
    for val in vals:
        try:
            val = float(val)
            if val < l_threshold:
                arr_vals.append(val)
        except:
            continue
    df_compare.at[col, 'count'] = len(arr_vals)
    df_compare.at[col, 'used'] = 1 if len(arr_vals) > 0 else 0
    


df_compare['modification'] = ''
for cm, val in cur_mods.items():
    df_compare.at[cm, 'modification'] = val[1]


df_compare['essential'] = '0'
for rn in  rxns_essential:
    df_compare.at[rn, 'essential'] = 1


df_compare['optima'] = 0
for rn in RxnOptimaEx:
    df_compare.at[rn, 'optima'] = 1


df_compare['invert'] = 0
df_compare['no_invert'] = 0
for rn, val in count_invert.items():
    df_compare.at[rn, 'invert'] = val[0]
    df_compare.at[rn, 'no_invert'] = val[1]



df_compare.to_csv(dir + 'compare_' + target + '.csv')







########################################################################################################################################
#####################################################   Random Forest    ###############################################################
########################################################################################################################################



df_random = pd.concat([df_random, df_compare['rel_biomass']], axis=1)
df_random = pd.concat([df_random, df_compare['count']], axis=1)
df_random = pd.concat([df_random, df_compare['invert']], axis=1)
df_random = pd.concat([df_random, df_compare['no_invert']], axis=1)
df_random = pd.concat([df_random, df_compare['used']], axis=1)
df_random = pd.concat([df_random, df_compare['essential']], axis=1)
df_random = pd.concat([df_random, df_compare['optima']], axis=1)
df_random = pd.concat([df_random, df_compare['any_flux']], axis=1)


df_random['corr'] = 0
df_random['icorr'] = 0
len_strain = len(strains)
for rn in df_random.index:
    df_random.at[rn, 'corr'] = 1 if (df_random.at[rn, 'no_invert'] - df_random.at[rn, 'invert'] > (len_strain/4)) else 0
    df_random.at[rn, 'icorr'] = 1 if (df_random.at[rn, 'invert'] > (len_strain/2)) else 0


df_random['no_flux'] = 0
for rn in rxns_no_flux:
    df_random.at[rn, 'no_flux'] = 1


df_random['genes_keio'] = ''
df_random['strain_keio'] = ''

csv_keio = './keio_parsed.csv'
with open(csv_keio, 'r') as file:
    # Create a CSV reader
    csv_reader = csv.reader(file)
    # Iterate through each row in the CSV file
    for row in csv_reader:
        rns = ast.literal_eval(row[3])
        for rn in rns:
            #print(rn)
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



df_all = df_random[['modification', 'any_flux', 'essential', 'optima', 'rel_biomass', 'used', 'corr']]
df_all.set_index('modification')
df_all['essential'] = df_all['essential'].astype('category').cat.codes
df_all['optima'] = df_all['optima'].astype('category').cat.codes
df_all['rel_biomass'] = df_all['rel_biomass'].astype('category').cat.codes
df_all['used'] = df_all['used'].astype('category').cat.codes
df_all['corr'] = df_all['corr'].astype('category').cat.codes
df_all['any_flux'] = df_all['any_flux'].astype('category').cat.codes
categories = df_all['modification'].astype('category')
category_codes = df_all['modification'].astype('category').cat.codes
df_all['modification'] = df_all['modification'].astype('category').cat.codes
hm_code2cat = dict(zip(category_codes, categories))
hm_cat2code = dict(zip(categories, category_codes))
scaler = preprocessing.MinMaxScaler(feature_range=(0,1))
X = scaler.fit_transform(df_all.drop("modification", axis=1))
df_scaled= pd.DataFrame(X, columns=df_all.drop("modification", axis=1).columns, index=df_all.index)
df_scaled["modification"] = df_all["modification"]
df_scaled.head()




df = df_scaled[df_scaled['modification'] != hm_cat2code['']]
df_train, df_test = model_selection.train_test_split(df, test_size=0.3)
print("X_train shape:", df_train.drop("modification",axis=1).shape, "| X_test shape:", df_test.drop("modification",axis=1).shape)
print(df_train.shape[1], "features:", df_train.drop("modification",axis=1).columns.to_list())


corr_matrix = df.copy()
for col in corr_matrix.columns:
    if corr_matrix[col].dtype == "O":
        corr_matrix[col] = corr_matrix[col].factorize(sort=True)[0]


corr_matrix = corr_matrix.corr(method="pearson")
sns.heatmap(corr_matrix, vmin=-1., vmax=1., annot=True, fmt='.2f', cmap="YlGnBu", cbar=True, linewidths=0.5)
plt.title("pearson correlation")
plt.show()



####################################### Grafica lasso y anova
X = df_train.drop("modification", axis=1).values
y = df_train["modification"].values
feature_names = df_train.drop("modification", axis=1).columns
## Anova
selector = feature_selection.SelectKBest(score_func=feature_selection.f_classif, k='all').fit(X,y)
anova_selected_features = feature_names[selector.get_support()]
## Lasso regularization
selector = feature_selection.SelectFromModel(estimator= linear_model.LogisticRegression(C=1, penalty="l1", solver='liblinear'), max_features=4).fit(X,y)
lasso_selected_features = feature_names[selector.get_support()]
## Plot
dtf_features = pd.DataFrame({"features":feature_names})
dtf_features["anova"] = dtf_features["features"].apply(lambda x: "anova" if x in anova_selected_features else "")
dtf_features["num1"] = dtf_features["features"].apply(lambda x: 1 if x in anova_selected_features else 0)
dtf_features["lasso"] = dtf_features["features"].apply(lambda x: "lasso" if x in lasso_selected_features else "")
dtf_features["num2"] = dtf_features["features"].apply(lambda x: 1 if x in lasso_selected_features else 0)
dtf_features["method"] = dtf_features[["anova","lasso"]].apply(lambda x: (x[0]+" "+x[1]).strip(), axis=1)
dtf_features["selection"] = dtf_features["num1"] + dtf_features["num2"]
sns.barplot(y="features", x="selection", hue="method", data=dtf_features.sort_values("selection", ascending=False), dodge=False)
plt.show()




############## Random Forest
X = df_train.drop("modification", axis=1).values
y = df_train["modification"].values
feature_names = df_train.drop("modification", axis=1).columns.tolist()
## Importance
model = ensemble.RandomForestClassifier(n_estimators=1000, criterion="entropy", random_state=0)
model.fit(X,y)
importances = model.feature_importances_
## Put in a pandas dtf
dtf_importances = pd.DataFrame({"IMPORTANCE":importances, "VARIABLE":feature_names}).sort_values("IMPORTANCE", ascending=False)
dtf_importances['cumsum'] =  dtf_importances['IMPORTANCE'].cumsum(axis=0)
dtf_importances = dtf_importances.set_index("VARIABLE")
    
## Plot
fig, ax = plt.subplots(nrows=1, ncols=2, sharex=False, sharey=False)
fig.suptitle("Features Importance", fontsize=20)
ax[0].title.set_text('variables')
dtf_importances[["IMPORTANCE"]].sort_values(by="IMPORTANCE").plot(kind="barh", legend=False, ax=ax[0]).grid(axis="x")
ax[0].set(ylabel="")
ax[1].title.set_text('cumulative')
dtf_importances[["cumsum"]].plot(kind="line", linewidth=4, legend=False, ax=ax[1])
ax[1].set(xlabel="", xticks=np.arange(len(dtf_importances)), xticklabels=dtf_importances.index)
plt.xticks(rotation=70)
plt.grid(axis='both')
plt.show()


col_avoid = ['modification']
X_names = []

for col_name in df.columns:
    if col_name in col_avoid:
        continue
    X_names.append(col_name)


X_train = df_train[X_names].values
y_train = df_train["modification"].values
X_test = df_test[X_names].values
y_test = df_test["modification"].values

model = ensemble.GradientBoostingClassifier()
param_dic = {'learning_rate':[0.15,0.1,0.05,0.01,0.005,0.001],      #weighting factor for the corrections by new trees when added to the model
'n_estimators':[100,250,500,750,1000,1250,1500,1750],  #number of trees added to the model
'max_depth':[2,3,4,5,6,7,8,9,10,11,12],    #maximum depth of the tree
'min_samples_split':[2,4,6,8,10,20,40],    #sets the minimum number of samples to split
'min_samples_leaf':[1,3,5,7,9],     #the minimum number of samples to form a leaf
'max_features':[2,3,4,5,6,7],     #square root of features is usually a good starting point
'subsample':[0.7,0.75,0.8,0.85,0.9,0.95,1]}       #the fraction of samples to be used for fitting the individual base learners. Values lower than 1 generally lead to a reduction of variance and an increase in bias.
## random search
random_search = model_selection.RandomizedSearchCV(model, 
       param_distributions=param_dic, n_iter=100, 
       scoring="accuracy").fit(X_train, y_train)
print("Best Model parameters:", random_search.best_params_)
print("Best Model mean accuracy:", random_search.best_score_)
model = random_search.best_estimator_


## train
model.fit(X_train, y_train)
## test
predicted_prob = model.predict_proba(X_test)[:,1]
predicted = model.predict(X_test)

## Accuray e AUC
accuracy = metrics.accuracy_score(y_test, predicted)
#auc = metrics.roc_auc_score(y_test, predicted_prob, multi_class='ovr')
print("Accuracy (overall correct predictions):",  round(accuracy,2))
#print("Auc:", round(auc,2))
    
## Precision e Recall
recall = metrics.recall_score(y_test, predicted,  average='weighted')
precision = metrics.precision_score(y_test, predicted, average='weighted')
print("Recall (all 1s predicted right):", round(recall,2))
print("Precision (confidence when predicting a 1):", round(precision,2))
print("Detail:")
print(metrics.classification_report(y_test, predicted, target_names=[str(i) for i in np.unique(y_test)]))


classes = np.unique(y_test)
fig, ax = plt.subplots()
cm = metrics.confusion_matrix(y_test, predicted, labels=classes)
sns.heatmap(cm, annot=True, fmt='d', cmap=plt.cm.Blues, cbar=False)
ax.set(xlabel="Pred", ylabel="True", title="Confusion matrix")
ax.set_yticklabels(labels=classes, rotation=0)
plt.show()



X_pred = df_all[X_names].values
predicted_prob_all = model.predict_proba(X_pred)[:,1]
predicted_all = model.predict(X_pred)

df_predicted = pd.DataFrame(columns=['Predicted'], index=list(df_all.index))
df_predicted['Predicted'] = predicted_all

for idx in df_predicted.index:
    df_predicted.at[idx, 'Predicted'] = hm_code2cat[df_predicted.at[idx, 'Predicted']] 


df_predicted.to_csv(dir + 'predicted.csv')


print("True:", y_test[4], "--> Pred:", predicted[4], "| Prob:", np.max(predicted_prob[4]))

idx = 3
explainer = lime_tabular.LimeTabularExplainer(training_data=X_train, feature_names=X_names, class_names=np.unique(y_train), mode="classification")
explained = explainer.explain_instance(X_test[idx], model.predict_proba, num_features=10)
explained.as_pyplot_figure()
plt.show()





with open(dir + 'model_rf.dat', 'wb') as file:
    pickle.dump(model, file)


with open(dir + 'df_train.dat', 'wb') as file:
    pickle.dump(df_train, file)

with open(dir + 'df_test.dat', 'wb') as file:
    pickle.dump(df_test, file)







