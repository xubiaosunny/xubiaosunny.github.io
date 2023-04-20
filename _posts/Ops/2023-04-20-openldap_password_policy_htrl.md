---
layout: post
title: "OpenLDAP环境搭建及密码策略配置"
date: 2023-04-20 10:58:28 +0800
categories: 技术
tags: LDAP OpenLDAP
---

## OpenLDAP环境搭建

OpenLDAP采用[bitnami/openldap](https://hub.docker.com/r/bitnami/openldap)镜像

该镜像本身本身是不支持ppolicy的，我们需要自定义加载需要的模块，网上的资料比较少，按照很多教程比如修改slapd.conf配置文件等都不好使，我查看了bitnami/openldap内的slapd.conf是空的，
而且镜像内服务的启动命令是`/opt/bitnami/openldap/sbin/slapd -h ldap://:1389/ ldapi:/// -F /opt/bitnami/openldap/etc/slapd.d -d 256`，没有指定slapd.conf配置文件。
最终在bitnami/openldap的文档和以下两个issues中找到了方法。

* https://github.com/bitnami/containers/issues/6671
* https://github.com/bitnami/containers/issues/982#issuecomment-1220354408

我们需要自定义两个ldif，分别为`memberof.ldif`和`ppolicy.ldif`，具体内容如下。将其放到宿主机`/configs/openldap/schemas`文件夹下。

memberof.ldif（也许不需要也可以，没有测试，加载了memberof模块可以显示memberof属性也好）

```properties
dn: cn=module,cn=config
cn: module
objectClass: olcModuleList
olcModulePath: /opt/bitnami/openldap/lib/openldap
olcModuleLoad: memberof.so
olcModuleLoad: refint.so

dn: olcOverlay=memberof,olcDatabase={2}mdb,cn=config
objectClass: olcMemberOf
objectClass: olcOverlayConfig
olcOverlay: memberof

dn: olcOverlay=refint,olcDatabase={2}mdb,cn=config
objectClass: olcConfig
objectClass: olcOverlayConfig
objectClass: olcRefintConfig
objectClass: top
olcOverlay: refint
olcRefintAttribute: memberof member manager owner
```

ppolicy.ldif

```properties
dn: cn=module,cn=config
cn: module
objectClass: olcModuleList
olcModulePath: /opt/bitnami/openldap/lib/openldap
olcModuleLoad: ppolicy.so

dn: olcOverlay=ppolicy,olcDatabase={2}mdb,cn=config
objectClass: olcConfig
objectClass: olcOverlayConfig
objectClass: olcPPolicyConfig
objectClass: top
olcOverlay: ppolicy
olcPPolicyDefault: cn=default,ou=policies,dc=example,dc=com
```

docker容器启动命令

```bash
docker run -d --name openldap \
  -p 1389:1389 -p 1636:1636 \
  -v /configs/openldap:/bitnami/openldap \
  -v /configs/openldap/schemas:/schemas \
  -e LDAP_ROOT=dc=example,dc=com \
  -e LDAP_ADMIN_USERNAME=admin \
  -e LDAP_ADMIN_PASSWORD=yourpassword \
  -e LDAP_USERS=test \
  -e LDAP_PASSWORDS=123456 \
  -e LDAP_ALLOW_ANON_BINDING=no \
  bitnami/openldap:2.5-debian-11
```

查看`slapd.d/cn\=config/cn\=module\{1\}.ldif`可以看出已经加载`ppolicy`模块

```bash
cat /bitnami/openldap/slapd.d/cn\=config/cn\=module\{1\}.ldif
```

```
# AUTO-GENERATED FILE - DO NOT EDIT!! Use ldapmodify.
# CRC32 7a4bff6d
dn: cn=module{1}
objectClass: olcModuleList
cn: module{1}
olcModulePath: /opt/bitnami/openldap/lib/openldap
olcModuleLoad: {0}ppolicy.so
structuralObjectClass: olcModuleList
entryUUID: 92255272-72d3-103d-8d07-3738e8977bdd
creatorsName: cn=config
createTimestamp: 20230419075726Z
entryCSN: 20230419075726.993503Z#000000#000#000000
modifiersName: cn=config
modifyTimestamp: 20230419075726Z
```

## 密码策略配置

本文LDAP的目录结构大致如下

```plaintext
dc=example,dc=com
├── ou=groups
│   └── cn=testgroup
├── ou=policies
│   └── cn=default
└── ou=users
    ├── uid=test1
    └── uid=test2
```

创建`ou=policies,dc=example,dc=com`（同理创建groups和users目录）

```bash
cat << EOF | ldapadd -x -D "cn=admin,dc=example,dc=com"  -w yourpassword -H ldapi:///
dn: ou=policies,dc=example,dc=com
ou: policies
objectClass: organizationalUnit
objectClass: top
EOF
```

在上面的加载ppolicy模块的时候设置了默认策略为`cn=default,ou=policies,dc=example,dc=com`，所以我们需要创建该目录。
如果需要配置为其他目录则根据需求修改`ppolicy.ldif`中的`olcPPolicyDefault`来搭建新的OpenLDAP服务。

创建`cn=default,ou=policies,dc=example,dc=com`

```bash
cat << EOF | ldapadd -x -D "cn=admin,dc=example,dc=com"  -w yourpassword -H ldapi:///
dn: cn=default,ou=policies,dc=example,dc=com
cn: default
objectClass: pwdPolicy
objectClass: pwdPolicyChecker
objectClass: person
objectClass: top
pwdAttribute: userPassword
pwdMinAge: 0
pwdMaxAge: 2592000
pwdInHistory: 5
pwdCheckQuality: 0
pwdMinLength: 5
pwdExpireWarning: 259200
pwdGraceAuthNLimit: 0
pwdLockout: TRUE
pwdLockoutDuration: 300
pwdMaxFailure: 5
pwdFailureCountInterval: 30
pwdMustChange: FALSE
pwdAllowUserChange: TRUE
pwdSafeModify: FALSE
sn: dummy value
EOF
```

相关属性解释（摘于网络）

* pwdAllowUserChange：允许用户修改其密码
* pwdAttribute, pwdPolicy：对象的一个属性，用于标识用户密码。默认值(目前唯一支持的)是userPassword
* pwdExpireWarning：密码过期前警告天数
* pwdFailureCountInterval：多久时间后重置密码失败次数, 单位是秒
* pwdGraceAuthNLimit：密码过期后不能登录的天数，0代表禁止登录。
* pwdInHistory：开启密码历史记录，用于保证不能和之前设置的密码相同。
* pwdLockout：定义用户错误密码输入次数超过pwdMaxFailure定义后, 是否锁定用户, TRUE锁定（默认）.
* pwdLockoutDuration：密码连续输入错误次数后，帐号锁定时间。
* pwdMaxAge：密码有效期，到期需要强制修改密码, 2592000是30天
* pwdMaxFailure：密码最大失效次数，超过后帐号被锁定。
* pwdMinAge：密码最小有效期, 默认为0, 用户随时更改密码, 如果定义了, 用户在离上次更改密码 + 定义的时间之内不能更改密码
* pwdMinLength：用户修改密码时最短的密码长度
* pwdMustChange：用户在帐户锁定后由管理员重置帐户后是否必须更改密码, 并且只有在pwdLockout为TRUE时才相关, 如果值为FLASE(默认值), 管理员帮用户解锁用户后, 用户不必更改密码, 如果为TRUE, 就必须更改密码。如果使用pwdReset来解锁用户, 其值将覆盖此属性
* pwdSafeModify：该属性控制用户在密码修改操作期间是否必须发送当前密码。如果属性值为FALSE（缺省值），则用户不必发送其当前密码。如果属性值为TRUE，那么修改密码值时用户必须发送当前密码。

> 此外还可以设置`pwdCheckQuality`等相关属性启用密码强度策略；还可以为用户添加`pwdPolicySubentry`属性单独为某个用户指定其他的安全策略，例`pwdPolicySubentry: cn=test,ou=policies,dc=example,dc=com`;

## 密码策略验证

主要验证了以下策略是否生效

* 设置了`pwdMaxAge`密码过期
* 设置了`pwdInHistory`会记录历史密码，属性为`pwdHistory`
* 设置了`pwdMaxFailure`会记录认证错误历史，属性为`pwdFailureTime`；超过上限就会锁定帐号，属性为`pwdAccountLockedTime`，修改密码或者删除该属性即可重新激活帐号；
* 设置了`pwdMustChange`, 并且用户属性`pwdReset: TRUE`则需要修改密码。这里有个冲突：如果用户密码过期，他在认证的时候是不通过的，但是该用户如果设置了`pwdReset: TRUE`用户就能通过认证了。

我在修改了几次密码，故意输错5次以上密码，查询用户test1的结果如下（查询到`pwdHistory` `pwdFailureTime` `pwdAccountLockedTime`等属性值）：

```bash
# +号可以查询到隐藏属性
ldapsearch -x -H ldapi:/// \
  -D "cn=admin,dc=example,dc=comm" -w yourpassword \
  -b "uid=test1,ou=users,dc=example,dc=comm" +
```

```
# extended LDIF
#
# LDAPv3
# base <uid=test1,ou=users,dc=example,dc=com> with scope subtree
# filter: (objectclass=*)
# requesting: +
#

# test1, users, example.com
dn: uid=test1,ou=users,dc=example,dc=com
ufn: test1, users, example.com
structuralObjectClass: inetOrgPerson
entryUUID: 1cdede0a-7370-103d-9f69-6b8d5492a633
creatorsName: cn=admin,dc=example,dc=com
createTimestamp: 20230420023801Z
pwdHistory: 20230420024919Z#1.3.6.1.4.1.1466.115.121.1.40#46#{SSHA}tMrDy6qMD+T
 QIB8neKwMloilc0JZ0I2FrQAdmw==
pwdHistory: 20230420025003Z#1.3.6.1.4.1.1466.115.121.1.40#20#{CRYPT}yw8kobPae1
 6l6
pwdChangedTime: 20230420025003Z
pwdReset: TRUE
pwdFailureTime: 20230420055534.204043Z
pwdFailureTime: 20230420055536.465025Z
pwdFailureTime: 20230420055538.306704Z
pwdFailureTime: 20230420055540.142507Z
pwdFailureTime: 20230420055541.994890Z
pwdAccountLockedTime: 20230420055541Z
entryCSN: 20230420054612.329356Z#000000#000#000000
modifiersName: cn=admin,dc=example,dc=com
modifyTimestamp: 20230420054612Z
entryDN: uid=test1,ou=users,dc=example,dc=com
subschemaSubentry: cn=Subschema
hasSubordinates: FALSE

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

验证强制修改密码（为用户test1设置`pwdReset: TRUE`）和密码过期（设置pwdMaxAge为一个很小的值，如60。密码过期后会导致认证失败）

```bash
ldapwhoami -x -H ldapi:/// -D uid=test1,ou=users,dc=example,dc=com -w <userpassword> -e ppolicy -v

# 强制修改密码输出 
ldap_bind: Success (0); Password must be changed
dn:uid=test1,ou=users,dc=example,dc=com
Result: Success (0)

# 密码过期输出
ldap_bind: Invalid credentials (49); Password expired
```

## 客户端使用

OpenLDAP是没有界面的，为了方便操作可以使用[Apache Directory Studio](https://directory.apache.org/studio/)

MacOS下如果打不开，需要修改`/Applications/ApacheDirectoryStudio.app/Contents/Info.plist`，配置正确的java路径

```xml
...
  <array>
    <!-- to use a specific Java version (instead of the platform's default) uncomment one of the following options,
        or add a VM found via $/usr/libexec/java_home -V
      <string>-vm</string><string>/System/Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Commands/java</string>
      <string>-vm</string><string>/Library/Java/JavaVirtualMachines/1.8.0.jdk/Contents/Home/bin/java</string>
    -->
    <string>-vm</string><string>/usr/local/opt/openjdk@11/bin/java</string>
    <string>-keyring</string>
    <string>~/.eclipse_keyring</string>
  </array>
...
```

## 参考链接

* https://github.com/bitnami/containers/tree/main/bitnami/openldap
* https://www.cnblogs.com/cishi/p/9160520.html
* https://www.cnblogs.com/panwenbin-logs/p/16176894.html
