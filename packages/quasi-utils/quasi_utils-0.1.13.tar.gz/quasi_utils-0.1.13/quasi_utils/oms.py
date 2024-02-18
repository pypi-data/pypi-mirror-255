import contextlib
import json
from datetime import datetime as dt

from quasi_utils.oms_utils import request, base, get_details, ticker_transform


class OMS:
	def __init__(self, config=None, data_dir=None):
		self.base_url = 'https://api.kite.trade'
		self.api_key, self.api_secret, self.access_token = get_details(config, data_dir)
		self.headers = {'X-Kite-Version': '3', 'User-Agent': 'Kiteconnect-python/4.2.0',
		                'Authorization': f'token {self.api_key}:{self.access_token}'}
	
	def ltp(self, tickers):
		if not isinstance(tickers, list):
			tickers = [tickers]
		tickers_ = {'i': tickers}
		
		res = request('GET', f'{self.base_url}/quote/ltp', data=tickers_, params=tickers_,
		              headers=self.headers)
		if res.get('status_code') == 403:
			return None
		
		return {ticker_.split(':')[-1]: ltp['last_price'] for ticker_, ltp in res['data'].items()}
	
	def quote(self, tickers):
		if not isinstance(tickers, list):
			tickers = [tickers]
		
		res = request('GET', f'{self.base_url}/quote', params={'i': tickers}, headers=self.headers)
		if res.get('status_code') == 403:
			return None
		
		return res['data']
	
	def get_user(self):
		res = request('GET', f'{self.base_url}/user/profile', headers=self.headers)
		if res.get('status_code') == 403:
			return None
		
		return res
	
	def get_cash_needed(self, ticker, action, price, qty, price_type, trade_type='MIS', variety='regular',
	                    exchange='NFO'):
		data = {'tradingsymbol': ticker, 'exchange': exchange, 'transaction_type': action, 'price': price,
		        'quantity': qty, 'variety': variety, 'order_type': price_type, 'product': trade_type}
		
		res = request('POST', f'{self.base_url}/margins/orders', headers=self.headers, _json=[data])
		if res.get('status_code') == 403:
			return None
		
		return res
	
	def get_cash_details(self, verbose=False):
		res = request('GET', f'{self.base_url}/user/margins/equity', headers=self.headers)
		if res.get('status_code') == 403:
			return None
		
		data = res['data']
		
		return data if verbose else {'cash': round(data['net'], 1), 'pnl': data['utilised']['m2m_realised']}
	
	def get_instruments(self, tickers=None, exchange='NSE'):
		res = request('GET', f'{self.base_url}/instruments/{exchange}', data=None, headers=self.headers)
		if type(res) is dict and res.get('status_code') == 403:
			return None
		
		res = res.decode('utf-8').strip().split('\n')
		header, rows, data = res[0], res[1:], {}
		
		if not tickers:
			for idx, row in enumerate(rows):
				row = row.split(',')
				expiry = dt.strptime(row[5], '%Y-%m-%d') if row[5] != '' else ''
				
				data[row[2]] = {'token': row[0], 'name': row[3][1:-1], 'expiry': expiry, 'strike': row[-6],
				                'ticker_type': row[-3], 'segment': row[-2]}
		
		data = dict(sorted(data.items(), key=lambda x: (x[1]['expiry'], x[1]['name'])))
		for ticker, ticker_data in data.items():
			if ticker_data['expiry'] != '':
				ticker_data['expiry'] = dt.strftime(ticker_data['expiry'], '%d %b %Y')
		
		return data
	
	def get_orders(self, status=None, mould=False):
		res = request('GET', f'{self.base_url}/orders', data=None, headers=self.headers)
		if res.get('status_code') == 403:
			return None
		
		orders = res['data']
		
		rename = {'order_timestamp': 'time', 'transaction_type': 'action', 'tradingsymbol': 'ticker',
		          'price': 'price', 'status': 'Status', 'product': 'trade_type',
		          'quantity': 'qty', 'filled_quantity': 'filled_quantity', 'pending_quantity': 'pending_quantity'}
		values_dict = {'NRML': 'OVERNIGHT', 'MIS': 'INTRADAY', 'COMPLETE': 'COMPLETED'}
		from_format, to_format = '%Y-%m-%d %H:%M:%S', '%d-%b-%Y %H:%M:%S'
		
		if status:
			orders = [order for order in orders if status in order['status']]
		
		new_orders = []
		
		for order in orders:
			with contextlib.suppress(TypeError):
				order['order_timestamp'] = dt.strptime(order['order_timestamp'], from_format).strftime(to_format)
				order['exchange_timestamp'] = dt.strptime(order['exchange_timestamp'], from_format).strftime(to_format)
			
			if mould:
				temp_orders = {}
				
				for k in order.keys():
					if k in rename:
						if k == 'price' and order['price'] == 0:
							temp_orders['price'] = round(order['average_price'], 2)
						elif k == 'product':
							temp_orders['trade_type'] = values_dict[order['product']]
						elif k == 'status':
							temp_orders['status'] = values_dict.get(order['status']) or order['status']
						elif k == 'tradingsymbol':
							temp_orders['ticker'] = ticker_transform(order['tradingsymbol'])
						elif k == 'transaction_type':
							temp_orders['action'] = order['transaction_type'].title()
						else:
							temp_orders[rename[k]] = order[k]
				
				new_orders.append(temp_orders)
		
		return new_orders if mould else orders
	
	def get_positions(self, only_open=False):
		res = request('GET', f'{self.base_url}/portfolio/positions', data=None, headers=self.headers)
		if res.get('status_code') == 403:
			return None
		
		positions = res['data']['net']
		
		return [position for position in positions if position['quantity']] if only_open else positions
	
	def place_order(self, ticker, action, price, qty, price_type, trade_type='MIS', variety='regular', exchange='NFO',
	                trigger_price=None, iceberg_legs=None, iceberg_quantity=None):
		data = {'tradingsymbol': ticker, 'exchange': exchange, 'transaction_type': action, 'price': price,
		        'quantity': qty, 'variety': variety, 'order_type': price_type, 'product': trade_type,
		        'trigger_price': trigger_price, 'iceberg_legs': iceberg_legs, 'iceberg_quantity': iceberg_quantity}
		
		res = request('POST', f'{self.base_url}/orders/{variety}', data=data, headers=self.headers)
		if res.get('status_code') == 403:
			return None
		
		return res
	
	def cancel_order(self, order_ids, variety='regular'):
		res = {}
		
		order_ids = [order_ids] if not isinstance(order_ids, list) else order_ids
		for _id in order_ids:
			res = request('DELETE', f'{self.base_url}/orders/{variety}/{_id}',
			              headers=self.headers, data=None)
			if res.get('status_code') == 403:
				return None
			
			res[_id] = res
		
		return res
	
	def modify_order(self, order_id=None, price=None, qty=None, price_type=None, variety='regular'):
		data = {}
		if price:
			data['price'] = price
		if qty:
			data['quantity'] = qty
		if price_type:
			data['order_type'] = price_type
		
		res = request('PUT', f'{self.base_url}/orders/{variety}/{order_id}',
		              data=data, headers=self.headers)
		if res.get('status_code') == 403:
			return None
		
		return res
	
	def place_gtt(self, buy_price, trade_type, qty, thresh=None, ticker=None, prefix=None, strike=None, exchange='NFO'):
		base_price, ticker = base(buy_price * thresh) if thresh else base(buy_price), ticker or f'{prefix}{strike}'
		
		condition = {'exchange': exchange, 'tradingsymbol': ticker, 'trigger_values': [base_price],
		             'last_price': self.ltp(f'{exchange}:{ticker}')[ticker]}
		orders = [{'exchange': exchange, 'tradingsymbol': ticker, 'transaction_type': 'SELL', 'quantity': qty,
		           'order_type': 'LIMIT', 'product': trade_type, 'price': base(base_price * 0.98)}]
		data = {'condition': json.dumps(condition), 'orders': json.dumps(orders), 'type': 'single'}
		
		res = request('POST', f'{self.base_url}/gtt/triggers', data=data, headers=self.headers)
		if res.get('status_code') == 403:
			return None
		
		return res
	
	def delete_gtt_orders(self, ids):
		if ids == 'all':
			for order in self.fetch_gtt_orders():
				res = request('DELETE', f'{self.base_url}/gtt/triggers/{order["id"]}',
				              headers=self.headers, data=None)
				if res.get('status_code') == 403:
					return None
		else:
			if not isinstance(ids, list):
				ids = [ids]
			
			for id_ in ids:
				res = request('DELETE', f'{self.base_url}/gtt/triggers/{id_}',
				              headers=self.headers, data=None)
				if res.get('status_code') == 403:
					return None
	
	def fetch_gtt_orders(self):
		res = request('GET', f'{self.base_url}/gtt/triggers', headers=self.headers, data=None)
		if res.get('status_code') == 403:
			return None
		
		return res['data']


if __name__ == '__main__':
	obj = OMS(config='zerodha', data_dir='../../backend/oms/execute/data')
	# print(obj.ltp(['NSE:RELIANCE']))
	# print(obj.get_cash_details(verbose=True))
	# print(json.dumps(obj.get_orders(mould=True,), indent=2))
	#
	# print(obj.cancel_order(order_ids='231004203428841', variety='amo'))
	# print(obj.modify_order(order_id='231004203471297', price=12.9, qty=500, price_type='LIMIT', variety='amo'))
	print(obj.get_instruments(exchange='NFO'))
	# print(obj.get_user()['data'])
