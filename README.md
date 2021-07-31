# py_releaser

This is a tool for create release note.

## Usage

```shell
./releaser.py pull [-m milestone] [-c config_file] [-L label1,label2,...]
./releaser.py list [-m milestone] [-c config_file] [-L label1,label2,...]
```

The pull option will create a collection of release note of `milestone` in `ti-srebot/docs` and create a pull request in `PingCAP/docs`.

The list option will print the release notes of `milestone`.

config.example.json:

```json
{
    "repos": ["pingcap/tidb", "tikv/tikv", "pingcap/pd", "pingcap/br", "pingcap/dumpling", "pingcap/tidb-lightning", "pingcap/ticdc"],
    "labels": ["type/enhancement", "type/bug-fix", "type/new-feature", "compatibility-breaker"],
    "token": "{ti_srebot_TOKEN}",
    "alias": {
        "pingcap/tics" : "PingCAP/TiFlash",
        "pingcap/tidb" : "PingCAP/TiDB",
        "tikv/tikv" : "TiKV/TiKV",
        "pingcap/pd" : "PD",
        "pingcap/br" : "PingCAP/BR",
        "pingcap/dumpling" : "PingCAP/Dumpling",
        "pingcap/tidb-lightning" : "PingCAP/Lightning",
        "pingcap/ticdc" : "PingCAP/TiCDC",

        "compatibility-breaker" : "Compatibility Changes",
        "type/bug-fix" : "Bug Fixes",
        "type/enhancement" : "Improvements",
        "type/new-feature" : "New Features"
    },
    "tools": ["pingcap/br", "pingcap/dumpling", "pingcap/tidb-lightning", "pingcap/ticdc"]
}
```

The tool will collect pull requests  that are from repositories in `repo` and are with labels in `labels`. Then the tool will extract the release notes in the body of the pull request and catogarize them by label.

In the dict `alias`, `key` means the 

- repo and `value` means the name you want them show in the final release note. 
- Or the name of a label and `value` means the name of the categories you want show in the final release note. 

