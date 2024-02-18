
import os
from test.test_init.kraken_testfn import kraken_testfn
from test.test_init.kraken_testfn.Class_kraken_testfn import Testfn
from test.test_init.kraken_testfn.Class_kraken_testfns import Testfns


"""
Project structure created by kraken_init

To dos
1. Configure pypi package publishing
- Todo: Configure github pypi publish action - DONE 
- Todo: Create pypi token (https://pypi.org/manage/account/)
- Todo: Add pypi api token to github secret (https://github.com/tactik8/krakentestfn/settings/secrets/actions)

2. Configure google cloud
- Todo: Create new cloud run service (https://console.cloud.google.com/run?project=kraken-v2-369412)

3. Add packages 
- Todo: Add required packages to setup.py
- Todo: Add required packages to requirements.txt
"""

def test():
    """Perform tests
    """
    os.system("pip install pytest")
    os.system("python -m pytest kraken_testfn* -vv")


#test()

#flask_routes.run_api()

testfn = Testfn()

testfns = Testfns()

    

import os

"""
Project structure created by kraken_init

To dos
1. Configure pypi package publishing
- Todo: Configure github pypi publish action - DONE 
- Todo: Create pypi token (https://pypi.org/manage/account/)
- Todo: Add pypi api token to github secret (https://github.com/tactik8/krakenfunction/settings/secrets/actions)

2. Configure google cloud
- Todo: Create new cloud run service (https://console.cloud.google.com/run?project=kraken-v2-369412)

3. Add packages 
- Todo: Add required packages to setup.py
- Todo: Add required packages to requirements.txt
"""

def test():
    """Perform tests
    """
    os.system("pip install pytest")
    os.system("python -m pytest kraken_function* -vv")


#test()

import kraken_init

#kraken_init.init('kraken_testfn', True, 'test/test_init')

from test.test_init.kraken_testfn import kraken_testfn as m

from test.test_init.kraken_testfn.class_kraken_testfn import Testfn
from test.test_init.kraken_testfn.class_kraken_testfns import Testfns

t = Testfn()

tt = Testfns()

for i in t:
    print(t._id)

tt.set(t)
tt.set(t)

for i in tt:
    print(i._id)
    