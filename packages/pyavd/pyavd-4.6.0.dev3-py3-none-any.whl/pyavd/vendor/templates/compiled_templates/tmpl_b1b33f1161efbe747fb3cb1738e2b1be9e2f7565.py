from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/router-isis.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_router_isis = resolve('router_isis')
    l_0_ethernet_interfaces = resolve('ethernet_interfaces')
    l_0_vlan_interfaces = resolve('vlan_interfaces')
    l_0_loopback_interfaces = resolve('loopback_interfaces')
    l_0_node_sid_loopbacks = resolve('node_sid_loopbacks')
    l_0_rcf = resolve('rcf')
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
        t_3 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_4 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_5 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_5((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis)):
        pass
        yield '\n### Router ISIS\n\n#### Router ISIS Summary\n\n| Settings | Value |\n| -------- | ----- |\n'
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'instance')):
            pass
            yield '| Instance | '
            yield str(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'instance'))
            yield ' |\n'
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'net')):
            pass
            yield '| Net-ID | '
            yield str(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'net'))
            yield ' |\n'
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'is_type')):
            pass
            yield '| Type | '
            yield str(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'is_type'))
            yield ' |\n'
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family')):
            pass
            yield '| Address Family | '
            yield str(t_3(context.eval_ctx, environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family'), ', '))
            yield ' |\n'
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'router_id')):
            pass
            yield '| Router-ID | '
            yield str(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'router_id'))
            yield ' |\n'
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'log_adjacency_changes')):
            pass
            yield '| Log Adjacency Changes | '
            yield str(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'log_adjacency_changes'))
            yield ' |\n'
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'mpls_ldp_sync_default'), True):
            pass
            yield '| MPLS LDP Sync Default | '
            yield str(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'mpls_ldp_sync_default'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'timers'), 'local_convergence'), 'protected_prefixes'), True):
            pass
            yield '| Local Convergence Delay (ms) | '
            yield str(t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'timers'), 'local_convergence'), 'delay'), 10000))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'advertise'), 'passive_only'), True):
            pass
            yield '| Advertise Passive-only | '
            yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'advertise'), 'passive_only'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'segment_routing_mpls'), 'enabled')):
            pass
            yield '| SR MPLS Enabled | '
            yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'segment_routing_mpls'), 'enabled'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'spf_interval'), 'interval')):
            pass
            yield '| SPF Interval | '
            yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'spf_interval'), 'interval'))
            yield ' |\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'spf_interval'), 'wait_interval')):
                pass
                yield '| SPF Interval Wait Time| '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'spf_interval'), 'wait_interval'))
                yield ' |\n'
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart')):
            pass
            if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 'enabled'), True):
                pass
                yield '| Graceful-restart Enabled | '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 'enabled'))
                yield ' |\n'
            if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 't2'), 'level_1_wait_time')):
                pass
                yield '| Graceful-restart t2 Level-1 | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 't2'), 'level_1_wait_time'))
                yield ' |\n'
            if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 't2'), 'level_2_wait_time')):
                pass
                yield '| Graceful-restart t2 Level-2 | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 't2'), 'level_2_wait_time'))
                yield ' |\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 'restart_hold_time')):
                pass
                yield '| Graceful-restart Restart-hold-time | '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'graceful_restart'), 'restart_hold_time'))
                yield ' |\n'
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'redistribute_routes')):
            pass
            yield '\n#### ISIS Route Redistribution\n\n| Route Type | Route-Map | Include Leaked |\n| ---------- | --------- | -------------- |\n'
            for l_1_redistribute_route in t_2(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'redistribute_routes'), 'source_protocol'):
                l_1_include_leaked = resolve('include_leaked')
                l_1_src_protocol = l_1_route_map = missing
                _loop_vars = {}
                pass
                l_1_src_protocol = t_1(environment.getattr(l_1_redistribute_route, 'source_protocol'), '-')
                _loop_vars['src_protocol'] = l_1_src_protocol
                l_1_route_map = t_1(environment.getattr(l_1_redistribute_route, 'route_map'), '-')
                _loop_vars['route_map'] = l_1_route_map
                if ((undefined(name='src_protocol') if l_1_src_protocol is missing else l_1_src_protocol) in ['static', 'connected', 'ospf']):
                    pass
                    l_1_include_leaked = t_1(environment.getattr(l_1_redistribute_route, 'include_leaked'), '-')
                    _loop_vars['include_leaked'] = l_1_include_leaked
                else:
                    pass
                    l_1_include_leaked = '-'
                    _loop_vars['include_leaked'] = l_1_include_leaked
                if ((undefined(name='src_protocol') if l_1_src_protocol is missing else l_1_src_protocol) == 'isis'):
                    pass
                    l_1_src_protocol = str_join(((undefined(name='src_protocol') if l_1_src_protocol is missing else l_1_src_protocol), ' instance', ))
                    _loop_vars['src_protocol'] = l_1_src_protocol
                if (((undefined(name='src_protocol') if l_1_src_protocol is missing else l_1_src_protocol) in ['ospf', 'ospfv3']) and t_5(environment.getattr(l_1_redistribute_route, 'ospf_route_type'))):
                    pass
                    l_1_src_protocol = str_join(((undefined(name='src_protocol') if l_1_src_protocol is missing else l_1_src_protocol), ' ', environment.getattr(l_1_redistribute_route, 'ospf_route_type'), ))
                    _loop_vars['src_protocol'] = l_1_src_protocol
                yield '| '
                yield str((undefined(name='src_protocol') if l_1_src_protocol is missing else l_1_src_protocol))
                yield ' | '
                yield str((undefined(name='route_map') if l_1_route_map is missing else l_1_route_map))
                yield ' | '
                yield str((undefined(name='include_leaked') if l_1_include_leaked is missing else l_1_include_leaked))
                yield ' |\n'
            l_1_redistribute_route = l_1_src_protocol = l_1_route_map = l_1_include_leaked = missing
        yield '\n#### ISIS Interfaces Summary\n\n| Interface | ISIS Instance | ISIS Metric | Interface Mode |\n| --------- | ------------- | ----------- | -------------- |\n'
        for l_1_ethernet_interface in t_2((undefined(name='ethernet_interfaces') if l_0_ethernet_interfaces is missing else l_0_ethernet_interfaces), 'name'):
            l_1_row_isis_instance = resolve('row_isis_instance')
            l_1_row_isis_metric = resolve('row_isis_metric')
            l_1_row_intf_mode = resolve('row_intf_mode')
            _loop_vars = {}
            pass
            if t_5(environment.getattr(l_1_ethernet_interface, 'isis_enable')):
                pass
                l_1_row_isis_instance = environment.getattr(l_1_ethernet_interface, 'isis_enable')
                _loop_vars['row_isis_instance'] = l_1_row_isis_instance
                l_1_row_isis_metric = t_1(environment.getattr(l_1_ethernet_interface, 'isis_metric'), '-')
                _loop_vars['row_isis_metric'] = l_1_row_isis_metric
                if t_5(environment.getattr(l_1_ethernet_interface, 'isis_network_point_to_point'), True):
                    pass
                    l_1_row_intf_mode = 'point-to-point'
                    _loop_vars['row_intf_mode'] = l_1_row_intf_mode
                elif t_5(environment.getattr(l_1_ethernet_interface, 'isis_passive'), True):
                    pass
                    l_1_row_intf_mode = 'passive'
                    _loop_vars['row_intf_mode'] = l_1_row_intf_mode
                else:
                    pass
                    l_1_row_intf_mode = '-'
                    _loop_vars['row_intf_mode'] = l_1_row_intf_mode
                yield '| '
                yield str(environment.getattr(l_1_ethernet_interface, 'name'))
                yield ' | '
                yield str((undefined(name='row_isis_instance') if l_1_row_isis_instance is missing else l_1_row_isis_instance))
                yield ' | '
                yield str((undefined(name='row_isis_metric') if l_1_row_isis_metric is missing else l_1_row_isis_metric))
                yield ' | '
                yield str((undefined(name='row_intf_mode') if l_1_row_intf_mode is missing else l_1_row_intf_mode))
                yield ' |\n'
        l_1_ethernet_interface = l_1_row_isis_instance = l_1_row_isis_metric = l_1_row_intf_mode = missing
        for l_1_vlan_interface in t_2((undefined(name='vlan_interfaces') if l_0_vlan_interfaces is missing else l_0_vlan_interfaces), 'name'):
            l_1_row_isis_instance = resolve('row_isis_instance')
            l_1_row_isis_metric = resolve('row_isis_metric')
            l_1_row_intf_mode = resolve('row_intf_mode')
            _loop_vars = {}
            pass
            if t_5(environment.getattr(l_1_vlan_interface, 'isis_enable')):
                pass
                l_1_row_isis_instance = environment.getattr(l_1_vlan_interface, 'isis_enable')
                _loop_vars['row_isis_instance'] = l_1_row_isis_instance
                l_1_row_isis_metric = t_1(environment.getattr(l_1_vlan_interface, 'isis_metric'), '-')
                _loop_vars['row_isis_metric'] = l_1_row_isis_metric
                if t_5(environment.getattr(l_1_vlan_interface, 'isis_network_point_to_point'), True):
                    pass
                    l_1_row_intf_mode = 'point-to-point'
                    _loop_vars['row_intf_mode'] = l_1_row_intf_mode
                elif t_5(environment.getattr(l_1_vlan_interface, 'isis_passive'), True):
                    pass
                    l_1_row_intf_mode = 'passive'
                    _loop_vars['row_intf_mode'] = l_1_row_intf_mode
                else:
                    pass
                    l_1_row_intf_mode = '-'
                    _loop_vars['row_intf_mode'] = l_1_row_intf_mode
                yield '| '
                yield str(environment.getattr(l_1_vlan_interface, 'name'))
                yield ' | '
                yield str((undefined(name='row_isis_instance') if l_1_row_isis_instance is missing else l_1_row_isis_instance))
                yield ' | '
                yield str((undefined(name='row_isis_metric') if l_1_row_isis_metric is missing else l_1_row_isis_metric))
                yield ' | '
                yield str((undefined(name='row_intf_mode') if l_1_row_intf_mode is missing else l_1_row_intf_mode))
                yield ' |\n'
        l_1_vlan_interface = l_1_row_isis_instance = l_1_row_isis_metric = l_1_row_intf_mode = missing
        for l_1_loopback_interface in t_2((undefined(name='loopback_interfaces') if l_0_loopback_interfaces is missing else l_0_loopback_interfaces), 'name'):
            l_1_row_isis_instance = resolve('row_isis_instance')
            l_1_row_isis_metric = resolve('row_isis_metric')
            l_1_row_intf_mode = resolve('row_intf_mode')
            _loop_vars = {}
            pass
            if t_5(environment.getattr(l_1_loopback_interface, 'isis_enable')):
                pass
                l_1_row_isis_instance = environment.getattr(l_1_loopback_interface, 'isis_enable')
                _loop_vars['row_isis_instance'] = l_1_row_isis_instance
                l_1_row_isis_metric = t_1(environment.getattr(l_1_loopback_interface, 'isis_metric'), '-')
                _loop_vars['row_isis_metric'] = l_1_row_isis_metric
                if t_5(environment.getattr(l_1_loopback_interface, 'isis_network_point_to_point'), True):
                    pass
                    l_1_row_intf_mode = 'point-to-point'
                    _loop_vars['row_intf_mode'] = l_1_row_intf_mode
                elif t_5(environment.getattr(l_1_loopback_interface, 'isis_passive'), True):
                    pass
                    l_1_row_intf_mode = 'passive'
                    _loop_vars['row_intf_mode'] = l_1_row_intf_mode
                else:
                    pass
                    l_1_row_intf_mode = '-'
                    _loop_vars['row_intf_mode'] = l_1_row_intf_mode
                yield '| '
                yield str(environment.getattr(l_1_loopback_interface, 'name'))
                yield ' | '
                yield str((undefined(name='row_isis_instance') if l_1_row_isis_instance is missing else l_1_row_isis_instance))
                yield ' | '
                yield str((undefined(name='row_isis_metric') if l_1_row_isis_metric is missing else l_1_row_isis_metric))
                yield ' | '
                yield str((undefined(name='row_intf_mode') if l_1_row_intf_mode is missing else l_1_row_intf_mode))
                yield ' |\n'
        l_1_loopback_interface = l_1_row_isis_instance = l_1_row_isis_metric = l_1_row_intf_mode = missing
        l_0_node_sid_loopbacks = []
        context.vars['node_sid_loopbacks'] = l_0_node_sid_loopbacks
        context.exported_vars.add('node_sid_loopbacks')
        for l_1_loopback_interface in t_2((undefined(name='loopback_interfaces') if l_0_loopback_interfaces is missing else l_0_loopback_interfaces), 'name'):
            _loop_vars = {}
            pass
            if (t_5(environment.getattr(environment.getattr(l_1_loopback_interface, 'node_segment'), 'ipv4_index')) or t_5(environment.getattr(environment.getattr(l_1_loopback_interface, 'node_segment'), 'ipv6_index'))):
                pass
                context.call(environment.getattr((undefined(name='node_sid_loopbacks') if l_0_node_sid_loopbacks is missing else l_0_node_sid_loopbacks), 'append'), l_1_loopback_interface, _loop_vars=_loop_vars)
        l_1_loopback_interface = missing
        if (t_4((undefined(name='node_sid_loopbacks') if l_0_node_sid_loopbacks is missing else l_0_node_sid_loopbacks)) > 0):
            pass
            yield '\n#### ISIS Segment-routing Node-SID\n\n| Loopback | IPv4 Index | IPv6 Index |\n| -------- | ---------- | ---------- |\n'
            for l_1_loopback_interface in t_2((undefined(name='node_sid_loopbacks') if l_0_node_sid_loopbacks is missing else l_0_node_sid_loopbacks)):
                l_1_row_ipv4_index = l_1_row_ipv6_index = missing
                _loop_vars = {}
                pass
                l_1_row_ipv4_index = t_1(environment.getattr(environment.getattr(l_1_loopback_interface, 'node_segment'), 'ipv4_index'), '-')
                _loop_vars['row_ipv4_index'] = l_1_row_ipv4_index
                l_1_row_ipv6_index = t_1(environment.getattr(environment.getattr(l_1_loopback_interface, 'node_segment'), 'ipv6_index'), '-')
                _loop_vars['row_ipv6_index'] = l_1_row_ipv6_index
                yield '| '
                yield str(environment.getattr(l_1_loopback_interface, 'name'))
                yield ' | '
                yield str((undefined(name='row_ipv4_index') if l_1_row_ipv4_index is missing else l_1_row_ipv4_index))
                yield ' | '
                yield str((undefined(name='row_ipv6_index') if l_1_row_ipv6_index is missing else l_1_row_ipv6_index))
                yield ' |\n'
            l_1_loopback_interface = l_1_row_ipv4_index = l_1_row_ipv6_index = missing
        if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'segment_routing_mpls'), 'prefix_segments')):
            pass
            yield '\n#### Prefix Segments\n\n| Prefix Segment | Index |\n| -------------- | ----- |\n'
            for l_1_prefix_segment in t_2(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'segment_routing_mpls'), 'prefix_segments'), 'prefix'):
                _loop_vars = {}
                pass
                if t_5(environment.getattr(l_1_prefix_segment, 'index')):
                    pass
                    yield '| '
                    yield str(environment.getattr(l_1_prefix_segment, 'prefix'))
                    yield ' | '
                    yield str(environment.getattr(l_1_prefix_segment, 'index'))
                    yield ' |\n'
            l_1_prefix_segment = missing
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4')):
            pass
            yield '\n#### ISIS IPv4 Address Family Summary\n\n| Settings | Value |\n| -------- | ----- |\n| IPv4 Address-family Enabled | True |\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'maximum_paths')):
                pass
                yield '| Maximum-paths | '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'maximum_paths'))
                yield ' |\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'bfd_all_interfaces')):
                pass
                yield '| BFD All-interfaces | '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'bfd_all_interfaces'))
                yield ' |\n'
            if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'mode')):
                pass
                yield '| TI-LFA Mode | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'mode'))
                yield ' |\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'level')):
                    pass
                    yield '| TI-LFA Level | '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'level'))
                    yield ' |\n'
            if t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'srlg'), 'enable'), True):
                pass
                yield '| TI-LFA SRLG Enabled | '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'srlg'), 'enable'))
                yield ' |\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'srlg'), 'strict'), True):
                    pass
                    yield '| TI-LFA SRLG Strict Mode | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'fast_reroute_ti_lfa'), 'srlg'), 'strict'))
                    yield ' |\n'
        if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'tunnel_source_labeled_unicast'), 'enabled'), True):
            pass
            yield '\n#### Tunnel Source\n\n| Source Protocol | RCF |\n| --------------- | --- |\n'
            l_0_rcf = t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv4'), 'tunnel_source_labeled_unicast'), 'rcf'), '-')
            context.vars['rcf'] = l_0_rcf
            context.exported_vars.add('rcf')
            yield '| BGP Labeled-Unicast | '
            yield str((undefined(name='rcf') if l_0_rcf is missing else l_0_rcf))
            yield ' |\n'
        if t_5(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6')):
            pass
            yield '\n#### ISIS IPv6 Address Family Summary\n\n| Settings | Value |\n| -------- | ----- |\n| IPv6 Address-family Enabled | True |\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'maximum_paths')):
                pass
                yield '| Maximum-paths | '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'maximum_paths'))
                yield ' |\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'bfd_all_interfaces')):
                pass
                yield '| BFD All-interfaces | '
                yield str(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'bfd_all_interfaces'))
                yield ' |\n'
            if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'mode')):
                pass
                yield '| TI-LFA Mode | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'mode'))
                yield ' |\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'level')):
                    pass
                    yield '| TI-LFA Level | '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'level'))
                    yield ' |\n'
            if t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'srlg'), 'enable'), True):
                pass
                yield '| TI-LFA SRLG Enabled | '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'srlg'), 'enable'))
                yield ' |\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'srlg'), 'strict'), True):
                    pass
                    yield '| TI-LFA SRLG Strict Mode | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_isis') if l_0_router_isis is missing else l_0_router_isis), 'address_family_ipv6'), 'fast_reroute_ti_lfa'), 'srlg'), 'strict'))
                    yield ' |\n'
        yield '\n#### Router ISIS Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/router-isis.j2', 'documentation/router-isis.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {'node_sid_loopbacks': l_0_node_sid_loopbacks, 'rcf': l_0_rcf})):
            yield event
        yield '```\n'

blocks = {}
debug_info = '7=47&15=50&16=53&18=55&19=58&21=60&22=63&24=65&25=68&27=70&28=73&30=75&31=78&33=80&34=83&36=85&37=88&39=90&40=93&42=95&43=98&45=100&46=103&47=105&48=108&51=110&52=112&53=115&55=117&56=120&58=122&59=125&61=127&62=130&65=132&71=135&72=140&73=142&74=144&75=146&77=150&79=152&80=154&82=156&83=158&85=161&95=169&96=175&97=177&98=179&99=181&100=183&101=185&102=187&104=191&106=194&112=203&113=209&114=211&115=213&116=215&117=217&118=219&119=221&121=225&123=228&129=237&130=243&131=245&132=247&133=249&134=251&135=253&136=255&138=259&140=262&144=271&145=274&146=277&147=279&150=281&156=284&157=288&158=290&159=293&162=300&168=303&169=306&170=309&174=314&181=317&182=320&184=322&185=325&187=327&188=330&189=332&190=335&193=337&194=340&195=342&196=345&200=347&206=350&207=354&209=356&216=359&217=362&219=364&220=367&222=369&223=372&224=374&225=377&228=379&229=382&230=384&231=387&239=390'