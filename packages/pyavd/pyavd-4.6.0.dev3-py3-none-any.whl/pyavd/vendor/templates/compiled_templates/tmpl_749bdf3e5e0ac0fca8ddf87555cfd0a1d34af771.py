from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/policy-maps-qos.j2'

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
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_3(environment.getattr((undefined(name='policy_maps') if l_0_policy_maps is missing else l_0_policy_maps), 'qos')):
        pass
        yield '\n### QOS Policy Maps\n\n#### QOS Policy Maps Summary\n'
        for l_1_policy_map in t_2(environment.getattr((undefined(name='policy_maps') if l_0_policy_maps is missing else l_0_policy_maps), 'qos'), 'name'):
            _loop_vars = {}
            pass
            yield '\n##### '
            yield str(environment.getattr(l_1_policy_map, 'name'))
            yield '\n\n| class | Set | Value |\n| ----- | --- | ----- |\n'
            for l_2_class in t_1(environment.getattr(l_1_policy_map, 'classes'), []):
                _loop_vars = {}
                pass
                for l_3_set in t_1(environment.getattr(l_2_class, 'set'), []):
                    _loop_vars = {}
                    pass
                    yield '| '
                    yield str(environment.getattr(l_2_class, 'name'))
                    yield ' | '
                    yield str(l_3_set)
                    yield ' | '
                    yield str(environment.getitem(environment.getattr(l_2_class, 'set'), l_3_set))
                    yield ' |\n'
                l_3_set = missing
            l_2_class = missing
        l_1_policy_map = missing
        yield '\n#### QOS Policy Maps Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/policy-maps-qos.j2', 'documentation/policy-maps-qos.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {})):
            yield event
        yield '```\n'

blocks = {}
debug_info = '7=30&12=33&14=37&18=39&19=42&20=46&28=56'