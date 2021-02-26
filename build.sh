#!/bin/bash
#
# Summary: Script to publish the blog contents on the blog instance
#

# Remote configuration
REMOTE="openqa-blog"
R_DIR="/srv/www/blog"


function restore() {
	set +e
	cp config.toml.bak config.toml
	rm -f config.toml.bak
}

if ! ping -c 1 "$REMOTE" >/dev/null; then
	echo "Cannot ping $REMOTE - Is the host up?"
	exit 1
fi


set -e
mv config.toml config.toml.bak
cp config.toml.bak config.toml
trap restore EXIT
sed 's|baseURL = .*|baseURL = "http://'"${REMOTE}"'"|' -i config.toml
echo "Building for $REMOTE ... "
echo ""
hugo
echo ""
echo "Pushing content to $REMOTE ... "
rsync -uar public/* "phoenix@${REMOTE}:${R_DIR}/"
cp config.toml.bak config.toml
echo "Rebuilding for public instance ... "
echo ""
hugo
echo ""
echo "Done. Visit http://openqa-blog/ to see the preview"
echo "      public/ contains the upstream ready contents (has its own git repo)"
