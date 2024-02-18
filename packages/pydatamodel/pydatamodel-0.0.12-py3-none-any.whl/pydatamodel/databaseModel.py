
# -*- coding: utf-8 -*-
#===========数据库建模等相关功能============
#数据库建模等相关功能
#许冠明
#20221217
#=======================================
import pandas as pd
import datetime
import os
import sys

def ddl_mysql_t(mapping_xlsx='D:/xuguanming/oldFiles/数据库建模/generating_engine/mapping/3.source_mapping_ams.xlsx',
                code_model_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/models/itl/ddl',
                target_schema='itl',
                etl_dt='etl_dt',
                etl_timestamp='etl_timestamp',
                start_dt='start_dt',
                end_dt='end_dt',
                engine='InnoDB',
                default_charset='utf8mb4',
                collate='utf8mb4_unicode_ci',
                output_path='D:/xuguanming/oldFiles/数据库建模/generating_engine/code/itl/ddl'):
    #基于Mapping文件，自动生成T层DDL代码
    #layer #t:T层，o：O层
    #许冠明
    #20221113
    #基于Mapping文件，自动生成T层DDL代码
    #许冠明
    #20221113
    Error=0
    if not os.path.exists(mapping_xlsx):
        Error=1
        print('不存在文件：'+mapping_xlsx)
    else:
        try:
            table=pd.read_excel(mapping_xlsx,sheet_name='table')
            column=pd.read_excel(mapping_xlsx,sheet_name='column') 
            table=table.loc[table['IsEffective']==1,]
            table.index=range(table.shape[0])
        except:
            print('错误：mapping文件sheet名不正确，必须包含两个sheet，分别为table和column！')
            Error=1
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    code_create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if Error==0:
        n=table.shape[0]
        if n==0:
            print('错误：IsEffective 无取值1！')
        for i in range(n):
            #i=0 
            print('No.'+str(i+1)+' in '+str(n)+' Tables:'+target_schema+"."+table['TargetTable'][i])
            #读入模板
            tabletype=''
            if table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='st':#全量状态 有主健，拉链表               
                with open(code_model_path+'/itl_ddl_f_st.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-st'
            elif table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='ev':#全量流水                
                with open(code_model_path+'/itl_ddl_f_ev.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-ev'
            elif table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='sn':#全量快照                
                with open(code_model_path+'/itl_ddl_f_sn.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-sn'
            else:
                with open(code_model_path+'/itl_ddl_other.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='other'
            table_comment= '' if str(table.loc[i,'SourceTableComment'])=='nan' else str(table.loc[i,'SourceTableComment'])
            if pd.isna(table['SystemFlag'][i]):
                tmpColumn=column.loc[pd.isna(column['SystemFlag']) & (column['SourceTable']==table['SourceTable'][i]),:].copy()
            else:
                tmpColumn=column.loc[(column['SystemFlag']==table['SystemFlag'][i]) & (column['SourceTable']==table['SourceTable'][i]),:].copy()
            if(tmpColumn.shape[0]==0):
                print('错误：mapping文件的table和column关联不上，请确认SystemFlag或者SourceTable是否写错！')
                sys.exit(1)
            tmpColumn.index=range(tmpColumn.shape[0])
            
            #tmpColumn['ColumnSet']=None
            for j in range(tmpColumn.shape[0]):#j=1
                str1=tmpColumn.loc[j,'SourceTableColumn']
                str2=tmpColumn.loc[j,'SourceTableColumnType']
                str3='NOT NULL' if tmpColumn.loc[j,'IsNotNull']==1 else 'NULL'
                str4='' if str(tmpColumn.loc[j,'DefaultValue'])=='nan'  else str(tmpColumn.loc[j,'DefaultValue'])
                str5='COMMENT'
                str6="''" if str(tmpColumn.loc[j,'SourceTableColumnComment'])=='nan' else "'"+str(tmpColumn.loc[j,'SourceTableColumnComment']) +"'"
                tmpColumn.loc[j,'ColumnSet']=str1+' '+str2+' '+str3+' '+str4+' '+str5+' '+str6
            
            itl_table_name=table['TargetTable'][i]
            itl_schema=target_schema
            itl_column_name=list(tmpColumn['ColumnSet'])

            if tabletype=='f-st':
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                key_columns_list.append(etl_dt)
                key_columns= ','.join(key_columns_list)
                key_set=", PRIMARY KEY (%s)" % key_columns
            elif tabletype=='f-ev':
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                if len(key_columns_list)==0:#无主键
                    key_set=""
                else:
                    key_columns_list.append(etl_dt)
                    key_columns= ','.join(key_columns_list)
                    key_set=", PRIMARY KEY (%s)" % key_columns
            elif tabletype=='f-sn':
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                if len(key_columns_list)==0:#无主键
                    key_set=""
                else:
                    key_columns_list.append(etl_dt)
                    key_columns= ','.join(key_columns_list)
                    key_set=", PRIMARY KEY (%s)" % key_columns
            elif tabletype=='other':
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                if len(key_columns_list)==0:#无主键
                    key_set=""
                else:
                    key_columns_list.append(etl_dt)
                    key_columns= ','.join(key_columns_list)
                    key_set=", PRIMARY KEY (%s)" % key_columns
            
            
            index_columns_list=[etl_dt]
            index_columns_list_orgin=list(tmpColumn['SourceTableColumn'][tmpColumn['IsIndex']==1])
            index_columns_list.extend(index_columns_list_orgin)
            
            index_columns= ','.join(index_columns_list)
            
            code_model_temp=code_model.copy()
            
            for m in range(len(code_model_temp)):
                f1=code_model_temp[m].find('@')#是否包含此字符
                if f1>0:#如果包含
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{itl_column_name}'],keyvalue= [itl_column_name])

            sqlcode=''.join(code_model_temp)       
            sqlcode=sqlcode.replace("${itl_table_name}",itl_table_name)     
            sqlcode=sqlcode.replace("${itl_schema}",itl_schema)  
            sqlcode=sqlcode.replace("${key_set}",key_set) 
            sqlcode=sqlcode.replace("${index_columns}",index_columns) 
            sqlcode=sqlcode.replace("${table_comment}",table_comment) 
            sqlcode=sqlcode.replace("${code_create_time}",code_create_time) 
            sqlcode=sqlcode.replace("${etl_dt}",etl_dt) 
            sqlcode=sqlcode.replace("${etl_timestamp}",etl_timestamp) 
            
            f = open( output_path+'/ddl_'+itl_schema+'_'+itl_table_name+".sql",'w',encoding='utf-8')
            f.write(sqlcode)
            f.close()
            print('Done!')




def ddl_mysql_o(mapping_xlsx='D:/xuguanming/oldFiles/数据库建模/generating_engine/mapping/3.source_mapping_ams.xlsx',
                code_model_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/models/iol/ddl',
                target_schema='iol',
                etl_dt='etl_dt',
                etl_timestamp='etl_timestamp',
                start_dt='start_dt',
                end_dt='end_dt',
                engine='InnoDB',
                default_charset='utf8mb4',
                collate='utf8mb4_unicode_ci',
                output_path='D:/xuguanming/oldFiles/数据库建模/generating_engine/code/iol/ddl'):
    #基于Mapping文件，自动生成o层DDL代码
    #layer #t:T层，o：O层
    #许冠明
    #20221113
    Error=0
    if not os.path.exists(mapping_xlsx):
        Error=1
        print('不存在文件：'+mapping_xlsx)
    else:
        try:
            table=pd.read_excel(mapping_xlsx,sheet_name='table')
            column=pd.read_excel(mapping_xlsx,sheet_name='column')     
            table=table.loc[table['IsEffective']==1,]
            table.index=range(table.shape[0])
        except:
            print('错误：mapping文件sheet名不正确，必须包含两个sheet，分别为table和column！')
            Error=1
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    code_create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    

    if Error==0:
        n=table.shape[0]
        for i in range(n):
            #i=0   
            print('No.'+str(i+1)+' in '+str(n)+' Tables:'+target_schema+"."+table['TargetTable'][i])
            #读入模板
            tabletype=''
            if table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='st':#全量状态 有主健，拉链表               
                with open(code_model_path+'/iol_ddl_f_st.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-st'
            elif table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='ev':#全量流水 -有主键               
                with open(code_model_path+'/iol_ddl_f_ev.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-ev'
            elif table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='sn':#全量快照 -不考虑主键               
                with open(code_model_path+'/iol_ddl_f_sn.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-sn'
            else:
                with open(code_model_path+'/iol_ddl_other.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='other'
            table_comment= '' if str(table.loc[i,'SourceTableComment'])=='nan' else str(table.loc[i,'SourceTableComment'])
            if pd.isna(table['SystemFlag'][i]):
                tmpColumn=column.loc[pd.isna(column['SystemFlag']) & (column['SourceTable']==table['SourceTable'][i]),:].copy()
            else:
                tmpColumn=column.loc[(column['SystemFlag']==table['SystemFlag'][i]) & (column['SourceTable']==table['SourceTable'][i]),:].copy()
            if(tmpColumn.shape[0]==0):
                print('错误：mapping文件的table和column关联不上，请确认SystemFlag或者SourceTable是否写错！')
                sys.exit(1)
            tmpColumn.index=range(tmpColumn.shape[0])
            
            #tmpColumn['ColumnSet']=None
            for j in range(tmpColumn.shape[0]):#j=1
                str1=tmpColumn.loc[j,'SourceTableColumn']
                str2=tmpColumn.loc[j,'SourceTableColumnType']
                str3='NOT NULL' if tmpColumn.loc[j,'IsNotNull']==1 else 'NULL'
                str4='' if str(tmpColumn.loc[j,'DefaultValue'])=='nan'  else str(tmpColumn.loc[j,'DefaultValue'])
                str5='COMMENT'
                str6="''" if str(tmpColumn.loc[j,'SourceTableColumnComment'])=='nan' else "'"+str(tmpColumn.loc[j,'SourceTableColumnComment']) +"'"
                tmpColumn.loc[j,'ColumnSet']=str1+' '+str2+' '+str3+' '+str4+' '+str5+' '+str6
            
            iol_table_name=table['TargetTable'][i]
            iol_schema=target_schema
            iol_column_name=list(tmpColumn['ColumnSet'])
            if tabletype=='f-st': 
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                key_columns_list.append(start_dt)
                key_columns= ','.join(key_columns_list)
                key_set=", PRIMARY KEY (%s)" % key_columns
                
                index_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsIndex']==1])
                index_columns_list.append(start_dt)
                index_columns_list.append(end_dt)
                index_columns= ','.join(index_columns_list)
            elif tabletype=='f-ev':#流水表                 
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                if len(key_columns_list)==0:#无主键
                    key_set=""
                else:
                    key_columns_list.append(etl_dt)
                    key_columns= ','.join(key_columns_list)
                    key_set=", PRIMARY KEY (%s)" % key_columns
                
                index_columns_list=[etl_dt]
                index_columns_list_orgin=list(tmpColumn['SourceTableColumn'][tmpColumn['IsIndex']==1])
                index_columns_list.extend(index_columns_list_orgin)
                index_columns= ','.join(index_columns_list)
            elif tabletype=='f-sn':#快照 
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                if len(key_columns_list)==0:#无主键
                    key_set=""
                else:
                    key_columns_list.append(etl_dt)
                    key_columns= ','.join(key_columns_list)
                    key_set=", PRIMARY KEY (%s)" % key_columns
                
                index_columns_list=[etl_dt]
                index_columns_list_orgin=list(tmpColumn['SourceTableColumn'][tmpColumn['IsIndex']==1])
                index_columns_list.extend(index_columns_list_orgin)
                index_columns= ','.join(index_columns_list)
            elif tabletype=='other':#其他 
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                if len(key_columns_list)==0:#无主键
                    key_set=""
                else:
                    key_columns_list.append(etl_dt)
                    key_columns= ','.join(key_columns_list)
                    key_set=", PRIMARY KEY (%s)" % key_columns
                
                index_columns_list=[etl_dt]
                index_columns_list_orgin=list(tmpColumn['SourceTableColumn'][tmpColumn['IsIndex']==1])
                index_columns_list.extend(index_columns_list_orgin)
                index_columns= ','.join(index_columns_list)
            code_model_temp=code_model.copy()
            
            for m in range(len(code_model_temp)):
                f1=code_model_temp[m].find('@')#是否包含此字符
                if f1>0:#如果包含
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{iol_column_name}'],keyvalue= [iol_column_name])

            sqlcode=''.join(code_model_temp)       
            sqlcode=sqlcode.replace("${iol_table_name}",iol_table_name)     
            sqlcode=sqlcode.replace("${iol_schema}",iol_schema) 
            sqlcode=sqlcode.replace("${key_set}",key_set) 
            sqlcode=sqlcode.replace("${index_columns}",index_columns) 
            sqlcode=sqlcode.replace("${table_comment}",table_comment) 
            sqlcode=sqlcode.replace("${code_create_time}",code_create_time) 
            sqlcode=sqlcode.replace("${start_dt}",start_dt) 
            sqlcode=sqlcode.replace("${end_dt}",end_dt) 
            sqlcode=sqlcode.replace("${etl_dt}",etl_dt) 
            sqlcode=sqlcode.replace("${etl_timestamp}",etl_timestamp) 
            
            f = open( output_path+'/ddl_'+iol_schema+'_'+iol_table_name+".sql",'w',encoding='utf-8')
            f.write(sqlcode)
            f.close()
            print('Done!')





def ddl_mysql_m(mapping_xlsx='D:/xuguanming/oldFiles/数据库建模/generating_engine/mapping/4.iml_mapping_粤财资产数据中心.xlsx',
                code_model_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/models/iml/ddl',
                target_schema='iml',
                etl_dt='etl_dt',
                etl_timestamp='etl_timestamp',
                start_dt='start_dt',
                end_dt='end_dt',
                engine='InnoDB',
                default_charset='utf8mb4',
                collate='utf8mb4_unicode_ci',
                output_path='D:/xuguanming/oldFiles/数据库建模/generating_engine/code/iml/ddl'):
    #基于Mapping文件，自动生成o层DDL代码
    #layer #t:T层，o：O层
    #许冠明
    #20221113
    Error=0
    if not os.path.exists(mapping_xlsx):
        Error=1
        print('不存在文件：'+mapping_xlsx)
    else:
        try:
            table=pd.read_excel(mapping_xlsx,sheet_name='table')
            column=pd.read_excel(mapping_xlsx,sheet_name='column') 
            column_c=column['SourceTableColumn']
            del_sp_col=(column_c != 'etl_dt') \
            & (column_c != 'etl_timestamp') \
            & (column_c != 'etl_timestamp') \
            & (column_c != 'start_dt' )\
            & (column_c != 'end_dt')
            column=column.loc[del_sp_col,]
            column.index=range(column.shape[0])
            table=table.loc[table['IsEffective']==1,]
            table.index=range(table.shape[0])
        except:
            print('错误：mapping文件sheet名不正确，必须包含两个sheet，分别为table和column！')
            Error=1
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    code_create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    

    if Error==0:
        n=table.shape[0]
        for i in range(n):
            #i=0   
            print('No.'+str(i+1)+' in '+str(n)+' Tables:'+target_schema+"."+table['SourceTable'][i])
            #读入模板
            tabletype=''
            if table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='st':#全量状态 有主健，拉链表               
                with open(code_model_path+'/iml_ddl_f_st.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-st'
            elif table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='ev':#全量流水 -有主键               
                with open(code_model_path+'/iml_ddl_f_ev.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-ev'
            elif table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='sn':#全量快照 -不考虑主键               
                with open(code_model_path+'/iml_ddl_f_sn.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-sn'
            else:
                with open(code_model_path+'/iml_ddl_other.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='other'
            table_comment= '' if str(table.loc[i,'SourceTableComment'])=='nan' else str(table.loc[i,'SourceTableComment'])
            if pd.isna(table['SystemFlag'][i]):
                tmpColumn=column.loc[pd.isna(column['SystemFlag']) & (column['SourceTable']==table['SourceTable'][i]),:].copy()
            else:
                tmpColumn=column.loc[(column['SystemFlag']==table['SystemFlag'][i]) & (column['SourceTable']==table['SourceTable'][i]),:].copy()
            if(tmpColumn.shape[0]==0):
                print('错误：mapping文件的table和column关联不上，请确认SystemFlag或者SourceTable是否写错！')
                sys.exit(1)
            tmpColumn.index=range(tmpColumn.shape[0])
            
            #tmpColumn['ColumnSet']=None
            for j in range(tmpColumn.shape[0]):#j=1
                str1=tmpColumn.loc[j,'SourceTableColumn']
                str2=tmpColumn.loc[j,'SourceTableColumnType']
                str3='NOT NULL' if tmpColumn.loc[j,'IsNotNull']==1 else 'NULL'
                str4='' if str(tmpColumn.loc[j,'DefaultValue'])=='nan'  else str(tmpColumn.loc[j,'DefaultValue'])
                str5='COMMENT'
                str6="''" if str(tmpColumn.loc[j,'SourceTableColumnComment'])=='nan' else "'"+str(tmpColumn.loc[j,'SourceTableColumnComment']) +"'"
                tmpColumn.loc[j,'ColumnSet']=str1+' '+str2+' '+str3+' '+str4+' '+str5+' '+str6
            
            iml_table_name=table['SourceTable'][i]
            iml_schema=target_schema
            iml_column_name=list(tmpColumn['ColumnSet'])
            if tabletype=='f-st': 
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                key_columns_list.append(start_dt)
                key_columns= ','.join(key_columns_list)
                key_set=", PRIMARY KEY (%s)" % key_columns
                
                index_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsIndex']==1])
                index_columns_list.append(start_dt)
                index_columns_list.append(end_dt)
                index_columns= ','.join(index_columns_list)
            elif tabletype=='f-ev':#流水表                 
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                if len(key_columns_list)==0:#无主键
                    key_set=""
                else:
                    key_columns_list.append(etl_dt)
                    key_columns= ','.join(key_columns_list)
                    key_set=", PRIMARY KEY (%s)" % key_columns
                
                index_columns_list=[etl_dt]
                index_columns_list_orgin=list(tmpColumn['SourceTableColumn'][tmpColumn['IsIndex']==1])
                index_columns_list.extend(index_columns_list_orgin)
                index_columns= ','.join(index_columns_list)
            elif tabletype=='f-sn':#快照 
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                if len(key_columns_list)==0:#无主键
                    key_set=""
                else:
                    key_columns_list.append(etl_dt)
                    key_columns= ','.join(key_columns_list)
                    key_set=", PRIMARY KEY (%s)" % key_columns
                
                index_columns_list=[etl_dt]
                index_columns_list_orgin=list(tmpColumn['SourceTableColumn'][tmpColumn['IsIndex']==1])
                index_columns_list.extend(index_columns_list_orgin)
                index_columns= ','.join(index_columns_list)
            elif tabletype=='other':#其他 
                key_columns_list=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
                if len(key_columns_list)==0:#无主键
                    key_set=""
                else:
                    key_columns_list.append(etl_dt)
                    key_columns= ','.join(key_columns_list)
                    key_set=", PRIMARY KEY (%s)" % key_columns
                
                index_columns_list=[etl_dt]
                index_columns_list_orgin=list(tmpColumn['SourceTableColumn'][tmpColumn['IsIndex']==1])
                index_columns_list.extend(index_columns_list_orgin)
                index_columns= ','.join(index_columns_list)
            code_model_temp=code_model.copy()
            
            for m in range(len(code_model_temp)):
                f1=code_model_temp[m].find('@')#是否包含此字符
                if f1>0:#如果包含
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{iml_column_name}'],keyvalue= [iml_column_name])

            sqlcode=''.join(code_model_temp)       
            sqlcode=sqlcode.replace("${iml_table_name}",iml_table_name)     
            sqlcode=sqlcode.replace("${iml_schema}",iml_schema) 
            sqlcode=sqlcode.replace("${key_set}",key_set) 
            sqlcode=sqlcode.replace("${index_columns}",index_columns) 
            sqlcode=sqlcode.replace("${table_comment}",table_comment) 
            sqlcode=sqlcode.replace("${code_create_time}",code_create_time) 
            sqlcode=sqlcode.replace("${start_dt}",start_dt) 
            sqlcode=sqlcode.replace("${end_dt}",end_dt) 
            sqlcode=sqlcode.replace("${etl_dt}",etl_dt) 
            sqlcode=sqlcode.replace("${etl_timestamp}",etl_timestamp) 
            
            f = open( output_path+'/ddl_'+iml_schema+'_'+iml_table_name+".sql",'w',encoding='utf-8')
            f.write(sqlcode)
            f.close()
            print('Done!')





def linetext_replace(linetext='and ||| @{iol_o_pk}dd@{iol_t_pk}'
                     ,specialchar='|||'
                     ,keychar=['@{iol_o_pk}','@{iol_t_pk}']
                     ,keyvalue=[['ID','ID1'],['ID2','ID3']]
                     ):
    '''
    #author：许冠明
    #createtime:20221115
    #同一行，批量重复替换某字符
    #linetext：该行字符
    #specialchar：需要批量重复替换的标识字符
    #keychar：需被替换的字符串
    #keyvalue：目标字符串，list格式
    '''
    f1=linetext.find(specialchar)#是否包含此字符
    f2=0
    for i in range(len(keychar)):
        if linetext.find(keychar[i])>=0:
            f2=f2+1#是否包含此字符

    if f1>=0 and f2==len(keychar):#如果keychar有多个，那么必须要都包含才能执行替换。
        sep = '\n'+linetext[0:f1].rstrip()+' '
        str0= linetext[(f1+len(specialchar)):].strip()

        str2=''
        str3=''
        for m in range(len(keyvalue[0])):
            #print(m)
            str2= str2+ (''.rjust(f1) if m==0 else sep)
            str3= str0
            #print(str2)
            for n in range(len(keychar)):#n=1
                str3= str3.replace(keychar[n],keyvalue[n][m])
                #print(str3)
            str2=str2+str3
            #print(str2)
        str2=str2+'\n'
    else:
        str2=linetext
    return str2



def dml_mysql_t(
                mapping_xlsx='D:/xuguanming/oldFiles/数据库建模/generating_engine/mapping/3.source_mapping_ams.xlsx',
                code_model_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/models/itl/dml',
                 source_schema='ext',
                target_schema='itl',#itl层的schema
                etl_dt='etl_dt',
                etl_timestamp='etl_timestamp',
                output_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/code/itl/dml'
                ):
    #基于Mapping文件，自动生成T层DDL代码
    #许冠明
    #20221113
    Error=0
    if not os.path.exists(mapping_xlsx):
        Error=1
        print('不存在文件：'+mapping_xlsx)
    else:
        try:
            table=pd.read_excel(mapping_xlsx,sheet_name='table')
            column=pd.read_excel(mapping_xlsx,sheet_name='column')  
            table=table.loc[table['IsEffective']==1,]
            table.index=range(table.shape[0])
        except:
            print('错误：mapping文件sheet名不正确，必须包含两个sheet，分别为table和column！')
            Error=1
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    #读入模板
    with open(code_model_path+'/itl_dml.sql', "r",encoding='UTF-8') as f:
        code_model = f.readlines()# 
    f.close()

    if Error==0:
        n=table.shape[0]
        for i in range(n):
            #i=0   
            if pd.isna(table['SystemFlag'][i]):
                tmpColumn=column.loc[pd.isna(column['SystemFlag']) & (column['SourceTable']==table['SourceTable'][i]),:]
            else:
                tmpColumn=column.loc[(column['SystemFlag']==table['SystemFlag'][i]) & (column['SourceTable']==table['SourceTable'][i]),:]
            if(tmpColumn.shape[0]==0):
                print('错误：mapping文件的table和column关联不上，请确认SystemFlag或者SourceTable是否写错！')
                sys.exit(1)
            print('No.'+str(i+1)+' in '+str(n)+' Tables:'+target_schema+"."+table['TargetTable'][i])
  
            tmpColumn.index=range(tmpColumn.shape[0])
            itl_table_name=table['TargetTable'][i]
            itl_schema=target_schema
            itl_column_name=list(tmpColumn['SourceTableColumn'])
            ext_schema=source_schema
            ext_table_name=itl_table_name
            code_model_temp=code_model.copy()
            
            for m in range(len(code_model_temp)):
                f1=code_model_temp[m].find('@')#是否包含此字符
                if f1>0:#如果包含
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{itl_column_name}'],keyvalue= [itl_column_name])

            sqlcode=''.join(code_model_temp)       
            sqlcode=sqlcode.replace("${itl_table_name}",itl_table_name)     
            sqlcode=sqlcode.replace("${itl_schema}",itl_schema)  
            sqlcode=sqlcode.replace("${ext_schema}",ext_schema)  
            sqlcode=sqlcode.replace("${ext_table_name}",ext_table_name)  
            
            f = open( output_path+'/p_itl_'+itl_table_name+".sql",'w',encoding='utf-8')
            f.write(sqlcode)
            f.close()
            print('Done!')
'''            
dml_mysql_t(
                mapping_xlsx='D:/xuguanming/oldFiles/数据库建模/generating_engine/mapping/3.source_mapping_ams.xlsx',
                code_model_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/models/itl/dml',
                 source_schema='ext',
                target_schema='itl',#itl层的schema
                etl_dt='etl_dt',
                etl_timestamp='etl_timestamp',
                output_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/code/itl/dml'
                )
'''


def dml_mysql_o(
                mapping_xlsx='D:/xuguanming/oldFiles/数据库建模/generating_engine/mapping/3.source_mapping_ams.xlsx',
                code_model_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/models/iol/dml',
                source_schema='itl',
                target_schema='iol',#itl层的schema
                etl_dt='etl_dt',
                etl_timestamp='etl_timestamp',
                start_dt='start_dt',
                end_dt='end_dt',
                zipper_column='zipper_column',
                output_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/code/iol/dml'
                ):
    #基于Mapping文件，自动生成T层DDL代码
    #许冠明
    #20221113
    Error=0
    if not os.path.exists(mapping_xlsx):
        Error=1
        print('不存在文件：'+mapping_xlsx)
    else:
        try:
            table=pd.read_excel(mapping_xlsx,sheet_name='table')
            column=pd.read_excel(mapping_xlsx,sheet_name='column')     
            table=table.loc[table['IsEffective']==1,]
            table.index=range(table.shape[0])
        except:
            print('错误：mapping文件sheet名不正确，必须包含两个sheet，分别为table和column！')
            Error=1
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    code_create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    if Error==0:
        n=table.shape[0]
        for i in range(n):
            #i=0  
            print('No.'+str(i+1)+' in '+str(n)+' Tables:'+target_schema+"."+table['TargetTable'][i])
            #读入模板
            tabletype=''
            if table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='st':#全量状态 有主健，拉链表               
                with open(code_model_path+'/iol_dml_f_st.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-st'
            elif table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='ev':#全量流水 -有主键               
                with open(code_model_path+'/iol_dml_f_ev.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-ev'
            elif table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='sn':#全量快照 -不考虑主键               
                with open(code_model_path+'/iol_dml_f_sn.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-sn'
            
            if pd.isna(table['SystemFlag'][i]):
                tmpColumn=column.loc[pd.isna(column['SystemFlag']) & (column['SourceTable']==table['SourceTable'][i]),:].copy()
            else:
                tmpColumn=column.loc[(column['SystemFlag']==table['SystemFlag'][i]) & (column['SourceTable']==table['SourceTable'][i]),:].copy()
            
            
            if pd.isna(table['SystemFlag'][i]):
                tmpColumn=column.loc[pd.isna(column['SystemFlag']) & (column['SourceTable']==table['SourceTable'][i]),:]
            else:
                tmpColumn=column.loc[(column['SystemFlag']==table['SystemFlag'][i]) & (column['SourceTable']==table['SourceTable'][i]),:]
            if(tmpColumn.shape[0]==0):
                print('错误：mapping文件的table和column关联不上，请确认SystemFlag或者SourceTable是否写错！')
                sys.exit(1)
  
            tmpColumn.index=range(tmpColumn.shape[0])
            iol_table_name=table['TargetTable'][i]
            iol_schema=target_schema
            iol_column_name=list(tmpColumn['SourceTableColumn'])
            itl_column_name=iol_column_name
            itl_schema=source_schema
            itl_table_name=iol_table_name
            iol_is_pk=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
            iol_not_pk=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']!=1])
            iol_zipper_column_name=list(tmpColumn['SourceTableColumn'][tmpColumn['IsZipper']==1])
            
            code_model_temp=code_model.copy()
            
            for m in range(len(code_model_temp)):
                f1=code_model_temp[m].find('@')#是否包含此字符
                if f1>0:#如果包含
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{itl_column_name}','@{iol_column_name}'],keyvalue= [itl_column_name,iol_column_name])
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{iol_column_name}'],keyvalue= [iol_column_name])
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{itl_column_name}'],keyvalue= [itl_column_name])
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{iol_is_pk}'],keyvalue= [iol_is_pk])
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{iol_not_pk}'],keyvalue= [iol_not_pk])
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{iol_zipper_column_name}'],keyvalue= [iol_zipper_column_name])

            sqlcode=''.join(code_model_temp)       
            sqlcode=sqlcode.replace("${iol_table_name}",iol_table_name)     
            sqlcode=sqlcode.replace("${iol_schema}",iol_schema)  
            sqlcode=sqlcode.replace("${itl_schema}",itl_schema)  
            sqlcode=sqlcode.replace("${itl_table_name}",itl_table_name)  
            sqlcode=sqlcode.replace("${start_dt}",start_dt) 
            sqlcode=sqlcode.replace("${end_dt}",end_dt) 
            sqlcode=sqlcode.replace("${etl_dt}",etl_dt) 
            sqlcode=sqlcode.replace("${etl_timestamp}",etl_timestamp) 
            sqlcode=sqlcode.replace("${zipper_column}",zipper_column) 
            sqlcode=sqlcode.replace("${code_create_time}",code_create_time) 

            f = open( output_path+'/p_iol_'+iol_table_name+".sql",'w',encoding='utf-8')
            f.write(sqlcode)
            f.close()
            print('Done!')
'''            
dml_mysql_o(
                mapping_xlsx='D:/xuguanming/oldFiles/数据库建模/generating_engine/mapping/3.source_mapping_ams.xlsx',
                code_model_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/models/iol/dml',
                source_schema='itl',
                target_schema='iol',#itl层的schema
                etl_dt='etl_dt',
                etl_timestamp='etl_timestamp',
                start_dt='start_dt',
                end_dt='end_dt',
                zipper_column='zipper_column',
                output_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/code/iol/dml'
    )
'''



def dml_mysql_m(
                mapping_xlsx='D:/xuguanming/oldFiles/数据库建模/generating_engine/mapping/4.iml_mapping_粤财资产数据中心.xlsx',
                code_model_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/models/iml/dml',
                source_schema='iml',
                target_schema='iml',#itl层的schema
                etl_dt='etl_dt',
                etl_timestamp='etl_timestamp',
                start_dt='start_dt',
                end_dt='end_dt',
                zipper_column='zipper_column',
                output_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/code/iml/dml'
                ):
    #基于Mapping文件，自动生成M层DML代码
    #许冠明
    #20221113
    Error=0
    if not os.path.exists(mapping_xlsx):
        Error=1
        print('不存在文件：'+mapping_xlsx)
    else:
        try:
            table=pd.read_excel(mapping_xlsx,sheet_name='table')
            column=pd.read_excel(mapping_xlsx,sheet_name='column')  
            column_c=column['SourceTableColumn']
            del_sp_col=(column_c != 'etl_dt') \
            & (column_c != 'etl_timestamp') \
            & (column_c != 'etl_timestamp') \
            & (column_c != 'start_dt' )\
            & (column_c != 'end_dt')
            column=column.loc[del_sp_col,]
            column.index=range(column.shape[0])
            table=table.loc[table['IsEffective']==1,]
            table.index=range(table.shape[0])
        except:
            print('错误：mapping文件sheet名不正确，必须包含两个sheet，分别为table和column！')
            Error=1
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    code_create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    if Error==0:
        n=table.shape[0]
        for i in range(n):
            #i=0  
            print('No.'+str(i+1)+' in '+str(n)+' Tables:'+target_schema+"."+table['SourceTable'][i])
            #读入模板
            tabletype=''
            if table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='st':#全量状态 有主健，拉链表               
                with open(code_model_path+'/iml_dml_f_st.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-st'
            elif table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='ev':#全量流水 -有主键               
                with open(code_model_path+'/iml_dml_f_ev.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-ev'
            elif table.loc[i,'IncrementOrFull']=='f' and  table.loc[i,'SourceTableType']=='sn':#全量快照 -不考虑主键               
                with open(code_model_path+'/iml_dml_f_sn.sql', "r",encoding='UTF-8') as f:
                    code_model = f.readlines()# 
                f.close()
                tabletype='f-sn'
            
            if pd.isna(table['SystemFlag'][i]):
                tmpColumn=column.loc[pd.isna(column['SystemFlag']) & (column['SourceTable']==table['SourceTable'][i]),:].copy()
            else:
                tmpColumn=column.loc[(column['SystemFlag']==table['SystemFlag'][i]) & (column['SourceTable']==table['SourceTable'][i]),:].copy()
            
            
            if pd.isna(table['SystemFlag'][i]):
                tmpColumn=column.loc[pd.isna(column['SystemFlag']) & (column['SourceTable']==table['SourceTable'][i]),:]
            else:
                tmpColumn=column.loc[(column['SystemFlag']==table['SystemFlag'][i]) & (column['SourceTable']==table['SourceTable'][i]),:]
            if(tmpColumn.shape[0]==0):
                print('错误：mapping文件的table和column关联不上，请确认SystemFlag或者SourceTable是否写错！')
                sys.exit(1)
  
            tmpColumn.index=range(tmpColumn.shape[0])
            iml_table_name=table['SourceTable'][i]
            iml_schema=target_schema
            iml_column_name=list(tmpColumn['SourceTableColumn'])
            itl_column_name=iml_column_name
            itl_schema=source_schema
            itl_table_name=iml_table_name+'_tmp'
            iml_is_pk=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']==1])
            iml_not_pk=list(tmpColumn['SourceTableColumn'][tmpColumn['IsKey']!=1])
            iml_zipper_column_name=list(tmpColumn['SourceTableColumn'][tmpColumn['IsZipper']==1])
            
            code_model_temp=code_model.copy()
            
            for m in range(len(code_model_temp)):
                f1=code_model_temp[m].find('@')#是否包含此字符
                if f1>0:#如果包含
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{itl_column_name}','@{iml_column_name}'],keyvalue= [itl_column_name,iml_column_name])
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{iml_column_name}'],keyvalue= [iml_column_name])
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{itl_column_name}'],keyvalue= [itl_column_name])
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{iml_is_pk}'],keyvalue= [iml_is_pk])
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{iml_not_pk}'],keyvalue= [iml_not_pk])
                    code_model_temp[m]=linetext_replace(linetext=code_model_temp[m],keychar=['@{iml_zipper_column_name}'],keyvalue= [iml_zipper_column_name])

            sqlcode=''.join(code_model_temp)       
            sqlcode=sqlcode.replace("${iml_table_name}",iml_table_name)     
            sqlcode=sqlcode.replace("${iml_schema}",iml_schema)  
            sqlcode=sqlcode.replace("${itl_schema}",itl_schema)  
            sqlcode=sqlcode.replace("${itl_table_name}",itl_table_name)  
            sqlcode=sqlcode.replace("${start_dt}",start_dt) 
            sqlcode=sqlcode.replace("${end_dt}",end_dt) 
            sqlcode=sqlcode.replace("${etl_dt}",etl_dt) 
            sqlcode=sqlcode.replace("${etl_timestamp}",etl_timestamp) 
            sqlcode=sqlcode.replace("${zipper_column}",zipper_column) 
            sqlcode=sqlcode.replace("${code_create_time}",code_create_time) 

            f = open( output_path+'/p_iml_'+iml_table_name+".sql",'w',encoding='utf-8')
            f.write(sqlcode)
            f.close()
            print('Done!')
'''
dml_mysql_m(
                mapping_xlsx='D:/xuguanming/oldFiles/数据库建模/generating_engine/mapping/4.iml_mapping_粤财资产数据中心.xlsx',
                code_model_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/models/iml/dml',
                source_schema='iml',
                target_schema='iml',#iml层的schema
                etl_dt='etl_dt',
                etl_timestamp='etl_timestamp',
                start_dt='start_dt',
                end_dt='end_dt',
                zipper_column='zipper_column',
                output_path=r'D:/xuguanming/oldFiles/数据库建模/generating_engine/code/iml/dml'
                )
'''


def createSingleTableFromOracleToMysql(cursor=None,#数据库连接对象
                                       oracle_schema='DATAHUB',#oracle的schema
                                 oracle_table='AMC_COT_EXECUTE_PLAN_B',#oracle的表名
                                 mysql_schema='LDM',#mysql的schema
                                 mysql_table='AMC_COT_EXECUTE_PLAN_B',#mysql的表名
                                 key_words=['RANGE'],#mysql的关键字需要特殊处理
                                 ENGINE='InnoDB',
                                 DEFAULT_CHARSET='utf8mb4',
                                 COLLATE='utf8mb4_unicode_ci'):
    
    '''
    函数说明，在连接oracle数据库之后，输入oracle表名，输出mysql的创表sql语句。  
    xuguanming 20220127  
    参数调试示例：
    cursor=cr#数据库连接对象
    oracle_schema='DATAHUB' #oracle的schema
    oracle_table='AM_NH_EMPLOYEE'#oracle对应的表名
    mysql_schema='LDM'#mysql中需要创建的schema
    mysql_table='AM_NH_EMPLOYEE'#mysql中创建的表名
    key_words=['RANGE']#mysql关键字作为变量时将特殊处理
    ENGINE='InnoDB'
    DEFAULT_CHARSET='utf8mb4'
    COLLATE='utf8mb4_unicode_ci'
    '''
    
    oracle_schema=oracle_schema.upper()
    oracle_table=oracle_table.upper()
    mysql_schema=mysql_schema.upper()
    mysql_table=mysql_table.upper()
    
    sql="\
    select t.TABLE_NAME,\n\
    	   t.COLUMN_NAME,\n\
    	   pk.PRIMARY_KEY,\n\
    	   ind.index_position,\n\
    	   t.DATA_TYPE,\n\
    	   t.DATA_LENGTH,\n\
    	   t.DATA_PRECISION,\n\
    	   t.DATA_SCALE,\n\
    	   t.NULLABLE,\n\
    	   t.COLUMN_ID,\n\
    	   c.COMMENTS\n\
    from ALL_tab_columns t,\n\
    	 ALL_col_comments c\n\
    ---匹配主键n\n\
    		 left join (\n\
    		 select cu.COLUMN_NAME, cu.POSITION as PRIMARY_KEY\n\
    		 from ALL_cons_columns cu,\n\
    			  ALL_constraints au\n\
    		 where cu.constraint_name = au.constraint_name\n\
    		   and au.constraint_type = 'P'\n\
    		   and au.table_name = '%s'\n\
    		     AND cu.OWNER=au.OWNER\n\
                     and cu.OWNER= '%s'\n\
    	 ) pk on c.column_name = pk.COLUMN_NAME\n\
    ---匹配索引n\n\
    		 left join (\n\
    		 select t.COLUMN_NAME, COLUMN_POSITION as index_position, i.index_type\n\
    		 from ALL_ind_columns t,\n\
    			  ALL_indexes i\n\
    		 where t.index_name = i.index_name\n\
    		   and t.table_name = i.table_name\n\
    		   and t.table_name = '%s'\n\
    		     AND t.TABLE_OWNER=i.OWNER\n\
                     and t.TABLE_OWNER= '%s'\n\
    	 ) ind on c.COLUMN_NAME = ind.COLUMN_NAME\n\
    where t.table_name = c.table_name\n\
      and t.column_name = c.column_name\n\
      and t.table_name = '%s'\n\
      AND t.OWNER= c.OWNER\n\
        and t.OWNER = '%s'\n\
    order by COLUMN_ID" %(oracle_table,oracle_schema,oracle_table,oracle_schema,oracle_table,oracle_schema)
    #str(rsdf.loc[i,'DATA_PRECISION'])
    cursor.execute(sql)
    rs = cursor.fetchall()
    rsdf=pd.DataFrame(rs)
    #添加列名
    colsname = cursor.description 
    colsnamelist=[]
    for i in range(len(colsname)):
        colsnamelist.append(colsname[i][0])  
    rsdf.columns=colsnamelist
    
    rsdf['code']=None
    for i in range(rsdf.shape[0]):
        if key_words !=None:
            if rsdf.loc[i,'COLUMN_NAME'].upper() in key_words:#关键字不能直接作为列名，在这里处理
                rsdf.loc[i,'COLUMN_NAME']='`'+rsdf.loc[i,'COLUMN_NAME']+'`'
        
        if rsdf.loc[i,'NULLABLE']=="Y":
            NULLABLE='NULL'
            
        else:
            NULLABLE='NOT NULL'
            
        if rsdf.loc[i,'COMMENTS']==None:
            COMMENTS=''
        else:
            COMMENTS=rsdf.loc[i,'COMMENTS']
        #oracle和mysql字段类型转换
        if rsdf.loc[i,'DATA_TYPE']=='VARCHAR2' or rsdf.loc[i,'DATA_TYPE']=='CHAR':
            if rsdf.loc[i,'DATA_LENGTH']>=1000 :#字符串长度大于1000的。
                rsdf.loc[i,'DATA_TYPE_MYSQL']='TEXT'
            else:
                rsdf.loc[i,'DATA_TYPE_MYSQL']='VARCHAR('+str(rsdf.loc[i,'DATA_LENGTH'])+')'
        elif rsdf.loc[i,'DATA_TYPE']=='NUMBER':  
            if str(rsdf.loc[i,'DATA_PRECISION']) in('None','nan'):#空缺
                rsdf.loc[i,'DATA_TYPE_MYSQL']='INT' 
            else:
                rsdf.loc[i,'DATA_TYPE_MYSQL']='DECIMAL('+str(int(rsdf.loc[i,'DATA_PRECISION']))+','+str(int(rsdf.loc[i,'DATA_SCALE']))+')'
        elif (rsdf.loc[i,'DATA_TYPE'] == 'TIMESTAMP(6)') or (rsdf.loc[i,'DATA_TYPE'] == 'DATE') :
            rsdf.loc[i,'DATA_TYPE_MYSQL']='DATETIME'
        elif rsdf.loc[i,'DATA_TYPE']=='CLOB':
            rsdf.loc[i,'DATA_TYPE_MYSQL']='LONGTEXT'  
        elif rsdf.loc[i,'DATA_TYPE']=='NVARCHAR2':
            rsdf.loc[i,'DATA_TYPE_MYSQL']='NVARCHAR('+str(rsdf.loc[i,'DATA_LENGTH'])+')'
        else:
            rsdf.loc[i,'DATA_TYPE_MYSQL']= rsdf.loc[i,'DATA_TYPE']
            
        rsdf.loc[i,'code']="\t"+rsdf.loc[i,'COLUMN_NAME']+" "+rsdf.loc[i,'DATA_TYPE_MYSQL']+" "+NULLABLE+" COMMENT '"+ COMMENTS+"',"
        
       
        rsdf.loc[i,'SourceTable']=rsdf.loc[i,'TABLE_NAME']
        rsdf.loc[i,'SourceTableColumnOrder']=rsdf.loc[i,'COLUMN_ID']
        rsdf.loc[i,'SourceTableColumn']=rsdf.loc[i,'COLUMN_NAME']
        rsdf.loc[i,'SourceTableColumnType']=rsdf.loc[i,'DATA_TYPE_MYSQL']
        if(rsdf.loc[i,'COMMENTS'] is None):
            rsdf.loc[i,'SourceTableColumnComment']=""
        else:
            rsdf.loc[i,'SourceTableColumnComment']=rsdf.loc[i,'COMMENTS']
        if(rsdf.loc[i,'PRIMARY_KEY'] is None):
            rsdf.loc[i,'IsKey']=0
        else:
            rsdf.loc[i,'IsKey']=1
        rsdf.loc[i,'IsIndex']=0
        if(rsdf.loc[i,'NULLABLE'] =='Y'):
            rsdf.loc[i,'IsNotNull']=0
        else:
            rsdf.loc[i,'IsNotNull']=1
       
        rsdf.loc[i,'DefaultValue']=''
        rsdf.loc[i,'IsPartitionKey']=0
        if(rsdf.loc[i,'PRIMARY_KEY'] is None):
            rsdf.loc[i,'IsZipper']=1
        else:
            rsdf.loc[i,'IsZipper']=0

        rsdf.loc[i,'TableComment']=""
    
    #查询表的注释
    sql2="select * from all_tab_comments where TABLE_NAME='%s' and OWNER='%s'" % (oracle_table,oracle_schema)
    cursor.execute(sql2)
    rs2 = cursor.fetchall()
    tablecomments=pd.DataFrame(rs2)[3][0]
    if tablecomments==None:
        tablecomments=''
    
    #主键处理
    PRIMARY_KEY1=rsdf.loc[rsdf['PRIMARY_KEY']>0,'COLUMN_NAME']
    if PRIMARY_KEY1.shape[0]>0:
        PRIMARY_KEY_STR="PRIMARY KEY ("+",".join(PRIMARY_KEY1.to_list())+")"
    else:
        PRIMARY_KEY_STR=''
        rsdf.loc[rsdf.shape[0]-1,'code']=rsdf.loc[rsdf.shape[0]-1,'code'].rstrip(',')#没有主键，则去掉最后一个逗号

    codebase=[]
    code1=['DROP TABLE IF EXISTS %s.%s;\nCREATE TABLE %s.%s\n(' % (mysql_schema,mysql_table,mysql_schema,mysql_table)]
    code2=rsdf.loc[:,'code']
    code3=[PRIMARY_KEY_STR]
    #code3=", %s  TIMESTAMP NULL  COMMENT 'ETL处理时间'\n	, %s  DATE NOT NULL  COMMENT 'ETL日期'" % (etl_timestamp,etl_dt)
    code4=[") ENGINE = %s\nDEFAULT CHARSET = %s\nCOLLATE = %s comment '%s';" % (ENGINE,DEFAULT_CHARSET,COLLATE,tablecomments)]
    codebase.extend(code1)
    codebase.extend(code2)
    codebase.extend(code3)
    codebase.extend(code4)
    codebasefinal='\n'.join(codebase)
    
    #生成mapping excel

    
    return codebasefinal,rsdf[['SourceTable','SourceTableColumnOrder','SourceTableColumn','SourceTableColumnType'
                               ,'SourceTableColumnComment','IsKey','IsIndex','IsNotNull','DefaultValue','IsPartitionKey','IsZipper','TableComment']]


def createTotalTableFromOracleToMysql(cursor=None,
                                      oracle_schema='DATAHUB',
                                     oracle_tables=['CUST_INFO','PROJECT_INFO'],
                                     mysql_schema='LDM',
                                     mysql_tables=None,
                                     key_words=["RANGE"]):
    '''
    xuguanming 20220221
    说明：输入指定的oracle多个表，输出多个表的创表mysql语句
    cursor:oracle连接器
    oracle_schema:ORACLE的schema
    oracle_tables：指定的表名，必须是list形式
    mysql_schema：需要创建在mysql中的哪个schema中
    key_words：mysql关键字作为变量时将特殊处理
    '''
    sqltotal=[]
    
    if mysql_tables is None:
        mysql_tables=oracle_tables
    
    if len(oracle_tables)==len(mysql_tables):#两个的长度要一样
        for i in range(len(oracle_tables)):
            print('oracle表'+oracle_tables[i]+"，mysql表"+mysql_tables[i])
            crtsql=createSingleTableFromOracleToMysql(cursor=cursor,
                                                      oracle_schema=oracle_schema,
                                             oracle_table=oracle_tables[i],
                                             mysql_schema=mysql_schema,
                                             mysql_table=mysql_tables[i],
                                             key_words=key_words)
            sqltotal.append(crtsql[0])
            if i==0:
                mappingDf=crtsql[1]
            else:
                mappingDf=mappingDf.append(crtsql[1])
            print(oracle_tables[i]+'已完成')     
        sqltotal_str="\n\n".join(sqltotal)
        return sqltotal_str,mappingDf
    else:
        print('错误！oracle_tables 与 mysql_tables 长度不一致！')
            
'''
#示例：
import cx_Oracle
import pandas as pd
import os
import math
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
os.environ['TNS_ADMIN'] = 'C:\ProgramData\instantclient_21_3'
os.environ['Path'] = 'C:\ProgramData\instantclient_21_3'    
#-------------示例1：针对特定oracle表，输出mysql的创表语句,可以自定义mysql的表名--------------------#
    db = cx_Oracle.connect('odm', 'xxxxx', '192.198.8.188:1521/addb2')
    cr = db.cursor()    
    crtsql_tables1=createSingleTableFromOracleToMysql(cursor=cr,
                                                     oracle_schema='odm',
                                     oracle_table='AMC_REC',
                                     mysql_schema='ods',
                                     mysql_table='AMC_AST_ASSET_TEMP_B',
                                     key_words=['RANGE','LAW_EXAM_ID'])
    
    db.close()
    
    ##-------------------示例2：创建oracle库中的所有表，或者指定的多个表----------------------------#
    db = cx_Oracle.connect('hdm', 'xxxxx', '192.198.8.188:1521/addb2')
    cr = db.cursor()  
    sql="select table_name from all_tables where owner='HDM'" #指定hdm库
    cr.execute(sql)
    rs = cr.fetchall()
    oracle_tables0=pd.DataFrame(rs)[0].tolist()#找到库中的所有表
    oracle_tables=[]#筛选其中的部份表
    for i in oracle_tables0:
        if (i[0:4]=='AMC_') | (i[0:4]=='PCMC') :
            oracle_tables.append(i)
    oracle_tables.remove('AMC_AST_FREEZE_LOCK_B')
    #or指定
    oracle_tables=['AMC_AST_PACKAGE_OFFICIAL_B',
    'PCMC_KNP_PARA',
    'AMC_AST_ASSET_OFFICIAL_B',
    'AMC_SYS_ZONE_B',
    'AMC_REC_RECEIVE_B',
    'AMC_AST_TUNOVER_B',
    'PCMC_DEPT',
    'PCMC_USER',
    'PCMC_USER_ROLE',
    'PCMC_ROLE',
    'AMC_PRJ_PROJECTS_B',
    'AMC_ASS_REQUIREMENT_B',
    'AMC_MET_CONF_RESOLUTION_B',
    'AMC_CUS_BASIC_INFO_B']

    crtsql_tables=createTotalTableFromOracleToMysql(cursor=cr,
                                                    oracle_schema='HDM',
                                         oracle_tables=oracle_tables,
                                         mysql_schema='ods',
                                         key_words=["RANGE"])
    #sql输出到文件
    with open(r'D:\Xuguanming\项目信息\04_IT系统项目\202103_报表项目\code\报表code\ods\create_table.sql','w') as f:    #设置文件对象
        f.write(crtsql_tables)                 #将字符串写入文件中
        
    #对应kettle_job    
    oracle_tables_df=pd.DataFrame(oracle_tables)  
    oracle_tables_df['CHANNEL']='hdm'
    oracle_tables_df['SOURCE']=oracle_tables_df[0]
    oracle_tables_df['SIGN']=oracle_tables_df[0]
    oracle_tables_df['job_flag']=0
    oracle_tables_df=oracle_tables_df.drop(0,axis=1)    
    oracle_tables_df.to_excel(r'D:\Xuguanming\项目信息\04_IT系统项目\202103_报表项目\code\报表code\ods\kettle_jobs_AMC.xlsx',sheet_name='sheet1',index=False)

    db.close()

'''

def selectMysqlMetadata(mysqlConnect=None,#数据库连接对象
                                systemFlag="",
                                tableSchema='iol',
                                 tablelist=[]
                                 ):
    '''
    xuguanming 20221221
    说明：查看mysql指定表的元数据
    '''
    tablelist_char="'"+("','".join(tablelist)).upper()+"'"
    sql="select '%s' \n\
     , t1.TABLE_NAME                as sourceTable \n\
     , t1.ORDINAL_POSITION          as SourceTableColumnOrder \n\
     , t1.COLUMN_NAME               as SourceTableColumn \n\
     , t1.COLUMN_TYPE               as SourceTableColumnType \n\
     , t1.COLUMN_COMMENT            as SourceTableColumnComment \n\
     , if(t4.CONSTRAINT_NAME = 'PRIMARY', 1, 0) as IsKey \n\
     , if(t4.CONSTRAINT_NAME = 'PRIMARY', 1, 0) as IsIndex \n\
     , if(t4.CONSTRAINT_NAME = 'PRIMARY', 1, 0) as IsNotNull \n\
     , null                      as DefaultValue \n\
     , 0                         as IsPartitionKey \n\
     , if(t4.CONSTRAINT_NAME = 'PRIMARY', 0, 1) as IsZipper \n\
     , t2.TABLE_COMMENT as TableComment \n\
    from information_schema.COLUMNS t1 \n\
    left join information_schema.TABLES t2 on t1.TABLE_SCHEMA=t2.TABLE_SCHEMA and t1.TABLE_NAME=t2.TABLE_NAME \n\
    left join information_schema.KEY_COLUMN_USAGE t4 on t1.TABLE_SCHEMA=t4.TABLE_SCHEMA and t1.TABLE_NAME=t4.TABLE_NAME and t1.COLUMN_NAME=t4.COLUMN_NAME \n\
        where t1.TABLE_NAME in ( \n\
                         %s \n\
        ) \n\
        and t1.TABLE_SCHEMA ='%s' \n\
    order by t1.TABLE_NAME,t1.ORDINAL_POSITION \n\
        "  % (systemFlag,tablelist_char,tableSchema)
    if(mysqlConnect is None):
        MysqlMetadata=None
    else:    
        MysqlMetadata = pd.read_sql(sql=sql, con=mysqlConnect)
        MysqlMetadata.index=range(MysqlMetadata.shape[0])
    return [MysqlMetadata ,sql]
'''
conn = pymysql.connect(host='100.100.1.117',
                                   port=63306,
                                   user='xxxx',
                                   password='xxxx',
                                   database='iol',
                                   charset='utf8')   
res=selectMysqlMetadata(mysqlConnect=conn,#数据库连接对象
                                systemFlag="",
                                 tablelist=['AMC_DES_APPLY_B','AMC_CUS_BASIC_INFO_B']
                                 )
conn.close()
'''



