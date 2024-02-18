from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/router-isis.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_router_isis = resolve('router_isis')
    l_0_lu_cli = resolve('lu_cli')
    l_0_ti_lfa_cli = resolve('ti_lfa_cli')
    l_0_ti_lfa_srlg_cli = resolve('ti_lfa_srlg_cli')
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
    if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'instance')):
        pass
        yield '!\nrouter isis '
        yield str(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'instance'))
        yield '\n'
        if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'net')):
            pass
            yield '   net '
            yield str(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'net'))
            yield '\n'
        if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'is_type')):
            pass
            yield '   is-type '
            yield str(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'is_type'))
            yield '\n'
        for l_1_redistribute_route in t_1(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'redistribute_routes'), 'source_protocol'):
            l_1_redistribute_route_cli = resolve('redistribute_route_cli')
            _loop_vars = {}
            pass
            if t_2(environment.getattr(l_1_redistribute_route, 'source_protocol')):
                pass
                l_1_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_1_redistribute_route, 'source_protocol'), ))
                _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                if (environment.getattr(l_1_redistribute_route, 'source_protocol') == 'isis'):
                    pass
                    l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' instance', ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                elif (environment.getattr(l_1_redistribute_route, 'source_protocol') == 'ospf'):
                    pass
                    if t_2(environment.getattr(l_1_redistribute_route, 'include_leaked'), True):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' include leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if (not t_2(environment.getattr(l_1_redistribute_route, 'ospf_route_type'))):
                        pass
                        continue
                    l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' match ', environment.getattr(l_1_redistribute_route, 'ospf_route_type'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                elif (environment.getattr(l_1_redistribute_route, 'source_protocol') == 'ospfv3'):
                    pass
                    if (not t_2(environment.getattr(l_1_redistribute_route, 'ospf_route_type'))):
                        pass
                        continue
                    l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' match ', environment.getattr(l_1_redistribute_route, 'ospf_route_type'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                elif (environment.getattr(l_1_redistribute_route, 'source_protocol') in ['static', 'connected']):
                    pass
                    if t_2(environment.getattr(l_1_redistribute_route, 'include_leaked'), True):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' include leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                if t_2(environment.getattr(l_1_redistribute_route, 'route_map')):
                    pass
                    l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' route-map ', environment.getattr(l_1_redistribute_route, 'route_map'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                yield '   '
                yield str((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli))
                yield '\n'
        l_1_redistribute_route = l_1_redistribute_route_cli = missing
        if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'router_id')):
            pass
            yield '   router-id ipv4 '
            yield str(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'router_id'))
            yield '\n'
        if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'log_adjacency_changes'), True):
            pass
            yield '   log-adjacency-changes\n'
        elif t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'log_adjacency_changes'), False):
            pass
            yield '   no log-adjacency-changes\n'
        if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'mpls_ldp_sync_default'), True):
            pass
            yield '   mpls ldp sync default\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'timers'), 'local_convergence'), 'protected_prefixes'), True):
            pass
            if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'timers'), 'local_convergence'), 'delay')):
                pass
                yield '   timers local-convergence-delay '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'timers'), 'local_convergence'), 'delay'))
                yield ' protected-prefixes\n'
            else:
                pass
                yield '   timers local-convergence-delay protected-prefixes\n'
        if t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'advertise'), 'passive_only'), True):
            pass
            yield '   advertise passive-only\n'
        if t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'spf_interval'), 'interval')):
            pass
            if t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'spf_interval'), 'wait_interval')):
                pass
                yield '   spf-interval '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'spf_interval'), 'interval'))
                yield ' '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'spf_interval'), 'wait_interval'))
                yield '\n'
            else:
                pass
                yield '   spf-interval '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'spf_interval'), 'interval'))
                yield '\n'
        if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart')):
            pass
            if t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 'enabled'), True):
                pass
                yield '   graceful-restart\n'
            if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 't2'), 'level_1_wait_time')):
                pass
                yield '   graceful-restart t2 level-1 '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 't2'), 'level_1_wait_time'))
                yield '\n'
            if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 't2'), 'level_2_wait_time')):
                pass
                yield '   graceful-restart t2 level-2 '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 't2'), 'level_2_wait_time'))
                yield '\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 'restart_hold_time')):
                pass
                yield '   graceful-restart restart-hold-time '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 'restart_hold_time'))
                yield '\n'
        yield '   !\n'
        if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family')):
            pass
            for l_1_address_family in environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family'):
                _loop_vars = {}
                pass
                yield '   address-family '
                yield str(l_1_address_family)
                yield '\n'
                if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'isis_af_defaults')):
                    pass
                    for l_2_af_default in environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'isis_af_defaults'):
                        _loop_vars = {}
                        pass
                        yield '      '
                        yield str(l_2_af_default)
                        yield '\n'
                    l_2_af_default = missing
            l_1_address_family = missing
            yield '   !\n'
        if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4')):
            pass
            yield '   address-family ipv4 unicast\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'maximum_paths')):
                pass
                yield '      maximum-paths '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'maximum_paths'))
                yield '\n'
            if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'tunnel_source_labeled_unicast'), 'enabled'), True):
                pass
                l_0_lu_cli = 'tunnel source-protocol bgp ipv4 labeled-unicast'
                context.vars['lu_cli'] = l_0_lu_cli
                context.exported_vars.add('lu_cli')
                if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'tunnel_source_labeled_unicast'), 'rcf')):
                    pass
                    l_0_lu_cli = str_join(((undefined(name='lu_cli') if l_0_lu_cli is missing else l_0_lu_cli), ' rcf ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'tunnel_source_labeled_unicast'), 'rcf'), ))
                    context.vars['lu_cli'] = l_0_lu_cli
                    context.exported_vars.add('lu_cli')
                yield '      '
                yield str((undefined(name='lu_cli') if l_0_lu_cli is missing else l_0_lu_cli))
                yield '\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'bfd_all_interfaces'), True):
                pass
                yield '      bfd all-interfaces\n'
            if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'mode')):
                pass
                l_0_ti_lfa_cli = str_join(('fast-reroute ti-lfa mode ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'mode'), ))
                context.vars['ti_lfa_cli'] = l_0_ti_lfa_cli
                context.exported_vars.add('ti_lfa_cli')
                if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'level')):
                    pass
                    l_0_ti_lfa_cli = str_join(((undefined(name='ti_lfa_cli') if l_0_ti_lfa_cli is missing else l_0_ti_lfa_cli), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'level'), ))
                    context.vars['ti_lfa_cli'] = l_0_ti_lfa_cli
                    context.exported_vars.add('ti_lfa_cli')
                yield '      '
                yield str((undefined(name='ti_lfa_cli') if l_0_ti_lfa_cli is missing else l_0_ti_lfa_cli))
                yield '\n'
            if t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'srlg'), 'enable'), True):
                pass
                l_0_ti_lfa_srlg_cli = 'fast-reroute ti-lfa srlg'
                context.vars['ti_lfa_srlg_cli'] = l_0_ti_lfa_srlg_cli
                context.exported_vars.add('ti_lfa_srlg_cli')
                if t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'srlg'), 'strict'), True):
                    pass
                    l_0_ti_lfa_srlg_cli = str_join(((undefined(name='ti_lfa_srlg_cli') if l_0_ti_lfa_srlg_cli is missing else l_0_ti_lfa_srlg_cli), ' strict', ))
                    context.vars['ti_lfa_srlg_cli'] = l_0_ti_lfa_srlg_cli
                    context.exported_vars.add('ti_lfa_srlg_cli')
                yield '      '
                yield str((undefined(name='ti_lfa_srlg_cli') if l_0_ti_lfa_srlg_cli is missing else l_0_ti_lfa_srlg_cli))
                yield '\n'
            yield '   !\n'
        if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6')):
            pass
            yield '   address-family ipv6 unicast\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'maximum_paths')):
                pass
                yield '      maximum-paths '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'maximum_paths'))
                yield '\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'bfd_all_interfaces'), True):
                pass
                yield '      bfd all-interfaces\n'
            if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'mode')):
                pass
                l_0_ti_lfa_cli = str_join(('fast-reroute ti-lfa mode ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'mode'), ))
                context.vars['ti_lfa_cli'] = l_0_ti_lfa_cli
                context.exported_vars.add('ti_lfa_cli')
                if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'level')):
                    pass
                    l_0_ti_lfa_cli = str_join(((undefined(name='ti_lfa_cli') if l_0_ti_lfa_cli is missing else l_0_ti_lfa_cli), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'level'), ))
                    context.vars['ti_lfa_cli'] = l_0_ti_lfa_cli
                    context.exported_vars.add('ti_lfa_cli')
                yield '      '
                yield str((undefined(name='ti_lfa_cli') if l_0_ti_lfa_cli is missing else l_0_ti_lfa_cli))
                yield '\n'
            if t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'srlg'), 'enable'), True):
                pass
                l_0_ti_lfa_srlg_cli = 'fast-reroute ti-lfa srlg'
                context.vars['ti_lfa_srlg_cli'] = l_0_ti_lfa_srlg_cli
                context.exported_vars.add('ti_lfa_srlg_cli')
                if t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'srlg'), 'strict'), True):
                    pass
                    l_0_ti_lfa_srlg_cli = str_join(((undefined(name='ti_lfa_srlg_cli') if l_0_ti_lfa_srlg_cli is missing else l_0_ti_lfa_srlg_cli), ' strict', ))
                    context.vars['ti_lfa_srlg_cli'] = l_0_ti_lfa_srlg_cli
                    context.exported_vars.add('ti_lfa_srlg_cli')
                yield '      '
                yield str((undefined(name='ti_lfa_srlg_cli') if l_0_ti_lfa_srlg_cli is missing else l_0_ti_lfa_srlg_cli))
                yield '\n'
            yield '   !\n'
        if t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'segment_routing_mpls')):
            pass
            yield '   segment-routing mpls\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'segment_routing_mpls'), 'enabled'), True):
                pass
                yield '      no shutdown\n'
            elif t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'segment_routing_mpls'), 'enabled'), False):
                pass
                yield '      shutdown\n'
            for l_1_prefix_segment in t_1(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'segment_routing_mpls'), 'prefix_segments'), 'prefix'):
                _loop_vars = {}
                pass
                if (t_2(environment.getattr(l_1_prefix_segment, 'prefix')) and t_2(environment.getattr(l_1_prefix_segment, 'index'))):
                    pass
                    yield '      prefix-segment '
                    yield str(environment.getattr(l_1_prefix_segment, 'prefix'))
                    yield ' index '
                    yield str(environment.getattr(l_1_prefix_segment, 'index'))
                    yield '\n'
            l_1_prefix_segment = missing

blocks = {}
debug_info = '7=27&9=30&10=32&11=35&13=37&14=40&16=42&17=46&18=48&19=50&20=52&21=54&22=56&23=58&25=60&26=62&28=63&29=65&30=67&31=69&33=70&34=72&35=74&36=76&39=78&40=80&42=83&45=86&46=89&48=91&50=94&53=97&56=100&57=102&58=105&63=110&66=113&67=115&68=118&70=125&73=127&74=129&77=132&78=135&80=137&81=140&83=142&84=145&88=148&89=150&90=154&91=156&92=158&93=162&99=167&101=170&102=173&104=175&105=177&106=180&107=182&109=186&111=188&114=191&115=193&116=196&117=198&119=202&121=204&122=206&123=209&124=211&126=215&130=218&132=221&133=224&135=226&138=229&139=231&140=234&141=236&143=240&145=242&146=244&147=247&148=249&150=253&154=256&156=259&158=262&161=265&162=268&163=271'