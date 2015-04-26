#  _____     _               
# |  _  |___| |_ _ _ ___ ___ 
# |     |  _|  _| | |  _| . |
# |__|__|_| |_| |___|_| |___|
# http://32bits.io/Arturo/
#
import platform
import re

from ano import i18n


_ = i18n.language.ugettext

# +---------------------------------------------------------------------------+
# | System
# +---------------------------------------------------------------------------+
class System(object):
    
    def __init__(self, toolchain, systemMetadata, console):
        super(System, self).__init__()
        self._host = systemMetadata['host']
        self._url = systemMetadata['url']
        self._toolchain = toolchain
        self._console = console
        
    def getToolChain(self):
        return self._toolchain
    
    def getHost(self):
        return self._host
    
    def getUrl(self):
        return self._url

# +---------------------------------------------------------------------------+
# | ToolChain
# +---------------------------------------------------------------------------+
class ToolChain(object):
    
    # Map of host names (made all lowercase) returned from Python's platform.system method 
    # (https://docs.python.org/2/library/platform.html) to patterns matching host names
    # found in the package_index.json file.
    # The patterns themselves are then indexed by machine type (e.g. x86_64) and some patterns are repeated
    # where the machine can support them (e.g. 32 bit archiectures being usable by 64 bit machines but not
    # vice-versa).
    # Note that the pattern lists are a *prioritized list* of matches. That is, the first match will
    # be used even if subsequent matches could be made.
    #
    # Original logic taken from Arduino source at https://github.com/arduino/Arduino/blob/3788128385d0ca21f4652246f205f838d7c4cf54/arduino-core/src/cc/arduino/contributions/packages/HostDependentDownloadableContribution.java
    #
    
    HOST_PATTERNS = {"darwin"  :{ "x86_64"     :[ "^x86_64-apple-darwin.*",
                                                  "i[3456]86-apple-darwin.*"
                                                ],
                                  "i[3456]86"  :[ "i[3456]86-apple-darwin.*",
                                                ],
                                },
                     "windows" :{ ".*"         :[ "i[3456]86-.*mingw32",
                                                  "i[3456]86-.*cygwin"
                                                ],
                                },
                     "linux"   :{ "amd64"      :[ "x86_64-.*linux-gnu",
                                                ],
                                  ".*"         :[ "i[3456]86-.*linux-gnu",
                                                ],
                                },
                    }
    
    def __init__(self, package, toolChainMetadata, console):
        super(ToolChain, self).__init__()
        self._name = toolChainMetadata['name']
        self._version = toolChainMetadata['version']
        self._package = package
        self._systems = dict()
        self._console = console
        self._hostSystem = None
        for system in toolChainMetadata['systems']:
            self._systems[system['host']] = System(self, system, console) 
        
    def getName(self):
        return self._name
    
    def getPackage(self):
        return self._package

    def getVersion(self):
        return self._version
    
    def getCurrentHostName(self):
        return platform.system().lower()
        
    def getSystemForHost(self):
        if self._hostSystem == -1:
            return None
        elif self._hostSystem is not None:
            return self._hostSystem

        compiledHostPatterns = ToolChain._compileHostPatterns(ToolChain.HOST_PATTERNS, platform.system())
        if compiledHostPatterns:
            machine = platform.machine()
            for machinePattern, compiledHostPatternsList in compiledHostPatterns.iteritems():
                if machinePattern.match(machine):
                    for compiledHostPattern in compiledHostPatternsList:
                        for systemKey in self._systems.iterkeys():
                            if compiledHostPattern.match(systemKey):
                                self._hostSystem = self._systems[systemKey]
                                return self._hostSystem
        # mark as "not found" so we don't try to match it again.
        self._hostSystem = -1
        return None
        
    # +-----------------------------------------------------------------------+
    # | PRIVATE
    # +-----------------------------------------------------------------------+
    @classmethod
    def _compileHostPatterns(cls, rawHostPatterns, forHost):
        compiledMachineIndex = None
        machineIndex = rawHostPatterns.get(forHost.lower())
        if machineIndex:
            compiledMachineIndex = dict()
            for machinePattern, hostPatterns in machineIndex.iteritems():
                compiledHostPatterns = list()
                for hostPattern in hostPatterns:
                    compiledHostPatterns.append(re.compile(hostPattern))
                compiledMachineIndex[re.compile(machinePattern)] = compiledHostPatterns
        return compiledMachineIndex
        
    