SRC := bulmodule.c

CFLAGS := -I/opt/homebrew/opt/python@3.11/Frameworks/Python.framework/Versions/3.11/include/python3.11 -I/opt/homebrew/opt/python@3.11/Frameworks/Python.framework/Versions/3.11/include/python3.11 -Wsign-compare -Wunreachable-code -fno-common -dynamic -DNDEBUG -g -fwrapv -O3 -Wall -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX14.sdk
CFLAGS += -undefined dynamic_lookup

all:
	$(CC) $(CFLAGS) -shared -o spam.so $(SRC)
