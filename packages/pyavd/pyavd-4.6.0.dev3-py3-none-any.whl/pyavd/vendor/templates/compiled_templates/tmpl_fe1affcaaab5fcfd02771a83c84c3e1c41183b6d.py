from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/arp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_arp = resolve('arp')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['groupby']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'groupby' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if (t_3(environment.getattr(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'aging'), 'timeout_default')) or t_3(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'static_entries'))):
        pass
        yield '\n### ARP\n'
        if t_3(environment.getattr(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'aging'), 'timeout_default')):
            pass
            yield '\nGlobal ARP timeout: '
            yield str(environment.getattr(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'aging'), 'timeout_default'))
            yield '\n'
        if t_3(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'static_entries')):
            pass
            for l_1_entry in environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'static_entries'):
                _loop_vars = {}
                pass
                if (not t_3(environment.getattr(l_1_entry, 'vrf'))):
                    pass
                    context.call(environment.getattr(l_1_entry, 'update'), {'vrf': 'default'}, _loop_vars=_loop_vars)
            l_1_entry = missing
            yield '\n#### ARP Static Entries\n\n| VRF | IPv4 address | MAC address |\n| --- | ------------ | ----------- |\n'
            for (l_1_vrf, l_1_entries) in t_1(t_2(environment, environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'static_entries'), 'vrf')):
                _loop_vars = {}
                pass
                for l_2_entry in t_1(l_1_entries, 'ipv4_address'):
                    _loop_vars = {}
                    pass
                    yield '| '
                    yield str(l_1_vrf)
                    yield ' | '
                    yield str(environment.getattr(l_2_entry, 'ipv4_address'))
                    yield ' | '
                    yield str(environment.getattr(l_2_entry, 'mac_address'))
                    yield ' |\n'
                l_2_entry = missing
            l_1_vrf = l_1_entries = missing
        yield '\n#### ARP Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/arp.j2', 'documentation/arp.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {})):
            yield event
        yield '```\n'

blocks = {}
debug_info = '7=30&10=33&12=36&14=38&16=40&17=43&18=45&26=48&27=51&28=55&36=64'