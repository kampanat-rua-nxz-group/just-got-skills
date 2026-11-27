#!/usr/bin/env bash
# Collects the facts a digest note needs about one pull request. Read-only: it only reads from GitHub.
# Usage: gather.sh <out-dir> [<PR number, URL or branch>]
# Without a PR argument it uses the PR of the current branch. A number or branch needs the PR's repo as the
# working directory; a URL works from anywhere.
set -euo pipefail

out=${1:?Usage: gather.sh <out-dir> [<PR number, URL or branch>]}
pr_args=()
[ -n "${2:-}" ] && pr_args=("$2")
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$out"

gh pr view ${pr_args[@]+"${pr_args[@]}"} \
	--json number,title,body,url,state,author,baseRefName,baseRefOid,headRefName,headRefOid,additions,deletions,changedFiles \
	> "$out/pr.json"
url=$(jq -r .url "$out/pr.json")
number=$(jq -r .number "$out/pr.json")
owner=$(jq -r '.url | capture("github\\.com/(?<o>[^/]+)/").o' "$out/pr.json")
repo=$(jq -r '.url | capture("github\\.com/[^/]+/(?<r>[^/]+)/pull").r' "$out/pr.json")

jq -r .body "$out/pr.json" > "$out/description.md"
gh pr view "$url" --json files --jq '.files[] | "\(.additions)\t\(.deletions)\t\(.path)"' > "$out/files.tsv"
gh pr diff "$url" > "$out/full.diff"

# Review threads on the diff. A thread whose first comment comes from a GitHub App ("Bot") is an AI or CI thread.
gh api graphql -F owner="$owner" -F name="$repo" -F number="$number" -f query='
query($owner: String!, $name: String!, $number: Int!) {
	repository(owner: $owner, name: $name) {
		pullRequest(number: $number) {
			reviewThreads(first: 100) {
				totalCount
				nodes {
					path line diffSide isResolved isOutdated
					comments(first: 50) { nodes { author { __typename login } body url } }
				}
			}
		}
	}
}' --jq '.data.repository.pullRequest.reviewThreads
	| if .totalCount > (.nodes | length) then error("over 100 review threads: add pagination to gather.sh") else . end
	| [.nodes[] | {
		path, line,
		side: (if .diffSide == "LEFT" then "old" else "new" end),
		isResolved, isOutdated,
		startedByHuman: (.comments.nodes[0].author.__typename != "Bot"),
		comments: [.comments.nodes[] | {author: (.author.login // "ghost"), body, url}]
	}]' > "$out/threads.json"

python3 -I "$here/list_test_changes.py" "$out/full.diff" > "$out/test-changes.tsv"

# PRs the description links to, with their state: an open one is a dependency, a merged one is history.
{
	grep -oE 'github\.com/[^/[:space:]]+/[^/[:space:]]+/pull/[0-9]+' "$out/description.md" \
		| sed -E 's#github\.com/([^/]+/[^/]+)/pull/#\1 #' || true
	grep -oE '(^|[^[:alnum:]/&])#[0-9]+' "$out/description.md" | sed -E "s|.*#|$owner/$repo |" || true
} | sort -u | while read -r linked_repo linked_number; do
	[ "$linked_number" = "$number" ] && [ "$linked_repo" = "$owner/$repo" ] && continue
	gh pr view "$linked_number" -R "$linked_repo" --json state,url,title --jq '"\(.state)\t\(.url)\t\(.title)"' \
		2>/dev/null || echo "NOT_A_PR	$linked_repo#$linked_number	"
done > "$out/linked-prs.tsv"

head_sha=$(jq -r .headRefOid "$out/pr.json")
jq -r '"PR #\(.number): \(.title)\n\(.url)\n\(.headRefName) → \(.baseRefName), head \(.headRefOid), \(.state)"' "$out/pr.json"
jq -r '"+\(.additions) −\(.deletions) in \(.changedFiles) files. Budget: \(((.additions + .deletions) * 0.2) | floor) shown lines"' "$out/pr.json"
jq -r '[.[] | select(.startedByHuman and (.isResolved | not) and (.isOutdated | not))]
	| "Open human review threads (the note must show these): \(length)",
	  (.[] | "  \(.path):\(.line) by \(.comments[0].author) \(.comments[0].url)")' "$out/threads.json"
echo "Removed tests (the note must list these): $(grep -c '^removed' "$out/test-changes.tsv" || true)"
grep '^removed' "$out/test-changes.tsv" | sed 's/^/  /' || true
echo "Added tests: $(grep -c '^added' "$out/test-changes.tsv" || true)"
echo "Linked PRs:"
sed 's/^/  /' "$out/linked-prs.tsv"
if git rev-parse --git-dir > /dev/null 2>&1 && [ "$(git rev-parse HEAD)" != "$head_sha" ]; then
	echo "warning: local HEAD is not the PR head. Read code with: git show $head_sha:<path> (fetch it first if missing)"
fi
