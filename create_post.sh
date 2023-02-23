#!/bin/bash
#
# Summary: Create new blog post
#

# Directory for input
POSTS="content/posts/`date +%Y`"
TEMPLATE=".template.md"
FOLDER=0
TITLE=""

function usage() {
	echo "$0 [-f] [-t title]"
	echo "   -f             Create post in new folder"
	echo "   -t title       Define title"
}

# Parse arguments
while getopts "hft:l:" opt; do
	case $opt in
		h)
			usage
			exit 0
			;;
		f)
			FOLDER=1
			;;
		t)
			TITLE="$OPTARG"
			;;
		:)
			echo "Option -$opt requires an argument" >&2
			exit 1
			;;
	esac	
done

if [[ $TITLE == "" ]]; then
	printf "New post title: "
	read TITLE
fi
if [[ $TITLE == "" ]]; then
	echo "error: no title" >&2
	exit 1
fi

DATE=`date --iso`
# 2021-00-00T00:00:00+01:00
#TIMESTAMP="`date +%Y-%m-%d`T`date +%H:%M:%S`+02:00"
TIMESTAMP=`date +%Y-%m-%dT%H:%M:%S%:z`
DATESTAMP=`date +%Y-%m-%d`
URL="/`date +%Y`/`date +%m`/`date +%d`/${TITLE// /-}/"
POST="$DATESTAMP-${TITLE// /_}"


if [[ $FOLDER == 1 ]]; then
	POSTDIR="${POSTS}/${POST}"
	FILE="$POSTDIR/index.md"
	echo "$POSTDIR"
	mkdir -p "$POSTDIR"
else
	POSTDIR="${POSTS}"
	FILE="$POSTDIR/$DATESTAMP-${TITLE// /_}.md"
fi

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
