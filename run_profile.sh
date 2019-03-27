todo_array=($(find ./bin/ -type f))

for i in "${todo_array[@]}"
do
    o=${i#./bin/}
	echo $o
	./$i > ./poly_trace_rll_maxCLSize/${o}_rll_maxCLSize.txt &
    
	NPROC=$(($NPROC+1))
    if [ "$NPROC" -ge 4 ]; then
        wait
        NPROC=0
    fi
done
