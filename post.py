#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import argparse
import datetime

DESCRIPTION = """
    Post automated tools
"""

POSTHEAD = """\
---
layout: post
title: "{title}"
date: {time}
categories: {categories}
tags: {tags}
---\
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_post(name, title, categories='', tags=''):
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    file_name = date_str + '-' + name + '.md'
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(BASE_DIR, '_posts/{}'.format(file_name)), 'w+') as f:
        head = POSTHEAD.format(title=title, time=now, categories=" ".join(categories),
                               tags=" ".join(tags))
        f.writelines(head)
        print(head)


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("-n", "--name", help="post file name", required=True)
    parser.add_argument("-t", "--title", help="post title")
    parser.add_argument("-c", "--categories", help="post categories: if there are more than one, please use ',' split")
    parser.add_argument("-ta", "--tags", help="post tags: if there are more than one, please use ',' split ")
    args = parser.parse_args()

    if not args.title:
        args.title = ""

    if args.categories:
        args.categories = args.categories.split(',')
    else:
        args.categories = []

    if args.tags:
        args.tags = args.tags.split(',')  
    else:
        args.tags = []  
    
    create_post(args.name, args.title, args.categories, args.tags)


if __name__ == "__main__":
    main()
