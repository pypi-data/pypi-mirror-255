#!/bin/bash
git add ./rinch_sql/__version__.py
git commit -m"$(head -n 1 rinch_sql/__version__.py)"
git push

git add .
git commit -m"$(head -n 1 rinch_sql/__version__.py)"
git push
