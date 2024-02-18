#!/bin/bash

# Pulls all of the Percona Operator k8s deployment files for a specific commit from GitHub
#
# Motivation: We may want to modify the default deployment config and we want
# to version the deployment files, but we don't want to include their whole
# repository within ours.
#
# In retropect, it would have been much easier to just clone the whole repo
# locally and then cherry-pick the files using file system commands :)

# This just needs permission to read public repos. Pass as env variable.
# Without a token, you might get API rate-limited
auth="Authorization: Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"

# This recursively lists all blobs under 'deploy/' using the GitHub API
# 2a0c2c692219d0052b9cba89017bfab4c353cb3e = v1.14.0
blobs=$(curl -X GET 'https://api.github.com/repos/percona/percona-server-mongodb-operator/git/trees/2a0c2c692219d0052b9cba89017bfab4c353cb3e?recursive=1' --header "${auth}" | jq '.tree[] | select(.type == "blob") | select (.path | startswith("deploy/"))')
echo ${blobs}

# Extract .path attributes into Bash array
paths=$(jq -r '.path' <<< "${blobs}")
paths=(${paths})

# Extract .url attributes into Bash array
urls=$(jq -r '.url' <<< "${blobs}")
urls=(${urls})

# Get individual file contents
for i in "${!paths[@]}"; do
    d=$(dirname "${paths[i]}")
    f=$(basename "${paths[i]}")
    url="${urls[i]}"
    echo $d $f $url
    mkdir -p "${d}"
    blob=$(curl -X GET "${url}" --header "${auth}")
    content=$(jq -r '.content' <<< "${blob}")
    echo "${content}" | base64 --decode > "${d}/${f}"
done
