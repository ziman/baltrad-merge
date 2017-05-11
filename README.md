# baltrad-merge

A set of utilities for merging data files coming from Baltrad.

## Installation

1. Install Docker: `https://docs.docker.com/engine/installation/mac/`
2. Pull the Docker image: `docker pull ziman/baltrad-merge`
3. Clone baltrad-merge: `https://github.com/ziman/baltrad-merge`
4. To run, go to directory: `cd baltrad-merge`


## Synopsis

```bash
./recurse.py INPUT OUTPUT WORKDIR --radar RADAR --date-from YYYY/MM/DD --date-to YYYY/MM/DD
```

* `INPUT`: path to input directory
* `OUTPUT`: path to output directory
* `WORKDIR`: path to work directory, will be cleaned up after every run (unless interrupted)
* `--radar` can be specified in multiple ways
	* specify country, eg. `--radar fr`
    * specify radar within country, eg. `--radar frbou`
    * any combination of the above, eg. `--radar 'nl|seang|sevar|frbou|frge'` -- needs the apostrophes! (or double quotes)
* `--date-from YYYY/MM/DD` will start from 00:00 of that day
* `--date-to: YYYY/MM/DD` will stop at 24:00 of that day

## Expected directory structure for `--date-from` and `--date-to`

If you are specifying `--date-from` or `--date-to` (or both), the `INPUT`
directory must contain a hierarchical directory structure in the form
`YYYY/MM/DD`.  For example:

* `INPUT/2016/09/21/01/00/bejab_.....h5` is okay
* `INPUT/2016/09/21/myradar/bejab_.....h5` is okay
* `INPUT/myradar/09/21/12/bejab_.....h5` is not okay

In other words, the first three directories subordinate to `INPUT` will be interpreted as `YYYY/MM/DD` if (and only if) `--date-from` or `--date-to` are given.
