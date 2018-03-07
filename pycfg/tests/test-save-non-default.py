#!/usr/bin/env python

program_name = 'pycfgtest'

# TODO: test actual saving
#cfg.save_non_default()

from pycfg import config


def set_defaults(cfg):
    cfg.default(foo="foo")
    cfg.default(bar="bar")
    cfg.default(mylist=[1])
    cfg.default(otherlist=[1])


def setup():
    global cfg
    cfg = config(program_name)
    set_defaults(cfg)
    cfg.bar = "bar2"
    cfg.quux = "quux2"
    cfg.mylist.append(2)
    global all
    global trimmed
    all = str(cfg)
    trimmed = cfg.__str__(include_defaults=False)


def test_default_not_saved():
    assert("foo = 'foo'" in all)
    assert("foo = 'foo'" not in trimmed)


def test_non_default_saved():
    assert("bar = 'bar2'" in trimmed)


def test_value_saved_when_no_default_exists():
    assert("quux = 'quux2'" in trimmed)


def test_mutable_default_modified():
    assert("mylist = [1, 2]" in trimmed)


def test_mutable_default_not_modified():
    assert("otherlist" not in trimmed)


def test_deleted_by_default():
    cfg.default(bob='Bob')
    assert "bob = 'Bob'" in str(cfg)
    # delete the value...  is it still saved?
    cfg.default(None)
    cfg.bob = None  # same as "del cfg['bob']"
    assert "bob = None" in str(cfg)
    # omitted entirely when the default is an exception
    cfg.default(KeyError)
    assert "bob =" not in str(cfg)
