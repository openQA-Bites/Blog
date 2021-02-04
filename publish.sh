#!/bin/bash
#
# Summary: Script to publish the blog contents on the blog instance
#

set -e
cd openqa_blog
hugo
rsync -uarv public/* phoenix@openqa-blog:/srv/www/blog/
