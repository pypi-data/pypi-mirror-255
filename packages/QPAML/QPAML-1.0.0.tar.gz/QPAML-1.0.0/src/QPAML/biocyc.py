from QPAML.functions import *
import math
import os

cdir = current_directory = os.path.dirname(os.path.abspath(__file__))


class Adapter:
    '''
    Esta clase se encarga de manejar todo lo relacionado a convertir nomemclaturas entre BIGG y BioCyc
    '''
    def __init__(self, model):
        self.hm_cpd_bigg_bc = get_bigg_biocyc_cpd(model, cdir + '/bigg/bigg_models_metabolites.txt')
        self.hm_rn_bigg_bc = get_bigg_biocyc_rn(model, cdir + '/bigg/bigg_models_reactions.txt')
        self.hm_rn_bc_bigg = {}
        for bigg, arr_bc in self.hm_rn_bigg_bc.items():
            for bc in arr_bc:
                hm_append(self.hm_rn_bc_bigg, bc, bigg)
        self.hm_cpd_bc_bigg = {}
        for bigg, arr_bc in self.hm_cpd_bigg_bc.items():
            for bc in arr_bc:
                hm_append(self.hm_cpd_bc_bigg, bc, bigg)
        

    def get_rn_biocyc(self, rn_bigg):
        if rn_bigg in self.hm_rn_bigg_bc:
            return self.hm_rn_bigg_bc[rn_bigg]
        else:
            raise Exception(rn_bigg + " has not a biocyc id")

    def get_rn_bigg(self, rn_biocyc):
        if rn_biocyc in self.hm_rn_bc_bigg:
            return self.hm_rn_bc_bigg[rn_biocyc]
        else:
            raise Exception(rn_biocyc + " has not a bigg id")
        
    def get_cpd_biocyc(self, cpd_bigg):
        if cpd_bigg in self.hm_cpd_bigg_bc:
            return self.hm_cpd_bigg_bc[cpd_bigg]
        else:
            raise Exception(cpd_bigg + " has not a biocyc id")

    def get_cpd_bigg(self, cpd_biocyc):
        if cpd_biocyc in self.hm_cpd_bc_bigg:
            return self.hm_cpd_bc_bigg[cpd_biocyc]
        else:
            raise Exception(cpd_biocyc + " has not a bigg id")
        
    def get_empty_bigg(self, rns_bigg):
        empty = []
        for bg in rns_bigg:
            if not isinstance(bg, str):
                bg = bg.id
            if bg not in self.hm_rn_bigg_bc:
                empty.append(bg)
        return empty

class Pathway:
    def __init__(self, name, rns, superpathway):
        self.name = name
        self.rns = rns
        self.superpathway = superpathway

    

class Regulation:
    def __init__(self, name, mode, regulator, type, regulated_entity):
        self.name = name 
        self.mode = mode
        self.type = type
        self.regulator = regulator
        self.regulated_entity = regulated_entity
    def __str__(self):
        return self.name    
    

class Compound:
    def __init__(self, name, types, gibbs, mw, smiles):
        self.name = name
        self.types = types
        if len(gibbs) == 0:
            gibbs = [math.nan]
        self.gibbs = float(gibbs[0])
        self.mw = mw
        self.smiles = smiles
    def __str__(self):
        return self.name
    
    
class EnzRxns:
    def __init__(self, name, regulated_by, regulation, reaction, enzyme, promoter):
        self.name = name
        self.regulated_by = regulated_by
        self.regulation = regulation
        self.reaction = reaction
        self.enzyme = enzyme
        self.promoter = promoter
    def __str__(self):
        return self.name
    
class ReactionBC:
    def __init__(self, name, left, right, direction, enzymatic_reaction, types, gibbs, EC_number, gene, protein, operon, spontaneus):
        self.name = name
        self.types = types
        self.left = left
        self.right = right
        self.enzymatic_reaction = enzymatic_reaction
        self.EC_number = EC_number
        self.gene = gene
        self.protein = protein
        self.operon = operon
        self.spontaneus = spontaneus
        if len(gibbs) == 0:
            gibbs = [math.nan]
        self.gibbs = float(gibbs[0])
        if len(direction) == 1:
            self.direction = direction[0]
        else:
            self.direction = 'REVERSIBLE'
    
    def __str__(self):
        return self.name
    
    def get_cpds(self):
        cpds = []
        for left in self.left:
            if left not in cpds:
                cpds.append(left)
        for right in self.right:
            if right not in cpds:
                cpds.append(right)
        return cpds


    def use_cpd(self, cpd_id):
        return 1 if (cpd_id in self.left or cpd_id in self.right) else 0



    def decompose(self, item, hm_compound, hm_complex, hm_protein):
        res = {}
        if item in hm_compound:
            res = {item:{}}
        if item in hm_complex:
            for component in hm_complex[item].components:
                res[component] = self.decompose(component, hm_compound, hm_complex, hm_protein)
        if item in hm_protein:
            for component in hm_protein[item].components:
                res[component] = self.decompose(component, hm_compound, hm_complex, hm_protein)
        return res

    def get_keys(self, hm):
        res = []
        for key, value in hm.items():
            if key not in res:
                res.append(key)
            for key2 in self.get_keys(value):
                if key2 not in res:
                    res.append(key2)
        return res

    def get_regulators(self, hm_compound, hm_complex, hm_protein):
        regulators = {}
        for reg in self.get_regulations():
            for regulator in reg.regulator:
                if regulator not in regulators:        
                    regulators[regulator] = self.decompose(regulator, hm_compound, hm_complex, hm_protein)
        return regulators
    

    def get_regulators_cpd(self, hm_compound, hm_complex, hm_protein):
        regulators = {}
        for reg in self.get_regulations_cpd():
            for regulator in reg.regulator:
                if regulator not in regulators:        
                    regulators[regulator] = self.decompose(regulator, hm_compound, hm_complex, hm_protein)
        return regulators
    
    def get_regulators_tf(self, hm_compound, hm_complex, hm_protein):
        regulators = {}
        for reg in self.get_regulations_tf():
            for regulator in reg.regulator:
                if regulator not in regulators:        
                    regulators[regulator] = self.decompose(regulator, hm_compound, hm_complex, hm_protein)
        return regulators

    def get_regulators_list(self, hm_compound, hm_complex, hm_protein):
        regulator_list = self.get_keys(self.get_regulators(hm_compound, hm_complex, hm_protein))
        return regulator_list
    


    def get_regulators_list_cpd(self, hm_compound, hm_complex, hm_protein):
        regulator_list = self.get_keys(self.get_regulators_cpd(hm_compound, hm_complex, hm_protein))
        return regulator_list
    

    def get_regulators_list_tf(self, hm_compound, hm_complex, hm_protein):
        regulator_list = self.get_keys(self.get_regulators_tf(hm_compound, hm_complex, hm_protein))
        return regulator_list

    def get_regulations_cpd(self):
        regulations = self.get_regulations()
        regulations_cpd = []
        for regulation in regulations:
            if 'Regulation-of-Enzyme-Activity' in regulation.type:
                regulations_cpd.append(regulation)
        return regulations_cpd


    def get_regulations_tf(self):
        regulations = self.get_regulations()
        regulations_tf = []
        for regulation in regulations:
            if 'Transcription-Factor-Binding' in regulation.type:
                regulations_tf.append(regulation)
        return regulations_tf


    def get_regulations(self):
        regulations = []
        for er in self.enzymatic_reaction:
            for reg in er.regulation:
                if reg not in regulations:
                    regulations.append(reg)
        return regulations

    def is_regulated(self):
        return 0 if len(self.get_regulations()) == 0 else 1
            
    def regulated_by_cpd(self):
        for creg in self.get_regulations():
            for treg in creg.type:
                if treg == 'Regulation-of-Enzyme-Activity':
                    return 1
        return 0
    
    def regulated_by_tf(self):
        for creg in self.get_regulations():
            for treg in creg.type:
                if treg == 'Transcription-Factor-Binding':
                    return 1
        return 0
    
    def regulated_by_tf_cpd(self):
        for cer in self.enzymatic_reaction:
            for creg in cer.regulation:
                for treg in creg.type:
                    if treg == 'Allosteric-Regulation-of-RNAP':
                        return 1
        return 0
        
    def count_enzymes(self):
        return len(self.enzymatic_reaction)
                
    def get_ec_1(self):
        if len(self.EC_number) == 0:
            return math.nan
        ECt = self.EC_number[0].replace('EC-', '').split('.')
        EC1 = ECt[0]
        return EC1
        
class Complex:
    def __init__(self, id, name, components, regulates):
        self.id = id
        self.name = name
        self.components = components
        self.regulates = regulates
        


class TU:
    def __init__(self, name, components, promoter, regulated_by):
        self.name = name
        self.components = components
        self.promoter = promoter
        self.regulated_by = regulated_by
    
    def count_genes(self, hm_genes):
        count = 0
        for comp in self.components:
            if comp in hm_genes:
                count += 1
        return count
    

class Promoter:
    def __init__(self, id, name, factor, component_of, regulated_by):
        self.id = id
        self.name = name
        self.factor = factor
        self.regulated_by = regulated_by
        self.component_of = component_of

    

class Protein:
    def __init__(self, name, gene, type, promoter, components):
        self.name = name
        self.gene = gene
        self.type = type
        self.components = components
        self.promoter = promoter
    
    def update_promoter(self, hm_protein):
        for comp in self.components:
            if comp in hm_protein:
                for p in hm_protein[comp].promoter:
                    if p not in self.promoter:
                        self.promoter.append(p)
        

class Gene:
    def __init__(self, name, protein, component_of, promoter, regulated_by):
        self.name = name
        self.protein = protein
        self.component_of = component_of
        self.promoter = promoter
        self.regulated_by = regulated_by

def append_unique(array, item):
    if item not in array:
        array.append(item)
    return

def hm_append(hm, key, value):
    if key not in hm:
        hm[key] = []
    hm[key].append(value)

def load_file(path, unicode):
    lines = []
    with open(path, "r", encoding=unicode) as file:
        for line in file:
            lines.append(line.strip())
    return lines
    


def get_registries(path, unicode):
    current_text_list = []
    registries = []
    with open(path, "r", encoding=unicode) as file:
        for line in file:
            if line.startswith("#"):
                continue
            if line.startswith('//'):
                registries.append(current_text_list)
                current_text_list = []
            else:
                current_text_list.append(line.strip())
    return registries

def get_label(reg, label):
    res = []
    for line in reg:
        if line.startswith(label + ' '):
            res.append(line[len(label)+3:])
    return res


def get_promoters(reg_dir):
    promoter_path = reg_dir + "/promoters.dat"
    hm_promoter = {}
    for registry in get_registries(promoter_path, 'unicode_escape'):
        id = get_label(registry, 'UNIQUE-ID')[0]
        name = get_label(registry, 'COMMON-NAME')[0]
        factor = get_label(registry, 'BINDS-SIGMA-FACTOR')
        component_of = get_label(registry, 'COMPONENT-OF')
        regulated_by = get_label(registry, 'REGULATED-BY')
        current_promoter = Promoter(id, name, factor, component_of, regulated_by)
        hm_promoter[id] = current_promoter
    return hm_promoter


def get_pathways(reg_dir):
    regulation_path = reg_dir + "/pathways.dat"
    hm_pathway = {}
    hm_rn_pathway = {}
    for registry in get_registries(regulation_path, 'unicode_escape'):
        name = get_label(registry, 'UNIQUE-ID')[0]
        rns = get_label(registry, 'REACTION-LIST')
        for rn in rns:
            hm_rn_pathway[rn] = name
        superpathway = get_label(registry, 'SUPER-PATHWAYS')
        current_pathway = Pathway(name, rns, superpathway)
        hm_pathway[name] = current_pathway
    return hm_pathway, hm_rn_pathway




def get_regulation(reg_dir):
    regulation_path = reg_dir + "/regulation.dat"
    hm_regulation = {}
    for registry in get_registries(regulation_path, 'unicode_escape'):
        name = get_label(registry, 'UNIQUE-ID')[0]
        mode = get_label(registry, 'MODE')
        type = get_label(registry, 'TYPES')
        regulator = get_label(registry, 'REGULATOR')
        regulated_entity = get_label(registry, 'REGULATED-ENTITY')
        current_regulation = Regulation(name, mode, regulator, type, regulated_entity)
        hm_regulation[name] = current_regulation
    return hm_regulation


def get_complex(reg_dir):
    complex_path = reg_dir + "/protligandcplxes.dat"
    hm_complex = {}
    for registry in get_registries(complex_path, 'unicode_escape'):
        id = get_label(registry, 'UNIQUE-ID')[0]
        name = get_label(registry, 'COMMON-NAME')[0]
        components = get_label(registry, 'COMPONENTS')
        regulates = get_label(registry, 'REGULATES')
        current_complex = Complex(id, name, components, regulates)
        hm_complex[id] = current_complex
    return hm_complex

def get_compounds(reg_dir):
    compounds_path = reg_dir + "/compounds.dat"
    hm_types_cpd = {}
    hm_compound = {}
    for registry in get_registries(compounds_path, 'ISO-8859-1'):
        name = get_label(registry, 'UNIQUE-ID')[0]
        types = get_label(registry, 'TYPES')
        gibbs = get_label(registry, 'GIBBS-0')
        mw = get_label(registry, 'MOLECULAR-WEIGHT')
        smiles = get_label(registry, 'SMILES')
        smiles = '' if len(smiles) == 0 else smiles[0]
        current_compound = Compound(name, types, gibbs, mw, smiles)
        hm_compound[name] = current_compound
        for type in types:
            if type not in hm_types_cpd:
                hm_types_cpd[type] = []
            hm_types_cpd[type].append(name)
    return hm_types_cpd, hm_compound

def get_enzrxns(hm_regulation, hm_protein, hm_gene, hm_TU, reg_dir):
    enzrxns_path = reg_dir + "/enzrxns.dat"
    hm_enzrxns = {}
    for registry in get_registries(enzrxns_path, 'utf-8'):
        name = get_label(registry, 'UNIQUE-ID')[0]
        regulated_by = get_label(registry, 'REGULATED-BY')
        reaction = get_label(registry, 'REACTION')
        enzyme = get_label(registry, 'ENZYME')
        promoter = []
        regulation = []
        for enz in enzyme:
            if enz in hm_protein:
                for p in hm_protein[enz].promoter:
                    if p not in promoter:
                        promoter.append(p)
                for g in hm_protein[enz].gene:
                    if g in hm_gene:
                        for tu in hm_gene[g].component_of:
                            if tu in hm_TU:
                                for p in hm_TU[tu].promoter:
                                    if p not in promoter:
                                        promoter.append(p)
                        for reg in hm_gene[g].regulated_by:
                            if reg in hm_regulation:
                                if hm_regulation[reg] not in regulation:
                                    regulation.append(hm_regulation[reg])
                if 'Protein-Complexes' in hm_protein[enz].type:
                    for component in hm_protein[enz].components:
                        if component in hm_protein:
                            for g in hm_protein[component].gene:
                                if g in hm_gene:
                                    for tu in hm_gene[g].component_of:
                                        if tu in hm_TU:
                                            for p in hm_TU[tu].promoter:
                                                if p not in promoter:
                                                    promoter.append(p)
                                            for reg in hm_TU[tu].regulated_by:
                                                if reg in hm_regulation:
                                                    if hm_regulation[reg] not in regulation:
                                                        regulation.append(hm_regulation[reg])
                                    for reg in hm_gene[g].regulated_by:
                                        if reg in hm_regulation:
                                            if hm_regulation[reg] not in regulation:
                                                regulation.append(hm_regulation[reg])
        for p in promoter:
            for reg in hm_regulation.values():
                if p in reg.regulated_entity:
                    if reg not in regulation:
                        regulation.append(reg)  
        for cur_reg in regulated_by:
            if cur_reg not in regulation:
                regulation.append(hm_regulation[cur_reg])
        current_enzRxns = EnzRxns(name, regulated_by, regulation, reaction, enzyme, promoter)
        hm_enzrxns[name] = current_enzRxns
    return hm_enzrxns
    


def get_reactions(hm_enzrxns, hm_protein, hm_gene, hm_gene_tu, hm_TU, reg_dir):
    reaction_path = reg_dir + "/reactions.dat"
    hm_reaction = {}
    nodes = []
    att_reactions = {}
    metabolites = []
    cpd_transported = []
    for registry in get_registries(reaction_path, 'utf-8'):
        types = get_label(registry, 'TYPES')
        name = get_label(registry, 'UNIQUE-ID')[0]
        left = get_label(registry, 'LEFT')
        right = get_label(registry, 'RIGHT')
        direction = get_label(registry, 'REACTION-DIRECTION')
        lst_enzrxn = get_label(registry, 'ENZYMATIC-REACTION')
        spontaneus = False
        lst_spontaneus = get_label(registry, 'SPONTANEOUS?')
        if len(lst_spontaneus) == 1:
            spontaneus = lst_spontaneus[0] == 'T'
        operon = False
        enzymatic_reaction = []
        protein = []
        gene = []
        for enzrxn in lst_enzrxn:
            if enzrxn in hm_enzrxns:
                enzymatic_reaction.append(hm_enzrxns[enzrxn])
                for prot in hm_enzrxns[enzrxn].enzyme:
                    protein.append(prot)
                    for cgene in hm_protein[prot].gene:
                        gene.append(cgene)
                        if cgene in hm_gene_tu:
                            count_genes = hm_TU[hm_gene_tu[cgene]].count_genes(hm_gene)
                            if count_genes > 1:
                                operon = True
        gibbs = get_label(registry, 'GIBBS-0')
        EC_number = get_label(registry, 'EC-NUMBER')
        if len(get_label(registry, '^COMPARTMENT')) > 0:
            append_unique(types, 'Transport-Reactions')
        current_reaction = ReactionBC(name, left, right, direction, enzymatic_reaction, types, gibbs, EC_number, gene, protein, operon, spontaneus)
        #str(current_reaction)
        hm_reaction[name] = current_reaction
        #Se anotan los nodos que son reacciones
        att_reactions[current_reaction.name] = {'type': 'R'}
        # Se anotan los nodos que son metabolitos, metabolitos transportados y nodos
        append_unique(nodes, current_reaction.name)
        if current_reaction.direction == 'REVERSIBLE':
            append_unique(nodes, current_reaction.name + '_r')
        for current_left in current_reaction.left:
            append_unique(nodes, current_left)
            append_unique(metabolites, current_left)
            if 'Transport-Reactions' in current_reaction.types:
                append_unique(cpd_transported, current_left)
        for current_right in current_reaction.right:
            append_unique(nodes, current_right)
            append_unique(metabolites, current_right)
            if 'Transport-Reactions' in current_reaction.types:
                append_unique(cpd_transported, current_right)
    return hm_reaction, nodes, att_reactions, metabolites, cpd_transported


def get_TU(hm_promoter, reg_dir):
    TU_path = reg_dir + "/transunits.dat"
    hm_TU = {}
    for registry in get_registries(TU_path, 'ISO-8859-1'):    
        name = get_label(registry, 'UNIQUE-ID')[0]
        components = get_label(registry, 'COMPONENTS')
        regulated_by = get_label(registry, 'REGULATED-BY')
        promoter = []
        for c_comp in components:
            if c_comp in hm_promoter:
                promoter.append(c_comp)
        cur_TU = TU(name, components, promoter, regulated_by)
        hm_TU[name] = cur_TU
    return hm_TU



def get_protein(hm_gene, reg_dir):
    TU_path = reg_dir + "/proteins.dat"
    hm_protein = {}
    for registry in get_registries(TU_path, 'ISO-8859-1'):    
        name = get_label(registry, 'UNIQUE-ID')[0]
        gene = get_label(registry, 'GENE')
        type = get_label(registry, 'TYPES')
        components = get_label(registry, 'COMPONENTS')
        promoter = []
        for g in gene:
            if g in hm_gene:
                for p in hm_gene[g].promoter:
                    promoter.append(p)
        cur_protein = Protein(name, gene, type, promoter, components)
        hm_protein[name] = cur_protein
    return hm_protein



def get_gene(hm_promoter, hm_TU, reg_dir):
    TU_path = reg_dir + "/genes.dat"
    hm_gene = {}
    for registry in get_registries(TU_path, 'ISO-8859-1'):    
        name = get_label(registry, 'UNIQUE-ID')[0]
        gene = get_label(registry, 'PRODUCT')
        component_of = get_label(registry, 'COMPONENT-OF')
        regulated_by = get_label(registry, 'REGULATED-BY')
        promoter = []
        for c_o in component_of:
            if c_o in hm_TU:
                cTU = hm_TU[c_o]
                for comp in cTU.components:
                    if comp in hm_promoter:
                        promoter.append(comp)
        cur_gene = Gene(name, gene, component_of, promoter, regulated_by)
        hm_gene[name] = cur_gene
    return hm_gene


def get_hm_gene_tu(hm_TU, hm_gene):
    hm_gene_TU = {}
    for tu, value in hm_TU.items():
        for gene in value.components:
            if gene in hm_gene:
                hm_gene_TU[gene] = tu
    return hm_gene_TU


def get_bigg_biocyc_rn(model, bigg_rn_path):
    hm_bigg_biocyc_rn = {}
    lines = load_file(bigg_rn_path, 'ISO-8859-1')
    for line in lines:
        parts = line.split('\t')
        rn = parts[0]
        if rn not in model.reactions:
            continue
        db = parts[4]
        if db != '':
            db_parts = db.split('; ')
            for db_part in db_parts:
                if db_part.startswith('BioCyc: '):
                    if rn not in hm_bigg_biocyc_rn:
                        hm_bigg_biocyc_rn[rn] = []
                    append_unique(hm_bigg_biocyc_rn[rn], db_part[len('BioCyc: http://identifiers.org/biocyc/META:'):])
    for rn in model.reactions:
        if 'biocyc' in model.reactions.get_by_id(rn.id).annotation:
            links = model.reactions.get_by_id(rn.id).annotation['biocyc']
            if isinstance(links, str):
                links = [links]
            for link in links:
                if rn.id not in hm_bigg_biocyc_rn:
                    hm_bigg_biocyc_rn[rn.id] = []
                append_unique(hm_bigg_biocyc_rn[rn.id], link.split(':')[1])
    return hm_bigg_biocyc_rn


def get_bigg_biocyc_cpd(model, bigg_cpd_path):
    hm_bigg_biocyc_cpd = {}
    lines = load_file(bigg_cpd_path, 'ISO-8859-1')
    for line in lines:
        parts = line.split('\t')
        cpd = parts[0]
        db = ''
        if len(parts) > 4:
            db = parts[4]
        if db != '':
            db_parts = db.split('; ')
            for db_part in db_parts:
                if db_part.startswith('BioCyc: '):
                    if cpd not in hm_bigg_biocyc_cpd:
                        hm_bigg_biocyc_cpd[cpd] = []
                    append_unique(hm_bigg_biocyc_cpd[cpd], db_part[len('BioCyc: http://identifiers.org/biocyc/META:'):])
    for cpd in model.metabolites:
        if 'biocyc' in model.metabolites.get_by_id(cpd.id).annotation:
            links = model.metabolites.get_by_id(cpd.id).annotation['biocyc']
            if isinstance(links, str):
                links = [links]
            for link in links:
                if cpd.id not in hm_bigg_biocyc_cpd:
                    hm_bigg_biocyc_cpd[cpd.id] = []
                append_unique(hm_bigg_biocyc_cpd[cpd.id], link.split(':')[1])
    return hm_bigg_biocyc_cpd




def get_cpd_in_rn(hm_reaction):
    met_in_reactions = []
    for name, rn in hm_reaction.items():
        for cpd in rn.get_cpds():
            if cpd not in met_in_reactions:
                met_in_reactions.append(cpd)
    return met_in_reactions



def update_promoters(hm_protein):
    for prot in hm_protein.values():
        prot.update_promoter(hm_protein)


def update_regulation(hm_enzrxn, met_in_reactions):
    for name, er in hm_enzrxn.items():
        for reg in er.regulation:
            if 'Regulation-of-Enzyme-Activity' in reg.type:
                for regulator in reg.regulator:
                    if regulator not in met_in_reactions:
                        er.regulation.remove(reg)
                        