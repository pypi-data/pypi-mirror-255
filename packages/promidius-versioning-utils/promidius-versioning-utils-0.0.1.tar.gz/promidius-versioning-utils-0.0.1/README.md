# versioning-utils
Repository to host my python versioning package and upload to pyPi

Useful to keep track of the version of your python packages in your projects.

Supported file structure:

```
project root
├── src
│   └── package_name
│       ├── __init__.py
│       └── __version__.py
│
├── tests
│   └── ...
│
├── versions_metadata.json
└── ...
```

You can have versions_metadata.json in the root of your project, or other place you desire as long as you pass it to the function

Creates a simple json:
```json
{
  "package_name": {
      "version": "<version>",
      "commit_hash": "<comit_hash>"
    }
}
```

Convenient way to keep track of extensions versions in your projects.

