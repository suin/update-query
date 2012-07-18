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

"""
Initialize with new token
"""
def init(args):
	if args.name is None:
		args.name = get_new_file_name("Environment name")

	if environment_exists(args.name):
		print "Environment '%s' already exists." % (args.name)
		print "Please try other name."
		exit(1)

	now = time.strftime('%Y%m%d_%H%M')
	filename = "%s~%s.apply_token" % (now, args.name)
	
	if os.path.exists(filename):
		print "Token %s already exists" % (filename)
		exit(1)
	
	file = open(filename, 'w')
	file.write('-- apply token for "%s"' % (args.name))
	file.close()
	print "New token '%s' was created." % (filename)

"""
Create new file
"""
def create(args):
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

"""
List up all tokens
"""
def tokens(args):
	for token in glob.glob('*.apply_token'):
		print "  " + token

"""
fetch new file name via interactive
"""
def get_new_file_name(question, error_message = None):

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

"""
Concatenate all update queries together
"""
def apply(args):

	environments = get_all_environment_names()
	
	if len(environments) < 1:
		print "Sorry, there is no environments."
		print ""
		print "If you use this first, initialize environment tokens:"
		print "    $ %s init" % (os.path.basename(__file__))
		exit(1)
	
	if args.name is None:
		print "We know these environments:"
		for name in environments:
			print "  * " + name
		args.name = fetch_environment_name()
	
	if environment_exists(args.name) is False:
		print "Sorry, such an environment not found: %s" % (args.name)
		exit(1)
	
	environment_last_apply = get_environment_last_apply_datetime(args.name)
	
	candidates = glob.glob('*.sql')
	candidates.sort()
	candidates = [candidate for candidate in candidates if re.match(r'^[0-9]{8}_[0-9]{4}_.+\.sql$', candidate)]

	apply_query_files = []

	for candidate in candidates:
		candiadte_datetime = ''.join(candidate.split('_', 2)[0:2])
		
		if candiadte_datetime > environment_last_apply:
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

	reflesh_token(args.name)
	
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
	

"""
Determine if environment name exists
"""
def environment_exists(name):
	return name in get_all_environment_names()

"""
Return known environment names
"""
def get_all_environment_names():
	environment_names = []
	for name in glob.glob('*.apply_token'):
		environment_name = name.split('~')[1].split('.apply_token')[0]
		environment_names.append(environment_name)
	return environment_names

def get_environment_last_apply_datetime(name):
	for filename in glob.glob('*.apply_token'):
		environment_name = filename.split('~')[1].split('.apply_token')[0]
		if environment_name == name:
			return filename.split('~')[0].replace('_', '')
	return False

"""
Fetch environment name via interactive
"""
def fetch_environment_name():
	environment_name = raw_input("Environment name: ")
	
	if environment_name == '':
		environment_name = fetch_environment_name()
	
	return environment_name

"""

"""
def reflesh_token(name):
	for filename in glob.glob('*.apply_token'):
		environment_name = filename.split('~')[1].split('.apply_token')[0]
		if environment_name == name:
			info = filename.split('~')
			info[0] = time.strftime('%Y%m%d_%H%M')
			new_filename = '~'.join(info)
			os.rename(filename, new_filename)
			print "Token renamed %s -> %s" % (filename, new_filename)
	return False

"""
Main
"""
def main():
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
