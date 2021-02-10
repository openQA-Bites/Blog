#!/bin/bash
#
# Summary: Script to publish the blog contents on the blog instance
#

function restore() {
	set +e
	cp config.toml.bak config.toml
	rm -f config.toml.bak
}

set -e
mv config.toml config.toml.bak
cp config.toml.bak config.toml
trap restore EXIT
sed 's|baseURL = .*|baseURL = "http://openqa-blog"|' -i config.toml
hugo
echo "Pushing content ... "
rsync -uar public/* phoenix@openqa-blog:/srv/www/blog/
cp config.toml.bak config.toml
hugo
echo "Done. Visit http://openqa-blog/ to see the result"