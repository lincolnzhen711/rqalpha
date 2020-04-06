from rqalpha.api import *
from strategies.utils import *
import talib
init_rqdata()
# pool = ['A', 'AG', 'AL', 'AU', 'C', 'CF', 'CS', 'CU', 'FG', 'I', 'J', 'JD', 'JM', 'L', 'M','MA', 'NI', 'OI', 'P', 'PP', 'RB', 'RM', 'RU', 'SR', 'TA', 'V', 'Y', 'ZC', 'ZN']
pool = ['A888']
# result = all_instruments(type ='Future')
# filtered = result[['listed_date','underlying_symbol']]
# filtered = filtered.loc[filtered['listed_date'] != '0000-00-00']
# # dates = filtered.groupby('underlying_symbol', sort=False).apply(lambda x: x.sort_values('listed_date', ascending=True).first()).reset_index(drop=True)
# dates = filtered.sort_values('listed_date', ascending=True).groupby('underlying_symbol', as_index=False).first()
# print(dates['underlying_symbol'].values.tolist())


whole_future = ['A', 'AG', 'AL', 'AP', 'AU', 'B', 'BB', 'BU', 'C', 'CF', 'CJ', 'CS', 'CU', 'CY', 'EB', 'EG', 'ER', 'FB', 'FG', 'FU', 'HC', 'I', 'IC', 'IF', 'IH', 'J', 'JD', 'JM', 'JR', 'L', 'LR', 'M', 'MA', 'ME', 'NI', 'NR', 'OI', 'P', 'PB', 'PG', 'PM', 'PP', 'RB', 'RI', 'RM', 'RO', 'RR', 'RS', 'RU', 'S', 'SA', 'SC', 'SF', 'SM', 'SN', 'SP', 'SR', 'SS', 'T', 'TA', 'TC', 'TF', 'TS', 'UR', 'V', 'WH', 'WR', 'WS', 'WT', 'Y', 'ZC', 'ZN']
whole_listed_date = ['2002-03-15', '2012-05-10', '1999-01-04', '2017-12-22', '2008-01-09', '2004-12-22', '2013-12-06', '2013-10-09', '2004-09-22', '2004-06-01', '2019-04-30', '2014-12-19', '1999-01-04', '2017-08-18', '2019-09-26', '2018-12-10', '2009-04-20', '2013-12-06', '2012-12-03', '2004-08-25', '2014-03-21', '2013-10-18', '2015-04-16', '2010-04-16', '2015-04-16', '2011-04-15', '2013-11-08', '2013-03-22', '2013-11-18', '2007-07-31', '2014-07-08', '2000-07-17', '2014-06-17', '2011-10-28', '2015-03-27', '2019-08-12', '2012-07-16', '2007-10-29', '2011-03-24', '2020-03-30', '2012-01-17', '2014-02-28', '2009-03-27', '2012-07-24', '2012-12-28', '2007-06-08', '2019-08-16', '2012-12-28', '1999-01-04', '1999-01-04', '2019-12-06', '2018-03-26', '2014-08-08', '2014-08-08', '2015-03-27', '2018-11-27', '2006-01-06', '2019-09-25', '2015-03-20', '2006-12-18', '2013-09-26', '2013-09-06', '2018-08-17', '2019-08-09', '2009-05-25', '2012-07-24', '2009-03-27', '2003-03-28', '1999-01-04', '2006-01-09', '2015-05-18', '2007-03-26']

pool = ['RB2010']
prices = get_price('RB2010', '2020-03-30', '2020-04-03', '1d', 'close')
short_avg = talib.SMA(prices, 5)
print(short_avg[-1])
