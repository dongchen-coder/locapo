for i in ./*hist.txt
do
    fname=`basename $i`
    echo $fname
    ./main $fname -a 0.5 --osl -s 1
# gcc -g3 -o3 "$i" -o "${i%.c}.out"
done
