#! /bin/bash

DEFS=
target=
test_dir=
log=/dev/null
timeout_sec=10

usage()
{
	echo
	echo build.sh
	echo usage: build.sh [options] target
	echo Options:
	echo " -h		Get some help."
	echo " -p PROGRAM"
	echo "		Load the exact PROTEST user program while the test."
	echo " -f FUNCTION"
	echo "		Call the excat FUNCTION while the test."
	echo " -l logfile"
	echo "		Write the log to the logfile"
	echo " -t testcase dir"
	echo "		The dir with testcase module."
	echo " -T timeout_sec"
	echo "		Set timeout seconds, default is 10 seconds."
	exit 1
}

function check_ret {
	if [ $1 -eq 124 ]; then
		red "Time exceeded when building your project. Did you add the code running gxemul in your Makefile?"
		exit 124
	fi
	if [ $1 -ne 0 ]; then
		echo "Compile Error!"
		exit $1
	fi
}

function do_build {
	echo "Begin build at `date`"
	echo "Cleanning the project................."
	echo
	docker run --rm --mount type=bind,src="$target",dst=/usr/src/workdir \
		-w /usr/src/workdir \
		os2022-test timeout $timeout_sec bash -c "make clean"
	check_ret $?

	echo
	echo "Building the project.................."
	echo
	if [ $test_dir ]; then
		test_dir_in_docker=/usr/src/testdir$RANDOM
		docker run --rm --mount type=bind,src="$target",dst=/usr/src/workdir \
			--mount type=bind,src="$test_dir",dst=$test_dir_in_docker,readonly \
			-w /usr/src/workdir \
			os2022-test timeout $timeout_sec make "DEFS=$DEFS" "test_dir=$test_dir_in_docker" vmlinux
		ret=$?
	else
		docker run --rm --mount type=bind,src="$target",dst=/usr/src/workdir \
			-w /usr/src/workdir \
			os2022-test timeout $timeout_sec make "DEFS=$DEFS" vmlinux
		ret=$?
	fi
	check_ret $ret
	echo
	echo "End build at `date`"
	return $ret
}

[ $# -eq 0 ] && usage

while :
do
	case $1 in
		-h)
			usage
			;;
		-f)
			shift
			DEFS=$DEFS' -DFTEST='$1
			shift
			;;
		-p)
			shift
			DEFS=$DEFS' -DPTEST='$1
			shift
			;;
		-t)
			shift
			test_dir=`realpath $1`
			shift
			;;
		-l)
			shift
			log=$1
			shift
			;;
		-T)
			shift
			timeout_sec=$1
			shift
			;;
		*)
			break
			;;
	esac
done

if [ ! $1 ] ; then
	echo "Please specify the target directory."
	exit 1
fi

target=`realpath $1`
cd $target
do_build |& tee $log	# build and copy all stdout/stderr output to logfile
exit $PIPESTATUS
