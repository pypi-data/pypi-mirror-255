from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/as-path.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_as_path = resolve('as_path')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_3((undefined(name='as_path') if l_0_as_path is missing else l_0_as_path)):
        pass
        yield '!\n'
        if t_3(environment.getattr((undefined(name='as_path') if l_0_as_path is missing else l_0_as_path), 'regex_mode')):
            pass
            yield 'ip as-path regex-mode '
            yield str(environment.getattr((undefined(name='as_path') if l_0_as_path is missing else l_0_as_path), 'regex_mode'))
            yield '\n'
        for l_1_as_path_access_list in t_2(environment.getattr((undefined(name='as_path') if l_0_as_path is missing else l_0_as_path), 'access_lists'), 'name'):
            _loop_vars = {}
            pass
            if (t_3(environment.getattr(l_1_as_path_access_list, 'name')) and t_3(environment.getattr(l_1_as_path_access_list, 'entries'))):
                pass
                for l_2_as_path_access_list_entry in environment.getattr(l_1_as_path_access_list, 'entries'):
                    l_2_as_path_access_list_cli = resolve('as_path_access_list_cli')
                    _loop_vars = {}
                    pass
                    if (t_3(environment.getattr(l_2_as_path_access_list_entry, 'type')) and t_3(environment.getattr(l_2_as_path_access_list_entry, 'match'))):
                        pass
                        l_2_as_path_access_list_cli = str_join(('ip as-path access-list ', environment.getattr(l_1_as_path_access_list, 'name'), ))
                        _loop_vars['as_path_access_list_cli'] = l_2_as_path_access_list_cli
                        l_2_as_path_access_list_cli = str_join(((undefined(name='as_path_access_list_cli') if l_2_as_path_access_list_cli is missing else l_2_as_path_access_list_cli), ' ', environment.getattr(l_2_as_path_access_list_entry, 'type'), ))
                        _loop_vars['as_path_access_list_cli'] = l_2_as_path_access_list_cli
                        l_2_as_path_access_list_cli = str_join(((undefined(name='as_path_access_list_cli') if l_2_as_path_access_list_cli is missing else l_2_as_path_access_list_cli), ' ', environment.getattr(l_2_as_path_access_list_entry, 'match'), ))
                        _loop_vars['as_path_access_list_cli'] = l_2_as_path_access_list_cli
                        l_2_as_path_access_list_cli = str_join(((undefined(name='as_path_access_list_cli') if l_2_as_path_access_list_cli is missing else l_2_as_path_access_list_cli), ' ', t_1(environment.getattr(l_2_as_path_access_list_entry, 'origin'), 'any'), ))
                        _loop_vars['as_path_access_list_cli'] = l_2_as_path_access_list_cli
                        yield str((undefined(name='as_path_access_list_cli') if l_2_as_path_access_list_cli is missing else l_2_as_path_access_list_cli))
                        yield '\n'
                l_2_as_path_access_list_entry = l_2_as_path_access_list_cli = missing
        l_1_as_path_access_list = missing

blocks = {}
debug_info = '7=30&9=33&10=36&12=38&13=41&14=43&15=47&16=49&17=51&18=53&19=55&20=57'