# -*- coding: utf-8 -*-
import re
import datetime as dt
from dateutil.relativedelta import relativedelta as rd
import pandas as pd
import numpy as np
from .api import quantim

class bi_data(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def get_positions_afps_cl(self, ref_date=None):
        '''
        Get Value at Risk results and suport information.
        '''
        ref_date = dt.datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0) - rd(days=1) if ref_date is None else dt.datetime.strptime(ref_date, '%Y-%m-%d') 
        key = f'inputs/benchmarks/positions/cl/afps/{ref_date.year}/{ref_date.strftime("%m")}/data.json'

        data = {'bucket':"condor-sura", 'key':key}
        try:
            resp = self.api_call('retrieve_json_s3', method="post", data=data, verify=False)
            keys = list(resp.keys())
            resp_dfs = {k:pd.DataFrame(resp[k]) for k in keys}
        except:
            print(f"Data not available for {ref_date}. Try previous month!")
            keys, resp_dfs = None, None
        return keys, resp_dfs

    def process_positions_afps_cl(self, ref_date=None):
        keys, resp_dfs = self.get_positions_afps_cl(ref_date=ref_date)

        asset_class_df = resp_dfs['CARTERA AGREGADA DE LOS FONDOS DE PENSIONES POR TIPO DE FONDO'].set_index('glosa')
        asset_class_df['index'] = [k.replace('tipofondo -', '').strip() for k in asset_class_df['index'].values]
        asset_class_df = asset_class_df.loc[np.in1d(asset_class_df['index'], ['A', 'B', 'C', 'D', 'E'])]

        consol_df = pd.DataFrame()
        acc_map = [{'id':'SUBTOTAL RENTA VARIABLE', 'label':'Renta Variable'},
                {'id':'SUBTOTAL RENTA FIJA', 'label':'Renta Fija'},
                {'id':'SUBTOTAL DERIVADOS', 'label':'Derivados'},
                {'id':'SUBTOTAL OTROS', 'label':'Otros'},
                    ]
        for x in acc_map:
            consol_df = pd.concat([consol_df, asset_class_df.loc[x['id']].set_index('index')[['porcentaje']].rename(columns={'porcentaje':x['label']}).T], axis=0)

        asset_class_df.loc[x['id']].set_index('index')[['porcentaje']].rename(columns={'porcentaje':x['label']}).T
        asset_class_df.loc[[k for k in  asset_class_df.index if re.search('^RENTA VARIABLE', k) is not None]]

        inv_nac_loc = np.where([k.startswith('INVERSIÓN NACIONAL TOTAL') for k in asset_class_df.index])[0][0]
        inv_inter_loc = np.where([k.startswith('INVERSIÓN EXTRANJERA TOTAL') for k in asset_class_df.index])[0][0]
        rv_loc = np.where([True if re.search('^RENTA VARIABLE', k) is not None else False for k in  asset_class_df.index])[0]
        rf_loc = np.where([True if re.search('^RENTA FIJA', k) is not None else False for k in  asset_class_df.index])[0]

        # RV and RF Local and Inter
        consol_df = pd.concat([consol_df, 
                            asset_class_df.iloc[rv_loc[(rv_loc>inv_nac_loc) & (rv_loc<inv_inter_loc)]].set_index('index')[['porcentaje']].rename(columns={'porcentaje':'Renta Variable Nacional'}).T, 
                            asset_class_df.iloc[rv_loc[(rv_loc>inv_inter_loc)]].set_index('index')[['porcentaje']].rename(columns={'porcentaje':'Renta Variable Internacional'}).T, 
                            asset_class_df.iloc[rf_loc[(rf_loc>inv_nac_loc) & (rf_loc<inv_inter_loc)]].set_index('index')[['porcentaje']].rename(columns={'porcentaje':'Renta Fija Nacional'}).T, 
                            asset_class_df.iloc[rf_loc[(rf_loc>inv_inter_loc)]].set_index('index')[['porcentaje']].rename(columns={'porcentaje':'Renta Fija Internacional'}).T
                            ], axis=0) 
        consol_df = consol_df.reset_index().rename(columns={'index':'Clase de Activo'})

        # Por emisor
        asset_detail_df = resp_dfs['CARTERA DE LOS FONDOS DE PENSIONES POR TIPO DE FONDO, INVERSIÓN EN EL EXTRANJERO POR EMISOR'].fillna({'nemo':''})
        asset_detail_df['index'] = [k.replace('tipofondo -', '').strip() for k in asset_detail_df['index'].values]
        asset_detail_df = asset_detail_df.loc[np.in1d(asset_detail_df['index'], ['A', 'B', 'C', 'D', 'E'])]
        asset_detail_df = asset_detail_df.groupby(['index', 'nemo', 'glosa']).sum().reset_index(level='index').pivot(columns='index', values='monto_dolares').reset_index()

        return consol_df, asset_detail_df 