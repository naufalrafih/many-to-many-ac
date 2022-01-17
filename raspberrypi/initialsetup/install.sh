export SCRIPT_ROOT_DIR=$(cd `dirname "$0"` && pwd)
$SCRIPT_ROOT_DIR/pipenvinstall.sh
$SCRIPT_ROOT_DIR/zerotierinstall.sh