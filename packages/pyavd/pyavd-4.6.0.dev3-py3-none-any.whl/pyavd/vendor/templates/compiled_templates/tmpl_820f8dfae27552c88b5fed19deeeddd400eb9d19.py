from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/policy-maps-qos.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_policy_maps = resolve('policy_maps')
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
        t_3 = environment.filters['lower']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'lower' found.")
    try:
        t_4 = environment.filters['replace']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'replace' found.")
    pass
    l_1_loop = missing
    for l_1_policy_map, l_1_loop in LoopContext(t_2(environment.getattr((undefined(name='policy_maps') if l_0_policy_maps is missing else l_0_policy_maps), 'qos'), 'name'), undefined):
        _loop_vars = {}
        pass
        yield '!\npolicy-map type quality-of-service '
        yield str(environment.getattr(l_1_policy_map, 'name'))
        yield '\n'
        l_2_loop = missing
        for l_2_class, l_2_loop in LoopContext(t_1(environment.getattr(l_1_policy_map, 'classes'), []), undefined):
            _loop_vars = {}
            pass
            if (environment.getattr(l_2_loop, 'index') > 1):
                pass
                yield '   !\n'
            yield '   class '
            yield str(environment.getattr(l_2_class, 'name'))
            yield '\n'
            for l_3_set in t_1(environment.getattr(l_2_class, 'set'), []):
                l_3_cli_set = missing
                _loop_vars = {}
                pass
                l_3_cli_set = t_3(t_4(context.eval_ctx, l_3_set, '_', '-'))
                _loop_vars['cli_set'] = l_3_cli_set
                if ((undefined(name='cli_set') if l_3_cli_set is missing else l_3_cli_set) in ['cos', 'dscp', 'traffic-class', 'drop-precedence']):
                    pass
                    yield '      set '
                    yield str((undefined(name='cli_set') if l_3_cli_set is missing else l_3_cli_set))
                    yield ' '
                    yield str(environment.getitem(environment.getattr(l_2_class, 'set'), l_3_set))
                    yield '\n'
            l_3_set = l_3_cli_set = missing
        l_2_loop = l_2_class = missing
    l_1_loop = l_1_policy_map = missing

blocks = {}
debug_info = '7=37&9=41&10=44&11=47&14=51&15=53&16=57&17=59&18=62'