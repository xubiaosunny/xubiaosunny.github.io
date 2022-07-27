FROM ruby:3

RUN bundle config mirror.https://rubygems.org https://mirrors.tuna.tsinghua.edu.cn/rubygems
RUN bundle install
RUN bundle exec jekyll build

WORKDIR /code
