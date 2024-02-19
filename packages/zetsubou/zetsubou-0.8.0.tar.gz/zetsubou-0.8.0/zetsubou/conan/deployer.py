import os
from typing import Optional
from conan import ConanFile
from conan.tools.files import save


def emit_list(lst):
    return '\n       - '.join(lst)


def emit_property(out, prop, tmpl):
    if prop is not None and len(prop) > 0:
        out.append(tmpl.format(data = emit_list(prop)))


def fix_no_ext(libs, paths):
    results = []
    for path in paths:
        for _, _, filenames in os.walk(path):
            for file in filenames:
                for lib in libs:
                    if file.find(lib) != -1:
                        results.append(os.path.basename(file))
    return results


def _emit_cpp_info(dep_cpp_info):
    sections = []
    emit_property(sections, dep_cpp_info.includedirs,
        '    includes:\n'
        '       interface:\n'
        '       - {data}\n')

    emit_property(sections, dep_cpp_info.defines,
        '    defines:\n'
        '       interface:\n'
        '       - {data}\n')

    emit_property(sections, dep_cpp_info.cxxflags,
        '    compiler_flags:\n'
        '       interface:\n'
        '       - {data}\n')

    emit_property(sections, fix_no_ext(dep_cpp_info.libs, dep_cpp_info.libdirs),
        '    link_libraries:\n'
        '       interface:\n'
        '       - {data}\n')

    emit_property(sections, dep_cpp_info.libdirs,
        '    linker_paths:\n'
        '       interface:\n'
        '       - {data}\n')

    emit_property(sections, dep_cpp_info.sharedlinkflags + dep_cpp_info.exelinkflags,
        '    linker_flags:\n'
        '       interface:\n'
        '       - {data}\n')

    emit_property(sections, dep_cpp_info.bindirs,
        '    distribute_files:\n'
        '       patterns:\n'
        '       - "*"\n'
        '       paths:\n'
        '       - {data}\n')

    return sections


def generate_dependencies(conanfile: ConanFile):
    result = {}

    for _, dependency in conanfile.dependencies.items():

        components = []
        for comp_key, component in dependency.cpp_info.components.items():
            if comp_key is None:
                continue

            comp_name = f"{dependency.ref.name}{comp_key}".replace("-", "_")

            components.append(comp_name)

            sections = _emit_cpp_info(component)
            result[f'{comp_name}.part.yml'] = ''.join(sections)

        sections = _emit_cpp_info(dependency.cpp_info)

        emit_property(sections, components,
        '    dependencies:\n'
        '       interface:\n'
        '       - {data}\n')

        dep_name = dependency.ref.name.replace("-", "_")
        result[f'{dep_name}.part.yml'] = ''.join(sections)

    return result


def generate(conanfile:ConanFile, output_folder:Optional[str] = None):
    generator_files = generate_dependencies(conanfile)

    generate_folder = conanfile.folders.generators_folder if output_folder is None else output_folder

    for generator_file, content in generator_files.items():
        save(conanfile, os.path.join(generate_folder, generator_file), content)


# Conan 2.0 - Deployer entrypoint
def deploy(graph, output_folder: str, **kwargs):
    conanfile = graph.root.conanfile
    generate(conanfile, output_folder)


# Used to inject deployer into conan
def get_conan_deployer_path():
    return os.path.realpath(__file__)
