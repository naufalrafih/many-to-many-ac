export SCRIPT_ROOT_DIR=$(cd `dirname "$0"` && pwd)
export REPO=git@github.com:naufalrafih/many-to-many-ac.git
$SCRIPT_ROOT_DIR/pipenvinstall.sh
$SCRIPT_ROOT_DIR/zerotierinstall.sh
$SCRIPT_ROOT_DIR/gitinstall.sh
$SCRIPT_ROOT_DIR/sshsetup.sh
git clone $REPO