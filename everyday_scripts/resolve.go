package main

import (
	"fmt"
	"net"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: go-dig <hostname>")
		return
	}

	hostname := os.Args[1]

	// Perform an A record lookup
	ips, err := net.LookupIP(hostname)
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Printf("A records for %s: ", hostname)
	ip_list := ""
	for _, ip := range ips {
		ip_list += ip.String() + " "
	}

	fmt.Println(ip_list)

	// Perform an NS record lookup
	nameservers, err := net.LookupNS(hostname)
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Printf("\nNS records for %s: ", hostname)
	ns_list := ""
	for _, ns := range nameservers {
		ns_list += ns.Host + " "
	}
	fmt.Println(ns_list)
}
