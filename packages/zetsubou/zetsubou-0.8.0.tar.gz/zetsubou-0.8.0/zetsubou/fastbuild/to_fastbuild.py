from zetsubou.project.model.toolchain import ECompilerFamily


def compiler_family_to_fastbuild(compiler : ECompilerFamily):
    compiler_family = {
         ECompilerFamily.MSVC : 'msvc',
         ECompilerFamily.CLANG : 'clang',
         ECompilerFamily.GCC : 'gcc',
         ECompilerFamily.CUSTOM : 'custom',
    }

    if compiler in compiler_family:
        return compiler_family.get(compiler)

    return 'auto'
