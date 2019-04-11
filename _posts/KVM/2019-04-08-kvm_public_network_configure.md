---
layout: post
title: "KVM网络配置之公网"
date: 2019-04-08 17:38:06
categories: 技术
tags: KVM Linux
---

[上篇](/技术/2019/04/02/kvm_private_network_configure.html)记录了kvm私有网络的相关配置，这篇记录一下如何给虚拟机配置公网。
具体网络拓扑图参考[上篇](/技术/2019/04/02/kvm_private_network_configure.html)，`router1`模拟分配公网IP地址。192.168.11.0网段模拟为公网IP地址段。

## 为kvm虚拟机绑定IP地址

以vm1为例为其分配192.168.11.14。

首先查看vm1的配置文件

```xml
...
    <interface type='bridge'>
      <mac address='52:54:00:27:c7:f3'/>
      <source bridge='br0'/>
      <target dev='vnet0'/>
      <model type='rtl8139'/>
      <alias name='net0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
...
```

通过挂载虚拟机img镜像方式修改vm1的`/etc/network/interfaces`，将interface改为静态ip。我这里的虚拟机系统为ubuntu10.04，其他系统请配置相应的网络管理工具。

```conf
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
auto ens3
iface ens3 inet static
address 192.168.11.14
netmask 255.255.255.0
gateway 192.168.11.1
dns-nameservers 192.168.11.1
```

为了防止用户随意更改ip地址，使用`ebtables`对网桥br0添加规则

```bash
ebtables -t nat -N vm1-vnet0-I
ebtables -t nat -N vm1-vnet0-O

ebtables -t nat -A vm1-vnet0-I -s ! 52:54:00:27:c7:f3 -j DROP
ebtables -t nat -A vm1-vnet0-I -p IPv4 --ip-src 192.168.11.14 -j ACCEPT
ebtables -t nat -A vm1-vnet0-I -p ARP --arp-ip-src 192.168.11.14 -j ACCEPT
ebtables -t nat -A vm1-vnet0-I -p ARP --arp-mac-src ! 52:54:00:27:c7:f3 -j DROP
ebtables -t nat -A vm1-vnet0-I -p ARP --arp-op Request -j ACCEPT
ebtables -t nat -A vm1-vnet0-I -p ARP --arp-op Reply -j ACCEPT
ebtables -t nat -A vm1-vnet0-I -j DROP

ebtables -t nat -A vm1-vnet0-O -p ARP --arp-op Reply --arp-mac-dst ! 52:54:00:27:c7:f3 -j DROP
ebtables -t nat -A vm1-vnet0-O -p IPv4 --ip-dst 192.168.11.14 -j ACCEPT
ebtables -t nat -A vm1-vnet0-O -p ARP --arp-ip-dst 192.168.11.14 -j ACCEPT
ebtables -t nat -A vm1-vnet0-O -p ARP --arp-op Request -j ACCEPT
ebtables -t nat -A vm1-vnet0-O -p ARP --arp-op Reply -j ACCEPT
ebtables -t nat -A vm1-vnet0-O -j DROP

ebtables -t nat -A PREROUTING -i vnet0 -j vm1-vnet0-I

ebtables -t nat -A POSTROUTING -o vnet0 -j vm1-vnet0-O
```

如果想要移除mac地址与ip绑定，执行以下规则

```bash
ebtables -t nat -D PREROUTING -i vnet0 -j vm1-vnet0-I
ebtables -t nat -D POSTROUTING -o vnet0 -j vm1-vnet0-O
ebtables -t nat -F vm1-vnet0-I
ebtables -t nat -X vm1-vnet0-I
ebtables -t nat -F vm1-vnet0-O
ebtables -t nat -X vm1-vnet0-O
```

## 限制虚拟机带宽

设置vm1的带宽为1Mbps

```bash
/usr/bin/virsh domiftune vm1 vnet0 --inbound "125,125,150" --outbound "125,125,150" --live
```

inbound和outbound的三位数值(avg, peak, burst)分别对应<实际限速值KByte/s>,<峰值KByte/s>,<突发值KByte/s>

我们公司的的计算方式为`avg=peak` `burst=1.2*peak`。

使用`iperf`测速为`1.05 Mbits/sec`，而对没有限制带宽的vm2测速为`695 Mbits/sec`，因此可以看出带宽限制有效。

> 其他限制资源的地方还有磁盘IOPS：`/usr/bin/virsh blkdeviotune vm1 vda --write-iops-sec 15 --write-bytes-sec 2048 --read-bytes-sec 4096 --read-iops-sec 15`

## 总结

我们公司是使用静态ip加防火墙来实现公网ip的分配，但我在`vultr`也有虚拟机，我查看发现`vultr`并没有在虚拟机内使用静态ip而是dhcp。我估计他们是在路由器层面做了mac地址与ip绑定，等以后在研究一下。
`
