from threading import Thread
import os
import sys
import subprocess
import shlex


class DummyObject:
	pass


# UTILITIES COPIED FROM BLASTER SERVER CODE
def parse_cmd_line_arguments():
	from sys import argv
	args = []
	args_map = {}
	i = 0
	num_args = len(argv)
	while(i < num_args):
		arg = argv[i]
		if(arg.startswith("-")):
			if("=" in arg):
				key, val = arg.split("=", 1)
				args_map[key.lstrip("-")] = val
			else:
				next_arg = True
				if(i + 1 < num_args and not argv[i + 1].startswith("-")):
					next_arg = argv[i + 1]
					i += 1
				args_map[arg.lstrip("-")] = next_arg
		else:
			args.append(arg)

		i += 1
	return args, args_map


# PARSE COMMAND LINE ARGUMENTS BY DEFAULT
CommandLineArgs, CommandLineNamedArgs = parse_cmd_line_arguments()


def run_shell(cmd, output_parser=None, shell=False, max_buf=5000, fail=True, state=None, env=None, **kwargs):

	state = state if state is not None else DummyObject()
	state.total_output = ""
	state.total_err = ""

	# keep parsing output
	def process_output(proc_out, proc_in):
		while(state.is_running):
			_out = proc_out.read(1)
			if(not _out):
				break
			_out = _out.decode('utf-8', 'ignore')
			# add to our input
			state.total_output += _out
			if(len(state.total_output) > 2 * max_buf):
				state.total_output = state.total_output[-max_buf:]

			if(output_parser):
				# parse the output and if it returns something
				# we write that to input file(generally stdin)
				_inp = output_parser(state.total_output, state.total_err)
				if(_inp):
					proc_in.write(_inp)
			else:
				print(_out, end="", flush=True)

	def process_error(proc_err, proc_in):
		while(state.is_running):
			_err = proc_err.read(1)
			if(not _err):
				break
			_err = _err.decode('utf-8', 'ignore')
			# add to our input
			state.total_err += _err
			if(len(state.total_err) > 2 * max_buf):
				state.total_err = state.total_err[-max_buf:]
			if(output_parser):
				# parse the output and if it returns something
				# we write that to input file(generally stdin)
				_inp = output_parser(state.total_output, state.total_err)
				if(_inp):
					proc_in.write(_inp)
			else:
				print(_err, end="", flush=True)

	if(isinstance(cmd, str) and not shell):
		cmd = shlex.split(cmd)

	dup_stdin = os.dup(sys.stdin.fileno()) if shell else subprocess.PIPE
	_env = os.environ.copy()
	if(env):
		_env.update(env)

	state.proc = proc = subprocess.Popen(
		cmd,
		stdin=dup_stdin,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		shell=shell,
		env=_env,
		**kwargs
	)
	state.is_running = True

	# process output reader
	output_parser_thread = Thread(
		target=process_output,
		args=(
			proc.stdout,
			proc.stdin
		)
	)
	# process err reader
	err_parser_thread = Thread(
		target=process_error,
		args=(
			proc.stderr,
			proc.stdin
		)
	)
	output_parser_thread.start()
	err_parser_thread.start()

	os.close(dup_stdin) if dup_stdin != subprocess.PIPE else None

	# just keep printing error
	# wait for process to terminate
	ret_code = proc.wait()
	state.return_code = ret_code
	state.is_running = False
	output_parser_thread.join()
	err_parser_thread.join()
	state.proc = None
	if(ret_code and fail):
		raise Exception(f"Non zero return code :{ret_code}")
	return state


def nsplit(_str, delimiter, n):
	parts = _str.split(delimiter, n)
	for i in range(n + 1 - len(parts)):
		parts.append(None)
	return parts
