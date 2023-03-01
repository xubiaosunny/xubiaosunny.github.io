---
layout: post
title: "Windows下安装Office2019批量许可证版(VOL)及使用KMS激活"
date: 2023-03-01 16:36:06 +0800
categories: 折腾
tags: Office Windows KMS
---

很少使用windows来办公，windows下一直使用WPS来临时使用，最近工作上需要调试一个程序，需要调用Word。便准备安装一个Office，我预想的是直接安装一个正版office，然后用KMS激活即可，结果发现不好使。
上网查询才发现只用VOL版本的才能使用KMS激活，而官网下载professional plus版本是不行的。

## Office 2019 VOL下载及安装

### 1. 下载 Office Deployment Tool (ODT)  

网上搜索Office Deployment Tool或者直接到以下网址下载ODT程序

https://www.microsoft.com/en-us/download/details.aspx?id=49117

运行程序，会生成以下文件

```
setup.exe
configuration-Office365-x64.xml
configuration-Office365-x86.xml
configuration-Office2019Enterprise.xml
configuration-Office2021Enterprise.xml
```

### 2. 配置configuration.xml

直接以上面的xml文件为模版修改得到自己的配置文件，也可以到以下网址在界面配置然后导出。

https://config.office.com/deploymentsettings

这是我生成的配置文件（64位，Office 专业增强版 2019）

```xml
<Configuration ID="55a9fbbc-ed27-4276-9b41-9a589db8dd65">
  <Add OfficeClientEdition="64" Channel="PerpetualVL2019">
    <Product ID="ProPlus2019Volume" PIDKEY="NMMKJ-6RK4F-KMJVX-8D9MJ-6MWKP">
      <Language ID="MatchOS" />
      <ExcludeApp ID="Access" />
      <ExcludeApp ID="Groove" />
      <ExcludeApp ID="Lync" />
      <ExcludeApp ID="OneDrive" />
      <ExcludeApp ID="OneNote" />
      <ExcludeApp ID="Publisher" />
    </Product>
  </Add>
  <Property Name="SharedComputerLicensing" Value="0" />
  <Property Name="FORCEAPPSHUTDOWN" Value="FALSE" />
  <Property Name="DeviceBasedLicensing" Value="0" />
  <Property Name="SCLCacheOverride" Value="0" />
  <Property Name="AUTOACTIVATE" Value="1" />
  <Updates Enabled="FALSE" />
  <RemoveMSI />
  <AppSettings>
    <User Key="software\microsoft\office\16.0\excel\options" Name="defaultformat" Value="51" Type="REG_DWORD" App="excel16" Id="L_SaveExcelfilesas" />
    <User Key="software\microsoft\office\16.0\powerpoint\options" Name="defaultformat" Value="27" Type="REG_DWORD" App="ppt16" Id="L_SavePowerPointfilesas" />
    <User Key="software\microsoft\office\16.0\word\options" Name="defaultformat" Value="" Type="REG_SZ" App="word16" Id="L_SaveWordfilesas" />
  </AppSettings>
</Configuration>
```

### 3. 下载及安装

将第2步生成的`configuration.xml`的配置文件放到第1步ODT生成的文件同级目录，并在【终端】或者【cmd】中切换到此目录。

下载（取决于网速，大概下载2个多G的文件）

```
setup /download configuration.xml
```

安装
```
setup /configure configuration.xml
```

## KMS激活Office

使用管理员打开终端或者cmd，并切换目录到`C:\Program Files\Microsoft Office\Office16`

> 32位Office在C:\Program Files (x86)\Microsoft Office\Office16\

```shell
cd 'C:\Program Files\Microsoft Office\Office16\'

# 查看状态信息
cscript ospp.vbs /dstatus

# 卸载原本的激活码【xxxxx为密钥后五位】（本文不需要卸载原本的激活码）
cscript ospp.vbs /unpkey:xxxxx

# 设置激活码（不同版本激活码不同，本文在配置文件中已经注入专业增强版的批量密钥，不需要再次设置激活码）
cscript ospp.vbs /inpkey:xxxxx-xxxxx-xxxxx-xxxxx

# 设置激活服务器
cscript ospp.vbs /sethst:kms.03k.org

# 激活
cscript ospp.vbs /act
```

## 参考链接：

* https://www.aihao.cc/thread-12243-1-1.html
* https://www.coolhub.top/tech-articles/kms_list.html
* https://blog.51cto.com/u_15065851/4059834