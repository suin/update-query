#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Update query management tool
#

import os
import argparse
import commands
import sys
import re
import time
import glob

class TokenCollection:
	"""
	Token collection object
	"""
	def __init__(self, tokens = []):
		"""
		Returns new TokenCollection object
		"""
		self.tokens = tokens
		self.index = 0
	
	def __len__(self):
		return len(self.tokens)
	
	def __iter__(self):
		"""
		Returns this instance
		"""
		return self
	
	def append(self, token):
		"""
		Appends a token object to this collection
		"""
		self.tokens.append(token)
		return self
	
	def next(self):
		"""
		Returns current token object
		"""
		if self.index >= len(self.tokens):
			self.index = 0
			raise StopIteration
		result = self.tokens[self.index]
		self.index += 1
		return result
	
	def has(self, environment_name):
		"""
		Determines if this has the token
		"""
		if self.find(environment_name) is False:
			return False
		else:
			return True
	
	def find(self, environment_name):
		"""
		Returns token object
		"""
		for token in self.tokens:
			if token.get_environment_name() == environment_name:
				return token
		return False


class Token:
	"""
	Token file object
	"""
	def __init__(self, filename):
		"""
		Returns new Token object
		"""
		if self._isValidFilename(filename) is False:
			raise Exception("Token file name is not valid: %s" % filename)
		self.filename = filename
		self.original_filename = filename
	
	def get_filename(self):
		"""
		Returns file name
		"""
		return self.filename
	
	def get_original_filename(self):
		"""
		Returns original file name
		"""
		return self.original_filename
	
	def get_datetime(self):
		"""
		Returns datetime
		"""
		return self.filename.split('~')[0].replace('_', '')
	
	def get_environment_name(self):
		"""
		Returns environment name
		"""
		return self.filename.split('~')[1].split('.')[0]
	
	def log(self, message):
		"""
		Logs message
		"""
		now = time.strftime('%Y-%m-%d %H:%M:%S')
		file = open(self.filename, 'a')
		file.write("-- [%s] %s\n" % (now, message))
	
	def update_time(self):
		"""
		Updates time
		"""
		info = self.filename.split('~')
		info[0] = time.strftime('%Y%m%d_%H%M')
		new_filename = '~'.join(info)
		self._rename(new_filename)

	@staticmethod
	def _isValidFilename(filename):
		"""
		Determines if the file name is valid
		"""
		if re.match(r'^[0-9]{8}_[0-9]{4}~.+\.apply_token$', filename):
			return True
		else:
			return False
	
	def _rename(self, new):
		"""
		Renames filename
		"""
		old = self.filename
		os.rename(old, new)
		self.original_filename = old
		self.filename = new

def init(args):
	"""
	Initialize with new token
	"""
	if args.name is None:
		args.name = get_new_file_name("Environment name")

	tokens = get_all_tokens()

	if tokens.has(args.name):
		print "Environment '%s' already exists." % (args.name)
		print "Please try other name."
		exit(1)

	now = time.strftime('%Y%m%d_%H%M')
	filename = "%s~%s.apply_token" % (now, args.name)
	
	if os.path.exists(filename):
		print "Token %s already exists" % (filename)
		exit(1)
	
	file = open(filename, 'w')
	file.write("-- [%s] update-query create '%s'\n" % (time.strftime('%Y-%m-%d %H:%M:%S'), args.name))
	file.close()
	print "New token '%s' was created." % (filename)


def create(args):
	"""
	Create new file
	"""
	if args.name is None:
		args.name = get_new_file_name("New file name")
	
	now = time.strftime('%Y%m%d_%H%M')
	filename = "%s_%s.sql" % (now, args.name)
	
	if os.path.exists(filename):
		print "File %s already exists" % (filename)
		exit(1)
	
	file = open(filename, 'w')
	file.write('')
	file.close()
	print "New file '%s' was created." % (filename)
	print "Please edit it."

def tokens(args):
	"""
	List up all tokens
	"""
	tokens = get_all_tokens()
	for token in tokens:
		print "  " + token.get_filename()

def get_new_file_name(question, error_message = None):
	"""
	fetch new file name via interactive
	"""

	if error_message:
		message = "%s (%s): " % (question, error_message)
	else:
		message = "%s: " % (question)

	new_file_name = raw_input(message)
	new_file_name = new_file_name.replace(' ', '_')
	
	if new_file_name[-4:].lower() == '.sql':
		new_file_name = get_new_file_name(question = question, error_message = "don't end with .sql")
	
	if re.match(r'^[a-zA-Z0-9_]+$', new_file_name) is None:
		new_file_name = get_new_file_name(question = question, error_message = "you can use alphabet, number, space and underscore")

	return new_file_name

def apply(args):
	"""
	Concatenate all update queries together
	"""
	tokens = get_all_tokens()
	
	if len(tokens) < 1:
		print "Sorry, there is no environments."
		print ""
		print "If you use this first, initialize environment tokens:"
		print "    $ %s init" % (os.path.basename(__file__))
		exit(1)
	
	if args.name is None:
		print "We know these environments:"
		for token in tokens:
			print "  * " + token.get_environment_name()
		args.name = fetch_environment_name()
	
	if tokens.has(args.name) is False:
		print "Sorry, such an environment not found: %s" % (args.name)
		exit(1)
	
	selected_token = tokens.find(args.name)
	
	candidates = glob.glob('*.sql')
	candidates.sort()
	candidates = [candidate for candidate in candidates if re.match(r'^[0-9]{8}_[0-9]{4}_.+\.sql$', candidate)]

	apply_query_files = []

	for candidate in candidates:
		candiadte_datetime = ''.join(candidate.split('_', 2)[0:2])
		
		if candiadte_datetime > selected_token.get_datetime():
			apply_query_files.append(candidate)
	
	if len(apply_query_files) < 1:
		print "There is no update for %s" % (args.name)
		exit()
	
	contents = []
	
	for filename in apply_query_files:
		file = open(filename, 'r')
		content = "-- %(filename)s\n%(contents)s" % {'filename': filename, 'contents': file.read().strip()}
		file.close()
		contents.append(content)

	patch_contents = "\n\n".join(contents)
	patch_filename = 'patch.%s.%s.sql' % (args.name, time.strftime('%Y%m%d_%H%M'))

	if os.path.exists(patch_filename):
		print "Patch file already exists: %s" % (patch_filename)
		exit(1)

	for filename in apply_query_files:
		selected_token.log('update-query cat "%s" >> "%s"' % (filename, patch_filename))

	selected_token.update_time()
	original_filename = selected_token.get_original_filename()
	new_filename = selected_token.get_filename()
	selected_token.log('update-query mv %s %s' % (original_filename, new_filename))
	print "Token renamed %s -> %s" % (original_filename, new_filename)
	
	file = open(patch_filename, 'w')
	file.write(patch_contents)
	file.close()
	
	print "------------------------------"
	print "Patch file was created!"
	print ""
	print "  * " + patch_filename
	print ""
	print "Please apply the patch update queries in above file to the SQL server."
	print "After you apply, please delete patch file from here."


def get_all_tokens():
	"""
	Returns all tokens
	"""
	tokens = TokenCollection()
	for name in glob.glob('*.apply_token'):
		tokens.append(Token(name))
	return tokens

def fetch_environment_name():
	"""
	Fetch environment name via interactive
	"""
	environment_name = raw_input("Environment name: ")
	
	if environment_name == '':
		environment_name = fetch_environment_name()
	
	return environment_name

def main():
	"""
	Main
	"""
	parser = argparse.ArgumentParser(description='Update query management tool')

	subparsers = parser.add_subparsers(title='commands', metavar='command')

	parser_init = subparsers.add_parser('init', help='initialize with new token')
	parser_init.set_defaults(func=init)
	parser_init.add_argument('name', type=str, nargs='?', help='environment name', default=None)

	parser_create = subparsers.add_parser('create', help='create new update query')
	parser_create.set_defaults(func=create)
	parser_create.add_argument('name', type=str, nargs='?', help='new file name', default=None)

	parser_apply = subparsers.add_parser('apply', help='concatenate update queries together and create a patch')
	parser_apply.set_defaults(func=apply)
	parser_apply.add_argument('name', type=str, nargs='?', help='environment name to apply update queries', default=None)

	parser_tokens = subparsers.add_parser('tokens', help='list up all tokens')
	parser_tokens.set_defaults(func=tokens)

	args = parser.parse_args()
	
	args.func(args)

if __name__ == "__main__":
	main()
