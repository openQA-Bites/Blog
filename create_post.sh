#!/bin/bash
#
# Summary: Create new blog post
#

# Directory for input
POSTS="content/posts"
TEMPLATE="$POSTS/_template.md"

if [[ $# -gt 0 ]]; then
	TITLE="$@"
else
	printf "New post title: "
	read TITLE
fi

if [[ $TITLE == "" ]]; then
	echo "No title given"
	exit 1
fi

set -e
#set -x

DATE=`date --iso`
# 2021-00-00T00:00:00+01:00
TIMESTAMP="`date +%Y-%m-%d`T`date +%H:%M:%S`+01:00"
URL="/`date +%Y`/`date +%m`/`date +%d`/$TITLE/"

FILENAME="`date +%Y-%m-%d`.md"
FILE="$POSTS/$FILENAME"

if [[ -s "$FILE" ]]; then
	echo "File $FILE exists already"
else
	echo "Creating $FILE ... "
	cp "$TEMPLATE" "$FILE"
	sed "s!title:.*!title: $TITLE!" -i $FILE
	sed "s!date:.*!date: $TIMESTAMP!" -i $FILE
	sed "s!url:.*!url: $URL!" -i $FILE
fi
$EDITOR $FILE
