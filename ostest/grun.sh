#!/bin/bash

timeout=10
cpu=R3000
gxemul=/OSLAB/gxemul
machine=testmips
mem=64
out=
fs=0
img=
debugflag=
expectfile=/home/git/ostest/expect.test

usage()
{
	echo
	echo "run.sh"
	echo "Usage: run.sh [Options] img [outputfile]"
	echo
	echo "Options:"
	echo " -h	 get some help."
	echo " -E t      try to emulate machine type t."
	echo " -C x      try to emulate a specific CPU."
	echo " -M m      emulate m MBs of physical RAM."
	echo " -t timeout	the maximum time that the emulator running."
	echo " -m 	 manual mode."
	echo " -v 	 debug mode."
	echo " -f fs 	 fs.img"
	echo " -e expect.test	 the specific expect file to use."
	echo
	echo " img:"
	echo "		The elf file to load."
	echo " outputfile:"
	echo "		Specify the output file."
	exit 1
}

[ $# -eq 0 ] && usage

while :
do
	case $1 in
		-h)
			usage
			;;
		-E)
			shift
			machine=$1
			shift
			;;
		-C)
			shift
			cpu=$1
			shift
			;;
		-M)
			shift
			mem=$1
			shift
			;;
		-t)
			shift
			timeout=$1
			shift
			;;
		-m)
			timeout=0
			out=/dev/stdout
			shift
			;;
		-v)
			timeout=0
			out=/dev/stdout
			debugflag="-V"
			shift
			;;

		-f)
			shift
			fs=$1
			shift
			;;

		-e)
			shift
			expectfile=$1
			shift
			;;
		*)
			break
			;;
	esac
done


if [ $1 ] ; then
	img=$1
else
	echo "Please sepcify the imgine of the kernel!"
	exit 1
fi

shift
if [ $1 ] ; then
	out=$1
fi

if [ $timeout -ne 0 ];then
ulimit -t $timeout
fi

expect $expectfile $fs $img >$out
