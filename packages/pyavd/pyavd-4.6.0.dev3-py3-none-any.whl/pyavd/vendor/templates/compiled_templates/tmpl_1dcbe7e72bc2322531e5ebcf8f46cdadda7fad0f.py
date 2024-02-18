from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ip-nat-part2.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_nat = resolve('ip_nat')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_2((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat)):
        pass
        yield '!\n'
        for l_1_pool in t_1(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'pools'), []):
            _loop_vars = {}
            pass
            if (t_2(environment.getattr(l_1_pool, 'name')) and t_2(environment.getattr(l_1_pool, 'prefix_length'))):
                pass
                yield 'ip nat pool '
                yield str(environment.getattr(l_1_pool, 'name'))
                yield ' prefix-length '
                yield str(environment.getattr(l_1_pool, 'prefix_length'))
                yield '\n'
                for l_2_range in t_1(environment.getattr(l_1_pool, 'ranges'), []):
                    l_2_range_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_range_cli = str_join(('range ', environment.getattr(l_2_range, 'first_ip'), ' ', environment.getattr(l_2_range, 'last_ip'), ))
                    _loop_vars['range_cli'] = l_2_range_cli
                    if (t_2(environment.getattr(l_2_range, 'first_port')) and t_2(environment.getattr(l_2_range, 'last_port'))):
                        pass
                        l_2_range_cli = str_join(((undefined(name='range_cli') if l_2_range_cli is missing else l_2_range_cli), ' ', environment.getattr(l_2_range, 'first_port'), ' ', environment.getattr(l_2_range, 'last_port'), ))
                        _loop_vars['range_cli'] = l_2_range_cli
                    yield '   '
                    yield str((undefined(name='range_cli') if l_2_range_cli is missing else l_2_range_cli))
                    yield '\n'
                l_2_range = l_2_range_cli = missing
                if t_2(environment.getattr(l_1_pool, 'utilization_log_threshold')):
                    pass
                    yield '   utilization threshold '
                    yield str(environment.getattr(l_1_pool, 'utilization_log_threshold'))
                    yield ' action log\n'
        l_1_pool = missing
        if t_2(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization')):
            pass
            yield 'ip nat synchronization\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'description')):
                pass
                yield '   description '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'description'))
                yield '\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'expiry_interval')):
                pass
                yield '   expiry-interval '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'expiry_interval'))
                yield '\n'
            if t_1(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'shutdown'), False):
                pass
                yield '   shutdown\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'peer_address')):
                pass
                yield '   peer-address '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'peer_address'))
                yield '\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'local_interface')):
                pass
                yield '   local-interface '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'local_interface'))
                yield '\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range')):
                pass
                if (t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'first_port')) and t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'last_port'))):
                    pass
                    yield '   port-range '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'first_port'))
                    yield ' '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'last_port'))
                    yield '\n'
                if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'split_disabled'), False):
                    pass
                    yield '   port-range split disabled\n'

blocks = {}
debug_info = '7=24&9=27&10=30&11=33&12=37&13=41&14=43&15=45&17=48&19=51&20=54&24=57&26=60&27=63&29=65&30=68&32=70&35=73&36=76&38=78&39=81&41=83&42=85&44=88&46=92'