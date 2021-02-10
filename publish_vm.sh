#!/bin/bash
#
# Summary: Script to publish the blog contents on the blog instance
#

set -e
hugo
echo "Pushing content ... "
rsync -uar public/* phoenix@openqa-blog:/srv/www/blog/
echo "Done. Visit http://openqa-blog/ to see the result"