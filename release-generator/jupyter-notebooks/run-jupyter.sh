#!/bin/bash
#
# Launch Jupyter for the Cytoscape SNAPSHOT Release Builder notebook.
#
# The notebook reads its configuration from the environment, and Jupyter passes its own
# environment to the kernel - so these values have to be set before Jupyter starts, not
# from inside a cell.  This script sets them, checks the toolchain, and only then starts
# Jupyter.  Run with -h for the full list.
#
# ENVIRONMENT
#
#   STARTING_BRANCH    default: develop
#       Branch of github.com/cytoscape/cytoscape to build.  Use develop for a major
#       release and release/3.X.X for a minor one.  It must name a branch whose cy.sh
#       supports 'pull' and 'build'; the notebook checks this in section 2a.
#
#   JAVA_HOME          default: /opt/jdk-17
#       JDK used for the build.  Must be 17 or newer - Cytoscape compiles with
#       --release 17 - and must be a JDK, not a JRE, because maven needs javac.
#
#   MAVEN_HOME         default: /opt/maven
#       Maven installation.  $MAVEN_HOME/bin is placed on the PATH the notebook builds
#       with in section 1.
#
#   PUBLISH_ROOT       default: /var/www/html/cytoscape-builds
#       Where section 5 publishes.  Installers land in
#       $PUBLISH_ROOT/Cytoscape-<version>/<date>, with <version> read from the pom.xml
#       of the tree that was just built.
#
#   ADMIN_SCRIPTS_DIR  default: the checkout this script lives in
#       Which cytoscape-admin-scripts checkout the notebook builds in.  Defaulting to
#       this script's own checkout means running it from a test clone keeps the entire
#       run inside that clone, leaving the live checkout untouched.
#
#   PORT               default: 8888
#       Port Jupyter listens on.  Jupyter is started with --no-browser, so reach it by
#       tunnelling: ssh -N -L $PORT:localhost:$PORT <user>@<builder>
#
# NOTES
#
#   PATH is deliberately not set by this script.  Jupyter itself usually comes from
#   Anaconda, so replacing PATH would make it unfindable.  The notebook rebuilds PATH
#   from JAVA_HOME and MAVEN_HOME for the build itself, in section 1.
#
# USAGE
#
#   ./run-jupyter.sh
#   ./run-jupyter.sh -h
#   STARTING_BRANCH=release/3.11.1 ./run-jupyter.sh
#   PORT=8889 JAVA_HOME=/opt/jdk-21 ./run-jupyter.sh
#
set -u

HERE=$(cd "$(dirname "$0")" && pwd)

usage() {
  sed -n '/^# ENVIRONMENT$/,/^set -u$/p' "$0" | sed -e 's/^# \{0,1\}//' -e '/^set -u$/d'
  exit 0
}

case "${1:-}" in
  -h|--help|help) usage ;;
  '') ;;
  *) echo "unknown argument: $1" 1>&2; echo "try: $(basename "$0") -h" 1>&2; exit 2 ;;
esac

# Which branch to build, and the toolchain to build it with.
export STARTING_BRANCH=${STARTING_BRANCH:-develop}
export JAVA_HOME=${JAVA_HOME:-/opt/jdk-17}
export MAVEN_HOME=${MAVEN_HOME:-/opt/maven}

# Where installers are published, and which checkout the notebook builds in.  The
# checkout defaults to the one this script lives in, so running it from a test clone
# keeps the whole run inside that clone.
export PUBLISH_ROOT=${PUBLISH_ROOT:-/var/www/html/cytoscape-builds}
export ADMIN_SCRIPTS_DIR=${ADMIN_SCRIPTS_DIR:-$(cd "$HERE/../.." && pwd)}

PORT=${PORT:-8888}

# PATH is deliberately left alone here: Jupyter itself usually comes from Anaconda, and
# the notebook rebuilds PATH from JAVA_HOME and MAVEN_HOME for the build in section 1.

FAILED=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; FAILED=$((FAILED+1)); }

echo "== configuration =="
pass "STARTING_BRANCH   = $STARTING_BRANCH"
pass "PUBLISH_ROOT      = $PUBLISH_ROOT"
if [ -d "$ADMIN_SCRIPTS_DIR" ]; then pass "ADMIN_SCRIPTS_DIR = $ADMIN_SCRIPTS_DIR"
else fail "ADMIN_SCRIPTS_DIR = $ADMIN_SCRIPTS_DIR is not a directory"; fi

echo
echo "== toolchain =="
# Compare major versions numerically.  JDK 17 GA reports itself as bare "17" with no
# minor part, while later builds report "17.0.14" - a glob on "17.*" misses the former.
if [ -x "$JAVA_HOME/bin/javac" ]; then
  jv=$("$JAVA_HOME/bin/javac" -version 2>&1 | awk '{print $2}')
  jmaj=${jv%%.*}
  case "$jmaj" in
    ''|*[!0-9]*) fail "javac version '$jv' not understood" ;;
    *) if [ "$jmaj" -ge 17 ]; then pass "javac $jv"
       else fail "javac $jv - Cytoscape compiles with --release 17"; fi ;;
  esac
else
  fail "$JAVA_HOME/bin/javac is missing - is JAVA_HOME a JRE?"
fi

if [ -x "$JAVA_HOME/bin/java" ]; then
  rv=$("$JAVA_HOME/bin/java" -version 2>&1 | head -1)
  rmaj=$(printf '%s\n' "$rv" | sed -n 's/.*version "\([0-9][0-9]*\).*/\1/p')
  case "$rmaj" in
    ''|*[!0-9]*) fail "java runtime version not understood: $rv" ;;
    *) if [ "$rmaj" -ge 17 ]; then pass "$rv"
       else fail "java runtime $rmaj - expected 17 or newer: $rv"; fi ;;
  esac
else
  fail "$JAVA_HOME/bin/java is missing"
fi

if [ -x "$MAVEN_HOME/bin/mvn" ]; then pass "maven at $MAVEN_HOME/bin/mvn"
else fail "$MAVEN_HOME/bin/mvn is missing"; fi

# cy.sh uses 'git -C', which arrived in git 1.8.5.
gv=$(git --version 2>/dev/null | awk '{print $3}')
lowest=$(printf '%s\n%s\n' 1.8.5 "$gv" | sort -V | head -1)
if [ -n "$gv" ] && [ "$lowest" = "1.8.5" ]; then pass "git $gv at $(command -v git)"
else fail "git '$gv' is below 1.8.5 - cy.sh needs 'git -C'"; fi

if command -v jupyter > /dev/null 2>&1; then pass "jupyter at $(command -v jupyter)"
else fail "jupyter is not on PATH"; fi

echo
if [ "$FAILED" -ne 0 ]; then
  echo "$FAILED check(s) failed - not starting jupyter."
  exit 1
fi

echo "Starting jupyter on port $PORT.  Tunnel from your workstation with:"
echo "  ssh -N -L $PORT:localhost:$PORT $(whoami)@$(hostname)"
echo

cd "$ADMIN_SCRIPTS_DIR" || exit 1
exec jupyter lab --no-browser --port "$PORT"
