"""
function gitInfo(state) {
    // fatal: no tag exactly matches 'bf5efa0810d9f097b7c6ba8390f97c008d98d80e'
    return Promise.all([
        run('git show --format=%H%n%h%n%an%n%at%n%cn%n%ct%n%d --name-status | head -n 8'),
        run('git log -1 --pretty=%s'),
        run('git log -1 --pretty=%N'),
        run('git config --get remote.origin.url'),
        run('git rev-parse --abbrev-ref HEAD'),
        run('git describe --exact-match --tags $(git rev-parse HEAD)').catch(function() {
            // For non-prod ui we can be tolerant of a missing version, but not for prod.
            if (state.buildConfig.release) {
                throw new Error('This is a release build, a semver tag is required');
            }
            mutant.log('Not on a tag, but that is ok since this is not a release build');
            mutant.log('version will be unavailable in the ui');
            return '';
        })
    ]).spread(function(infoString, subject, notes, url, branch, tag) {
        const info = infoString.split('\n');
        let version;
        tag = tag.trim('\n');
        if (/^fatal/.test(tag)) {
            version = null;
        } else {
            const m = /^v([\d]+)\.([\d]+)\.([\d]+)$/.exec(tag);
            if (m) {
                version = m.slice(1).join('.');
            } else {
                version = null;
            }
        }

        // in Travis, the origin url may end in .git, remove it if so.
        // another way, but more can go wrong...
        // let [_m, originUrl] = url.match(/^(https:.+?)(?:[.]git)?$/) || [];

        url = url.trim('\n');
        if (url.endsWith('.git')) {
            url = url.slice(0, -4);
        }

        return {
            commitHash: info[0],
            commitAbbreviatedHash: info[1],
            authorName: info[2],
            authorDate: new Date(parseInt(info[3]) * 1000).toISOString(),
            committerName: info[4],
            committerDate: new Date(parseInt(info[5]) * 1000).toISOString(),
            reflogSelector: info[6],
            subject: subject.trim('\n'),
            commitNotes: notes.trim('\n'),
            originUrl: url,
            branch: branch.trim('\n'),
            tag: tag,
            version: version
        };
    });
}
"""
import subprocess
import sys
from typing import List

import toml


def print_lines(prefix: str, lines: List[str]):
    for index, line in enumerate(lines):
        print(f"{prefix} {index}: {line}")


def run_command(command, ignore_error=False):
    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as cpe:
        if ignore_error:
            return str(cpe), False
        print("Error running git command:")
        print(f"Command: {cpe.cmd}")
        if cpe.stderr is not None:
            print_lines("stderr", cpe.stderr.split("\n"))
        print(str(cpe))
        sys.exit(1)

    if ignore_error:
        return process.stdout, True
    return process.stdout


def git_info():
    output = run_command(
        ["git", "show", "--format=%H%n%h%n%an%n%at%n%cn%n%ct%n%d", "--name-status"]
    )

    [
        commit_hash,
        commit_hash_abbreviated,
        author_name,
        author_date,
        committer_name,
        committer_date,
        *_,
    ] = output.split("\n")
    # print('hash', commit_hash)
    return {
        "commit_hash": commit_hash,
        "commit_hash_abbreviated": commit_hash_abbreviated,
        "author_name": author_name,
        "author_date": int(author_date) * 1000,
        "committer_name": committer_name,
        "committer_date": int(committer_date) * 1000,
    }


def git_url():
    output = run_command(["git", "config", "--get", "remote.origin.url"])
    url = output.rstrip("\n")
    if url.endswith(".git"):
        url = url[0:-4]
    return url


def git_branch():
    output = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return output.rstrip("\n")


def git_tag(commit_hash):
    result, success = run_command(
        ["git", "describe", "--exact-match", "--tags", commit_hash], ignore_error=True
    )
    if success:
        return result
    else:
        return None


def git_config():
    output = run_command(["git", "config", "--global", "--add", "safe.directory", "*"])
    return output.rstrip("\n")


def save_info(info):
    with open("/kb/module/config/git-info.toml", "w") as fout:
        toml.dump(
            info,
            fout,
        )


def main():
    git_config()
    info = git_info()
    url = git_url()
    info["url"] = url

    branch = git_branch()
    tag = git_tag(info["commit_hash"])

    info["branch"] = branch
    info["tag"] = tag

    save_info(info)

    sys.exit(0)


main()
