import json
import os
import shutil
# import logging

from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from textwrap import indent

from g3elements.config import SWSystemDictWrapper
from g3elements.config.type_hinting import SystemDict

from ..utils import (
    format_template, write_to_file
)

from g3hardware import HWModule, HWIsle


env = Environment(
    loader=FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates/')
        ),
    keep_trailing_newline=False,
    trim_blocks=True,
    )
env.globals['timestamp'] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def get_system_dict(path: str) -> SystemDict:
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def makedirs_physical(system_name: str) -> str:
    path = os.path.join(
        os.getcwd(),
        'Physical',
        system_name
        )
    os.makedirs(os.path.join(path, 'CPU'), exist_ok=True)
    return path


# TODO: Would be nice to moce to some kind of wrapper

def is_safety_configuration(config_hw: list[dict]) -> bool:
    for isle in config_hw:
        if 'SL8101' in isle['head']['type']:
            return True
    return False


def get_hardware_module_name(module_type: str, config_hw: list[dict]) -> str:
    module_type_lower = module_type.lower()
    for isle in config_hw:
        if module_type_lower in isle['head']['type'].lower():
            head = isle['head']
            return f"{head['type']}_{head['cabinet']}_{head['name_suffix']}"
    raise ValueError(f'Module "{module_type}" data was not found')

# END TODO ##


# Hardware.hw #

def create_hw_isles(config_hw: dict) -> HWIsle | None:
    isles: list[HWIsle] = []
    for isle_data in config_hw:
        module_type = isle_data['head']['type']
        cabinet = isle_data['head']['cabinet']
        name_suffix = isle_data['head']['name_suffix']
        head = HWModule.new(
            module_type=module_type,
            module_name_suffix=f"{cabinet}_{name_suffix}"
            )
        tail = []
        for module_data in isle_data['tail']:
            module_type = module_data['type']
            cabinet = module_data['cabinet']
            name_suffix = module_data['name_suffix']
            module = HWModule.new(
                module_type=module_type,
                module_name_suffix=f"{cabinet}_{name_suffix}"
            )
            tail.append(module)
        isles.append(HWIsle(head, *tail))
    # move the CPU isle to the start of the isle list
    cp1584_isle_i = -1
    for i, isle in enumerate(isles):
        if isle.head.type == 'X20cCP1584':
            cp1584_isle_i = i
            break
    if cp1584_isle_i == -1:
        raise ValueError(
            "X20cCP1584 CPU module was not found in the hardware configuration"
            )
    if cp1584_isle_i != 0:
        isles.insert(0, isles.pop(cp1584_isle_i))
    # connect the isles
    for i, isle in enumerate(isles[:-1]):
        isle.next_isle = isles[i + 1]
    if not isles:
        return None
    return isles[0]


def generate_hardware_hw_contents(
    config_hw: dict, system_name: str, cp1584_name: str
) -> str:
    if not (hw_isle := create_hw_isles(config_hw)):
        return ''
    contents = hw_isle.to_xml_str()
    return contents.format(
        HOST_NAME=f'{system_name}_plc',
        PROJECT_ZONE=system_name,
        CP1584_NAME=cp1584_name
    )

# END Hardware.hw #


# Iomap.iom #

def generate_iomap_iom_contents(system: SWSystemDictWrapper) -> list[str]:
    iomap_lines = []
    for zone, _, device_path, device_data in system.iter_devices_system():
        if zone == 'Common':
            continue
        zone_taskname = system.get_zone_taskname(zone)
        for key, value in device_data['control'].get('iomap', {}).items():
            device_varname = system.get_device_varname(device_data)
            if (
                (
                    'RequestorDigital' in device_path and
                    'inputs' in key and
                    'Safety' not in key
                ) or
                (
                    'GPIO' in device_path
                )
            ):
                device = device_varname
            else:
                device = f'fb{device_varname}'
            iomap_line = f'::{zone_taskname}:{device}.{key} AT {value};'
            iomap_lines.append(indent(iomap_line, '    '))
    return iomap_lines

# END Iomap.iom #


def generate_physical_files(system_config_path: str) -> None:
    system = get_system_dict(system_config_path)
    sw_system_wrapper = SWSystemDictWrapper(system['Software'])
    project_name = sw_system_wrapper.get_project_name()
    system_name = sw_system_wrapper.get_system_name()
    zone_tasknames = sw_system_wrapper.zone_tasknames
    physical_path = makedirs_physical(system_name)
    # create Physical.pkg file
    write_to_file(
        os.path.dirname(physical_path),
        'Physical.pkg',
        format_template(env, 'physical_pkg.tpl', system_names=[system_name])
        )
    # create Config.pkg file
    write_to_file(
        physical_path,
        'Config.pkg',
        format_template(env, 'config_pkg.tpl', cpu_type='CPU')
        )
    # create Hardware.hw and Hardware.hwl files
    cpu_name = get_hardware_module_name(
        'cp1584', system['Hardware']  # type: ignore
        )
    hardware_hw = generate_hardware_hw_contents(
        system['Hardware'], system_name, cpu_name  # type: ignore
        )
    write_to_file(
        physical_path,
        'Hardware.hw',
        format_template(env, 'hardware_hw.tpl', hardware=hardware_hw)
        )
    write_to_file(
        physical_path,
        'Hardware.hwl',
        ''  # create an empty hwl file is enough
        )
    # create Cpu.pkg file
    is_safety = is_safety_configuration(system['Hardware'])  # type: ignore
    physical_cp1584_path = os.path.join(physical_path, 'CPU')
    write_to_file(
        physical_cp1584_path,
        'Cpu.pkg',
        format_template(env, 'cpu_pkg.tpl', add_mapp_safety=is_safety)
        )
    # optionally copy mappSafety:
    if is_safety:
        mapp_safety_path_src = os.path.join(
            os.path.dirname(physical_path), 'Core', 'CPU', 'mappSafety'
            )
        mapp_safety_path_dst = os.path.join(
            physical_path, 'CPU', 'mappSafety'
            )
        shutil.copytree(
            mapp_safety_path_src, mapp_safety_path_dst, dirs_exist_ok=True
            )
        for path in (
            os.path.join(mapp_safety_path_dst, '.git'),
            os.path.join(mapp_safety_path_dst, '.gitignore')
        ):
            if os.path.isfile(path):
                os.remove(path)
        sl_name = get_hardware_module_name(
            'sl8101', system['Hardware']  # type: ignore
            )
        write_to_file(
            mapp_safety_path_dst,
            'Config.sfdomain',
            format_template(env, 'config_sfdomain.tpl', sl8101_name=sl_name)
            )
    # create IoMap.iom file
    iomap = generate_iomap_iom_contents(sw_system_wrapper)
    write_to_file(
        physical_cp1584_path,
        'IoMap.iom',
        format_template(env, 'iomap_iom.tpl', iomap=iomap)
        )
    # create Zone.sw file
    tasks: dict[str, list[tuple[str, str]]] = {
        'tasks_cyclic1': [],
        'tasks_cyclic2': [
            ('Comm', f'{project_name}.{system_name}.Comm.prg')
            ],
        'tasks_cyclic3': [
            ('System', f'{project_name}.{system_name}.System.prg')
            ],
        'tasks_cyclic4': []
    }
    tasks_cyclic4 = tasks['tasks_cyclic4']
    for taskname in zone_tasknames:
        tasks_cyclic4.append(
            (taskname, f'{project_name}.{system_name}.{taskname}.prg')
            )
    libraries_list = sw_system_wrapper.get_project_libraries()
    libraries: list[tuple[str, str]] = []
    for lib in libraries_list:
        lib_cou, lib_name = lib.split('.')
        libraries.append(
            (lib_name, f'Libraries.Specific.{lib_cou}.{lib_name}.lby')
        )
    write_to_file(
        physical_cp1584_path,
        'Zone.sw',
        format_template(env, 'zone_sw.tpl', **tasks, libraries=libraries)
        )
