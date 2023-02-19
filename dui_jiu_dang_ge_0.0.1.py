# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 20:22:00 2023

@author: ChenQ1Chen
"""
import tushare as ts
import pandas as pd
import numpy as np
print(ts.__version__)

#df=ts.get_hist_data('600900',ktype='W') 
#print(历史周线)
#df.to_csv('E:/600900.csv')
pd = pd.read_csv('E:/600900.csv')
#length=df.index.size

#筛选出特定日期的值
#df_2023=df[(df["date"]>="2022-02-10")&(df["date"]<="2023-02-10")]

pd_2022H1 = pd[(pd["date"]>="2022-01-01")&(pd["date"]<="2022-07-01")]
#print (pd_2022H1)


print("初始价格",pd_2022H1.iloc[-1].open) #iloc 按照数值选择对应行，负数从末尾开始
start=pd_2022H1.iloc[-1].open #初始持仓价取第一个交易日的开盘价
money=100000 #可用金额手动设置
init_pct=50 #初始仓位比例手动设置
num_trade=800#一笔交易的股票数量
#每一步的波动深度,0.02卖出，0.02买入
grid_sell=0.02
grid_buy=0.02
grid_price=start#网格的初始价格，取第一笔开盘价
cost_buy=3/10000#买入的交易成本，保底6元，券商5元居多，多算1元是预留给过户费
cost_sell=3/10000+1/1000#卖出的交易成本，保底6元另计
print("每笔交易股数",num_trade)
#根据初始可用金额与持仓比例，算出初始持仓数量，以100股为最小单位，向下取整
num_hold=int(np.floor(money*init_pct/100/start/100))*100
money_hold=money-num_hold*start
print("当前持仓数",num_hold,"当前现金",'%.2f'%money_hold,"当前资产",'%.2f'%(num_hold*grid_price+money_hold))

#因为是负值开始计数，所以不能iloc取负0，否则就多了一条最新数据，而没有从最旧数据开始
length=pd_2022H1.index.size
for i in range(1, length+1):
    current=pd_2022H1.iloc[-i].open#当周开盘价设为当前价
    print (pd_2022H1.iloc[-i].date,"开盘价",'%.2f'%current,end='  ')#print不换行,用,end=' '结尾
    difference=(current-start)/start#计算当前价与基准价的偏差
    print("较初始价涨幅",'%.2f'% (difference*100),"%",end='  ')
    #if语句里写太多东西不好读，考虑把买入卖出都改成函数，且每一步的台阶需要更新
    
    if  current>grid_price+grid_sell*start:#当前价格高于网格上一格则卖出
        #print("旧的网格价为",grid_price,end='  ')  
        #正值向0取整，需要向下取整，用np.floor
        grid_price=grid_price+start*grid_sell*np.floor((current-grid_price)/(grid_sell*start))
        #print("卖出,新的网格价为",grid_price)
        #暂且假设钱够用，可以透支到负
        money_hold=money_hold+current*num_trade-max(cost_sell*current*num_trade,6)
        num_hold=num_hold-num_trade
        print("卖出",end='  ')
        print("当前持仓数",num_hold,"当前现金",'%.2f'%money_hold,"当前资产",'%.2f'%(num_hold*current+money_hold))
    else:  
        if current<grid_price-grid_buy*start:#当前价格低于网格下一格则买入
            #print("旧的网格价为",grid_price,end='  ')   
            #print((current-grid_price),(grid_sell*start),np.ceil((current-grid_price)/(grid_sell*start)))
            #负值向0取整，需要向上取整，用np.ceil
            grid_price=grid_price+start*grid_buy*np.ceil((current-grid_price)/(grid_sell*start))
            money_hold=money_hold-current*num_trade-max(cost_buy*current*num_trade,6)
            num_hold=num_hold+num_trade
            #print("买入,新的网格价为",grid_price)
            print("买入",end='  ')
            print("当前持仓数",num_hold,"当前现金",'%.2f'%money_hold,"当前资产",'%.2f'%(num_hold*current+money_hold))
        else:
            
            print("持仓不动",end='  ')
            print("当前持仓数",num_hold,"当前现金",'%.2f'%money_hold,"当前资产",'%.2f'%(num_hold*current+money_hold))
    pass

