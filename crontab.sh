PROJECT_ROOT=~/Projects/sl-mayor-mailbox
DATE=$(date +"%Y-%m-%d")

echo "Update at $DATE"
cd $PROJECT_ROOT

msg=$(make)
echo $msg

git add category && git add imgs && git add README.md && git commit -m "[Mailbox Update] $DATE" && git push && echo "Successfully updated the remote repo!"
