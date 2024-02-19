# Simple yaml writer with no dependencies
# Can be used in Conan generator
from typing import List
from enum import Enum


def is_enum(obj):
    if obj is None:
        return False
    return isinstance(obj, Enum)


def is_obj(obj):
    if obj is None:
        return False
    return hasattr(obj, '__dict__')


def is_list(obj):
    if obj is None:
        return False
    return isinstance(obj, list)


class _yaml_context:
    buffer: List[str] = []
    cur_indent: int = 0
    DEF_INDENT = 2
    prefix_once = None

    def push_obj(self, obj):
        self.cur_indent += self.DEF_INDENT

    def pop_obj(self, obj):
        self.cur_indent -= self.DEF_INDENT

    def assign(self, key:str, val=None):
        indent = self.cur_indent
        prefix = ''

        if self.prefix_once is not None:
            prefix = self.prefix_once
            self.prefix_once = None
            indent -= len(prefix)

        if val is None:
            self.buffer.append(f'{" " * indent}{prefix}{key}:')
        else:
            self.buffer.append(f'{" " * indent}{prefix}{key}: {str(val)}')


def _handle_key_val(ctx:_yaml_context, key:str, val):
    if val is None:
        return
    if is_enum(val):
        ctx.assign(key, val.name)
    elif is_list(val):
        if len(val) == 0:
            return
        ctx.assign(key)
        ctx.push_obj(val)
        for sub_obj in val:
            ctx.prefix_once = '- '
            _handle_obj(ctx, sub_obj)
        ctx.pop_obj(val)
    elif is_obj(val):
        ctx.assign(key)
        ctx.push_obj(val)
        _handle_obj(ctx, val)
        ctx.pop_obj(val)
    else:
        ctx.assign(key, val)


def _handle_obj(ctx:_yaml_context, obj):
    for name, value in vars(obj).items():
        _handle_key_val(ctx, name, value)


def to_yaml(obj) -> str:
    ctx = _yaml_context()
    _handle_obj(ctx, obj)
    return '\n'.join(ctx.buffer)
