package main

import "unsafe"

func main() {
	msg := "hello, evfwt\n"

	// Direct syscall to write - no fmt package
	_, _ = write(1, unsafe.Pointer(&[]byte(msg)[0]), len(msg))
}

// write syscall for ARM Linux
func write(fd int, p unsafe.Pointer, n int) (int, error) {
	r1, _, err := syscall(4, uintptr(fd), uintptr(p), uintptr(n))
	if err != 0 {
		return int(r1), error(err)
	}
	return int(r1), nil
}

// syscall for ARM
func syscall(trap, a1, a2, a3 uintptr) (r1, r2 uintptr, err uintptr)

// Assembly implementation would go in a .s file, but we'll use a simpler approach
