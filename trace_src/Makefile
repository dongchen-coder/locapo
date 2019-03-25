# objects := $(patsubst %.c,%.o,$(wildcard *.c))

# foo : $(objects)
# 	clang++ -o foo $(objects)

SRC=$(wildcard *.cpp)

test: $(SRC)
	clang++ -g -o $@ $^