### pythonstock V2 项目简介
基于https://github.com/pythonstock/stock的项目进行开发

所做的改动有：
    1.对于抓取数据的种类进行了扩展
    2.增加了技术分析的种类，以及分析图像的展示方式
    3.增加了点数图的展示
    4.为后续加入各种机器学习方法和强化学习方法扩展了接口

以下内容为原项目的readme
```
项目地址：https://github.com/pythonstock/stock
PythonStock V2 是基于Python的pandas，akshare，bokeh，tornado，stockstats，ta-lib等框架开发的全栈股票系统。
项目创建于2017年7月17日，每月不定期更新。
1）可以直接使用docker直接本地部署运行，整个项目在docker hub上压缩后200MB，本地占用500MB磁盘空间。
2）使用Docker解决了Python库安装问题，使用Mariadb（MySQL）存储数据。借助akshare抓取数据。
3）使用cron做定时任务，每天进行数据抓取计算，每天18点开始进行数据计算，计算当日数据，使用300天数据进行计算，大约需要15分钟计算完毕。
4）股票数据接口防止被封，按天进行数据缓存，储存最近3天数据，每天定时清除，同时使用read_pickle to_pickle 的gzip压缩模式存储。
5）使用tornado开发web系统，支持每日股票数据-东财，龙虎榜-个股上榜-新浪，数据中心-大宗交易行情等。
6）数据展示系统，是通用数据展示系统，配置字典模板之后，页面自动加载数据，并完成数据展示，后续自己开发的指标数据可以加入进去。
7）增加曲线数据分析，在查看股票中，可以直接跳转到东方财富页面查看相关信息，点击指标之后使用Bokeh将多达 17 个指标的数据绘图，进行图表展示。
8) 2.0 最大的更新在于替换tushare库（因部分库不能使用），使用akshare进行数据抓取。

基础库版本

1，pandas使用【 1.3.5 】版本，升级了
2，numpy使用【 1.21.5 】版本，升级了
3，akshare使用【 1.3.50 】版本，升级了
4，bokeh使用【 2.4.2 】版本，升级了
5，stockstats使用【 0.3.2 】版本

```

2.0 说明
 ![image](https://raw.githubusercontent.com/pythonstock/stock/master/web/static/img/stock2-001.png)
 ![image](https://raw.githubusercontent.com/pythonstock/stock/master/web/static/img/stock2-002.png)

 bokeh 绘图指标数据：
 
  ![image](https://raw.githubusercontent.com/pythonstock/stock/master/web/static/img/stock2-003.png)
 

然后根据3个指标进行股票数据计算：
```

KDJ:
1，超买区：K值在80以上，D值在70以上，J值大于90时为超买。一般情况下，股价有可能下跌。投资者应谨慎行事，局外人不应再追涨，局内人应适时卖出。
2，超卖区：K值在20以下，D值在30以下为超卖区。一般情况下，股价有可能上涨，反弹的可能性增大。局内人不应轻易抛出股票，局外人可寻机入场。

RSI:
1．当六日指标上升到达80时，表示股市已有超买现象，如果一旦继续上升，超过90以上时，则表示已到严重超买的警戒区，股价已形成头部，极可能在短期内反转回转。
2．当六日强弱指标下降至20时，表示股市有超卖现象，如果一旦继续下降至10以下时则表示已到严重超卖区域，股价极可能有止跌回升的机会。

CCI
1、当CCI＞﹢100时，表明股价已经进入非常态区间——超买区间，股价的异动现象应多加关注。
2、当CCI＜﹣100时，表明股价已经进入另一个非常态区间——超卖区间，投资者可以逢低吸纳股票。

购买条件结果表：guess_indicators_lite_buy_daily
购买条件结果表：guess_indicators_lite_sell_daily

```

每日股票指标数据计算17个指标如下（数据表 guess_indicators_daily）： 


| 计算指标           | 说明 |
|---------- |------------------------------------------|
| 1，交易量delta指标分析     | The Volume Delta (Vol ∆)  |
| 2，计算n天差     |  可以计算，向前n天，和向后n天的差。  |
| 3，n天涨跌百分百计算     |  可以看到，-n天数据和今天数据的百分比。  |
| 4, CR指标     | http://wiki.mbalib.com/wiki/CR%E6%8C%87%E6%A0%87 价格动量指标 CR跌穿a、b、c、d四条线，再由低点向上爬升160时，为短线获利的一个良机，应适当卖出股票。 CR跌至40以下时，是建仓良机。而CR高于300~400时，应注意适当减仓。  |
| 5，最大值，最小值     |  计算区间最大值 volume max of three days ago, yesterday and two days later stock["volume_-3,2,-1_max"] volume min between 3 days ago and tomorrow stock["volume_-3~1_min"] 实际使用的时候使用 -2~2 可计算出5天的最大，最小值。 |
| 6, KDJ指标     | http://wiki.mbalib.com/wiki/%E9%9A%8F%E6%9C%BA%E6%8C%87%E6%A0%87    随机指标(KDJ)一般是根据统计学的原理，通过一个特定的周期（常为9日、9周等）内出现过的最高价、 最低价及最后一个计算周期的收盘价及这三者之间的比例关系，来计算最后一个计算周期的未成熟随机值RSV， 然后根据平滑移动平均线的方法来计算K值、D值与J值，并绘成曲线图来研判股票走势。 （3）在使用中，常有J线的指标，即3乘以K值减2乘以D值（3K－2D＝J），其目的是求出K值与D值的最大乖离程度， 以领先KD值找出底部和头部。J大于100时为超买，小于10时为超卖。 |
| 7，SMA指标     | http://wiki.mbalib.com/wiki/Sma 简单移动平均线（Simple Moving Average，SMA） 可以动态输入参数，获得几天的移动平均。 |
| 8, MACD指标     | http://wiki.mbalib.com/wiki/MACD   平滑异同移动平均线(Moving Average Convergence Divergence，简称MACD指标)，也称移动平均聚散指标 MACD 则可发挥其应有的功能，但当市场呈牛皮盘整格局，股价不上不下时，MACD买卖讯号较不明显。 当用MACD作分析时，亦可运用其他的技术分析指标如短期 K，D图形作为辅助工具，而且也可对买卖讯号作双重的确认。 |
| 9, BOLL指标     | http://wiki.mbalib.com/wiki/BOLL   布林线指标(Bollinger Bands) |
| 10, RSI指标     | http://wiki.mbalib.com/wiki/RSI    相对强弱指标（Relative Strength Index，简称RSI），也称相对强弱指数、相对力度指数 2）强弱指标保持高于50表示为强势市场，反之低于50表示为弱势市场。 （3）强弱指标多在70与30之间波动。当六日指标上升到达80时，表示股市已有超买现象，如果一旦继续上升，超过90以上时，则表示已到严重超买的警戒区，股价已形成头部，极可能在短期内反转回转。 |
| 11, W%R指标     | http://wiki.mbalib.com/wiki/%E5%A8%81%E5%BB%89%E6%8C%87%E6%A0%87 威廉指数（Williams%Rate）该指数是利用摆动点来度量市场的超买超卖现象。 |
| 12, CCI指标     | http://wiki.mbalib.com/wiki/%E9%A1%BA%E5%8A%BF%E6%8C%87%E6%A0%87 顺势指标又叫CCI指标，其英文全称为“Commodity Channel Index”， 是由美国股市分析家唐纳德·蓝伯特（Donald Lambert）所创造的，是一种重点研判股价偏离度的股市分析工具。 1、当CCI指标从下向上突破﹢100线而进入非常态区间时，表明股价脱离常态而进入异常波动阶段， 中短线应及时买入，如果有比较大的成交量配合，买入信号则更为可靠。 2、当CCI指标从上向下突破﹣100线而进入另一个非常态区间时，表明股价的盘整阶段已经结束， 将进入一个比较长的寻底过程，投资者应以持币观望为主。 CCI, default to 14 days |
| 13, TR、ATR指标     | http://wiki.mbalib.com/wiki/%E5%9D%87%E5%B9%85%E6%8C%87%E6%A0%87   均幅指标（Average True Ranger,ATR）均幅指标（ATR）是取一定时间周期内的股价波动幅度的移动平均值，主要用于研判买卖时机。 |
| 14, DMA指标     | http://wiki.mbalib.com/wiki/DMA   DMA指标（Different of Moving Average）又叫平行线差指标，是目前股市分析技术指标中的一种中短期指标，它常用于大盘指数和个股的研判。 DMA, difference of 10 and 50 moving average stock[‘dma’] |
| 15, DMI，+DI，-DI，DX，ADX，ADXR指标    | http://wiki.mbalib.com/wiki/DMI    动向指数Directional Movement Index,DMI）   http://wiki.mbalib.com/wiki/ADX   平均趋向指标（Average Directional Indicator，简称ADX）   http://wiki.mbalib.com/wiki/%E5%B9%B3%E5%9D%87%E6%96%B9%E5%90%91%E6%8C%87%E6%95%B0%E8%AF%84%E4%BC%B0   平均方向指数评估（ADXR）实际是今日ADX与前面某一日的ADX的平均值。ADXR在高位与ADX同步下滑，可以增加对ADX已经调头的尽早确认。 ADXR是ADX的附属产品，只能发出一种辅助和肯定的讯号，并非入市的指标，而只需同时配合动向指标(DMI)的趋势才可作出买卖策略。 在应用时，应以ADX为主，ADXR为辅。 |
| 16, TRIX，MATRIX指标     | http://wiki.mbalib.com/wiki/TRIX   TRIX指标又叫三重指数平滑移动平均指标（Triple Exponentially Smoothed Average） |
| 17, VR，MAVR指标     | http://wiki.mbalib.com/wiki/%E6%88%90%E4%BA%A4%E9%87%8F%E6%AF%94%E7%8E%87   成交量比率（Volumn Ratio，VR）（简称VR），是一项通过分析股价上升日成交额（或成交量，下同）与股价下降日成交额比值， 从而掌握市场买卖气势的中期技术指标。 |


### 使用方法
首先需要打开mysql服务，然后运行web文件夹下面的main.py


### 本地访问端口

> http://localhost:9999 股票系统 


### 股票系统设计

相关博客资料：
https://blog.csdn.net/freewebsys/category_9285317.html

数据分析清洗使用pandas，numpy。
http://pandas.pydata.org/

数据存储到磁盘上，使用Mysql数据库。存储股票数据。
https://pypi.python.org/pypi/mysqlclient

web框架使用tornado
http://www.tornadoweb.org/en/stable/

tornado web系统
http://docs.pythontab.com/tornado/introduction-to-tornado/


### 架构设计
全系使用python实现。因为都是python的类库，互相之间调用方便。
从数据抓取，数据处理，到数据展示数据运算都是python实现。

最终的数据都到前端展示出来。主要分为4个文件夹。

> jobs 抓取数据并存储实现类。
> 
> libs 通用工具类。
> 
> web 前端展示框架。
> 
> supervisor 进程管理工具。


### 应用部署

需要mysql数据库启动。项目放到/data/stock 目录。
```
CREATE DATABASE IF NOT EXISTS `stock_data` CHARACTER SET utf8 COLLATE utf8_general_ci;
```

使用 :

http://docs.sqlalchemy.org/en/latest/core/reflection.html

## 更新日志




