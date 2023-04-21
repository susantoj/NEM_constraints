"""
Python functions for wrangling public NEMDE constraint equation formulations:
    - get_constraint_list (month, year, prefix)
    - find_constraint (constraint, start_date, end_date)
    - get_LHS_terms(constraint, month, year)
    - get_RHS_terms(constraint, month, year)
    - get_constraint_details (constraint, month, year)
    - find_generic_RHS_func (equation_id, start_date, end_date)
    - get_generic_RHS_func(equation_id, month, year)

Last updated: @JSusanto / Apr 2023
"""

import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta


def get_mms_table(month, year, table):
    """"Get a table from MMS at a specific month and year and return a DataFrame"""
    
    if month < 10:
        str_month = '0' + str(month)
    else:
        str_month = str(month)
    
    url_prefix = 'https://nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/' + str(year) + '/MMSDM_' + str(year) + '_' + str_month + '/MMSDM_Historical_Data_SQLLoader/DATA/PUBLIC_DVD_'
    url_suffix = '_' + str(year) + str_month + '010000.zip'
    
    return pd.read_csv(url_prefix + table + url_suffix, compression='zip', header=1)


def get_constraint_list(month, year, prefix = None):
    """Get list of constraints from a specific month/year and with an optional prefix
        Inputs: 
            month   specified integer month
            year    specified integer year
            prefix  optional string prefix, e.g. 'Q_', 'S_', etc 
            
        Returns: 
            df      a dataframe with list of constraints from GENCONDATA table
    """
    
    pd.set_option('display.max_rows', None)
    df = get_mms_table(month, year, 'GENCONDATA')
    df.drop(index=df.index[-1],axis=0,inplace=True)
    
    if prefix:
        df = df[df['GENCONID'].str.startswith(prefix)]
        
    print(df[['GENCONID','DESCRIPTION']])
    
    return df


def find_constraint(constraint, start_date = date(2009,7,1), end_date = None):
    """Find the last update of a specific constraint over an optional period of dates
        Inputs: 
            constraint      string of constraint to search for
            start_date      date object for date to start search (optional, default is July 2009)
            end_date        date object for date end search (optional, default is now)
            
        Returns: 
            df              a dataframe with the constraint description from GENCONDATA table
            found           True if constraint found, False otherwise
    """
    
    df = pd.DataFrame()
    
    if not end_date:
        end_date = date.today() - relativedelta(months=2)
    
    cur_date = end_date
        
    while df.empty and cur_date > start_date:
        print('Searching archive from ' + cur_date.strftime("%B %Y"))
        df = get_mms_table(cur_date.month, cur_date.year, 'GENCONDATA')
        df.drop(index=df.index[-1],axis=0,inplace=True)
        
        df = df[df['GENCONID'].str.startswith(constraint)]
        
        cur_date = cur_date - relativedelta(months=1)
    
    if df.empty:
        print('Constraint equation not found over period ' + start_date.strftime("%B %Y") + ' and ' + end_date.strftime("%B %Y"))
        found = False
    else:    
        df = df.drop(df.columns[[0, 2, 3]],axis = 1)
        print(df.iloc[0])
        found = True
    
    return df, found


def get_LHS_terms(constraint, month, year):
    """Get LHS terms for a constraint equation
        Inputs: 
            constraint  string of the specific constraint equation
            month       specified integer month
            year        specified integer year
            
        Returns: 
            df          a dataframe with the LHS terms of the constraint equation
                        (returns empty dataframe if constraint equation not found)
    """
    
    dict_LHS = {'type' : [], 'ID' : [], 'DUID' : [], 'factor' : [], 'bidtype' : []}
    
    # Connection points
    df = get_mms_table(month, year, 'SPDCONNECTIONPOINTCONSTRAINT')
    df.drop(index=df.index[-1],axis=0,inplace=True)   
    df = df[df['GENCONID'] == constraint]
    
    if not df.empty:
        df_lookup = get_mms_table(month, year, 'DUDETAIL')
        df_lookup.drop(index=df_lookup.index[-1],axis=0,inplace=True)
        
        for i in range(len(df)):
            df_DUID = df_lookup[df_lookup['CONNECTIONPOINTID'] == df['CONNECTIONPOINTID'].iloc[i]]['DUID']
            if df_DUID.empty:
                DUID = 'DUID not found'
            else:
                DUID = df_DUID.iloc[0]
            
            dict_LHS['type'].append('CONNECTIONPOINT')
            dict_LHS['ID'].append(df['CONNECTIONPOINTID'].iloc[i])
            dict_LHS['DUID'].append(DUID) 
            dict_LHS['factor'].append(df['FACTOR'].iloc[i])
            dict_LHS['bidtype'].append(df['BIDTYPE'].iloc[i])
    
    # Interconnectors
    df = get_mms_table(month, year, 'SPDINTERCONNECTORCONSTRAINT')
    df.drop(index=df.index[-1],axis=0,inplace=True)   
    df = df[df['GENCONID'] == constraint]
    
    if not df.empty:
        for i in range(len(df)):
            dict_LHS['type'].append('INTERCONNECTOR')
            dict_LHS['ID'].append(df['INTERCONNECTORID'].iloc[i])
            dict_LHS['DUID'].append(df['INTERCONNECTORID'].iloc[i])
            dict_LHS['factor'].append(df['FACTOR'].iloc[i])
            dict_LHS['bidtype'].append('N/A')
    
    # Regions
    df = get_mms_table(month, year, 'SPDREGIONCONSTRAINT')
    df.drop(index=df.index[-1],axis=0,inplace=True)   
    df = df[df['GENCONID'] == constraint]
    
    if not df.empty:
        for i in range(len(df)):
            dict_LHS['type'].append('REGION')
            dict_LHS['ID'].append(df['REGIONID'].iloc[i])
            dict_LHS['DUID'].append(df['REGIONID'].iloc[i])
            dict_LHS['factor'].append(df['FACTOR'].iloc[i])
            dict_LHS['bidtype'].append('N/A')
    
    return pd.DataFrame(dict_LHS)


def get_RHS_terms(constraint, month, year):
    """Get RHS terms for a constraint equation
        Inputs: 
            constraint  string of the specific constraint equation
            month       specified integer month
            year        specified integer year
            
        Returns: 
            df          a dataframe with the RHS terms of the constraint equation
                        (returns empty dataframe if constraint equation not found)
    """
    
    dict_RHS = {'term_ID' : [], 'ID' : [], 'type' : [], 'description' : [], 'factor' : [], 'operation' : []}
    
    df = get_mms_table(month, year, 'GENERICCONSTRAINTRHS')
    df.drop(index=df.index[-1],axis=0,inplace=True)
    
    df = df[df['GENCONID'] == constraint]
    
    if df.empty:
        print('Constraint equation not found...')
    else:
        # Lookup table for SCADA terms
        df_ems = get_mms_table(month, year, 'EMSMASTER')
        df_ems.drop(index=df_ems.index[-1],axis=0,inplace=True)
        
        for i in range(len(df)):
            spd_type = df['SPD_TYPE'].iloc[i]
            
            if spd_type in ['A', 'S', 'I', 'T', 'R']:
                # SCADA terms in EMSMASTER table
                df1 = df_ems[df_ems['SPD_ID'] == df['SPD_ID'].iloc[i]]['DESCRIPTION']
                if df1.empty:
                    desc = '-'
                else:
                    desc = df1.iloc[0]
                
            elif spd_type == 'X':
                # Generic function
                # Note that generic functions may be defined in previous month/years and need to be found separately
                desc = 'Generic RHS function'
                    
            else:
                desc = '-'
            
            str_op = str(df['OPERATION'].iloc[i])
            if str_op == 'nan':
                str_op = '-'
            
            dict_RHS['term_ID'].append(df['TERMID'].iloc[i])
            dict_RHS['ID'].append(df['SPD_ID'].iloc[i])
            dict_RHS['description'].append(desc)
            dict_RHS['factor'].append(df['FACTOR'].iloc[i])
            dict_RHS['operation'].append(str_op)
            dict_RHS['type'].append(spd_type)
        
    return pd.DataFrame(dict_RHS).sort_values(by='term_ID')
        

def get_constraint_details(constraint, month, year):
    """Get details of a specific constraint equation formulation
        Inputs: 
            constraint  string of the specific constraint equation
            month       specified integer month
            year        specified integer year
            
        Returns: 
            df          a dataframe with the constraint description from GENCONDATA table
            LHS         a dataframe with the LHS terms of the constraint equation
            RHS         a dataframe with the LHS terms of the constraint equation
            
                        (return empty dataframes if constraint equation not found)
    """
    
    df = get_mms_table(month, year, 'GENCONDATA')
    df.drop(index=df.index[-1],axis=0,inplace=True)
    
    df = df[df['GENCONID'] == constraint]

    if df.empty:
        print('Constraint equation not found...')
    else:    
        df = df.drop(df.columns[[0, 2, 3]],axis = 1)
    
    return df, get_LHS_terms(constraint, month, year), get_RHS_terms(constraint, month, year)


def find_generic_RHS_func(equation_id, start_date = date(2009,7,1), end_date = None):
    """Find the last update of a specific generic RHS function
        Inputs: 
            equation_id     string of generic function ID to search for
            start_date      date object for date to start search (optional, default is July 2009)
            end_date        date object for date end search (optional, default is now)
            
        Returns: 
            df              a dataframe with the generic function description
            found           True if constraint found, False otherwise
    """
    
    df = pd.DataFrame()
    
    if not end_date:
        end_date = date.today() - relativedelta(months=2)
    
    cur_date = end_date
        
    while df.empty and cur_date > start_date:
        print('Searching archive from ' + cur_date.strftime("%B %Y"))
        df = get_mms_table(cur_date.month, cur_date.year, 'GENERICEQUATIONDESC')
        df.drop(index=df.index[-1],axis=0,inplace=True)
        
        df = df[df['EQUATIONID'].str.startswith(equation_id)]
        
        cur_date = cur_date - relativedelta(months=1)
    
    if df.empty:
        print('Generic RHS function not found over period ' + start_date.strftime("%B %Y") + ' and ' + end_date.strftime("%B %Y"))
        found = False
    else:    
        df = df.drop(df.columns[[0, 2, 3]],axis = 1)
        print(df.iloc[0])
        found = True
    
    return df, found


def get_generic_RHS_func(equation_id, month, year):
    """Get terms for a generic RHS function
        Inputs: 
            equation_id     string of the specific generic function ID
            month           specified integer month
            year            specified integer year
            
        Returns: 
            df          a dataframe with the terms of the generic RHS function
                        (returns empty dataframe if constraint equation not found)
    """
        
    dict_RHS_func = {'term_ID' : [], 'ID' : [], 'type' : [], 'description' : [], 'factor' : [], 'operation' : []}
    
    df = get_mms_table(month, year, 'GENERICEQUATIONRHS')
    df.drop(index=df.index[-1],axis=0,inplace=True)
    
    df = df[df['EQUATIONID'] == equation_id]
    
    if df.empty:
        print('Generic RHS function not found...')
    else:
        # Lookup table for SCADA terms
        df_ems = get_mms_table(month, year, 'EMSMASTER')
        df_ems.drop(index=df_ems.index[-1],axis=0,inplace=True)
        
        for i in range(len(df)):
            spd_type = df['SPD_TYPE'].iloc[i]
            
            if spd_type in ['A', 'S', 'I', 'T', 'R']:
                # SCADA terms in EMSMASTER table
                df1 = df_ems[df_ems['SPD_ID'] == df['SPD_ID'].iloc[i]]['DESCRIPTION']
                if df1.empty:
                    desc = '-'
                else:
                    desc = df1.iloc[0]
            else:
                desc = '-'
            
            str_op = str(df['OPERATION'].iloc[i])
            if str_op == 'nan':
                str_op = '-'
            
            dict_RHS_func['term_ID'].append(df['TERMID'].iloc[i])
            dict_RHS_func['ID'].append(df['SPD_ID'].iloc[i])
            dict_RHS_func['description'].append(desc)
            dict_RHS_func['factor'].append(df['FACTOR'].iloc[i])
            dict_RHS_func['operation'].append(str_op)
            dict_RHS_func['type'].append(spd_type)
        
    return pd.DataFrame(dict_RHS_func).sort_values(by='term_ID')