from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/port-channel-interfaces.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_port_channel_interfaces = resolve('port_channel_interfaces')
    try:
        t_1 = environment.filters['arista.avd.convert_dicts']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.convert_dicts' found.")
    try:
        t_2 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_3 = environment.filters['arista.avd.hide_passwords']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.hide_passwords' found.")
    try:
        t_4 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_5 = environment.filters['indent']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'indent' found.")
    try:
        t_6 = environment.filters['replace']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'replace' found.")
    try:
        t_7 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    for l_1_port_channel_interface in t_4((undefined(name='port_channel_interfaces') if l_0_port_channel_interfaces is missing else l_0_port_channel_interfaces), 'name'):
        l_1_encapsulation_cli = resolve('encapsulation_cli')
        l_1_dfe_algo_cli = resolve('dfe_algo_cli')
        l_1_dfe_hold_time_cli = resolve('dfe_hold_time_cli')
        l_1_hide_passwords = resolve('hide_passwords')
        l_1_interface_ip_nat = resolve('interface_ip_nat')
        _loop_vars = {}
        pass
        yield '!\ninterface '
        yield str(environment.getattr(l_1_port_channel_interface, 'name'))
        yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'description')):
            pass
            yield '   description '
            yield str(environment.getattr(l_1_port_channel_interface, 'description'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'logging'), 'event'), 'link_status'), True):
            pass
            yield '   logging event link-status\n'
        elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'logging'), 'event'), 'link_status'), False):
            pass
            yield '   no logging event link-status\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'logging'), 'event'), 'storm_control_discards'), True):
            pass
            yield '   logging event storm-control discards\n'
        elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'logging'), 'event'), 'storm_control_discards'), False):
            pass
            yield '   no logging event storm-control discards\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'shutdown'), True):
            pass
            yield '   shutdown\n'
        elif t_7(environment.getattr(l_1_port_channel_interface, 'shutdown'), False):
            pass
            yield '   no shutdown\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'mtu')):
            pass
            yield '   mtu '
            yield str(environment.getattr(l_1_port_channel_interface, 'mtu'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bgp'), 'session_tracker')):
            pass
            yield '   bgp session tracker '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bgp'), 'session_tracker'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'type'), 'routed'):
            pass
            yield '   no switchport\n'
        elif (t_2(environment.getattr(l_1_port_channel_interface, 'type')) in ['l3dot1q', 'l2dot1q']):
            pass
            if (t_7(environment.getattr(l_1_port_channel_interface, 'vlan_id')) and (environment.getattr(l_1_port_channel_interface, 'type') == 'l2dot1q')):
                pass
                yield '   vlan id '
                yield str(environment.getattr(l_1_port_channel_interface, 'vlan_id'))
                yield '\n'
            if t_7(environment.getattr(l_1_port_channel_interface, 'encapsulation_dot1q_vlan')):
                pass
                yield '   encapsulation dot1q vlan '
                yield str(environment.getattr(l_1_port_channel_interface, 'encapsulation_dot1q_vlan'))
                yield '\n'
            elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'vlan')):
                pass
                l_1_encapsulation_cli = str_join(('client dot1q ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'vlan'), ))
                _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'vlan')):
                    pass
                    l_1_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli), ' network dot1q ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'vlan'), ))
                    _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'network'), 'client'), True):
                    pass
                    l_1_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli), ' network client', ))
                    _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
            elif (t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'inner')) and t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'outer'))):
                pass
                l_1_encapsulation_cli = str_join(('client dot1q outer ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'outer'), ' inner ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'inner'), ))
                _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                if (t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'inner')) and t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'outer'))):
                    pass
                    l_1_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli), ' network dot1q outer ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'inner'), ' inner ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'outer'), ))
                    _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'client'), True):
                    pass
                    l_1_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli), ' network client', ))
                    _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
            elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'encapsulation_vlan'), 'client'), 'unmatched'), True):
                pass
                l_1_encapsulation_cli = 'client unmatched'
                _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
            if t_7((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli)):
                pass
                yield '   encapsulation vlan\n      '
                yield str((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli))
                yield '\n'
        elif (t_2(environment.getattr(l_1_port_channel_interface, 'type'), 'switched') == 'switched'):
            pass
            yield '   switchport\n'
        if (t_7(environment.getattr(l_1_port_channel_interface, 'vlans')) and t_7(environment.getattr(l_1_port_channel_interface, 'mode'), 'access')):
            pass
            yield '   switchport access vlan '
            yield str(environment.getattr(l_1_port_channel_interface, 'vlans'))
            yield '\n'
        if (t_7(environment.getattr(l_1_port_channel_interface, 'vlans')) and t_7(environment.getattr(l_1_port_channel_interface, 'mode'), 'trunk')):
            pass
            yield '   switchport trunk allowed vlan '
            yield str(environment.getattr(l_1_port_channel_interface, 'vlans'))
            yield '\n'
        if (t_7(environment.getattr(l_1_port_channel_interface, 'mode')) and (environment.getattr(l_1_port_channel_interface, 'mode') in ['trunk', 'trunk phone'])):
            pass
            if t_7(environment.getattr(l_1_port_channel_interface, 'native_vlan_tag'), True):
                pass
                yield '   switchport trunk native vlan tag\n'
            elif t_7(environment.getattr(l_1_port_channel_interface, 'native_vlan')):
                pass
                yield '   switchport trunk native vlan '
                yield str(environment.getattr(l_1_port_channel_interface, 'native_vlan'))
                yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'phone'), 'vlan')):
            pass
            yield '   switchport phone vlan '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'phone'), 'vlan'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'phone'), 'trunk')):
            pass
            yield '   switchport phone trunk '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'phone'), 'trunk'))
            yield '\n'
        if (t_7(environment.getattr(l_1_port_channel_interface, 'mode')) and (environment.getattr(l_1_port_channel_interface, 'mode') != 'access')):
            pass
            yield '   switchport mode '
            yield str(environment.getattr(l_1_port_channel_interface, 'mode'))
            yield '\n'
        for l_2_trunk_group in t_4(environment.getattr(l_1_port_channel_interface, 'trunk_groups')):
            _loop_vars = {}
            pass
            yield '   switchport trunk group '
            yield str(l_2_trunk_group)
            yield '\n'
        l_2_trunk_group = missing
        if t_7(environment.getattr(l_1_port_channel_interface, 'trunk_private_vlan_secondary'), True):
            pass
            yield '   switchport trunk private-vlan secondary\n'
        elif t_7(environment.getattr(l_1_port_channel_interface, 'trunk_private_vlan_secondary'), False):
            pass
            yield '   no switchport trunk private-vlan secondary\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'pvlan_mapping')):
            pass
            yield '   switchport pvlan mapping '
            yield str(environment.getattr(l_1_port_channel_interface, 'pvlan_mapping'))
            yield '\n'
        for l_2_vlan_translation in t_4(environment.getattr(l_1_port_channel_interface, 'vlan_translations')):
            l_2_vlan_translation_cli = resolve('vlan_translation_cli')
            _loop_vars = {}
            pass
            if (t_7(environment.getattr(l_2_vlan_translation, 'from')) and t_7(environment.getattr(l_2_vlan_translation, 'to'))):
                pass
                l_2_vlan_translation_cli = 'switchport vlan translation'
                _loop_vars['vlan_translation_cli'] = l_2_vlan_translation_cli
                if (t_2(environment.getattr(l_2_vlan_translation, 'direction')) in ['in', 'out']):
                    pass
                    l_2_vlan_translation_cli = str_join(((undefined(name='vlan_translation_cli') if l_2_vlan_translation_cli is missing else l_2_vlan_translation_cli), ' ', environment.getattr(l_2_vlan_translation, 'direction'), ))
                    _loop_vars['vlan_translation_cli'] = l_2_vlan_translation_cli
                l_2_vlan_translation_cli = str_join(((undefined(name='vlan_translation_cli') if l_2_vlan_translation_cli is missing else l_2_vlan_translation_cli), ' ', environment.getattr(l_2_vlan_translation, 'from'), ))
                _loop_vars['vlan_translation_cli'] = l_2_vlan_translation_cli
                l_2_vlan_translation_cli = str_join(((undefined(name='vlan_translation_cli') if l_2_vlan_translation_cli is missing else l_2_vlan_translation_cli), ' ', environment.getattr(l_2_vlan_translation, 'to'), ))
                _loop_vars['vlan_translation_cli'] = l_2_vlan_translation_cli
                yield '   '
                yield str((undefined(name='vlan_translation_cli') if l_2_vlan_translation_cli is missing else l_2_vlan_translation_cli))
                yield '\n'
        l_2_vlan_translation = l_2_vlan_translation_cli = missing
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'l2_protocol'), 'encapsulation_dot1q_vlan')):
            pass
            yield '   l2-protocol encapsulation dot1q vlan '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'l2_protocol'), 'encapsulation_dot1q_vlan'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'l2_protocol'), 'forwarding_profile')):
            pass
            yield '   l2-protocol forwarding profile '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'l2_protocol'), 'forwarding_profile'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'flow_tracker'), 'hardware')):
            pass
            yield '   flow tracker hardware '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'flow_tracker'), 'hardware'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'flow_tracker'), 'sampled')):
            pass
            yield '   flow tracker sampled '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'flow_tracker'), 'sampled'))
            yield '\n'
        if (t_7(t_2(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'identifier'), environment.getattr(l_1_port_channel_interface, 'esi'))) or t_7(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'))):
            pass
            yield '   evpn ethernet-segment\n'
            if t_7(t_2(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'identifier'), environment.getattr(l_1_port_channel_interface, 'esi'))):
                pass
                yield '      identifier '
                yield str(t_2(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'identifier'), environment.getattr(l_1_port_channel_interface, 'esi')))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'redundancy')):
                pass
                yield '      redundancy '
                yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'redundancy'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election')):
                pass
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'algorithm'), 'modulus'):
                    pass
                    yield '      designated-forwarder election algorithm modulus\n'
                elif (t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'algorithm'), 'preference') and t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'preference_value'))):
                    pass
                    l_1_dfe_algo_cli = str_join(('designated-forwarder election algorithm preference ', environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'preference_value'), ))
                    _loop_vars['dfe_algo_cli'] = l_1_dfe_algo_cli
                    if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'dont_preempt'), True):
                        pass
                        l_1_dfe_algo_cli = str_join(((undefined(name='dfe_algo_cli') if l_1_dfe_algo_cli is missing else l_1_dfe_algo_cli), ' dont-preempt', ))
                        _loop_vars['dfe_algo_cli'] = l_1_dfe_algo_cli
                    yield '      '
                    yield str((undefined(name='dfe_algo_cli') if l_1_dfe_algo_cli is missing else l_1_dfe_algo_cli))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'hold_time')):
                    pass
                    l_1_dfe_hold_time_cli = str_join(('designated-forwarder election hold-time ', environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'hold_time'), ))
                    _loop_vars['dfe_hold_time_cli'] = l_1_dfe_hold_time_cli
                    if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'subsequent_hold_time')):
                        pass
                        l_1_dfe_hold_time_cli = str_join(((undefined(name='dfe_hold_time_cli') if l_1_dfe_hold_time_cli is missing else l_1_dfe_hold_time_cli), ' subsequent-hold-time ', environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'subsequent_hold_time'), ))
                        _loop_vars['dfe_hold_time_cli'] = l_1_dfe_hold_time_cli
                    yield '      '
                    yield str((undefined(name='dfe_hold_time_cli') if l_1_dfe_hold_time_cli is missing else l_1_dfe_hold_time_cli))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'candidate_reachability_required'), True):
                    pass
                    yield '      designated-forwarder election candidate reachability required\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'candidate_reachability_required'), False):
                    pass
                    yield '      no designated-forwarder election candidate reachability required\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'mpls'), 'tunnel_flood_filter_time')):
                pass
                yield '      mpls tunnel flood filter time '
                yield str(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'mpls'), 'tunnel_flood_filter_time'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'mpls'), 'shared_index')):
                pass
                yield '      mpls shared index '
                yield str(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'mpls'), 'shared_index'))
                yield '\n'
            if t_7(t_2(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'route_target'), environment.getattr(l_1_port_channel_interface, 'rt'))):
                pass
                yield '      route-target import '
                yield str(t_2(environment.getattr(environment.getattr(l_1_port_channel_interface, 'evpn_ethernet_segment'), 'route_target'), environment.getattr(l_1_port_channel_interface, 'rt')))
                yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'snmp_trap_link_change'), False):
            pass
            yield '   no snmp trap link-change\n'
        elif t_7(environment.getattr(l_1_port_channel_interface, 'snmp_trap_link_change'), True):
            pass
            yield '   snmp trap link-change\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'l2_mtu')):
            pass
            yield '   l2 mtu '
            yield str(environment.getattr(l_1_port_channel_interface, 'l2_mtu'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'l2_mru')):
            pass
            yield '   l2 mru '
            yield str(environment.getattr(l_1_port_channel_interface, 'l2_mru'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'lacp_id')):
            pass
            yield '   lacp system-id '
            yield str(environment.getattr(l_1_port_channel_interface, 'lacp_id'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'lacp_fallback_timeout')):
            pass
            yield '   port-channel lacp fallback timeout '
            yield str(environment.getattr(l_1_port_channel_interface, 'lacp_fallback_timeout'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'lacp_fallback_mode')):
            pass
            yield '   port-channel lacp fallback '
            yield str(environment.getattr(l_1_port_channel_interface, 'lacp_fallback_mode'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'mlag')):
            pass
            yield '   mlag '
            yield str(environment.getattr(l_1_port_channel_interface, 'mlag'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'qos'), 'trust')):
            pass
            if (environment.getattr(environment.getattr(l_1_port_channel_interface, 'qos'), 'trust') == 'disabled'):
                pass
                yield '   no qos trust\n'
            else:
                pass
                yield '   qos trust '
                yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'qos'), 'trust'))
                yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'qos'), 'dscp')):
            pass
            yield '   qos dscp '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'qos'), 'dscp'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'qos'), 'cos')):
            pass
            yield '   qos cos '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'qos'), 'cos'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'shape'), 'rate')):
            pass
            yield '   shape rate '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'shape'), 'rate'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'spanning_tree_portfast'), 'edge'):
            pass
            yield '   spanning-tree portfast\n'
        elif t_7(environment.getattr(l_1_port_channel_interface, 'spanning_tree_portfast'), 'network'):
            pass
            yield '   spanning-tree portfast network\n'
        if (t_7(environment.getattr(l_1_port_channel_interface, 'spanning_tree_bpduguard')) and (environment.getattr(l_1_port_channel_interface, 'spanning_tree_bpduguard') in [True, 'True', 'enabled'])):
            pass
            yield '   spanning-tree bpduguard enable\n'
        elif t_7(environment.getattr(l_1_port_channel_interface, 'spanning_tree_bpduguard'), 'disabled'):
            pass
            yield '   spanning-tree bpduguard disable\n'
        if (t_7(environment.getattr(l_1_port_channel_interface, 'spanning_tree_bpdufilter')) and (environment.getattr(l_1_port_channel_interface, 'spanning_tree_bpdufilter') in [True, 'True', 'enabled'])):
            pass
            yield '   spanning-tree bpdufilter enable\n'
        elif t_7(environment.getattr(l_1_port_channel_interface, 'spanning_tree_bpdufilter'), 'disabled'):
            pass
            yield '   spanning-tree bpdufilter disable\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'spanning_tree_guard')):
            pass
            if (environment.getattr(l_1_port_channel_interface, 'spanning_tree_guard') == 'disabled'):
                pass
                yield '   spanning-tree guard none\n'
            else:
                pass
                yield '   spanning-tree guard '
                yield str(environment.getattr(l_1_port_channel_interface, 'spanning_tree_guard'))
                yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'vrf')):
            pass
            yield '   vrf '
            yield str(environment.getattr(l_1_port_channel_interface, 'vrf'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ip_proxy_arp'), True):
            pass
            yield '   ip proxy-arp\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ip_address')):
            pass
            yield '   ip address '
            yield str(environment.getattr(l_1_port_channel_interface, 'ip_address'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ip_verify_unicast_source_reachable_via')):
            pass
            yield '   ip verify unicast source reachable-via '
            yield str(environment.getattr(l_1_port_channel_interface, 'ip_verify_unicast_source_reachable_via'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ipv6_enable'), True):
            pass
            yield '   ipv6 enable\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ipv6_address')):
            pass
            yield '   ipv6 address '
            yield str(environment.getattr(l_1_port_channel_interface, 'ipv6_address'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ipv6_address_link_local')):
            pass
            yield '   ipv6 address '
            yield str(environment.getattr(l_1_port_channel_interface, 'ipv6_address_link_local'))
            yield ' link-local\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ipv6_nd_ra_disabled'), True):
            pass
            yield '   ipv6 nd ra disabled\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ipv6_nd_managed_config_flag'), True):
            pass
            yield '   ipv6 nd managed-config-flag\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ipv6_nd_prefixes')):
            pass
            for l_2_ipv6_nd_prefix in t_1(environment.getattr(l_1_port_channel_interface, 'ipv6_nd_prefixes'), 'ipv6_prefix'):
                l_2_ipv6_nd_prefix_cli = missing
                _loop_vars = {}
                pass
                l_2_ipv6_nd_prefix_cli = str_join(('ipv6 nd prefix ', environment.getattr(l_2_ipv6_nd_prefix, 'ipv6_prefix'), ))
                _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                if t_7(environment.getattr(l_2_ipv6_nd_prefix, 'valid_lifetime')):
                    pass
                    l_2_ipv6_nd_prefix_cli = str_join(((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli), ' ', environment.getattr(l_2_ipv6_nd_prefix, 'valid_lifetime'), ))
                    _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                if t_7(environment.getattr(l_2_ipv6_nd_prefix, 'preferred_lifetime')):
                    pass
                    l_2_ipv6_nd_prefix_cli = str_join(((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli), ' ', environment.getattr(l_2_ipv6_nd_prefix, 'preferred_lifetime'), ))
                    _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                if t_7(environment.getattr(l_2_ipv6_nd_prefix, 'no_autoconfig_flag'), True):
                    pass
                    l_2_ipv6_nd_prefix_cli = str_join(((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli), ' no-autoconfig', ))
                    _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                yield '   '
                yield str((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli))
                yield '\n'
            l_2_ipv6_nd_prefix = l_2_ipv6_nd_prefix_cli = missing
        if t_7(environment.getattr(l_1_port_channel_interface, 'access_group_in')):
            pass
            yield '   ip access-group '
            yield str(environment.getattr(l_1_port_channel_interface, 'access_group_in'))
            yield ' in\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'access_group_out')):
            pass
            yield '   ip access-group '
            yield str(environment.getattr(l_1_port_channel_interface, 'access_group_out'))
            yield ' out\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ipv6_access_group_in')):
            pass
            yield '   ipv6 access-group '
            yield str(environment.getattr(l_1_port_channel_interface, 'ipv6_access_group_in'))
            yield ' in\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ipv6_access_group_out')):
            pass
            yield '   ipv6 access-group '
            yield str(environment.getattr(l_1_port_channel_interface, 'ipv6_access_group_out'))
            yield ' out\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'mac_access_group_in')):
            pass
            yield '   mac access-group '
            yield str(environment.getattr(l_1_port_channel_interface, 'mac_access_group_in'))
            yield ' in\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'mac_access_group_out')):
            pass
            yield '   mac access-group '
            yield str(environment.getattr(l_1_port_channel_interface, 'mac_access_group_out'))
            yield ' out\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ospf_network_point_to_point'), True):
            pass
            yield '   ip ospf network point-to-point\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ospf_area')):
            pass
            yield '   ip ospf area '
            yield str(environment.getattr(l_1_port_channel_interface, 'ospf_area'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ospf_cost')):
            pass
            yield '   ip ospf cost '
            yield str(environment.getattr(l_1_port_channel_interface, 'ospf_cost'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ospf_authentication'), 'simple'):
            pass
            yield '   ip ospf authentication\n'
        elif t_7(environment.getattr(l_1_port_channel_interface, 'ospf_authentication'), 'message-digest'):
            pass
            yield '   ip ospf authentication message-digest\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ospf_authentication_key')):
            pass
            yield '   ip ospf authentication-key 7 '
            yield str(t_3(environment.getattr(l_1_port_channel_interface, 'ospf_authentication_key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
            yield '\n'
        for l_2_ospf_message_digest_key in t_4(t_1(environment.getattr(l_1_port_channel_interface, 'ospf_message_digest_keys'), 'id'), 'id'):
            _loop_vars = {}
            pass
            if (t_7(environment.getattr(l_2_ospf_message_digest_key, 'hash_algorithm')) and t_7(environment.getattr(l_2_ospf_message_digest_key, 'key'))):
                pass
                yield '   ip ospf message-digest-key '
                yield str(environment.getattr(l_2_ospf_message_digest_key, 'id'))
                yield ' '
                yield str(environment.getattr(l_2_ospf_message_digest_key, 'hash_algorithm'))
                yield ' 7 '
                yield str(t_3(environment.getattr(l_2_ospf_message_digest_key, 'key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
                yield '\n'
        l_2_ospf_message_digest_key = missing
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'pim'), 'ipv4'), 'sparse_mode'), True):
            pass
            yield '   pim ipv4 sparse-mode\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'pim'), 'ipv4'), 'dr_priority')):
            pass
            yield '   pim ipv4 dr-priority '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'pim'), 'ipv4'), 'dr_priority'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'vmtracer'), True):
            pass
            yield '   vmtracer vmware-esx\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'enable'), True):
            pass
            yield '   ptp enable\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'announce'), 'interval')):
            pass
            yield '   ptp announce interval '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'announce'), 'interval'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'announce'), 'timeout')):
            pass
            yield '   ptp announce timeout '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'announce'), 'timeout'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'delay_req')):
            pass
            yield '   ptp delay-req interval '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'delay_req'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'delay_mechanism')):
            pass
            yield '   ptp delay-mechanism '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'delay_mechanism'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'sync_message'), 'interval')):
            pass
            yield '   ptp sync-message interval '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'sync_message'), 'interval'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'role')):
            pass
            yield '   ptp role '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'role'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'vlan')):
            pass
            yield '   ptp vlan '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'vlan'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'transport')):
            pass
            yield '   ptp transport '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'ptp'), 'transport'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'service_profile')):
            pass
            yield '   service-profile '
            yield str(environment.getattr(l_1_port_channel_interface, 'service_profile'))
            yield '\n'
        for l_2_section in t_4(environment.getattr(l_1_port_channel_interface, 'storm_control')):
            _loop_vars = {}
            pass
            if t_7(environment.getattr(environment.getitem(environment.getattr(l_1_port_channel_interface, 'storm_control'), l_2_section), 'unit'), 'pps'):
                pass
                yield '   storm-control '
                yield str(t_6(context.eval_ctx, l_2_section, '_', '-'))
                yield ' level pps '
                yield str(environment.getattr(environment.getitem(environment.getattr(l_1_port_channel_interface, 'storm_control'), l_2_section), 'level'))
                yield '\n'
            else:
                pass
                yield '   storm-control '
                yield str(t_6(context.eval_ctx, l_2_section, '_', '-'))
                yield ' level '
                yield str(environment.getattr(environment.getitem(environment.getattr(l_1_port_channel_interface, 'storm_control'), l_2_section), 'level'))
                yield '\n'
        l_2_section = missing
        if ((t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'interval')) and t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'min_rx'))) and t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'multiplier'))):
            pass
            yield '   bfd interval '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'interval'))
            yield ' min-rx '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'min_rx'))
            yield ' multiplier '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'multiplier'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'echo'), True):
            pass
            yield '   bfd echo\n'
        elif t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'echo'), False):
            pass
            yield '   no bfd echo\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'neighbor')):
            pass
            yield '   bfd neighbor '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'neighbor'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'per_link'), 'enabled'), True):
            pass
            if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'bfd'), 'per_link'), 'rfc_7130'), True):
                pass
                yield '   bfd per-link rfc-7130\n'
            else:
                pass
                yield '   bfd per-link\n'
        for l_2_link_tracking_group in t_4(environment.getattr(l_1_port_channel_interface, 'link_tracking_groups'), 'name'):
            _loop_vars = {}
            pass
            if (t_7(environment.getattr(l_2_link_tracking_group, 'name')) and t_7(environment.getattr(l_2_link_tracking_group, 'direction'))):
                pass
                yield '   link tracking group '
                yield str(environment.getattr(l_2_link_tracking_group, 'name'))
                yield ' '
                yield str(environment.getattr(l_2_link_tracking_group, 'direction'))
                yield '\n'
        l_2_link_tracking_group = missing
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'service_policy'), 'pbr'), 'input')):
            pass
            yield '   service-policy type pbr input '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'service_policy'), 'pbr'), 'input'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'service_policy'), 'qos'), 'input')):
            pass
            yield '   service-policy type qos input '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'service_policy'), 'qos'), 'input'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'mpls'), 'ip'), True):
            pass
            yield '   mpls ip\n'
        elif t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'mpls'), 'ip'), False):
            pass
            yield '   no mpls ip\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'mpls'), 'ldp'), 'interface'), True):
            pass
            yield '   mpls ldp interface\n'
        elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'mpls'), 'ldp'), 'interface'), False):
            pass
            yield '   no mpls ldp interface\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'mpls'), 'ldp'), 'igp_sync'), True):
            pass
            yield '   mpls ldp igp sync\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'ip_nat')):
            pass
            l_1_interface_ip_nat = environment.getattr(l_1_port_channel_interface, 'ip_nat')
            _loop_vars['interface_ip_nat'] = l_1_interface_ip_nat
            template = environment.get_template('eos/interface-ip-nat.j2', 'eos/port-channel-interfaces.j2')
            for event in template.root_render_func(template.new_context(context.get_all(), True, {'dfe_algo_cli': l_1_dfe_algo_cli, 'dfe_hold_time_cli': l_1_dfe_hold_time_cli, 'encapsulation_cli': l_1_encapsulation_cli, 'interface_ip_nat': l_1_interface_ip_nat, 'port_channel_interface': l_1_port_channel_interface})):
                yield event
        if t_7(environment.getattr(l_1_port_channel_interface, 'isis_enable')):
            pass
            yield '   isis enable '
            yield str(environment.getattr(l_1_port_channel_interface, 'isis_enable'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'isis_circuit_type')):
            pass
            yield '   isis circuit-type '
            yield str(environment.getattr(l_1_port_channel_interface, 'isis_circuit_type'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'isis_metric')):
            pass
            yield '   isis metric '
            yield str(environment.getattr(l_1_port_channel_interface, 'isis_metric'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'isis_passive'), True):
            pass
            yield '   isis passive\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'isis_network_point_to_point'), True):
            pass
            yield '   isis network point-to-point\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'isis_hello_padding'), False):
            pass
            yield '   no isis hello padding\n'
        elif t_7(environment.getattr(l_1_port_channel_interface, 'isis_hello_padding'), True):
            pass
            yield '   isis hello padding\n'
        if (t_7(environment.getattr(l_1_port_channel_interface, 'isis_authentication_mode')) and (environment.getattr(l_1_port_channel_interface, 'isis_authentication_mode') in ['text', 'md5'])):
            pass
            yield '   isis authentication mode '
            yield str(environment.getattr(l_1_port_channel_interface, 'isis_authentication_mode'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'isis_authentication_key')):
            pass
            yield '   isis authentication key 7 '
            yield str(t_3(environment.getattr(l_1_port_channel_interface, 'isis_authentication_key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'traffic_policy'), 'input')):
            pass
            yield '   traffic-policy input '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'traffic_policy'), 'input'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'traffic_policy'), 'output')):
            pass
            yield '   traffic-policy output '
            yield str(environment.getattr(environment.getattr(l_1_port_channel_interface, 'traffic_policy'), 'output'))
            yield '\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'sflow')):
            pass
            if t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'sflow'), 'enable'), True):
                pass
                yield '   sflow enable\n'
            elif t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'sflow'), 'enable'), False):
                pass
                yield '   no sflow enable\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'sflow'), 'egress'), 'enable'), True):
                pass
                yield '   sflow egress enable\n'
            elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'sflow'), 'egress'), 'enable'), False):
                pass
                yield '   no sflow egress enable\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'sflow'), 'egress'), 'unmodified_enable'), True):
                pass
                yield '   sflow egress unmodified enable\n'
            elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_port_channel_interface, 'sflow'), 'egress'), 'unmodified_enable'), False):
                pass
                yield '   no sflow egress unmodified enable\n'
        if t_7(environment.getattr(l_1_port_channel_interface, 'eos_cli')):
            pass
            yield '   '
            yield str(t_5(environment.getattr(l_1_port_channel_interface, 'eos_cli'), 3, False))
            yield '\n'
    l_1_port_channel_interface = l_1_encapsulation_cli = l_1_dfe_algo_cli = l_1_dfe_hold_time_cli = l_1_hide_passwords = l_1_interface_ip_nat = missing

blocks = {}
debug_info = '7=54&9=63&10=65&11=68&13=70&15=73&18=76&20=79&23=82&25=85&28=88&29=91&31=93&32=96&34=98&36=101&37=103&39=106&41=108&42=111&43=113&44=115&45=117&46=119&47=121&48=123&50=125&51=127&52=129&53=131&54=133&55=135&57=137&58=139&60=141&62=144&64=146&67=149&68=152&70=154&71=157&73=159&74=161&76=164&77=167&80=169&81=172&83=174&84=177&86=179&87=182&89=184&90=188&92=191&94=194&97=197&98=200&100=202&101=206&102=208&103=210&104=212&106=214&107=216&108=219&111=222&112=225&114=227&115=230&117=232&118=235&120=237&121=240&123=242&125=245&126=248&128=250&129=253&131=255&132=257&134=260&135=262&136=264&137=266&139=269&141=271&142=273&143=275&144=277&146=280&148=282&150=285&154=288&155=291&157=293&158=296&160=298&161=301&164=303&166=306&169=309&170=312&172=314&173=317&175=319&176=322&178=324&179=327&181=329&182=332&184=334&185=337&187=339&188=341&191=347&194=349&195=352&197=354&198=357&200=359&201=362&203=364&205=367&208=370&210=373&213=376&215=379&218=382&219=384&222=390&225=392&226=395&228=397&231=400&232=403&234=405&235=408&237=410&240=413&241=416&243=418&244=421&246=423&249=426&252=429&253=431&254=435&255=437&256=439&258=441&259=443&261=445&262=447&264=450&267=453&268=456&270=458&271=461&273=463&274=466&276=468&277=471&279=473&280=476&282=478&283=481&285=483&288=486&289=489&291=491&292=494&294=496&296=499&299=502&300=505&302=507&303=510&304=513&307=520&310=523&311=526&313=528&316=531&319=534&320=537&322=539&323=542&325=544&326=547&328=549&329=552&331=554&332=557&334=559&335=562&337=564&338=567&340=569&341=572&343=574&344=577&346=579&347=582&348=585&350=592&353=597&356=600&358=606&360=609&363=612&364=615&366=617&367=619&373=625&374=628&375=631&378=636&379=639&381=641&382=644&384=646&386=649&389=652&391=655&394=658&397=661&398=663&399=665&401=668&402=671&404=673&405=676&407=678&408=681&410=683&413=686&416=689&418=692&421=695&423=698&425=700&426=703&428=705&429=708&431=710&432=713&434=715&435=717&437=720&440=723&442=726&445=729&447=732&451=735&452=738'