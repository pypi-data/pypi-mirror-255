# Copyright (c) 2023, Riverbank Computing Limited
# All rights reserved.
#
# This copy of SIP is licensed for use under the terms of the SIP License
# Agreement.  See the file LICENSE for more details.
#
# This copy of SIP may also used under the terms of the GNU General Public
# License v2 or v3 as published by the Free Software Foundation which can be
# found in the files LICENSE-GPL2 and LICENSE-GPL3 included in this package.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import os

from setuptools import find_packages, setup


# Get the version number.
version_file_name = os.path.join('sipbuild', 'version.py')
try:
    version_file = open(version_file_name)
    version = version_file.read().strip().split('\n')[1].split()[-1][1:-1]
    version_file.close()
except FileNotFoundError:
    # Provide a minimal version file.
    version = '0.1.0.dev0'
    version_file = open(version_file_name, 'w')
    version_file.write('SIP_VERSION = 0\nSIP_VERSION_STR = \'%s\'\n' % version)
    version_file.close()

# Do the setup.
setup(
        name='sip',
        version=version,
        license='SIP',
        python_requires='>=3.7',
        install_requires=['packaging', 'setuptools',
                'tomli;python_version<"3.11"'],
        packages=find_packages(),
        package_data={
            'sipbuild.module': ['source/*/*'],
        },
        entry_points={
            'console_scripts': [
                'sip-distinfo = sipbuild.distinfo.main:main',
                'sip-module = sipbuild.module.main:main',
                'sip-build = sipbuild.tools.build:main',
                'sip-install = sipbuild.tools.install:main',
                'sip-sdist = sipbuild.tools.sdist:main',
                'sip-wheel = sipbuild.tools.wheel:main']
        }
     )
