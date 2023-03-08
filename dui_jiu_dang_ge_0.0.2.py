# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 20:22:00 2023

@author: Cractor
"""
import tushare as ts
import pandas as pd
import numpy as np
print(ts.__version__)

#df = ts.get_hist_data('600900',ktype='W')
#print(历史周线)
#df.to_csv('C:/Users/ChenQiChen/Documents/tushare/df.csv')
pd = pd.read_csv('C:/Users/ChenQiChen/Documents/tushare/df.csv')
#length=df.index.size




#筛选出特定日期的值
#df_2023=df[(df["date"]>="2022-02-10")&(df["date"]<="2023-02-10")]
date_start = "2022-01-01"
date_end = "2022-07-01"
if date_start > date_end:
    print("日期设置错误")
    
pd_period = pd[(pd["date"] >= date_start) & (pd["date"] <= date_end)]
#print (pd_2022H1)


print("初始价格", pd_period.iloc[-1].open) #iloc 按照数值选择对应行，负数从末尾开始
start = pd_period.iloc[-1].open #初始持仓价取第一个交易日的开盘价
money = 1000000 #可用金额手动设置
init_pct = 50 #初始仓位比例手动设置
num_trade = 1000#一笔交易的股票数量
#每一步的波动深度,0.02卖出，0.02买入，如果要穷举从0.01到0.1哪个收益高，可以在整个程序外加一层循环
grid_sell = 0.02
grid_buy = 0.01
grid_price = start#网格的初始价格，取第一笔开盘价
cost_buy = 3/10000#买入的交易成本，保底6元，券商5元居多，多算1元是预留给过户费
cost_sell = 3/10000 + 1/1000#卖出的交易成本，保底6元另计
print("每笔交易股数",num_trade)
#根据初始可用金额与持仓比例，算出初始持仓数量，以100股为最小单位，向下取整
num_hold = int(np.floor(money * init_pct/100/start/100)) * 100
money_hold = money - num_hold * start
print("当前持仓数", num_hold, "当前现金", '%.2f'%money_hold, "当前资产", '%.2f'%(num_hold * grid_price + money_hold))


def sell_share(current, grid_price, grid_sell, start, money_hold, num_hold, num_trade):
    #股数足够一笔则卖出，不够则跳过
    if num_hold > num_trade:
        #正值向0取整，需要向下取整，用np.floor形成新的网格价
        grid_price = grid_price + start * grid_sell * np.floor((current - grid_price)/(grid_sell * start))
        #print("卖出,新的网格价为",grid_price)
        money_hold = money_hold + current * num_trade - max(cost_sell * current * num_trade, 6)
        num_hold = num_hold - num_trade
        print("卖出", end='  ')
    else:
        print("剩余持股不够卖，跳过")
        #注意缩进，这是在else之外的print
        # print("当前持仓数",num_hold,"当前现金",'%.2f'%money_hold,"当前资产",'%.2f'%(num_hold*current+money_hold))
    return current,grid_price,money_hold,num_hold

def buy_share(current, grid_price, grid_buy, start, money_hold, num_hold,num_trade):
    #钱够则买入，不够则跳过
    if money_hold > current * num_trade + max(cost_buy * current * num_trade, 5): 
        #print((current-grid_price),(grid_sell*start),np.ceil((current-grid_price)/(grid_sell*start)))
        #负值向0取整，需要向上取整，用np.ceil
        grid_price = grid_price + start * grid_buy * np.ceil((current - grid_price)/(grid_sell * start))
        money_hold = money_hold-current * num_trade - max(cost_buy * current * num_trade, 5)
        num_hold = num_hold + num_trade
        #print("买入,新的网格价为",grid_price,"当前持仓",num_hold)
        print("买入",end='  ')
    #else:
    #    print("钱不够买了，跳过")
    #注意缩进，这是在else之外的print 
   # print("当前持仓数",num_hold,"当前现金",'%.2f'%money_hold,"当前资产",'%.2f'%(num_hold*current+money_hold))
    return current,grid_price,money_hold,num_hold






#def grid(pd_period,date_start,date_end,current,grid_price,grid_buy,start,money_hold,num_hold,num_trade)

#因为是负值开始计数，所以不能iloc取负0，否则就多了一条最新数据，而没有从最旧数据开始
length = pd_period.index.size

for i in range(1, length+1):
    current = pd_period.iloc[-i].open#当周开盘价设为当前价
    print (pd_period.iloc[-i].date, "开盘价", '%.2f'%current, end='  ')#print不换行,用,end=' '结尾
    difference = (current - start) / start#计算当前价与基准价的偏差
    print("较初始价涨幅", '%.2f'% (difference*100), "%", end='  ')
    #print("当前网格价",grid_price)
    #print("当前num_hold值",num_hold)
    
    #if语句里写太多东西不好读，把买入卖出都改成函数，且验算是否有钱买入、有股卖出
    if  current > grid_price + grid_sell * start:#当前价格高于网格上一格则卖出
        #右斜杠\换行，换行的斜杠后面不能有任何符号，把买入卖出函数中更新的几个参数传出来
        current, grid_price, money_hold, num_hold = \
        sell_share(current, grid_price, grid_sell, start, money_hold, num_hold, num_trade)
        
    else:  
        if current < grid_price - grid_buy * start:#当前价格低于网格下一格则买入
            current, grid_price, money_hold, num_hold = \
            buy_share(current, grid_price, grid_buy, start, money_hold, num_hold, num_trade)            
        else:
            print("持仓不动")
    print("当前持仓数", num_hold, "当前现金", '%.2f'%money_hold, "当前资产", '%.2f'%(num_hold * current + money_hold))
    print(" ")
    pass
#循环结束之后的当前资产减去初始金钱，再除以初始金钱，作为网格交易函数的返回值
earning_rate = ((num_hold * current + money_hold) - money) / money
print("收益率", '%.2f'% (difference*100), "%") 
#return 0
