package main

import (
	"fmt"
	"net"
	"runtime"
	"time"
)

func main() {
	fmt.Println("=== Luckfox Network Test Program ===")
	fmt.Println("hello, evfwt")
	fmt.Println()

	// 显示系统信息
	fmt.Printf("OS: %s\n", runtime.GOOS)
	fmt.Printf("Architecture: %s\n", runtime.GOARCH)
	fmt.Printf("CPU Count: %d\n", runtime.NumCPU())
	fmt.Println()

	// 获取网络接口信息
	fmt.Println("Network Interfaces:")
	interfaces, err := net.Interfaces()
	if err != nil {
		fmt.Printf("Error getting interfaces: %v\n", err)
		return
	}

	for _, iface := range interfaces {
		fmt.Printf("\n[%s]\n", iface.Name)
		fmt.Printf("  MAC: %s\n", iface.HardwareAddr)
		fmt.Printf("  MTU: %d\n", iface.MTU)
		fmt.Printf("  Flags: %v\n", iface.Flags)

		// 获取IP地址
		addrs, err := iface.Addrs()
		if err != nil {
			fmt.Printf("  Error getting addresses: %v\n", err)
			continue
		}

		for _, addr := range addrs {
			fmt.Printf("  IP: %s\n", addr.String())
		}
	}

	// 测试网络连接
	fmt.Println("\n=== Testing Network Connectivity ===")
	testHosts := []string{
		"www.baidu.com:80",
		"8.8.8.8:53",
		"114.114.114.114:53",
	}

	for _, host := range testHosts {
		fmt.Printf("Testing %s ... ", host)
		conn, err := net.DialTimeout("tcp", host, 3*time.Second)
		if err != nil {
			fmt.Printf("FAIL: %v\n", err)
		} else {
			fmt.Printf("OK\n")
			conn.Close()
		}
	}

	fmt.Println("\n=== Program completed successfully ===")
}
