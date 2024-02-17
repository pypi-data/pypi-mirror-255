import os, re
from agent1c_metrics import read1c, settings
from pathlib import Path
from datetime import datetime, timedelta, time

def parse_1CV8Clst(cfg_file):
    cfgdata = {'cluster':[],'bases':[]}

    if not os.path.isfile(cfg_file):
        return cfgdata | {'message':f'File not exists: {cfg_file}'}
    
    try:
        data = read1c.lts(cfg_file)
    except read1c.ParseJSONException as e:
        return cfgdata | {'error':'Error when reading 1c file','file':cfg_file,'content':e.original_text}

    if data:

        cl_data = data[1]
    
        cluster_fields_list = ['id','name','port','host','p4','secure_connection','workers_restart_period','problem_workers_kill_after','unknown_8','unknown_9','unknown_10','cluster_managers','load_sharing_mode','unknown_13','force_kill_problem_workers','write_process_dump_due_to_memory_overload']
        cluster_fields = dict(map(lambda i: (i,lambda x: x),cluster_fields_list))
        # customization
        cluster_fields['host'] = lambda x: x.lower()

        cfgdata['cluster'] = {list(cluster_fields)[i] if i<len(cluster_fields) else f'p{i}':list(cluster_fields.values())[i](cl_data[i]) if i<len(cluster_fields) else cl_data[i] for i in range(len(cl_data))}

        ib_fields_list = ['id','name','discription','dbtype','dbserver','dbname','dbuser','dbpasshash','dbstr','unknown_p1','block','block_tasks','share_licence_by_server','unknown_p3','use_external_management','security_profile','security_profile_for_secure_mode','settings_version','reserving_workers']
        ib_block_fields = {
            'block_sessions':lambda x: bool(x),
            'block_start': lambda x: datetime.fromisoformat(str(x)[:4]+'-'+str(x)[4:6]+'-'+str(x)[6:8]+'T'+str(x)[8:10]+':'+str(x)[10:12]+':'+str(x)[12:]),
            'block_end': lambda x: datetime.fromisoformat(str(x)[:4]+'-'+str(x)[4:6]+'-'+str(x)[6:8]+'T'+str(x)[8:10]+':'+str(x)[10:12]+':'+str(x)[12:]),
            'block_message': lambda x: x,
            'block_unlock_code': lambda x: x,
            'block_param': lambda x: x,
        }
        ib_fields = dict(map(lambda i: (i,lambda x: x),ib_fields_list))
        # customization
        ib_fields['dbserver'] = lambda x: x.lower()
        ib_fields['block'] = lambda x: {list(ib_block_fields)[i] if i<len(ib_block_fields) else f'block_p{i}':list(ib_block_fields.values())[i](x[i]) if i<len(ib_block_fields) else x[i] for i in range(len(x))}

        for ibdata in data[2][1:]:
            ib = {list(ib_fields)[i] if i<len(ib_fields) else f'p{i}':list(ib_fields.values())[i](ibdata[i]) if i<len(ib_fields) else ibdata[i] for i in range(len(ibdata))}
            cfgdata['bases'].append(ib)

    return cfgdata

def parse_1cv8wsrv(lst_file):
    lst_data = {'clusters':[]}

    if not os.path.isfile(lst_file):
        return lst_data | {'message':f'File not exists: {lst_file}'}
    
    try:
        data = read1c.lts(lst_file)
    except read1c.ParseJSONException as e:
        return lst_data | {'error':'Error when reading 1c file','file':lst_file,'content':e.original_text}

    cluster_fields_list = ['id','name','port','host','p4','secure_connection','workers_restart_period','problem_workers_kill_after','unknown_8','unknown_9','unknown_10','cluster_managers','load_sharing_mode','unknown_13','force_kill_problem_workers','write_process_dump_due_to_memory_overload']
    cluster_fields = dict(map(lambda i: (i,lambda x: x),cluster_fields_list))
    # customization
    cluster_fields['host'] = lambda x: x.lower()

    for cl_data in data[0][1:]:
        lst_data['clusters'].append({list(cluster_fields)[i] if i<len(cluster_fields) else f'p{i}':list(cluster_fields.values())[i](cl_data[i]) if i<len(cluster_fields) else cl_data[i] for i in range(len(cl_data))}|{'length':len(cl_data)})
    
    return lst_data

def get_data():

    data = {'clusters':[]}

    for path1c in settings['folders']:
        
        filepath_1cv8wsrv = os.path.join(path1c,'1cv8wsrv.lst')
        filepath_srvribrg = os.path.join(path1c,'srvribrg.lst') # 8.1, 8.2 versions
        
        if os.path.isfile(filepath_srvribrg):
            cluster_info = parse_1cv8wsrv(filepath_srvribrg) # 8.1, 8.2
        else:
            cluster_info = parse_1cv8wsrv(filepath_1cv8wsrv)
        
        for cluster_item in cluster_info['clusters']:
            if (cluster_item['length'] == 8) or (cluster_item['length'] == 10):
                # version 8.1 OR version 8.2
                filepath_1CV8Reg = os.path.join(path1c,f"reg_{cluster_item['port']}",'1CV8Reg.lst')
                cluster_item['data'] = parse_1CV8Clst(filepath_1CV8Reg)
                cluster_item['cfgpath'] = filepath_1CV8Reg
                cluster_item['cfgver'] = '8.2'
            else:
                # version 8.3
                filepath_1CV8Clst = os.path.join(path1c,f"reg_{cluster_item['port']}",'1CV8Clst.lst')
                cluster_item['data'] = parse_1CV8Clst(filepath_1CV8Clst)
                cluster_item['cfgpath'] = filepath_1CV8Clst
                cluster_item['cfgver'] = '8.3'

            # add info of LOG size and type
            for ib in cluster_item['data']['bases']:
                ibpath = os.path.join(path1c,f"reg_{cluster_item['port']}",ib['id'],'1Cv8Log')

                # get log type
                ib['logtype'] = 'txt' if os.path.isfile(os.path.join(ibpath,'1Cv8.lgf')) else 'sqlite'
                
                # get size
                ib['logsize'] = 0
                ib['mtime'] = 0
                ib['logpath'] = ibpath
                if os.path.exists(ibpath):
                    for ele in os.scandir(ibpath):
                        #print('-',ele)
                        ib['logsize'] += os.path.getsize(ele)
                        ib['mtime'] = max(ib['mtime'],os.path.getmtime(ele))

                ib['mtime_iso'] = datetime.fromtimestamp(ib['mtime'])
                ib['mtime_lastday'] = ib['mtime_iso'] > datetime.today() - timedelta(days=1)
                ib['mtime_lastweek'] = ib['mtime_iso'] > datetime.today() - timedelta(days=7)
                ib['mtime_lastmonth'] = ib['mtime_iso'] > datetime.today() - timedelta(days=31)
                ib['inactivity'] = (datetime.now() - ib['mtime_iso']).days

        data['clusters'] += cluster_info['clusters']

    return data
