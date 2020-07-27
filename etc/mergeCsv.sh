#!/bin/bash

IS_THERE_NECESSARY_OPT=false

while getopts d:o: OPT; do
  case $OPT in
  d)
    IS_THERE_NECESSARY_OPT=true
    dir=$OPTARG
    ;;
  o)
    IS_THERE_NECESSARY_OPT=true
    output=$OPTARG
    ;;
  : | \?)
    echo "Invalid args."
    ;;
  esac
done

if [ "${IS_THERE_NECESSARY_OPT}" != true ]; then
  echo "Not found necessary options."
  exit 1
fi

# ファイル名取得
mapfile -t files < <(ls -1 "$dir")

# header取得
head -n 1 "$dir${files[0]}" | grep -v "^$" >"$output"

# ファイル内容の集約
for filename in "${files[@]}"; do
  tail -n +2 "$dir$filename" | grep -v "^$" >>"$output"
done
