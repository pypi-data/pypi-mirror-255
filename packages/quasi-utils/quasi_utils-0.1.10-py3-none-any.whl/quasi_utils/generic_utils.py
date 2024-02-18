import gzip
import pickle
import shutil


def uncompress(zip_path, file_path):
	with gzip.open(zip_path, 'rb') as f_in:
		with open(file_path, 'wb') as f_out:
			shutil.copyfileobj(f_in, f_out)


def text_to_pickle(text, direc):
	with open(direc, 'wb') as f:
		pickle.dump(text, f)


def pickle_to_text(direc):
	with open(direc, 'rb') as f:
		return pickle.load(f)


def colourise(text, colour, decorate=None, end_='\n'):
	_c = {'pink': '\033[95m', 'blue': '\033[94m', 'green': '\033[92m', 'yellow': '\033[93m', 'grey': '\033[97m',
	      'cyan': '\033[96m', 'end': '\033[0m', 'red': '\033[91m', 'underline': '\033[4m', 'bold': '\033[1m'}
	colour, end = _c[colour], _c['end']
	
	if decorate is not None:
		print(f'{_c[decorate]}{colour}{text}{end}', end=end_)
	else:
		print(f'{colour}{text}{end}', end=end_)
