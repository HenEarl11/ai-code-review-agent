#!/usr/bin/env bash
# scan_repo.sh - Clone a target repository (or scan the current checkout) and run a full scan
# Usage:
#   ./scripts/scan_repo.sh [git-url|.] [branch] [backend_url]
# Examples:
#   # Scan a remote repo
#   ./scripts/scan_repo.sh https://github.com/example/repo.git main http://localhost:5001
#   # Scan the current checkout (recommended for CI)
#   ./scripts/scan_repo.sh . main http://localhost:5001
# Notes:
# - Requires: git (when scanning a remote repo), curl, jq
# - The backend must be running and reachable at BACKEND_URL (/api/health). See README for Docker quickstart.
# - Exclusions: by default skips tests, vendor and common build directories. Use EXCLUDE_PATTERNS env var to add more (comma-separated).

set -u

# Positional args (both optional)
REPO_URL="${1:-.}"
BRANCH="${2:-main}"
BACKEND_URL="${3:-http://localhost:5001}"

# File extensions to scan (adjust as needed)
EXTENSIONS=("py" "tf" "tfvars" "js" "ts" "tsx" "jsx")

# Retry settings
MAX_RETRIES=3
RETRY_DELAY=3

# Workdir when cloning remote repos
WORKDIR="$(pwd)/.scan_tmp"
OUTDIR="$(pwd)/scan_results"

mkdir -p "$WORKDIR" "$OUTDIR"

function die() {
  echo "ERROR: $*" >&2
  exit 1
}

function check_deps() {
  for cmd in curl jq; do
    command -v "$cmd" >/dev/null 2>&1 || die "Required command '$cmd' not found. Install it and retry."
  done
  # git is only required when cloning a remote URL
  if [ "$REPO_URL" != "." ]; then
    command -v git >/dev/null 2>&1 || die "Required command 'git' not found. Install it and retry."
  fi
}

function health_check() {
  local url="$BACKEND_URL/api/health"
  echo "Checking backend health at $url"
  if curl -sSf "$url" >/dev/null; then
    echo "Backend healthy"
    return 0
  fi
  return 1
}

function clone_repo() {
  # If REPO_URL is '.' or omitted, scan the current working tree instead of cloning.
  if [ "$REPO_URL" = "." ] || [ -z "$REPO_URL" ]; then
    echo "Scanning current checkout at $(pwd)"
    WORKDIR="$(pwd)"
    return 0
  fi

  echo "Cloning $REPO_URL (branch: $BRANCH) into $WORKDIR"
  # Ensure the target path is removed entirely (including dotfiles) so git can clone cleanly.
  if [ -d "$WORKDIR" ]; then
    rm -rf "$WORKDIR"
  fi
  mkdir -p "$WORKDIR"
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$WORKDIR" || die "git clone failed"
}

# Default exclude directories (relative patterns)
DEFAULT_EXCLUDES=(".git" "node_modules" "vendor" "tests" "test" "__pycache__" "venv" ".venv" "build" "dist")

function build_find_prune_args() {
  # Merge default excludes with any user-provided EXCLUDE_PATTERNS (comma-separated)
  local excludes=()
  excludes+=("${DEFAULT_EXCLUDES[@]}")
  if [ -n "${EXCLUDE_PATTERNS:-}" ]; then
    IFS=',' read -r -a user_ex <<< "$EXCLUDE_PATTERNS"
    for e in "${user_ex[@]}"; do
      excludes+=("$e")
    done
  fi

  # Build -path ... -prune -o parts
  local args=()
  for e in "${excludes[@]}"; do
    # normalize to /** pattern
    args+=( -path "$WORKDIR/$e" -prune -o -path "$WORKDIR/$e/*" -prune -o )
  done
  echo "${args[@]}"
}

function file_list() {
  local root="$WORKDIR"
  # Simpler approach: find all files then filter by extension and exclude patterns using grep
  local exts
  exts=$(printf "%s|" "${EXTENSIONS[@]}" | sed 's/|$//')

  # Build exclude regex from DEFAULT_EXCLUDES + EXCLUDE_PATTERNS
  local excludes=()
  excludes+=("${DEFAULT_EXCLUDES[@]}")
  if [ -n "${EXCLUDE_PATTERNS:-}" ]; then
    IFS=',' read -r -a user_ex <<< "$EXCLUDE_PATTERNS"
    for e in "${user_ex[@]}"; do
      excludes+=("$e")
    done
  fi

  # Join excludes into a single regex like '(.git|node_modules|vendor)'
  local excl_regex
  excl_regex=$(printf "%s|" "${excludes[@]}" | sed 's/|$//')

  find "$root" -type f | grep -E ".((${exts}))$" | grep -Ev "(^|/)(${excl_regex})(/|$)" | sort
}

function safe_outpath() {
  local f="$1"
  # convert relative file path -> safe filename
  local rel
  rel="${f#$WORKDIR/}"
  # replace any char not in [A-Za-z0-9._/-] with '_'
  local safe
  safe=$(printf "%s" "$rel" | tr -c 'A-Za-z0-9._/-' '_')
  echo "$OUTDIR/$safe.json"
}

function detect_codebase_style() {
  # Simple heuristics to detect language/style based on repository files.
  local root="$WORKDIR"
  if [ -f "$root/pyproject.toml" ] || [ -f "$root/setup.py" ] || [ -f "$root/requirements.txt" ]; then
    echo "python"
    return
  fi
  if ls "$root"/*.tf >/dev/null 2>&1 || ls "$root"/*.tfvars >/dev/null 2>&1; then
    echo "terraform"
    return
  fi
  if [ -f "$root/package.json" ] || [ -f "$root/tsconfig.json" ]; then
    echo "typescript"
    return
  fi
  if [ -f "$root/go.mod" ]; then
    echo "golang"
    return
  fi
  echo "generic"
}

function analyze_file() {
  local f="$1"
  local outp
  outp=$(safe_outpath "$f")
  mkdir -p "$(dirname "$outp")"

  # determine language by extension
  local ext
  ext="${f##*.}"
  local lang
  case "$ext" in
    py) lang="python";;
    tf|tfvars) lang="terraform";;
    js|jsx|ts|tsx) lang="typescript";;
    *) lang="text";;
  esac

  # include detected codebase style in the payload so the backend can optionally use it
  local codebase_style
  codebase_style="${CODEBASE_STYLE:-generic}"

  local attempt=1
  while [ $attempt -le $MAX_RETRIES ]; do
    # Build JSON payload safely using jq reading file contents
    payload=$(jq -Rs --arg p "${f#$WORKDIR/}" --arg l "$lang" --arg cs "$codebase_style" '{file_path:$p, code:., language:$l, codebase_style:$cs}' < "$f")
    if [ -z "$payload" ]; then
      echo "Skipping empty payload for $f" >&2
      return 1
    fi

    echo "Analyzing ($attempt/$MAX_RETRIES): $f -> $outp (lang=$lang, style=$codebase_style)"
    http_code=$(curl -s -w "%{http_code}" -o "$outp.tmp" -X POST "$BACKEND_URL/api/analyze" \
      -H "Content-Type: application/json" -d "$payload" || true)

    if [ "$http_code" = "200" ]; then
      mv "$outp.tmp" "$outp"
      # normalize JSON (pretty)
      jq . "$outp" > "$outp.tmp" && mv "$outp.tmp" "$outp"
      return 0
    else
      echo "Attempt $attempt failed for $f (HTTP $http_code). Retrying in $RETRY_DELAY s..." >&2
      rm -f "$outp.tmp"
      attempt=$((attempt+1))
      sleep $RETRY_DELAY
    fi
  done

  echo "Failed to analyze $f after $MAX_RETRIES attempts" >&2
  return 2
}

function aggregate_results() {
  echo "Aggregating results in $OUTDIR"
  local all_json="$OUTDIR/all_results.json"
  jq -s '.' "$OUTDIR"/*.json 2>/dev/null > "$all_json" || echo '[]' > "$all_json"

  # Summary: total files, total issues, breakdown by severity and by type
  local summary="$OUTDIR/summary.json"
  jq '{
    files: (length),
    total_issues: (map(.analysis_data.issues | length) | add // 0),
    by_severity: (map(.analysis_data.issues // [] | map(.severity) ) | add | group_by(.) | map({(.[0]): length}) | add // {}),
    by_type: (map(.analysis_data.issues // [] | map(.type) ) | add | group_by(.) | map({(.[0]): length}) | add // {})
  }' "$all_json" > "$summary" || echo '{"files":0,"total_issues":0}' > "$summary"

  echo "Summary written to $summary"
  echo "Top-level results:"
  jq . "$summary"
}

#########################
# Main
#########################
check_deps

# Validate backend up front
if ! health_check; then
  echo "Backend not healthy at $BACKEND_URL. Try starting the backend (see README) and re-run this script." >&2
  exit 1
fi

clone_repo

# Auto-detect CODEBASE_STYLE if not provided externally
if [ -z "${CODEBASE_STYLE:-}" ]; then
  detected=$(detect_codebase_style)
  export CODEBASE_STYLE="$detected"
  echo "Auto-detected CODEBASE_STYLE=$CODEBASE_STYLE"
else
  echo "Using CODEBASE_STYLE from environment: $CODEBASE_STYLE"
fi

# iterate files
count=0
failures=0
while IFS= read -r file; do
  [ -z "$file" ] && continue
  analyze_file "$file"
  rc=$?
  if [ $rc -eq 0 ]; then
    count=$((count+1))
  else
    failures=$((failures+1))
  fi
done < <(file_list)

aggregate_results

echo "Done. Files analyzed: $count. Failures: $failures. Results in $OUTDIR"
exit 0
