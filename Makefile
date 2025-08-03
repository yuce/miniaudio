
.PHONY: clean

miniaudio.so: miniaudio.c
	cc -s -O3 -shared -fpic -Wall -Wextra -Wpedantic -o $@ $<

clean:
	rm -f miniaudio.so

