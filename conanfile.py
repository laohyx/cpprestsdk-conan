# File borrowed from CppRestSdk/2.8.0@ViaviSolutions/stable

from conans import ConanFile, CMake
from conans.tools import download, unzip
import os
import shutil
import zipfile

class CppRestSdkConan(ConanFile):
    name = "CppRestSdk"
    version = '2.8.0'
    license = 'Apache License 2.0'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {"shared": [True, False]}
    default_options = "shared=False"
    exports = 'CMakeLists.txt'
    generators = "cmake"
    requires = ('Boost/1.59.0@lasote/stable',
    'OpenSSL/1.0.2h@lasote/stable')

    def config(self):
        self.options["Boost"].shared = self.options.shared
        self.options["OpenSSL"].shared = self.options.shared
        self.options["OpenSSL"].zlib_dynamic = self.options.shared
        self.options["OpenSSL"].no_electric_fence = True

    def source(self):
        zip_name = 'cpprestsdk-{}.zip'.format(self.version)
        url = 'https://github.com/Microsoft/cpprestsdk/archive/v{}.zip'.format(self.version)
        download(url, zip_name)
        z = zipfile.ZipFile(zip_name, 'r')
        # if os.name == 'nt':
        #     z.extractall(os.path.join('\\\\?\\', os.getcwd()))
        # else:
        z.extractall()
        # print(os.listdir('cpprestsdk-{}/Release'.format(self.version)))
        # unzip(zip_name)
        shutil.move('cpprestsdk-{}'.format(self.version), 'cpprestsdk')
        # print(os.listdir('cpprestsdk/Release'))
        # os.unlink(zip_name)
        shutil.move(
            'cpprestsdk/Release/CMakeLists.txt',
            'cpprestsdk/Release/CMakeListsOriginal.cmake')
        shutil.move('CMakeLists.txt', 'cpprestsdk/Release/CMakeLists.txt')

    def build(self):
        if self.settings.os == "Linux":
            num_cores = 0
            with open('/proc/cpuinfo') as cpuinfo:
                for line in cpuinfo:
                    if line.startswith('processor'):
                        num_cores += 1
        else:
            num_cores = 1
        cmake = CMake(self.settings)
        cmake_options = '-DBUILD_TESTS=OFF -DBUILD_SAMPLES=OFF'
        if self.options.shared:
            cmake_options += ' -DBUILD_SHARED_LIBS=ON'
        else:
            cmake_options += ' -DBUILD_SHARED_LIBS=OFF'
        self.run('cd cpprestsdk/Release && cmake . %s %s' % (cmake.command_line, cmake_options))
        self.run('cd cpprestsdk/Release && cmake --build . %s' % (cmake.build_config))

    def package(self):
        self.copy("*", dst="include/cpprest", src="cpprestsdk/Release/include/cpprest", keep_path=False)
        self.copy("*", dst="include/cpprest/details", src="cpprestsdk/Release/include/cpprest/details", keep_path=False)
        self.copy("*", dst="include/pplx", src="cpprestsdk/Release/include/pplx", keep_path=False)
        if self.options.shared:
            libraries = [
                'libcpprest.so',
                'libcpprest.so.2.8',
                ]
            for lib in libraries:
                self.copy(lib, dst="lib", src="cpprestsdk/Release/Binaries/")
        else:
            self.copy('libcpprest.a', dst="lib", src="cpprestsdk/Release/lib/")

    def package_info(self):
        self.cpp_info.cppflags = ["-std=c++11"]
        if self.options.shared:
            self.cpp_info.libs = ["cpprest", "boost_system", "ssl", "crypto"]
        else:
            self.cpp_info.libs = ["cpprest", "boost_system", "boost_thread", "ssl", "crypto", "pthread", "dl"]
