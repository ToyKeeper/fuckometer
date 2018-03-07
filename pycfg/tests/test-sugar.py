#!/usr/bin/env python

"Test misc syntactic sugar in pycfg."

from nose.tools import raises
import pycfg


def setup():
    global cfg
    cfg = pycfg.config('test-sugar')

    cfg.default(foo='foo')


def test_contains_default():
    assert('foo' in cfg)


def test_contains_custom():
    cfg.foo2 = 'foo2'
    assert('foo2' in cfg)


def test_contains_missing():
    assert('nonexistent' not in cfg)


def test_len():
    c = pycfg.config()
    c.default(one=1, two=2)
    assert len(c) == 2


def test_iter_equals_len():
    l = len(cfg)
    i = 0
    for item in cfg:
        i += 1
    assert(i == l)


def test_default_doesnt_overwrite():
    cfg.defined = 1
    cfg.default(defined=2)
    assert(cfg.defined == 1)


def test_setattr():
    cfg.setattr_blah = 3
    assert cfg['setattr_blah'] == 3


def test_getattr():
    assert cfg.foo == 'foo'


def test_setitem():
    cfg['setitem_blah'] = 3
    assert(cfg.setitem_blah == 3)


def test_getitem():
    assert(cfg['foo'] == 'foo')


def test_private():
    "_private keys work only with cfg['_foo'] syntax"
    cfg._private = 'private'
    assert '_private' not in cfg
    cfg['_priv2'] = 'priv2'
    assert '_priv2' in cfg


def test_default_value():
    cfg.default(None)
    assert cfg.doesnt_exist == None
    cfg.default(3)
    assert cfg.doesnt_exist == 3


@raises(KeyError)
def test_default_exception():
    cfg.default(KeyError)  # set a default exception
    if cfg.doesnt_exist:
        assert 0


def test_delete_default():
    cfg.default(None)
    cfg.delme = 3
    assert 'delme' in cfg
    cfg.delme = None
    assert 'delme' not in cfg


def teardown():
    pass
