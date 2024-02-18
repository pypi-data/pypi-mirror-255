from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/monitor-connectivity.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_monitor_connectivity = resolve('monitor_connectivity')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_2((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity)):
        pass
        yield '!\nmonitor connectivity\n'
        if t_2(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'interval')):
            pass
            yield '   interval '
            yield str(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'interval'))
            yield '\n'
        if t_2(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'shutdown'), False):
            pass
            yield '   no shutdown\n'
        elif t_2(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'shutdown'), True):
            pass
            yield '   shutdown\n'
        for l_1_interface_set in t_1(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'interface_sets'), 'name'):
            _loop_vars = {}
            pass
            if (t_2(environment.getattr(l_1_interface_set, 'name')) and t_2(environment.getattr(l_1_interface_set, 'interfaces'))):
                pass
                yield '   interface set '
                yield str(environment.getattr(l_1_interface_set, 'name'))
                yield ' '
                yield str(environment.getattr(l_1_interface_set, 'interfaces'))
                yield '\n'
        l_1_interface_set = missing
        if t_2(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'local_interfaces')):
            pass
            yield '   local-interfaces '
            yield str(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'local_interfaces'))
            yield ' address-only default\n'
        for l_1_host in t_1(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'hosts'), 'name'):
            _loop_vars = {}
            pass
            if t_2(environment.getattr(l_1_host, 'name')):
                pass
                yield '   !\n   host '
                yield str(environment.getattr(l_1_host, 'name'))
                yield '\n'
                if t_2(environment.getattr(l_1_host, 'description')):
                    pass
                    yield '      description\n      '
                    yield str(environment.getattr(l_1_host, 'description'))
                    yield '\n'
                if t_2(environment.getattr(l_1_host, 'local_interfaces')):
                    pass
                    yield '      local-interfaces '
                    yield str(environment.getattr(l_1_host, 'local_interfaces'))
                    yield ' address-only\n'
                if t_2(environment.getattr(l_1_host, 'ip')):
                    pass
                    yield '      ip '
                    yield str(environment.getattr(l_1_host, 'ip'))
                    yield '\n'
                if t_2(environment.getattr(l_1_host, 'url')):
                    pass
                    yield '      url '
                    yield str(environment.getattr(l_1_host, 'url'))
                    yield '\n'
        l_1_host = missing
        for l_1_vrf in t_1(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'vrfs'), 'name'):
            _loop_vars = {}
            pass
            if t_2(environment.getattr(l_1_vrf, 'name')):
                pass
                yield '   vrf '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield '\n'
                for l_2_interface_set in t_1(environment.getattr(l_1_vrf, 'interface_sets'), 'name'):
                    _loop_vars = {}
                    pass
                    if (t_2(environment.getattr(l_2_interface_set, 'name')) and t_2(environment.getattr(l_2_interface_set, 'interfaces'))):
                        pass
                        yield '      interface set '
                        yield str(environment.getattr(l_2_interface_set, 'name'))
                        yield ' '
                        yield str(environment.getattr(l_2_interface_set, 'interfaces'))
                        yield '\n'
                l_2_interface_set = missing
                if t_2(environment.getattr(l_1_vrf, 'local_interfaces')):
                    pass
                    yield '      local-interfaces '
                    yield str(environment.getattr(l_1_vrf, 'local_interfaces'))
                    yield ' address-only default\n'
                if t_2(environment.getattr(l_1_vrf, 'description')):
                    pass
                    yield '      description\n      '
                    yield str(environment.getattr(l_1_vrf, 'description'))
                    yield '\n'
                for l_2_host in t_1(environment.getattr(l_1_vrf, 'hosts'), 'name'):
                    _loop_vars = {}
                    pass
                    if t_2(environment.getattr(l_2_host, 'name')):
                        pass
                        yield '      !\n      host '
                        yield str(environment.getattr(l_2_host, 'name'))
                        yield '\n'
                        if t_2(environment.getattr(l_2_host, 'description')):
                            pass
                            yield '         description\n         '
                            yield str(environment.getattr(l_2_host, 'description'))
                            yield '\n'
                        if t_2(environment.getattr(l_2_host, 'local_interfaces')):
                            pass
                            yield '         local-interfaces '
                            yield str(environment.getattr(l_2_host, 'local_interfaces'))
                            yield ' address-only\n'
                        if t_2(environment.getattr(l_2_host, 'ip')):
                            pass
                            yield '         ip '
                            yield str(environment.getattr(l_2_host, 'ip'))
                            yield '\n'
                        if t_2(environment.getattr(l_2_host, 'url')):
                            pass
                            yield '         url '
                            yield str(environment.getattr(l_2_host, 'url'))
                            yield '\n'
                l_2_host = missing
        l_1_vrf = missing

blocks = {}
debug_info = '7=24&10=27&11=30&13=32&15=35&18=38&19=41&20=44&23=49&24=52&26=54&27=57&29=60&30=62&32=65&34=67&35=70&37=72&38=75&40=77&41=80&45=83&46=86&47=89&48=91&49=94&50=97&53=102&54=105&56=107&58=110&60=112&61=115&63=118&64=120&66=123&68=125&69=128&71=130&72=133&74=135&75=138'