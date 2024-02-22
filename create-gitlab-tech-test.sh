#!/bin/bash

# exit when any command fails
set -e

# Check required env vars are set
if [ -z "${GITLAB_SECRET}" ]; then
    echo "GITLAB_SECRET env var needs to be set"
    exit 1
fi

# Read function parameters
# if [ "$1" == "" ]; then
#     echo "Specify lowercase first name for tech test project"
#     exit 1
# fi
if [ "$1" == "" ]; then
    echo "Specify GitLab username for the candidate"
    exit 1
fi
# FIRST_NAME=${1}
GITLAB_USERNAME=${1}
REPO_NAME="${GITLAB_USERNAME}-tech-test"


# Create GitLab project under user (not Journee) group/profile
result=$(curl --header "PRIVATE-TOKEN: ${GITLAB_SECRET}" -X POST --silent \
    "https://gitlab.com/api/v4/projects?name=${REPO_NAME}")
PROJECT_ID=$(echo ${result} | jq '.id')
echo -e "\nCreated project #${PROJECT_ID}\n"

# Push the repo content
git remote set-url origin-candidate git@gitlab.com:jgillard/${REPO_NAME}.git
git push -u origin-candidate main
echo -e "\nPushed code to project\n"

# Get the candidate's GitLab user ID
result=$(curl --header "PRIVATE-TOKEN: ${GITLAB_SECRET}" -X GET --silent \
    "https://gitlab.com/api/v4/users?username=${GITLAB_USERNAME}")
echo ${result}
GITLAB_USER_ID=$(echo $result | jq '.[0].id')
echo -e "\nFound GitLab user ID ${GITLAB_USER_ID} for ${GITLAB_USERNAME}\n"

# Add user to project
result=$(curl --header "PRIVATE-TOKEN: ${GITLAB_SECRET}" -X POST --silent \
    "https://gitlab.com/api/v4/projects/${PROJECT_ID}/members?user_id=${GITLAB_USER_ID}&access_level=30")
echo ${result}
echo -e "\nUser ${GITLAB_USERNAME} added to project\n"

# Create the task Issue
result=$(curl --header "PRIVATE-TOKEN: ${GITLAB_SECRET}" -X POST --silent \
    "https://gitlab.com/api/v4/projects/${PROJECT_ID}/issues?title=Tech%20test&assignee_id=${GITLAB_USER_ID}")
echo ${result}
ISSUE_URL=$(echo $result | jq '.web_url')
echo -e "\nCreated the task Issue\n"

# One last manual step
echo -e "\nNow copy TASK_1.md into the Issue description: ${ISSUE_URL}\n"