# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 13:55:47 2022

@author: Fanfan
"""
#####理想聚类 idc_clustering #####

import numpy as np 
import pandas as pd
import win32ui





def idc():
    input("提示：按任意键开始选择待学习的数据！")
    
    
    dlg = win32ui.CreateFileDialog(1)
    dlg.SetOFNInitialDir('C:/')
    dlg.DoModal()
    filename = dlg.GetPathName()
    arr = pd.read_csv(filename).values
    
    
    enter=input("提示：输入真实的分类数量，并按任意键继续！")
    num_class=int(enter)
    
    data={}
    for num in range(1,num_class+1):
        lists=[]
        classname0='class'+str(num)+'name'
        classname0=input('提示：输入分类'+str(num)+'所属分类类别名称，按任意键继续！')    
        classname1='class'+str(num)+'start'
        classname1=input('提示：分类'+str(num)+'开始行索引，按任意键继续！')
        classname2='class'+str(num)+'end'
        classname2=input('提示：分类'+str(num)+'结束行索引，按任意键继续！')
        lists.append(int(classname1))
        lists.append(int(classname2))
        data[classname0]=lists
    print(data)
    
    dic1={}
    for k,v in data.items():
        dic1[k]=arr[v[0]:v[1],:]
    print(dic1)
    
      
    dic2={} 
    diss=[] 
       
    input("提示：请确保测试数据具有和学习数据相同的属性列，并按任意键继续！")
    dlg1 = win32ui.CreateFileDialog(1)
    dlg1.SetOFNInitialDir('C:/')
    dlg1.DoModal()
    filename1 = dlg1.GetPathName()
    p2 = pd.read_csv(filename1).values    
    
    
    
    
    for k,v in dic1.items():
        dist=[]
        for vv in v:
            list2=[]
            for i in range(len(p2[0])):            
                d=(vv[i]-p2[0][i])**2
                list2.append(d)
            dd=sum(list2)
            dis=np.sqrt(dd)
            diss.append(dis)
            dist.append(dis)
            print(len(dist))
        dic2[k]=dist        
    
    
    for ks,vs in dic2.items():
        if(min(diss) in vs):
            print(ks)











