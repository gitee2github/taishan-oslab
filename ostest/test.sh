#!/bin/bash

ostest_dir=$(dirname $(realpath $0))
source $ostest_dir/utils.sh

totest=$1
standard=$2
logfile=/dev/null
if [ $# -gt 2 ]; then logfile=$3; fi
if [ ! -r $1 ] || [ ! -r $2 ]; then
	echo "Input test file or standard file not readable!."
	exit 0
fi

function do_test {

totalcount=0
exceptcount=0
passcount=0
errorcount=0

while read line
do
if [ "$line" = "" ] ; then
	continue
fi
totalcount=`expr $totalcount + 1`
echo $line|grep "^no" >/dev/null
if [ $? -eq 0 ] ; then
	except=`echo "$line"|awk -F \' '{print $2}'`
	grep -P "^$except" $totest >/dev/null
	if [ $? -eq 0 ] ; then
		echo "[EXCEPT] $except" >>$logfile
		exceptcount=`expr $exceptcount + 1`
	fi
else
	right=`echo "$line"|awk -F \' '{print $2}'`
	grep -P "^$right" $totest >/dev/null
	if [ $? -eq 0 ] ; then
		echo "[PASS] $right" >>$logfile
		passcount=`expr $passcount + 1`
	else
		echo "[MISS] $right " >>$logfile
		errorcount=`expr $errorcount + 1`
	fi
fi
done
blue PASSED:$passcount
blue TOTAL:$totalcount
if [ $totalcount = 0 ]; then return 0; fi
score=`expr 100 \* $passcount / $totalcount`
return $score
}

echo "totest=$totest" > $logfile
echo "standard=$standard" >> $logfile
sed 's/\t/\\\\t/g' $standard|sed 's/(/\\\\(/g' |sed 's/)/\\\\)/g' |sed 's/\^/\\\\\^/g' | do_test
exit $?
