from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from shutil import copyfile
import os

class A52decConan(ConanFile):
    name = "a52dec"
    version = "0.7.4"
    description = "a52dec is a test program for liba52. It decodes ATSC A/52 streams, "
    "and also includes a demultiplexer for mpeg-1 and mpeg-2 program streams"
    url = "https://github.com/conan-multimedia/a52dec"
    homepage = "http://liba52.sourceforge.net/"
    license = "GPLv2Plus"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"

    source_subfolder = "source_subfolder"

    def source(self):
        url = 'http://liba52.sourceforge.net/files/{name}-{version}.tar.gz'
        tools.get(url.format(name =self.name, version =self.version))
        os.rename( self.name + "-" + self.version, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({'LIBS' : "-lm"}):
                self.run("autoreconf -f -i")

                _args = ["--prefix=%s/builddir"%(os.getcwd()), "--with-pic", "--disable-silent-rules", "--enable-introspection"]
                if self.options.shared:
                    _args.extend(['--enable-shared=yes','--enable-static=no'])
                else:
                    _args.extend(['--enable-shared=no','--enable-static=yes'])

                autotools = AutoToolsBuildEnvironment(self)
                autotools.fpic = True
                autotools.configure(args=_args)
                autotools.make(args=["-j4"])
                autotools.install()

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

