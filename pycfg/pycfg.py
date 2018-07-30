#!/usr/bin/python

"""
PyCFG

An easy way to configure python programs at runtime.
"""

# Copyright (C) 2002 - 2008 Selene Scriven
#
# This program is free software: you can redistribute it and/or modify it under 
# the terms of the GNU Lesser General Public License as published by the Free 
# Software Foundation, either version 3 of the License, or (at your option) any 
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more 
# details.
#
# You should have received a copy of the GNU Lesser General Public License 
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

program_name = "pycfg"
program_version = "0.3"


class config(dict):
    """Configuration manager for python programs.
        This allows you to easily load configuration from multiple config
        files, and access the settings as members of a "cfg" object.

        Quick start example:
            >>> program = "test"
            >>> cfg = config(program)
            >>> cfg.default(one=1, two=2, foo="foo")
            >>> cfg.default(mylist=[3,4,5])
            >>> cfg.one
            1
            >>> print(cfg)
            foo = 'foo'
            mylist = [3, 4, 5]
            one = 1
            two = 2

        Now, load the config file(s).  First, tell it to use the config
        in the current directory.
            >>> cfg._loadpath.append("./%s.conf" % program)
            >>> cfg.load()

        If you've got the included test.conf, a few values should have changed:
            >>> cfg.one
            'One'
            >>> print(cfg)
            foo = 'bar'
            mylist = [3, 4, 5, 'a', 'b']
            one = 'One'
            two = 2
    """
    def __init__(self, name=program_name):
        dict.__init__(self)
        import os
        try:
            home = os.environ["HOME"]
        except:
            home = "/tmp"

        self._defaults = {}
        self._default = KeyError
        self._name = name
        self._loadpath = [
                "/etc/%s/%s.conf" % (self._name, self._name),
                "%s/.%s.conf" % (home, self._name),
                "%s/.%src" % (home, self._name),
                "%s/.%s/rc" % (home, self._name),
                "%s/.%s/%s.conf" % (home, self._name, self._name),
                ]
        self._docs = {}
        self._validate = {}
        self._validators = {
            "boolean": lambda x: x or not x,
            "int": lambda x: isinstance(x, int),
            "float": lambda x: isinstance(x, float),
            "str": lambda x: isinstance(x, str),
            "list": lambda x: isinstance(x, list),
            "tuple": lambda x: isinstance(x, tuple),
            "dict": lambda x: isinstance(x, dict),
            }

    def doc(self, **args):
        """Add documentation or help for an expected config value.
        This value will be displayed in the GUI and written to the config file.
        Usage: cfg.doc(name="text", name2=["line", "line"])

        Tests / Examples:
            >>> cfg = config()
            >>> cfg.default(verbose=0, speed=3)
            >>> cfg.doc(verbose="set the verbosity level")
            >>> cfg.doc(speed=["Go, speed racer!", "Go!"])
            >>> print(cfg)
            # Go, speed racer!
            # Go!
            speed = 3
            <BLANKLINE>
            # set the verbosity level
            verbose = 0
        """
        # store lines as tuples or lists, then join later in __str__()
        for k in args:
            v = args[k]
            if isinstance(v, str):
                v = (v, )
            self._docs[k] = v

    def default(self, *args, **kwargs):
        """Populate config object with default values, or
        set a default for all undefined items.
        Should be used to init required variables before loading config files.
        To raise a KeyError for undefined items, set the undefined default
        to any Exception.

        Example:
            >>> cfg = config()
            >>> cfg.verbose = 1
            >>> cfg.default(verbose=0, mode="monitor")
            >>> print(cfg.mode)
            monitor
            >>> print(cfg.verbose)
            1

        Default for undefined keys:
            >>> cfg.undefined
            Traceback (most recent call last):
              ...
            KeyError: 'undefined'
            >>> cfg.default(None)
            >>> print(cfg.undefined)
            None
            >>> cfg.default(3)
            >>> cfg.undefined
            3
            >>> cfg.default(Exception)
            >>> cfg['undefined']
            Traceback (most recent call last):
              ...
            KeyError: 'undefined'
        """
        for a in args:
            self._default = a

        import copy
        for k in kwargs.keys():
            v = kwargs[k]
            # TODO: if v is not mutable, save the original
            self._defaults[k] = copy.copy(v)
            if k not in self: self[k] = v

    # TODO: find a better name...  require?  assert?
    def check(self, **args):
        """Add a rule for validating data.
            Usage: cfg.check(myint="int", custom=lambda x: x > 30)
            Built-in test names are:
                boolean, int, float, str, list, tuple, dict
            See cfg.validate() for more details.
        """
        for k in args:
            v = args[k]
            if isinstance(v, str):
                func = self._validators[v]
                self._validate[k] = func
            else:
                self._validate[k] = v

    def validate(self):
        """Make sure all config data passes validation tests.
            Returns True on success, or raises ValueError otherwise.

            Tests / Examples:
                >>> cfg = config()

            Do built-in tests work?
                >>> cfg.default(goodint=3, badfloat="three")
                >>> cfg.check(goodint="int", badfloat="float")
                >>> cfg.validate()
                Traceback (most recent call last):
                 ...
                ValueError: object badfloat failed validation
                >>> cfg.badfloat = 3.0
                >>> cfg.validate()
                True

            Do arbitrary tests work?
                >>> cfg.default(digit=23)
                >>> cfg.doc(digit="must be 0-9")
                >>> cfg.check(digit = lambda x: x >= 0 and x < 10)
                >>> cfg.validate()
                Traceback (most recent call last):
                 ...
                ValueError: object digit failed validation: must be 0-9
                >>> cfg.digit = 8
                >>> cfg.validate()
                True
        """
        for k in self._validate:
            import sys
            func = self._validate[k]
            data = getattr(self, k)
            if not func(data):
                try: d = ": " + '\n'.join(self._docs[k])
                except KeyError: d = ""
                raise ValueError("object %s failed validation" % (k) + d)
        return True

    def merge_opts(self, opts):
        """Copy data from an optparse.OptionParser's options, after it has
        parsed the command line.  This is an easy way to allow command-line
        parameters override config values.

        Example:
            >>> cfg = config()
            >>> cfg.default(verbose=False)
            >>> from optparse import OptionParser
            >>> cli = OptionParser()
            >>> o = cli.add_option("-v", "--verbose", action="store_true")
            >>> (opts, args) = cli.parse_args(["-v"])
            >>> cfg.verbose
            False
            >>> cfg.merge_opts(opts)
            >>> print(cfg)
            verbose = True
        """
        # copy option data to config (override cfg)
        self.update(opts.__dict__)

    def load(self, path=None):
        """Search for and execute config files, and save the results.
        Will load files in the order specified by self._loadpath.  System-wide
        config files should be listed first, before user-specific files.
        """
        if path:
            self._parse(path)

        else:
            import os.path
            for name in self._loadpath:
                if os.path.exists(name):
                    self._parse(name)

    def _parse(self, filename):
        """Load an individual config file.
        Prints a traceback on error, waits for the user to press Enter, then
        continues to load the rest of the config files."""
        try:
            ns = {}
            ns.update(self)
            #execfile(filename, ns)
            exec(open(filename).read(), ns)
            self.update(ns)
        except:
            print("Error in config file %s" % filename)
            import traceback
            import sys
            foo = traceback.format_exception(*sys.exc_info())
            for item in foo:
                item = item[:-1]
                print(item)
            print("Press Enter to continue...")
            input()

    def save(self, path=None, include_defaults=True):
        """Save str(self) to 'path', or to one of the files in the load path.
        Will search from the end, overwriting the first file which exists.
        """
        if path:
            self._save(path, include_defaults)

        else:
            import os.path
            look = self._loadpath[:]
            look.reverse()
            for name in look:
                if os.path.exists(name):
                    self._save(name, include_defaults)
                    break

    def _save(self, path, include_defaults=True):
        if include_defaults: text = str(self)
        else: text = self.__str__(include_defaults=False)
        fp = open(path, "wb")
        fp.write(text)
        fp.write('\n')
        fp.close()
        return text

    def __getattr__(self, k):
        """Return self.k if _private.  Return self[k] otherwise.
        """
        if k.startswith('_'):
            return dict.__getattribute__(self, k)
        else:
            return self.__getitem__(k)

    def __getitem__(self, k):
        """Return self[k] if defined, or default value otherwise.
        """
        try:
            return dict.__getitem__(self, k)
        except KeyError as e:
            if type(self._default) == type(Exception):
                raise
            else:
                return self._default

    def __setattr__(self, k, v):
        """Set self.k if _private; or set self[k] otherwise.
        """
        if k.startswith('_'):
            return dict.__setattr__(self, k, v)
        else:
            return self.__setitem__(k, v)

    def __setitem__(self, k, v):
        """Set self[k] = v.  If v is the default value, delete self[k].
        """
        if v is self._default:
            del self[k]
        else:
            return dict.__setitem__(self, k, v)

    def __str__(self, include_defaults=True):
        """Format self as a plain-text config file.
        """
        import pprint as pp
        text = ""
        syms = self.keys()
        # include deleted defaults, if they have a value
        if type(self._default) != type(Exception):
            syms.extend(self._defaults.keys())
            syms = list(set(syms))  # remove dupes
        syms.sort()
        for k in syms:
            if k[0] != "_":
                if not include_defaults:
                    if (k in self._defaults) and \
                        (self[k] == self._defaults[k]):
                            continue
                if k in self._docs:
                    d = self._docs[k]
                    d = "# " + "\n# ".join(d)
                    text = text + "%s\n" % (d)
                key = "%s" % (k)
                val = "%s\n" % (pp.pformat(self[k]))
                # hide classes and other non-printables
                if not val.startswith("<"):
                    text = text + key + " = " + val
                if k in self._docs: text = text + "\n"
        text = text.strip()
        return text

    def edit_gui(self):
        """Allow the user to edit config values in a friendly GUI.
        Not yet functional."""
        import gtk
        self._build_gui()
        self._populate_gui()
        gtk.mainloop()

    def _build_gui(self):
        import gtk
        w = gtk.Window()
        w.set_title("PyCFG GUI: %s" % (self._name))
        w.connect("destroy", self._destroy_win)
        w.set_default_size(400, 400)
        self._win = w

        vb = gtk.VBox()
        w.add(vb)
        self._vb = vb

        self._build_menus()

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self._sw = sw
        vb.add(sw)

        t = gtk.Table()
        self._values = t
        sw.add_with_viewport(t)

        ab = gtk.Button("Add")
        ke = gtk.Entry()
        ve = gtk.Entry()
        ke.set_text("name")
        ve.set_text("value")
        t.attach(ke, 0, 1, 65530, 65531, 0, 0)
        t.attach(ve, 1, 2, 65530, 65531, 0, 0)
        t.attach(ab, 2, 3, 65530, 65531, 0, 0)

        l = gtk.Label("Note: this program does not actually work yet")
        vb.pack_start(l, 0, 0)

        w.show_all()

    def _build_menus(self):
        import gtk
        ag = gtk.AccelGroup()
        self._win.add_accel_group(ag)
        itemf = gtk.ItemFactory(gtk.MenuBar, "<main>", ag)
        itemf.create_items([
                ("/File", None, None, 0, "<Branch>"),
                ("/File/_Save", "<Control>S", None, 0, ""),
                ("/File/Save _As", "<Control>A", None, 0, ""),
                ("/File/_Quit", "<Control>Q", self._destroy_win, 0, ""),
                ("/Help", None, None, 0, "<LastBranch>"),
                ("/Help/About", None, None, 0, ""),
                ])
        mb = itemf.get_widget("<main>")
        self._vb.pack_start(mb, 0, 1)
        self._menubar = mb

    def _populate_gui(self):
        import gtk
        keys = self.keys()
        keys.sort()
        row = 0
        for k in keys:
            if k[:1] == "_": continue
            v = self[k]
            if isinstance(v, type(gtk)): continue
            # TODO: handle each data type specially
            #print "%s: %s" % (k,v)
            row += 1
            b = gtk.Button("del")
            l = gtk.Label(k)
            e = gtk.Entry()
            e.set_text(repr(v))
            self._values.attach(l, 0, 1, row, row + 1, 0, 0)
            self._values.attach(e, 1, 2, row, row + 1, 0, 0)
            self._values.attach(b, 2, 3, row, row + 1, 0, 0)
        self._win.show_all()

    def _destroy_win(self, *args):
        import gtk
        self._win.unrealize()
        while gtk.events_pending(): gtk.mainiteration()
        gtk.mainquit()


def main(args):
    """Edit config data for each program listed in 'args',
    or execute cfg doctests (if args==['test'])."""
    if args: programs = args
    else: programs = [program_name]
    if args[:1] == ["test"]:
        return _test()
    for p in programs:
        cfg = config(p)
        cfg.load()
        cfg.edit_gui()


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
