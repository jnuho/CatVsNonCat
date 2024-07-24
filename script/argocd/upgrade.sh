#!/bin/bash

# exit when any command fails
set -e

new_ver=$1

echo "new version: $new_ver"

# Simulate release of the new docker images
docker tag nginx:1.23.3 jnuho/nginx:$new_ver

# Push new version to dockerhub
docker push jnuho/nginx:$new_ver

# Create temporary folder
tmp_dir=$(mktemp -d)
echo $tmp_dir

# Clone GitHub repo
git clone git@github.com:jnuho/cvn-yaml.git $tmp_dir

# Update image tag
sed -i '' -e "s/jnuho\/nginx:.*/jnuho\/nginx:$new_ver/g" $tmp_dir/values.dev.yaml

cd $tmp_dir
git add .
git commit -m 'Update image to $new_ver'
git push origin main

# Optionally on build agents - remove folder
rm -rf $tmp_dir

