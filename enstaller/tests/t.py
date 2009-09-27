import os

from enstaller.indexed_repo import Chain, Req, filename_dist
import enstaller.indexed_repo.requirement as requirement


cwd = os.getcwd()

c = Chain(verbose=0)
for fn in ['index-add.txt', 'index-5.1.txt', 'index-5.0.txt']:
    c.add_repo('file://%s/' % cwd, fn)
# c.test()

def test_req(req, expected):
    print repr(req)
    files = [filename_dist(d) for d in c.install_order(req, True)]
    if expected != files:
        print "Expected:", expected
        print "Got:", files

# -----

requirement.PY_VER = '2.5'

test_req(Req('scipy 0.8.0.dev5698'), [
        'freetype-2.3.7-1.egg', 'libjpeg-7.0-1.egg', 'numpy-1.3.0-1.egg',
        'PIL-1.1.6-4.egg', 'scipy-0.8.0.dev5698-1.egg'])

test_req(Req('scipy'), ['numpy-1.3.0-1.egg', 'scipy-0.8.0-1.egg'])

test_req(Req('epdcore'), [
        'AppInst-2.0.4-1.egg', 'numpy-1.3.0-1.egg', 'scipy-0.8.0-1.egg',
        'EPDCore-1.2.5-1.egg'])

requirement.PY_VER = '2.6'

test_req(Req('scipy'), ['numpy-1.3.0-2.egg', 'scipy-0.8.0-2.egg'])

test_req(Req('epdcore'), [
        'numpy-1.3.0-2.egg', 'scipy-0.8.0-2.egg', 'EPDCore-2.0.0-1.egg'])
