---
layout: post
title: "KVM镜像制作及挂载镜像文件"
date: 2019-02-14 23:01:23 +0800
categories: 技术
tags: KVM
---

我们公司是做云计算的，但我一直在做上层业务开发没有机会接触虚拟化方面的东西，年前快过年几天公司任务较少加上业余时间学习了一下KVM相关技术。

## 安装软件包

```shell
apt update
apt install qemu-kvm libvirt-bin kpartx
```

## 镜像制作

生成镜像文件（raw格式）

```shell
qemu-img create -f raw ubuntu-18.04-x86_64.img 10G
```

虚拟机配置文件（`config.xml`）

```xml
<domain type = 'kvm'>
    <name>my-ubuntu-18.04</name>
    <memory>1048576</memory>
    <vcpu>1</vcpu>
    <os>
        <type>hvm</type>
        <boot dev = 'cdrom'/>
    </os>
    <features>
        <acpi/>
        <apic/>
        <pae/>
    </features>
    <clock offset = 'localtime'/>
    <on_poweroff>destroy</on_poweroff>
    <on_reboot>restart</on_reboot>
    <on_crash>destroy</on_crash>
    <devices>
        <emulator>/usr/bin/kvm</emulator>
        <disk type = 'file' device = 'disk'>
            <driver name = 'qemu' type = 'raw'/>
            <source file = '/data/img/ubuntu-18.04-x86_64.img'/>  <!-- 镜像文件，上面qemu-img创建 -->
            <target dev = 'hda' bus = 'ide'/>
        </disk>
        <disk type = 'file' device = 'cdrom'>
            <source file = '/data/iso/ubuntu-18.04.1-live-server-amd64.iso'/>  <!-- 安装介质文件 光盘镜像 -->
            <target dev = 'hdb' bus = 'ide'/>
        </disk>
        <interface type = 'bridge'>
            <source bridge = 'virbr0'/>
        </interface>
        <graphics type = 'vnc' listen = '0.0.0.0' autoport = 'yes' keymap = 'en-us'/>
    </devices>
</domain>
```

详细配置信息参考官方文档：

[https://libvirt.org/formatdomain.html](https://libvirt.org/formatdomain.html)

定义并启动虚拟机

```shell
# 定义虚拟机
virsh define config.xml

# 查看虚拟机
virsh list --all

# 启动虚拟机，名称与配置文件中name一致
virsh start my-ubuntu-18.04
```

### 连接虚拟机

可以直接使用`virsh console`来连接，但我这里报错，详见以下链接

[https://wiki.libvirt.org/page/Unable_to_connect_to_console_of_a_running_domain](https://wiki.libvirt.org/page/Unable_to_connect_to_console_of_a_running_domain)

我使用[noVNC](https://github.com/novnc/noVNC)来连接连接虚拟机

查看虚拟机`VNC`信息，参考

```shell
virsh vncdisplay my-ubuntu-18.04

# [output]
# :0
```

返回值是:数字N的格式。表示使用VNC显示器:N，对应的TCP端口号是5900+N。

也可以通过查看配置文件来查看

```shell
virsh dumpxml my-ubuntu-18.04

# [output]
# ...
# <graphics type='vnc' port='5900' autoport='yes' listen='0.0.0.0' keymap='en-us'>
#     <listen type='address' address='0.0.0.0'/>
# </graphics>
# ...
```

启动VNC server

```shell
./utils/launch.sh --vnc localhost:5900
```

然后可以在浏览器来连接虚拟机，跟电脑装系统一样一步步安装就好。

![](\assets\images\post\屏幕快照 2019-02-15 下午3.04.17.png)

### 硬盘启动虚拟机

刚才为了安装系统是使用`cdrom`启动的虚拟机，现在系统安装完成就可以使用磁盘启动，而且可以以此为镜像随意创建不同配置的虚拟机（修改配置文件中的CPU，内存等）

```xml
<domain type = 'kvm'>
    <name>my-ubuntu-18.04</name>  <!-- 虚拟机名 -->
    <memory>1048576</memory>  <!-- 内存，KiB -->
    <vcpu>1</vcpu>  <!-- CPU -->
    <os>
        <type>hvm</type>
        <boot dev = 'hd'/>  <!-- 改为磁盘启动 -->
    </os>
    <features>
        <acpi/>
        <apic/>
        <pae/>
    </features>
    <clock offset = 'localtime'/>
    <on_poweroff>destroy</on_poweroff>
    <on_reboot>restart</on_reboot>
    <on_crash>destroy</on_crash>
    <devices>
        <emulator>/usr/bin/kvm</emulator>
        <disk type = 'file' device = 'disk'>
            <driver name = 'qemu' type = 'raw'/>
            <source file = '/data/img/ubuntu-18.04-x86_64.img'/>  <!-- 可以复制该镜像以创建新的虚拟机 -->
            <target dev = 'hda' bus = 'ide'/>
        </disk>
        <interface type = 'bridge'>
            <source bridge = 'virbr0'/>
        </interface>
        <graphics type = 'vnc' listen = '0.0.0.0' autoport = 'yes' keymap = 'en-us'/>
    </devices>
</domain>
```

## 挂载镜像文件（可以在主机上修改虚拟机中的内容）

参考地址：[https://developer.huawei.com/ict/forum/thread-22565.html](https://developer.huawei.com/ict/forum/thread-22565.html)

加载 nbd 驱动

```shell
# 加载驱动。 卸载驱动 rmmod nbd
modprobe nbd max_part=8  
```

连接镜像并告诉内核

```shell
qemu-nbd -c /dev/nbd2 /data/img/ubuntu-18.04-x86_64.img
partx -a /dev/nbd2  # 这个命令不执行也可以完成挂载，但我公司代码中执行了该命令，可能这样做更好一些
```

挂载

```shell
mkdir /data/img/mount
mount /dev/nbd2p2 /data/img/mount

# 然后就可以访问镜像文件中的内容了
```

但如果是`LVM`分区时，挂载报错

```
mount: unknown filesystem type 'LVM2_member'
```

参考[http://www.361way.com/kvm-mount-img/3169.html](http://www.361way.com/kvm-mount-img/3169.html)

不知道为啥，我没有使用链接中的方法处理LVM，也可以直接挂载，但无法删除映射

```shell
kpartx -av /data/vm/my-centos/disk.img
mkdir /data/vm/my-centos/mount
mount /dev/mapper/centos-root /data/vm/my-centos/mount
```

报错如下：

```
device-mapper: remove ioctl on loop0p2 failed: Device or resource busy
loop deleted : /dev/loop0
```

解决如下：

```shell
losetup -d /dev/loop0
dmsetup remove_all
kpartx -d /dev/loop0
```

这样貌似是强行断开的，还是按照参考链接中的方法比较好

```shell
# 挂载

cd /data/vm/my-centos
fdisk -lu disk.img
# [output]
# Units: sectors of 1 * 512 = 512 bytes
# Sector size (logical/physical): 512 bytes / 512 bytes
# I/O size (minimum/optimal): 512 bytes / 512 bytes
# Disklabel type: dos
# Disk identifier: 0x00007103
#
# Device     Boot   Start      End  Sectors Size Id Type
# disk.img1  *       2048  2099199  2097152   1G 83 Linux
# disk.img2       2099200 16777215 14678016   7G 8e Linux LVM
losetup /dev/loop0 disk.img -o $((2099200*512))
pvscan
# [output]
#   PV /dev/loop0   VG centos          lvm2 [7.00 GiB / 0    free]
#   Total: 1 [7.00 GiB] / in use: 1 [7.00 GiB] / in no VG: 0 [0   ]
vgchange -ay centos
lvs
# [optput]
#   LV   VG     Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
#   root centos -wi-a-----   6.20g
#   swap centos -wi-a----- 820.00m
mount /dev/centos/root /data/vm/my-centos/mount

# 卸载

umount /dev/centos/root
vgchange -an centos
losetup  -d /dev/loop0
```
