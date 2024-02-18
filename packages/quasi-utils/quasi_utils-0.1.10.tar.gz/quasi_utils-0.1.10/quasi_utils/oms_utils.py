import json
import os
from configparser import ConfigParser
from datetime import datetime as dt
from zoneinfo import ZoneInfo

import boto3
import requests as r
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from quasi_utils.aws_utils import decrypt

urllib3.disable_warnings(InsecureRequestWarning)


def request(method, url, headers, data=None, params=None, _json=None, timeout=5, verify=False, allow_redirects=True):
	res = r.request(method, url, data=data, headers=headers, json=_json, params=params,
	                verify=verify, allow_redirects=allow_redirects, timeout=timeout, proxies=None)
	
	if res.status_code == 403:
		return {'status_code': 403}
	
	try:
		return json.loads(res.content.decode('utf8'))
	except json.decoder.JSONDecodeError:
		return res.content


def base(price, rounder=0.05, precision=2):
	return round(rounder * round(float(price) / rounder), precision)


def get_details(config_name, data_dir):
	config = ConfigParser()
	config.read(os.path.join(data_dir, 'config.ini'))
	z = config[config_name]
	api_key, api_secret, access_token = decrypt(z['api_key']), decrypt(z['api_secret']), decrypt(z['access_token'])
	
	return api_key, api_secret, access_token


def get_trade_number(orders):
	trade_num = 0
	
	if not orders:
		return trade_num
	
	for order in orders:
		if order['transaction_type'] == 'SELL':
			trade_num += 1
	
	return trade_num


def check_global_loss(o, global_stop_loss):
	margin = o.get_cash_details(verbose=True)
	pnl = margin['utilised']['m2m_realised']
	
	if pnl < 0:
		cash = margin['available']
		total_cash = cash['opening_balance'] + cash['intraday_payin'] + cash['collateral']
		
		return False if abs(pnl) > (total_cash * global_stop_loss) else margin['net']
	
	return margin['net']


def get_total_cash(o):
	margin = o.get_cash_details(verbose=True)
	cash = margin['available']
	
	return cash['opening_balance'] + cash['intraday_payin'] + cash['collateral']


def get_oms_session():
	s3 = boto3.client('s3')
	file_obj = s3.get_object(Bucket=os.environ['SESSION_BUCKET'], Key='session.json')
	
	return file_obj['Body'].read().decode('utf-8')


def ticker_transform(ticker):
	months = {'1': 'JAN', '2': 'FEB', '3': 'MAR', '4': 'APR', '5': 'MAY', '6': 'JUN', '7': 'JUL', '8': 'AUG',
	          '9': 'SEP', 'O': 'OCT', 'N': 'NOV', 'D': 'DEC'}
	date_modifier = {'01': 'st', '02': 'nd', '03': 'rd', '21': 'st', '22': 'nd', '23': 'rd'}
	
	today = dt.now(tz=ZoneInfo('Asia/Kolkata'))
	cur_month, cur_year = today.strftime('%b').upper(), today.strftime('%y')
	_ticker = ticker.split(cur_year)
	ticker, data = _ticker[0], ticker[len(_ticker[0]) + 2:]
	
	if any([x in data for x in months.values()]):
		month, date, strike = data[:3], '', data[3:]
		date_modified = ''
	else:
		month, date, strike = months[data[0]], data[1:3], data[3:]
		date_modified = date_modifier.get(date, 'th')
	
	return f'{ticker} {date}{date_modified}{month} {strike}'


def round_down(x, nearest_num=50):
	return x if x % nearest_num == 0 else x - (x % nearest_num)


def round_up(x, nearest_num=50):
	return x if x % nearest_num == 0 else x + (nearest_num - (x % nearest_num))
