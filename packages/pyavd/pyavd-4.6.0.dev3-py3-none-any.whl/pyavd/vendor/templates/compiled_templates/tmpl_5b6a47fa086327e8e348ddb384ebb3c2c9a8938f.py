from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/arp.j2'

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
    if t_3(environment.getattr(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'aging'), 'timeout_default')):
        pass
        yield '!\narp aging timeout default '
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
        for (l_1_vrf, l_1_entries) in t_1(t_2(environment, environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'static_entries'), 'vrf')):
            _loop_vars = {}
            pass
            for l_2_entry in t_1(l_1_entries, 'ipv4_address'):
                l_2_arp_entry_prefix = missing
                _loop_vars = {}
                pass
                l_2_arp_entry_prefix = 'arp'
                _loop_vars['arp_entry_prefix'] = l_2_arp_entry_prefix
                if (l_1_vrf != 'default'):
                    pass
                    l_2_arp_entry_prefix = str_join(((undefined(name='arp_entry_prefix') if l_2_arp_entry_prefix is missing else l_2_arp_entry_prefix), ' vrf ', l_1_vrf, ))
                    _loop_vars['arp_entry_prefix'] = l_2_arp_entry_prefix
                yield str((undefined(name='arp_entry_prefix') if l_2_arp_entry_prefix is missing else l_2_arp_entry_prefix))
                yield ' '
                yield str(environment.getattr(l_2_entry, 'ipv4_address'))
                yield ' '
                yield str(environment.getattr(l_2_entry, 'mac_address'))
                yield ' arpa\n'
            l_2_entry = l_2_arp_entry_prefix = missing
        l_1_vrf = l_1_entries = missing

blocks = {}
debug_info = '7=30&9=33&11=35&13=37&14=40&15=42&18=44&20=47&21=51&22=53&23=55&25=57'