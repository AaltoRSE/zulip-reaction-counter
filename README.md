# Zulip reaction counter

This counts reactions in Zulip and produces a report.  By default the
report lists all reactions and it's up to you to wrangle the data as
you see fit.

## Installation

```
pip install https://github.com/AaltoRSE/zulip-reaction-counter/archives/main
```

## Usage

Give it a zuliprc file and it outputs a csv file to stdout, currently
covering all history.  It starts with the most recent history and
works backwards in time.  Use `-h` to see more options, if any.

```
$ python reaction-counter.py ~/zuliprc
```
```
#stream,sender,reactor,reaction,timestamp
events,NAME1,NAME2,heart,1632736155
events,NAME1,NAME2,hand,1632736155
python-for-scicomp,NAME3,NAME4,ok,1632735570
coderefinery,NAME3,NAME5,+1,1632729055

```

## Status

Works but is a draft without extensive testing.  Let me know features
you need (or add it yourself).  For example:

* Limit to certain channels or a given narrow
* Automatically aggregate results by sender, receiver, or emoji


## See also

* Zulip API docs on getting messages: https://zulip.com/api/get-messages
