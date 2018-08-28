---
layout: post
title: "Git实用命令"
date: 2018-08-28 10:07:13
categories: 技术
tags: Git
---

## 撤销commit消息保留修改

```shell
git reset --soft [commit_id]
```

## 暂存修改

```shell
git stash
git stash apply
git stash list
git stash pop
git stash clear
```

## 删除恢复分支

```shell
# 删除分支
git branch -d <branch_name>
# 恢复分支
git branch <branch_name> <hash_val>
# 查看散列值
git reflog
```

## git pull 强制覆盖本地文件

```shell
git fetch --all  
git reset --hard origin/<branch_name>
git pull
```

## 拉取远程分支到本地

```shell
git checkout -b <branch_name> origin/<branch_name>
```
