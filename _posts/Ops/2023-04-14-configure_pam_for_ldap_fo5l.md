---
layout: post
title: "Linux PAM配置LDAP认证"
date: 2023-04-13 20:05:11 +0800
categories: 技术
tags: Linux PAM LDAP FreeIPA
---

为了不破坏宿主机的环境，采用虚拟机搭建环境来验证测试可行性。

到[linuxvmimages](https://www.linuxvmimages.com/)下载centos8的镜像，直接用VMware或者VirtualBox打开。

`yum update`的时候会报以下错误

```log
Failed to download metadata for repo ‘AppStream‘: Cannot download repomd.xml
```

原因是因为centos8已经停止支持了，需要切换到8-stream。

```bash
cd /etc/yum.repos.d
sed -i 's/$releasever/8-stream/' CentOS*repo
```

切换为清华源

```bash
sed -e 's|^mirrorlist=|#mirrorlist=|g' \
    -e 's|^#baseurl=http://mirror.centos.org/$contentdir|baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos|g' \
    -i.bak \
    /etc/yum.repos.d/CentOS-*.repo
```

安装需要的软件包

SSSD是介于本地用户和数据存储之间的进程，本地客户端首先连接SSSD，再由SSSD联系外部资源提供者(一台远程服务器)；
sssd-tools用来自动配置PAM的配置文件；
oddjob-mkhomedir用来自动创建用户的home目录；

```
yum install sssd sssd-tools sssd-ldap oddjob-mkhomedir
```

配置PAM认证为sssd

```bash
authselect select sssd with-mkhomedir --force
```

修改 `/etc/sssd/sssd.conf`

```conf
[sssd]
config_file_version = 2
services = nss, pam, ssh, sudo, autofs
domains = default
enable_files_domain = false

[nss]
homedir_substring = /home

[pam]

[sudo]

[autofs]

[ssh]

[domain/default]
id_provider = ldap
autofs_provider = ldap
auth_provider = ldap
chpass_provider = ldap
ldap_id_use_start_tls = False
ldap_uri = ldap://example.com:8009
ldap_search_base = dc=example,dc=com
ldap_default_bind_dn = uid=admin,cn=users,cn=accounts,dc=example,dc=com
ldap_default_authtok = your password
ldap_access_order = filter
ldap_access_filter = (objectClass=posixaccount)
ldap_tls_reqcert = allow
cache_credentials = true
enumerate = true
debug_level = 9
```

这时会报以下错误，原因是sssd配置文件权限不正确，使用`chmod 0600 /etc/sssd/sssd.conf`命令修复文件权限

```log
[sssd] [confdb_expand_app_domains] (0x0010): No domains configured, fatal error!
[sssd] [get_monitor_config] (0x0010): Failed to expand application domains
[sssd] [confdb_get_domains] (0x0020): No domains configured, fatal error!
[sssd] [get_monitor_config] (0x0010): No domains configured.
[sssd] [main] (0x0010): SSSD couldn't load the configuration database [1432158246]: No domain is enabled
[sssd] [sss_ini_read_sssd_conf] (0x0020): Permission check on config file failed.
[sssd] [confdb_init_db] (0x0020): Cannot convert INI to LDIF [1432158322]: [File ownership and permissions check failed]
[sssd] [confdb_setup] (0x0010): ConfDB initialization has failed [1432158322]: File ownership and permissions check failed
[sssd] [load_configuration] (0x0010): Unable to setup ConfDB [1432158322]: File ownership and permissions check failed
[sssd] [main] (0x0010): SSSD couldn't load the configuration database [1432158322]: File ownership and permissions check failed
[sssd] [sss_ini_read_sssd_conf] (0x0020): Permission check on config file failed.
[sssd] [confdb_init_db] (0x0020): Cannot convert INI to LDIF [1432158322]: [File ownership and permissions check failed]
[sssd] [confdb_setup] (0x0010): ConfDB initialization has failed [1432158322]: File ownership and permissions check failed
[sssd] [load_configuration] (0x0010): Unable to setup ConfDB [1432158322]: File ownership and permissions check failed
[sssd] [main] (0x0010): SSSD couldn't load the configuration database [1432158322]: File ownership and permissions check failed
[sssd] [sss_ini_read_sssd_conf] (0x0020): Permission check on config file failed.
[sssd] [confdb_init_db] (0x0020): Cannot convert INI to LDIF [1432158322]: [File ownership and permissions check failed]
[sssd] [confdb_setup] (0x0010): ConfDB initialization has failed [1432158322]: File ownership and permissions check failed
[sssd] [load_configuration] (0x0010): Unable to setup ConfDB [1432158322]: File ownership and permissions check failed
[sssd] [main] (0x0010): SSSD couldn't load the configuration database [1432158322]: File ownership and permissions check failed
[sssd] [sss_ini_read_sssd_conf] (0x0020): Permission check on config file failed.
[sssd] [confdb_init_db] (0x0020): Cannot convert INI to LDIF [1432158322]: [File ownership and permissions check failed]
[sssd] [confdb_setup] (0x0010): ConfDB initialization has failed [1432158322]: File ownership and permissions check failed
[sssd] [load_configuration] (0x0010): Unable to setup ConfDB [1432158322]: File ownership and permissions check failed
```

在ssh连接的时候会报以下错误

```log
centos8 sssd_be[13504]: Could not start TLS encryption. error:1416F086:SSL routines:tls_process_server_certificate:certificate verify failed (self signed certificate in certificate chain)
```

需要禁用服务器证书认证（或者配置tls），添加以下配置在[domain/default]中。

```
ldap_tls_reqcert = allow
#ldap_tls_cacert = /etc/pki/tls/cert.pem
```

> 注意`services = nss, pam, ssh, sudo, autofs`，如果没有`ssh`就不能使用ldap的用户登录ssh。`services`根据具情况配置。

其他实用命令

```bash
# 校验sssd配置是否正确
sssctl config-check
# 查看远程用户
getent passwd -s sss
```