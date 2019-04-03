---
layout: post
title: "KVM网络配置之私有网络"
date: 2019-04-02 17:42:01
categories: 技术
tags: KVM Linux
---

## 环境配置

VMware创建两台虚拟机代表两台物理机，并添加两个网络适配器，第一个使用桥接模式（由路由器分配ip，模拟公网），第二个使用仅主机模式（模拟内网）。

![](\assets\images\post\屏幕快照 2019-04-02 下午5.51.19.png)

在VMware虚拟机内配置网桥，网卡`ens33`对应网络适配器1，网卡`ens38`对应网络适配器2，`br0`桥接`ens33`,
`br1`桥接`ens38`。

```yaml
network:
    ethernets:
        ens33:
            dhcp4: no
            dhcp6: no
        ens38:
            dhcp4: no

    bridges:
        br0:
            interfaces: [ens33]
            addresses: [192.168.11.11/24]
            gateway4: 192.168.11.1
            nameservers:
                addresses: [192.168.11.1]
        br1:
            interfaces: [ens38]
            addresses: [10.10.10.11/24]
    version: 2
```

过程中遇到一个问题，因为第二台VMware虚机是我克隆第一台所得，虽然我在VMware中随机了网卡的mac地址，但两台虚机网桥mac地址相同，做了桥接路由器上记录的是桥的mac地址，于是ip冲突了。试了修改第二台桥的mac地址不好使，不得以将第二台虚机的网桥名称改为了`br20`和`br21`。

## 私网配置

### 建立vxlan网络

创建vxlan加入同一个多播组并启用

这里我使用的`VXLAN ID`为2000，多播地址为239.0.7.208，vxlan虚拟网卡为vxlan2000

```bash
/sbin/ip route add 239.0.7.208/32 dev br1

/sbin/ip link add vxlan2000 mtu 1500 numtxqueues 4 numrxqueues 4 type vxlan id 2000 group 239.0.7.208 ttl 10 dev br1

/sbin/ip link set vxlan2000 up
/sbin/ifconfig vxlan2000 up
```

创建网桥net1，绑定vxlan虚拟网卡并启用

```bash
/sbin/brctl addbr net1
/sbin/brctl addif net1 vxlan2000
/sbin/brctl stp net1 on
/sbin/ip link set net1 up
```

### kvm虚拟机加入到私网

创建kvm配置文件`join.xml`，mac地址随机生成一个，不要与同一私有网络的其他kvm虚机冲突。

```yaml
<interface type='bridge'>
    <mac address='fa:52:00:66:66:84'/>
    <source bridge='net1'/>
    <model type='e1000'/>
</interface>
```

在线添加interface（虚拟机状态必须为running）

```bash
/usr/bin/virsh attach-device vm1 join.xml
```

重新定义该kvm虚拟机

```bash
/usr/bin/virsh dumpxml vm1 | grep -v "target dev=.vnet"> config.xml
/usr/bin/virsh undefine vm1
/usr/bin/virsh define config.xml
```

通过`qemu-agent-command`执行命令配置私网网卡及ip（为vm1分配192.168.100.1）

```bash
/usr/bin/virsh qemu-agent-command vm1 '{"arguments": {"capture-output": true, "arg": ["-o", "link"], "path": "/sbin/ip"}, "execute": "guest-exec"}'

# guest-exec 会返回命令执行进程的id
# 通过以下命令获取对应pid（如1429）的返回
# /usr/bin/virsh qemu-agent-command vm1 '{"arguments": {"pid": 1429}, "execute": "guest-exec-status"}'

/usr/bin/virsh qemu-agent-command vm1 '{"arguments": {"capture-output": false, "arg": ["ens6", "192.168.100.1", "netmask", "255.255.255.0"], "path": "/sbin/ifconfig"}, "execute": "guest-exec"}'
```
> 如果没有安装配置qemu-agent则通过以下方式安装，参考[https://cloud.tencent.com/developer/article/1162113](https://cloud.tencent.com/developer/article/1162113)

编辑kvm虚拟机配置文件

```xml
<channel type='unix'>
  <source mode='bind' path='/var/lib/libvirt/qemu/org.qemu.guest_agent.0'/>
  <target type='virtio' name='org.qemu.guest_agent.0'/>
</channel>
```

kvm虚拟机内安装`qemu-guest-agent`（可以在镜像制作时就安装完成）

```bash
apt install qemu-guest-agent
```

### 将其他kvm虚拟机加入该私网

按照上面的流程将vm2和vm3加入私网`net1`，并分配ip为`192.168.100.2`和192.168.100.3`

网络拓扑图如下：

![](\assets\images\post\截图_09ba8d77-a472-471f-9bd9-84eeb29058d9.png)

### 离开私网

以上方法建立私有网络及加入私网的配置是临时的，当物理机和kvm虚拟机重启后都会失效。

所以当kvm虚拟机已经关机，只需要将kvm虚拟机的配置文件更新即可（删除`net1`interface）

```xml
<!-- 删除以下内容 -->
<interface type='bridge'>
  <mac address='fa:52:00:66:66:83'/>
  <source bridge='net1'/>
  <model type='e1000'/>
  <alias name='net1'/>
  <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
</interface>
```

然后重新定义kvm虚拟机

```bash
/usr/bin/virsh undefine vm1
/usr/bin/virsh define config.xml
```

如果kvm虚拟机没有重启或关机，需先手动卸载该interface，xml（join.xml）配置文件与加载时一样

```bash
/usr/bin/virsh detach-device vm1 join.xml
```

### 删除VXLan虚机网卡及网桥

如果没有kvm虚拟机加入到私网时，可以将其删除

```bash
/sbin/brctl delif net1 vxlan2000
/sbin/brctl stp net1 off
/sbin/ip link set net1 down
/sbin/brctl delbr net1

/sbin/ip link set vxlan2000 down
/sbin/ip link delete vxlan2000
/sbin/ip route del 239.0.7.208/32 dev vxlan2000
```

查看是否还有kvm虚拟机在私网（net1）内

```bash
ls /sys/class/net/net1/brif
```
若只剩下`vxlan2000`那么该物理机上没有虚拟机在该私网（net1）内了。
