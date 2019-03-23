for i in *.cpp
do
    echo "clang++   $i -o ${i%.c}.out"
    clang++   $i -o ${i%.c}.o
    # gcc -g3 -o3 "$i" -o "${i%.c}.out"
done
