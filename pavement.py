# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import os
import requests
import zipfile
import io
import shutil

from paver.easy import *


options(
    plugin = Bunch(
        name = 'lessons',
        source_dir = path('lessons'),
        package_dir = path('.'),
        tests = ['test'],
        ext_libs = path('lessons/ext-libs'),
        ext_src = path('lessons/ext-src'),
        lessons = ['_lessons'],
        excludes = [
            '*.pyc',
            '.git',
            '*.pro',
            'ext_src',
        ],
        # skip certain files inadvertently found by exclude pattern globbing
        skip_exclude = []
    ),
    sphinx = Bunch(
        docroot = path('docs'),
        sourcedir = path('docs/source'),
        builddir = path('docs/build')
    )
)


def read_requirements():
    """Return a list of runtime and list of test requirements"""
    lines = path('requirements.txt').lines()
    lines = [ l for l in [ l.strip() for l in lines] if l ]
    divider = '# test requirements'

    try:
        idx = lines.index(divider)
    except ValueError:
        raise BuildFailure(
            'Expected to find "%s" in requirements.txt' % divider)

    not_comments = lambda s,e: [ l for l in lines[s:e] if l[0] != '#']
    return not_comments(0, idx), not_comments(idx+1, None)


def _install(folder):
    '''install plugin to qgis'''
    builddocs(options)
    plugin_name = options.plugin.name
    src = path(__file__).dirname() / plugin_name
    dst = path('~').expanduser() / folder / 'python' / 'plugins' / plugin_name
    src = src.abspath()
    dst = dst.abspath()
    if not hasattr(os, 'symlink'):
        dst.rmtree()
        src.copytree(dst)
    elif not dst.exists():
        src.symlink(dst)
    # Symlink the build folder to the parent
    docs = path('..') / '..' / "docs" / 'build' / 'html'
    docs_dest = path(__file__).dirname() / plugin_name / "docs"
    docs_link = docs_dest / 'html'
    if not docs_dest.exists():
        docs_dest.mkdir()
    if not docs_link.islink():
        docs.symlink(docs_link)


@task
def install(options):
    _install(".qgis2")

@task
def installdev(options):
    _install(".qgis-dev")

@task
def install3(options):
    _install(".qgis3")

@task
def install_lessons(options):
    """Install sample lessons to QGIS plugin directory
    """
    src = path(__file__).dirname() / "examplelessons"
    dst = path('~').expanduser() / '.qgis2' / 'python' / 'plugins' / "examplelessons"
    src = src.abspath()
    dst = dst.abspath()
    if hasattr(src, 'symlink'):
        src.symlink(dst)
    else:
        dst.rmtree()
        src.copy(dst)

@task
def setup():
    """Install run-time dependencies"""
    clean = getattr(options, 'clean', False)
    ext_libs = options.plugin.ext_libs
    ext_src = options.plugin.ext_src
    if clean:
        ext_libs.rmtree()
    ext_libs.makedirs()

    runtime, test = read_requirements()
    os.environ['PYTHONPATH']=ext_libs.abspath()
    for req in runtime + test:
        sh('easy_install -a -d %(ext_libs)s %(dep)s' % {
            'ext_libs' : ext_libs.abspath(),
            'dep' : req
        })

@task
def install_devtools():
    """Install development tools
    """
    try:
        import pip
    except:
        error('FATAL: Unable to import pip, please install it first!')
        sys.exit(1)

    pip.main(['install', '-r', 'requirements-dev.txt'])


@task
@cmdopts([
    ('tests', 't', 'Package tests with plugin'),
    ('lessons', 'n', 'Package lessons with plugin')
])
def package(options):
    """Create plugin package
    """
    builddocs(options)
    package_file = options.plugin.package_dir / ('%s.zip' % options.plugin.name)
    with zipfile.ZipFile(package_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        if not hasattr(options.package, 'lessons'):
            options.plugin.excludes.extend(options.plugin.lessons)
        else:
            lessonsPath = os.path.abspath("./lessons/_lessonstemp")
            if os.path.exists(lessonsPath):
                shutil.rmtree(lessonsPath)
            # fix_print_with_import
            print("Downloading lessons...")
            r = requests.get("https://github.com/boundlessgeo/desktop-lessons/archive/master.zip", stream=True)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(path=lessonsPath)
            dstBase = "./lessons/_lessons"
            for f in os.listdir(os.path.join(lessonsPath, "desktop-lessons-master")):
                src = os.path.join(lessonsPath, "desktop-lessons-master", f)
                if os.path.isdir(src):
                    dst = os.path.join(dstBase, f)
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
            shutil.rmtree(lessonsPath)
        if not hasattr(options.package, 'tests'):
            options.plugin.excludes.extend(options.plugin.tests)
        _make_zip(zf, options)
    return package_file


@task
@consume_args
def pep8(args):
    """Check code for PEP8 violations
    """
    try:
        import pep8
    except:
        error('pep8 not found! Run "paver install_devtools".')
        sys.exit(1)

    # Errors to ignore
    ignore = ['E203', 'E121', 'E122', 'E123', 'E124', 'E125', 'E126', 'E127',
        'E128', 'E402']
    styleguide = pep8.StyleGuide(ignore=ignore,
                                 exclude=['*/ext-libs/*', '*/ext-src/*'],
                                 repeat=True, max_line_length=79,
                                 parse_argv=args)
    styleguide.input_dir(options.plugin.source_dir)
    info('===== PEP8 SUMMARY =====')
    styleguide.options.report.print_statistics()


@task
@consume_args
def autopep8(args):
    """Format code according to PEP8
    """
    try:
        import autopep8
    except:
        error('autopep8 not found! Run "paver install_devtools".')
        sys.exit(1)

    if any(x not in args for x in ['-i', '--in-place']):
        args.append('-i')

    args.append('--ignore=E261,E265,E402,E501')
    args.insert(0, 'dummy')

    cmd_args = autopep8.parse_args(args)

    excludes = ('ext-lib', 'ext-src')
    for p in options.plugin.source_dir.walk():
        if any(exclude in p for exclude in excludes):
            continue

        if p.fnmatch('*.py'):
            autopep8.fix_file(p, options=cmd_args)


@task
@consume_args
def pylint(args):
    """Check code for errors and coding standard violations
    """
    try:
        from pylint import lint
    except:
        error('pylint not found! Run "paver install_devtools".')
        sys.exit(1)

    if not 'rcfile' in args:
        args.append('--rcfile=pylintrc')

    args.append(options.plugin.source_dir)
    lint.Run(args)


def _make_zip(zipFile, options):
    excludes = set(options.plugin.excludes)
    skips = options.plugin.skip_exclude

    src_dir = options.plugin.source_dir
    exclude = lambda p: any([path(p).fnmatch(e) for e in excludes])
    def filter_excludes(root, items):
        if not items:
            return []
        # to prevent descending into dirs, modify the list in place
        for item in list(items):  # copy list or iteration values change
            itempath = path(os.path.relpath(root)) / item
            if exclude(item) and item not in skips:
                debug('Excluding %s' % itempath)
                items.remove(item)
        return items

    for root, dirs, files in os.walk(src_dir):
        for f in filter_excludes(root, files):
            relpath = os.path.relpath(root)
            zipFile.write(path(root) / f, path(relpath) / f)
        filter_excludes(root, dirs)

    for root, dirs, files in os.walk(options.sphinx.builddir):
        for f in files:
            relpath = os.path.join(options.plugin.name, "docs", os.path.relpath(root, options.sphinx.builddir))
            zipFile.write(path(root) / f, path(relpath) / f)

@task
def builddocs(options):
    sh("git submodule init")
    sh("git submodule update")
    cwd = os.getcwd()
    os.chdir(options.sphinx.docroot)
    sh("make html")
    os.chdir(cwd)
