from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ethernet-interfaces.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ethernet_interfaces = resolve('ethernet_interfaces')
    l_0_POE_CLASS_MAP = missing
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.hide_passwords']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.hide_passwords' found.")
    try:
        t_3 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_4 = environment.filters['float']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'float' found.")
    try:
        t_5 = environment.filters['format']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'format' found.")
    try:
        t_6 = environment.filters['indent']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'indent' found.")
    try:
        t_7 = environment.filters['replace']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No filter named 'replace' found.")
    try:
        t_8 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_8(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    l_0_POE_CLASS_MAP = {0: '15.40', 1: '4.00', 2: '7.00', 3: '15.40', 4: '30.00', 5: '45.00', 6: '60.00', 7: '75.00', 8: '90.00'}
    context.vars['POE_CLASS_MAP'] = l_0_POE_CLASS_MAP
    context.exported_vars.add('POE_CLASS_MAP')
    for l_1_ethernet_interface in t_3((undefined(name='ethernet_interfaces') if l_0_ethernet_interfaces is missing else l_0_ethernet_interfaces), 'name'):
        l_1_encapsulation_cli = resolve('encapsulation_cli')
        l_1_dfe_algo_cli = resolve('dfe_algo_cli')
        l_1_dfe_hold_time_cli = resolve('dfe_hold_time_cli')
        l_1_host_mode_cli = resolve('host_mode_cli')
        l_1_auth_cli = resolve('auth_cli')
        l_1_auth_failure_fallback_mba = resolve('auth_failure_fallback_mba')
        l_1_address_locking_cli = resolve('address_locking_cli')
        l_1_interface_ip_nat = resolve('interface_ip_nat')
        l_1_hide_passwords = resolve('hide_passwords')
        l_1_poe_link_down_action_cli = resolve('poe_link_down_action_cli')
        l_1_poe_limit_cli = resolve('poe_limit_cli')
        _loop_vars = {}
        pass
        yield '!\ninterface '
        yield str(environment.getattr(l_1_ethernet_interface, 'name'))
        yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'profile')):
            pass
            yield '   profile '
            yield str(environment.getattr(l_1_ethernet_interface, 'profile'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'description')):
            pass
            yield '   description '
            yield str(environment.getattr(l_1_ethernet_interface, 'description'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'shutdown'), True):
            pass
            yield '   shutdown\n'
        elif t_8(environment.getattr(l_1_ethernet_interface, 'shutdown'), False):
            pass
            yield '   no shutdown\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'load_interval')):
            pass
            yield '   load-interval '
            yield str(environment.getattr(l_1_ethernet_interface, 'load_interval'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'mtu')):
            pass
            yield '   mtu '
            yield str(environment.getattr(l_1_ethernet_interface, 'mtu'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'logging'), 'event')):
            pass
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'logging'), 'event'), 'link_status'), True):
                pass
                yield '   logging event link-status\n'
            elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'logging'), 'event'), 'link_status'), False):
                pass
                yield '   no logging event link-status\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'logging'), 'event'), 'congestion_drops'), True):
                pass
                yield '   logging event congestion-drops\n'
            elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'logging'), 'event'), 'congestion_drops'), False):
                pass
                yield '   no logging event congestion-drops\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'logging'), 'event'), 'spanning_tree'), True):
                pass
                yield '   logging event spanning-tree\n'
            elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'logging'), 'event'), 'spanning_tree'), False):
                pass
                yield '   no logging event spanning-tree\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'logging'), 'event'), 'storm_control_discards'), True):
                pass
                yield '   logging event storm-control discards\n'
            elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'logging'), 'event'), 'storm_control_discards'), False):
                pass
                yield '   no logging event storm-control discards\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'flowcontrol'), 'received')):
            pass
            yield '   flowcontrol receive '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'flowcontrol'), 'received'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'speed')):
            pass
            yield '   speed '
            yield str(environment.getattr(l_1_ethernet_interface, 'speed'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'l2_mtu')):
            pass
            yield '   l2 mtu '
            yield str(environment.getattr(l_1_ethernet_interface, 'l2_mtu'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'l2_mru')):
            pass
            yield '   l2 mru '
            yield str(environment.getattr(l_1_ethernet_interface, 'l2_mru'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'bgp'), 'session_tracker')):
            pass
            yield '   bgp session tracker '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'bgp'), 'session_tracker'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'mac_security'), 'profile')):
            pass
            yield '   mac security profile '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'mac_security'), 'profile'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'error_correction_encoding'), 'enabled'), False):
            pass
            yield '   no error-correction encoding\n'
        else:
            pass
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'error_correction_encoding'), 'fire_code'), True):
                pass
                yield '   error-correction encoding fire-code\n'
            elif t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'error_correction_encoding'), 'fire_code'), False):
                pass
                yield '   no error-correction encoding fire-code\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'error_correction_encoding'), 'reed_solomon'), True):
                pass
                yield '   error-correction encoding reed-solomon\n'
            elif t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'error_correction_encoding'), 'reed_solomon'), False):
                pass
                yield '   no error-correction encoding reed-solomon\n'
        if (t_8(environment.getattr(l_1_ethernet_interface, 'mode'), 'access') or t_8(environment.getattr(l_1_ethernet_interface, 'mode'), 'dot1q-tunnel')):
            pass
            if t_8(environment.getattr(l_1_ethernet_interface, 'vlans')):
                pass
                yield '   switchport access vlan '
                yield str(environment.getattr(l_1_ethernet_interface, 'vlans'))
                yield '\n'
        if (t_8(environment.getattr(l_1_ethernet_interface, 'mode')) and (environment.getattr(l_1_ethernet_interface, 'mode') in ['trunk', 'trunk phone'])):
            pass
            if t_8(environment.getattr(l_1_ethernet_interface, 'native_vlan_tag'), True):
                pass
                yield '   switchport trunk native vlan tag\n'
            elif t_8(environment.getattr(l_1_ethernet_interface, 'native_vlan')):
                pass
                yield '   switchport trunk native vlan '
                yield str(environment.getattr(l_1_ethernet_interface, 'native_vlan'))
                yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'phone'), 'vlan')):
            pass
            yield '   switchport phone vlan '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'phone'), 'vlan'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'phone'), 'trunk')):
            pass
            yield '   switchport phone trunk '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'phone'), 'trunk'))
            yield '\n'
        for l_2_vlan_translation in t_3(environment.getattr(l_1_ethernet_interface, 'vlan_translations')):
            l_2_vlan_translation_cli = resolve('vlan_translation_cli')
            _loop_vars = {}
            pass
            if (t_8(environment.getattr(l_2_vlan_translation, 'from')) and t_8(environment.getattr(l_2_vlan_translation, 'to'))):
                pass
                l_2_vlan_translation_cli = 'switchport vlan translation'
                _loop_vars['vlan_translation_cli'] = l_2_vlan_translation_cli
                if (t_1(environment.getattr(l_2_vlan_translation, 'direction')) in ['in', 'out']):
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
        if t_8(environment.getattr(l_1_ethernet_interface, 'mode'), 'trunk'):
            pass
            if t_8(environment.getattr(l_1_ethernet_interface, 'vlans')):
                pass
                yield '   switchport trunk allowed vlan '
                yield str(environment.getattr(l_1_ethernet_interface, 'vlans'))
                yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'mode')):
            pass
            yield '   switchport mode '
            yield str(environment.getattr(l_1_ethernet_interface, 'mode'))
            yield '\n'
        for l_2_trunk_group in t_3(environment.getattr(l_1_ethernet_interface, 'trunk_groups')):
            _loop_vars = {}
            pass
            yield '   switchport trunk group '
            yield str(l_2_trunk_group)
            yield '\n'
        l_2_trunk_group = missing
        if t_8(environment.getattr(l_1_ethernet_interface, 'type'), 'routed'):
            pass
            yield '   no switchport\n'
        elif (t_1(environment.getattr(l_1_ethernet_interface, 'type')) in ['l3dot1q', 'l2dot1q']):
            pass
            if (t_8(environment.getattr(l_1_ethernet_interface, 'vlan_id')) and (environment.getattr(l_1_ethernet_interface, 'type') == 'l2dot1q')):
                pass
                yield '   vlan id '
                yield str(environment.getattr(l_1_ethernet_interface, 'vlan_id'))
                yield '\n'
            if t_8(environment.getattr(l_1_ethernet_interface, 'encapsulation_dot1q_vlan')):
                pass
                yield '   encapsulation dot1q vlan '
                yield str(environment.getattr(l_1_ethernet_interface, 'encapsulation_dot1q_vlan'))
                yield '\n'
            elif t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'vlan')):
                pass
                l_1_encapsulation_cli = str_join(('client dot1q ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'vlan'), ))
                _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                if t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'vlan')):
                    pass
                    l_1_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli), ' network dot1q ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'vlan'), ))
                    _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'network'), 'client'), True):
                    pass
                    l_1_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli), ' network client', ))
                    _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
            elif (t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'inner')) and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'outer'))):
                pass
                l_1_encapsulation_cli = str_join(('client dot1q outer ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'outer'), ' inner ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'client'), 'dot1q'), 'inner'), ))
                _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                if (t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'inner')) and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'outer'))):
                    pass
                    l_1_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli), ' network dot1q outer ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'inner'), ' inner ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'outer'), ))
                    _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                elif t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'network'), 'dot1q'), 'client'), True):
                    pass
                    l_1_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli), ' network client', ))
                    _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
            elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'encapsulation_vlan'), 'client'), 'unmatched'), True):
                pass
                l_1_encapsulation_cli = 'client unmatched'
                _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
            if t_8((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli)):
                pass
                yield '   encapsulation vlan\n      '
                yield str((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli))
                yield '\n'
        elif (t_1(environment.getattr(l_1_ethernet_interface, 'type'), 'switched') == 'switched'):
            pass
            yield '   switchport\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'trunk_private_vlan_secondary'), True):
            pass
            yield '   switchport trunk private-vlan secondary\n'
        elif t_8(environment.getattr(l_1_ethernet_interface, 'trunk_private_vlan_secondary'), False):
            pass
            yield '   no switchport trunk private-vlan secondary\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'pvlan_mapping')):
            pass
            yield '   switchport pvlan mapping '
            yield str(environment.getattr(l_1_ethernet_interface, 'pvlan_mapping'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'l2_protocol'), 'encapsulation_dot1q_vlan')):
            pass
            yield '   l2-protocol encapsulation dot1q vlan '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'l2_protocol'), 'encapsulation_dot1q_vlan'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'l2_protocol'), 'forwarding_profile')):
            pass
            yield '   l2-protocol forwarding profile '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'l2_protocol'), 'forwarding_profile'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'flow_tracker'), 'hardware')):
            pass
            yield '   flow tracker hardware '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'flow_tracker'), 'hardware'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'flow_tracker'), 'sampled')):
            pass
            yield '   flow tracker sampled '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'flow_tracker'), 'sampled'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment')):
            pass
            yield '   evpn ethernet-segment\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'identifier')):
                pass
                yield '      identifier '
                yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'identifier'))
                yield '\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'redundancy')):
                pass
                yield '      redundancy '
                yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'redundancy'))
                yield '\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election')):
                pass
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'algorithm'), 'modulus'):
                    pass
                    yield '      designated-forwarder election algorithm modulus\n'
                elif (t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'algorithm'), 'preference') and t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'preference_value'))):
                    pass
                    l_1_dfe_algo_cli = str_join(('designated-forwarder election algorithm preference ', environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'preference_value'), ))
                    _loop_vars['dfe_algo_cli'] = l_1_dfe_algo_cli
                    if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'dont_preempt'), True):
                        pass
                        l_1_dfe_algo_cli = str_join(((undefined(name='dfe_algo_cli') if l_1_dfe_algo_cli is missing else l_1_dfe_algo_cli), ' dont-preempt', ))
                        _loop_vars['dfe_algo_cli'] = l_1_dfe_algo_cli
                    yield '      '
                    yield str((undefined(name='dfe_algo_cli') if l_1_dfe_algo_cli is missing else l_1_dfe_algo_cli))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'hold_time')):
                    pass
                    l_1_dfe_hold_time_cli = str_join(('designated-forwarder election hold-time ', environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'hold_time'), ))
                    _loop_vars['dfe_hold_time_cli'] = l_1_dfe_hold_time_cli
                    if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'subsequent_hold_time')):
                        pass
                        l_1_dfe_hold_time_cli = str_join(((undefined(name='dfe_hold_time_cli') if l_1_dfe_hold_time_cli is missing else l_1_dfe_hold_time_cli), ' subsequent-hold-time ', environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'subsequent_hold_time'), ))
                        _loop_vars['dfe_hold_time_cli'] = l_1_dfe_hold_time_cli
                    yield '      '
                    yield str((undefined(name='dfe_hold_time_cli') if l_1_dfe_hold_time_cli is missing else l_1_dfe_hold_time_cli))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'candidate_reachability_required'), True):
                    pass
                    yield '      designated-forwarder election candidate reachability required\n'
                elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'designated_forwarder_election'), 'candidate_reachability_required'), False):
                    pass
                    yield '      no designated-forwarder election candidate reachability required\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'mpls'), 'tunnel_flood_filter_time')):
                pass
                yield '      mpls tunnel flood filter time '
                yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'mpls'), 'tunnel_flood_filter_time'))
                yield '\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'mpls'), 'shared_index')):
                pass
                yield '      mpls shared index '
                yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'mpls'), 'shared_index'))
                yield '\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'route_target')):
                pass
                yield '      route-target import '
                yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'evpn_ethernet_segment'), 'route_target'))
                yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'dot1x')):
            pass
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'pae'), 'mode')):
                pass
                yield '   dot1x pae '
                yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'pae'), 'mode'))
                yield '\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'authentication_failure')):
                pass
                if (t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'authentication_failure'), 'action'), 'allow') and t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'authentication_failure'), 'allow_vlan'))):
                    pass
                    yield '   dot1x authentication failure action traffic allow vlan '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'authentication_failure'), 'allow_vlan'))
                    yield '\n'
                elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'authentication_failure'), 'action'), 'drop'):
                    pass
                    yield '   dot1x authentication failure action traffic drop\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'reauthentication'), True):
                pass
                yield '   dot1x reauthentication\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'port_control')):
                pass
                yield '   dot1x port-control '
                yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'port_control'))
                yield '\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'port_control_force_authorized_phone'), True):
                pass
                yield '   dot1x port-control force-authorized phone\n'
            elif t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'port_control_force_authorized_phone'), False):
                pass
                yield '   no dot1x port-control force-authorized phone\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'host_mode')):
                pass
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'host_mode'), 'mode'), 'single-host'):
                    pass
                    yield '   dot1x host-mode single-host\n'
                elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'host_mode'), 'mode'), 'multi-host'):
                    pass
                    l_1_host_mode_cli = 'dot1x host-mode multi-host'
                    _loop_vars['host_mode_cli'] = l_1_host_mode_cli
                    if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'host_mode'), 'multi_host_authenticated'), True):
                        pass
                        l_1_host_mode_cli = str_join(((undefined(name='host_mode_cli') if l_1_host_mode_cli is missing else l_1_host_mode_cli), ' authenticated', ))
                        _loop_vars['host_mode_cli'] = l_1_host_mode_cli
                    yield '   '
                    yield str((undefined(name='host_mode_cli') if l_1_host_mode_cli is missing else l_1_host_mode_cli))
                    yield '\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'mac_based_authentication'), 'enabled'), True):
                pass
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'mac_based_authentication'), 'host_mode_common'), True):
                    pass
                    yield '   dot1x mac based authentication host-mode common\n'
                    if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'mac_based_authentication'), 'always'), True):
                        pass
                        yield '   dot1x mac based authentication always\n'
                else:
                    pass
                    l_1_auth_cli = 'dot1x mac based authentication'
                    _loop_vars['auth_cli'] = l_1_auth_cli
                    if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'mac_based_authentication'), 'always'), True):
                        pass
                        l_1_auth_cli = str_join(((undefined(name='auth_cli') if l_1_auth_cli is missing else l_1_auth_cli), ' always', ))
                        _loop_vars['auth_cli'] = l_1_auth_cli
                    yield '   '
                    yield str((undefined(name='auth_cli') if l_1_auth_cli is missing else l_1_auth_cli))
                    yield '\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'timeout')):
                pass
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'timeout'), 'quiet_period')):
                    pass
                    yield '   dot1x timeout quiet-period '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'timeout'), 'quiet_period'))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'timeout'), 'reauth_timeout_ignore'), True):
                    pass
                    yield '   dot1x timeout reauth-timeout-ignore always\n'
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'timeout'), 'tx_period')):
                    pass
                    yield '   dot1x timeout tx-period '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'timeout'), 'tx_period'))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'timeout'), 'reauth_period')):
                    pass
                    yield '   dot1x timeout reauth-period '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'timeout'), 'reauth_period'))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'timeout'), 'idle_host')):
                    pass
                    yield '   dot1x timeout idle-host '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'timeout'), 'idle_host'))
                    yield ' seconds\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'reauthorization_request_limit')):
                pass
                yield '   dot1x reauthorization request limit '
                yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'reauthorization_request_limit'))
                yield '\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'unauthorized'), 'access_vlan_membership_egress'), True):
                pass
                yield '   dot1x unauthorized access vlan membership egress\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'unauthorized'), 'native_vlan_membership_egress'), True):
                pass
                yield '   dot1x unauthorized native vlan membership egress\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'eapol')):
                pass
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'eapol'), 'disabled'), True):
                    pass
                    yield '   dot1x eapol disabled\n'
                elif t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'eapol'), 'authentication_failure_fallback_mba'), 'enabled'), True):
                    pass
                    l_1_auth_failure_fallback_mba = 'dot1x eapol authentication failure fallback mba'
                    _loop_vars['auth_failure_fallback_mba'] = l_1_auth_failure_fallback_mba
                    if t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'eapol'), 'authentication_failure_fallback_mba'), 'timeout')):
                        pass
                        l_1_auth_failure_fallback_mba = str_join(((undefined(name='auth_failure_fallback_mba') if l_1_auth_failure_fallback_mba is missing else l_1_auth_failure_fallback_mba), ' timeout ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'dot1x'), 'eapol'), 'authentication_failure_fallback_mba'), 'timeout'), ))
                        _loop_vars['auth_failure_fallback_mba'] = l_1_auth_failure_fallback_mba
                    yield '   '
                    yield str((undefined(name='auth_failure_fallback_mba') if l_1_auth_failure_fallback_mba is missing else l_1_auth_failure_fallback_mba))
                    yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'snmp_trap_link_change'), False):
            pass
            yield '   no snmp trap link-change\n'
        elif t_8(environment.getattr(l_1_ethernet_interface, 'snmp_trap_link_change'), True):
            pass
            yield '   snmp trap link-change\n'
        if (t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'address_locking'), 'ipv4'), True) or t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'address_locking'), 'ipv6'), True)):
            pass
            l_1_address_locking_cli = 'address locking'
            _loop_vars['address_locking_cli'] = l_1_address_locking_cli
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'address_locking'), 'ipv4'), True):
                pass
                l_1_address_locking_cli = ((undefined(name='address_locking_cli') if l_1_address_locking_cli is missing else l_1_address_locking_cli) + ' ipv4')
                _loop_vars['address_locking_cli'] = l_1_address_locking_cli
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'address_locking'), 'ipv6'), True):
                pass
                l_1_address_locking_cli = ((undefined(name='address_locking_cli') if l_1_address_locking_cli is missing else l_1_address_locking_cli) + ' ipv6')
                _loop_vars['address_locking_cli'] = l_1_address_locking_cli
            yield '   '
            yield str((undefined(name='address_locking_cli') if l_1_address_locking_cli is missing else l_1_address_locking_cli))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'vrf')):
            pass
            yield '   vrf '
            yield str(environment.getattr(l_1_ethernet_interface, 'vrf'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ip_proxy_arp'), True):
            pass
            yield '   ip proxy-arp\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ip_address')):
            pass
            yield '   ip address '
            yield str(environment.getattr(l_1_ethernet_interface, 'ip_address'))
            yield '\n'
            if t_8(environment.getattr(l_1_ethernet_interface, 'ip_address_secondaries')):
                pass
                for l_2_ip_address_secondary in environment.getattr(l_1_ethernet_interface, 'ip_address_secondaries'):
                    _loop_vars = {}
                    pass
                    yield '   ip address '
                    yield str(l_2_ip_address_secondary)
                    yield ' secondary\n'
                l_2_ip_address_secondary = missing
            for l_2_ip_helper in t_3(environment.getattr(l_1_ethernet_interface, 'ip_helpers'), 'ip_helper'):
                l_2_ip_helper_cli = missing
                _loop_vars = {}
                pass
                l_2_ip_helper_cli = str_join(('ip helper-address ', environment.getattr(l_2_ip_helper, 'ip_helper'), ))
                _loop_vars['ip_helper_cli'] = l_2_ip_helper_cli
                if t_8(environment.getattr(l_2_ip_helper, 'vrf')):
                    pass
                    l_2_ip_helper_cli = str_join(((undefined(name='ip_helper_cli') if l_2_ip_helper_cli is missing else l_2_ip_helper_cli), ' vrf ', environment.getattr(l_2_ip_helper, 'vrf'), ))
                    _loop_vars['ip_helper_cli'] = l_2_ip_helper_cli
                if t_8(environment.getattr(l_2_ip_helper, 'source_interface')):
                    pass
                    l_2_ip_helper_cli = str_join(((undefined(name='ip_helper_cli') if l_2_ip_helper_cli is missing else l_2_ip_helper_cli), ' source-interface ', environment.getattr(l_2_ip_helper, 'source_interface'), ))
                    _loop_vars['ip_helper_cli'] = l_2_ip_helper_cli
                yield '   '
                yield str((undefined(name='ip_helper_cli') if l_2_ip_helper_cli is missing else l_2_ip_helper_cli))
                yield '\n'
            l_2_ip_helper = l_2_ip_helper_cli = missing
        if (t_8(environment.getattr(l_1_ethernet_interface, 'ip_address'), 'dhcp') and t_8(environment.getattr(l_1_ethernet_interface, 'dhcp_client_accept_default_route'), True)):
            pass
            yield '   dhcp client accept default-route\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ip_verify_unicast_source_reachable_via')):
            pass
            yield '   ip verify unicast source reachable-via '
            yield str(environment.getattr(l_1_ethernet_interface, 'ip_verify_unicast_source_reachable_via'))
            yield '\n'
        if ((t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'bfd'), 'interval')) and t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'bfd'), 'min_rx'))) and t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'bfd'), 'multiplier'))):
            pass
            yield '   bfd interval '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'bfd'), 'interval'))
            yield ' min-rx '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'bfd'), 'min_rx'))
            yield ' multiplier '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'bfd'), 'multiplier'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'bfd'), 'echo'), True):
            pass
            yield '   bfd echo\n'
        elif t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'bfd'), 'echo'), False):
            pass
            yield '   no bfd echo\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'dhcp_server_ipv4'), True):
            pass
            yield '   dhcp server ipv4\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'dhcp_server_ipv6'), True):
            pass
            yield '   dhcp server ipv6\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ipv6_enable'), True):
            pass
            yield '   ipv6 enable\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ipv6_address')):
            pass
            yield '   ipv6 address '
            yield str(environment.getattr(l_1_ethernet_interface, 'ipv6_address'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ipv6_address_link_local')):
            pass
            yield '   ipv6 address '
            yield str(environment.getattr(l_1_ethernet_interface, 'ipv6_address_link_local'))
            yield ' link-local\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ipv6_nd_ra_disabled'), True):
            pass
            yield '   ipv6 nd ra disabled\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ipv6_nd_managed_config_flag'), True):
            pass
            yield '   ipv6 nd managed-config-flag\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ipv6_nd_prefixes')):
            pass
            for l_2_prefix in environment.getattr(l_1_ethernet_interface, 'ipv6_nd_prefixes'):
                l_2_ipv6_nd_prefix_cli = missing
                _loop_vars = {}
                pass
                l_2_ipv6_nd_prefix_cli = str_join(('ipv6 nd prefix ', environment.getattr(l_2_prefix, 'ipv6_prefix'), ))
                _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                if t_8(environment.getattr(l_2_prefix, 'valid_lifetime')):
                    pass
                    l_2_ipv6_nd_prefix_cli = str_join(((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli), ' ', environment.getattr(l_2_prefix, 'valid_lifetime'), ))
                    _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                    if t_8(environment.getattr(l_2_prefix, 'preferred_lifetime')):
                        pass
                        l_2_ipv6_nd_prefix_cli = str_join(((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli), ' ', environment.getattr(l_2_prefix, 'preferred_lifetime'), ))
                        _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                if t_8(environment.getattr(l_2_prefix, 'no_autoconfig_flag'), True):
                    pass
                    l_2_ipv6_nd_prefix_cli = str_join(((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli), ' no-autoconfig', ))
                    _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                yield '   '
                yield str((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli))
                yield '\n'
            l_2_prefix = l_2_ipv6_nd_prefix_cli = missing
        for l_2_destination in t_3(environment.getattr(l_1_ethernet_interface, 'ipv6_dhcp_relay_destinations'), 'address'):
            l_2_destination_cli = missing
            _loop_vars = {}
            pass
            l_2_destination_cli = str_join(('ipv6 dhcp relay destination ', environment.getattr(l_2_destination, 'address'), ))
            _loop_vars['destination_cli'] = l_2_destination_cli
            if t_8(environment.getattr(l_2_destination, 'vrf')):
                pass
                l_2_destination_cli = str_join(((undefined(name='destination_cli') if l_2_destination_cli is missing else l_2_destination_cli), ' vrf ', environment.getattr(l_2_destination, 'vrf'), ))
                _loop_vars['destination_cli'] = l_2_destination_cli
            if t_8(environment.getattr(l_2_destination, 'local_interface')):
                pass
                l_2_destination_cli = str_join(((undefined(name='destination_cli') if l_2_destination_cli is missing else l_2_destination_cli), ' local-interface ', environment.getattr(l_2_destination, 'local_interface'), ))
                _loop_vars['destination_cli'] = l_2_destination_cli
            elif t_8(environment.getattr(l_2_destination, 'source_address')):
                pass
                l_2_destination_cli = str_join(((undefined(name='destination_cli') if l_2_destination_cli is missing else l_2_destination_cli), ' source-address ', environment.getattr(l_2_destination, 'source_address'), ))
                _loop_vars['destination_cli'] = l_2_destination_cli
            if t_8(environment.getattr(l_2_destination, 'link_address')):
                pass
                l_2_destination_cli = str_join(((undefined(name='destination_cli') if l_2_destination_cli is missing else l_2_destination_cli), ' link-address ', environment.getattr(l_2_destination, 'link_address'), ))
                _loop_vars['destination_cli'] = l_2_destination_cli
            yield '   '
            yield str((undefined(name='destination_cli') if l_2_destination_cli is missing else l_2_destination_cli))
            yield '\n'
        l_2_destination = l_2_destination_cli = missing
        if (t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'channel_group'), 'id')) and t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'channel_group'), 'mode'))):
            pass
            yield '   channel-group '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'channel_group'), 'id'))
            yield ' mode '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'channel_group'), 'mode'))
            yield '\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'lacp_timer'), 'mode')):
                pass
                yield '   lacp timer '
                yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'lacp_timer'), 'mode'))
                yield '\n'
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'lacp_timer'), 'multiplier')):
                pass
                yield '   lacp timer multiplier '
                yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'lacp_timer'), 'multiplier'))
                yield '\n'
            if t_8(environment.getattr(l_1_ethernet_interface, 'lacp_port_priority')):
                pass
                yield '   lacp port-priority '
                yield str(environment.getattr(l_1_ethernet_interface, 'lacp_port_priority'))
                yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'lldp'), 'transmit'), False):
            pass
            yield '   no lldp transmit\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'lldp'), 'receive'), False):
            pass
            yield '   no lldp receive\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'lldp'), 'ztp_vlan')):
            pass
            yield '   lldp tlv transmit ztp vlan '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'lldp'), 'ztp_vlan'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'mpls'), 'ldp'), 'igp_sync'), True):
            pass
            yield '   mpls ldp igp sync\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'mpls'), 'ldp'), 'interface'), True):
            pass
            yield '   mpls ldp interface\n'
        elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'mpls'), 'ldp'), 'interface'), False):
            pass
            yield '   no mpls ldp interface\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'access_group_in')):
            pass
            yield '   ip access-group '
            yield str(environment.getattr(l_1_ethernet_interface, 'access_group_in'))
            yield ' in\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'access_group_out')):
            pass
            yield '   ip access-group '
            yield str(environment.getattr(l_1_ethernet_interface, 'access_group_out'))
            yield ' out\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ipv6_access_group_in')):
            pass
            yield '   ipv6 access-group '
            yield str(environment.getattr(l_1_ethernet_interface, 'ipv6_access_group_in'))
            yield ' in\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ipv6_access_group_out')):
            pass
            yield '   ipv6 access-group '
            yield str(environment.getattr(l_1_ethernet_interface, 'ipv6_access_group_out'))
            yield ' out\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'mac_access_group_in')):
            pass
            yield '   mac access-group '
            yield str(environment.getattr(l_1_ethernet_interface, 'mac_access_group_in'))
            yield ' in\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'mac_access_group_out')):
            pass
            yield '   mac access-group '
            yield str(environment.getattr(l_1_ethernet_interface, 'mac_access_group_out'))
            yield ' out\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'multicast')):
            pass
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'multicast'), 'ipv4'), 'boundaries')):
                pass
                for l_2_boundary in environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'multicast'), 'ipv4'), 'boundaries'):
                    l_2_boundary_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_boundary_cli = str_join(('multicast ipv4 boundary ', environment.getattr(l_2_boundary, 'boundary'), ))
                    _loop_vars['boundary_cli'] = l_2_boundary_cli
                    if t_8(environment.getattr(l_2_boundary, 'out'), True):
                        pass
                        l_2_boundary_cli = str_join(((undefined(name='boundary_cli') if l_2_boundary_cli is missing else l_2_boundary_cli), ' out', ))
                        _loop_vars['boundary_cli'] = l_2_boundary_cli
                    yield '   '
                    yield str((undefined(name='boundary_cli') if l_2_boundary_cli is missing else l_2_boundary_cli))
                    yield '\n'
                l_2_boundary = l_2_boundary_cli = missing
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'multicast'), 'ipv6'), 'boundaries')):
                pass
                for l_2_boundary in environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'multicast'), 'ipv6'), 'boundaries'):
                    _loop_vars = {}
                    pass
                    yield '   multicast ipv6 boundary '
                    yield str(environment.getattr(l_2_boundary, 'boundary'))
                    yield ' out\n'
                l_2_boundary = missing
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'multicast'), 'ipv4'), 'static'), True):
                pass
                yield '   multicast ipv4 static\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'multicast'), 'ipv6'), 'static'), True):
                pass
                yield '   multicast ipv6 static\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'mpls'), 'ip'), True):
            pass
            yield '   mpls ip\n'
        elif t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'mpls'), 'ip'), False):
            pass
            yield '   no mpls ip\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ip_nat')):
            pass
            l_1_interface_ip_nat = environment.getattr(l_1_ethernet_interface, 'ip_nat')
            _loop_vars['interface_ip_nat'] = l_1_interface_ip_nat
            template = environment.get_template('eos/interface-ip-nat.j2', 'eos/ethernet-interfaces.j2')
            for event in template.root_render_func(template.new_context(context.get_all(), True, {'address_locking_cli': l_1_address_locking_cli, 'auth_cli': l_1_auth_cli, 'auth_failure_fallback_mba': l_1_auth_failure_fallback_mba, 'dfe_algo_cli': l_1_dfe_algo_cli, 'dfe_hold_time_cli': l_1_dfe_hold_time_cli, 'encapsulation_cli': l_1_encapsulation_cli, 'ethernet_interface': l_1_ethernet_interface, 'host_mode_cli': l_1_host_mode_cli, 'interface_ip_nat': l_1_interface_ip_nat, 'poe_limit_cli': l_1_poe_limit_cli, 'poe_link_down_action_cli': l_1_poe_link_down_action_cli, 'POE_CLASS_MAP': l_0_POE_CLASS_MAP})):
                yield event
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ip_nat'), 'service_profile')):
                pass
                yield '   ip nat service-profile '
                yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ip_nat'), 'service_profile'))
                yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ospf_cost')):
            pass
            yield '   ip ospf cost '
            yield str(environment.getattr(l_1_ethernet_interface, 'ospf_cost'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ospf_network_point_to_point'), True):
            pass
            yield '   ip ospf network point-to-point\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ospf_authentication'), 'simple'):
            pass
            yield '   ip ospf authentication\n'
        elif t_8(environment.getattr(l_1_ethernet_interface, 'ospf_authentication'), 'message-digest'):
            pass
            yield '   ip ospf authentication message-digest\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ospf_authentication_key')):
            pass
            yield '   ip ospf authentication-key 7 '
            yield str(t_2(environment.getattr(l_1_ethernet_interface, 'ospf_authentication_key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'ospf_area')):
            pass
            yield '   ip ospf area '
            yield str(environment.getattr(l_1_ethernet_interface, 'ospf_area'))
            yield '\n'
        for l_2_ospf_message_digest_key in t_3(environment.getattr(l_1_ethernet_interface, 'ospf_message_digest_keys'), 'id'):
            _loop_vars = {}
            pass
            if (t_8(environment.getattr(l_2_ospf_message_digest_key, 'hash_algorithm')) and t_8(environment.getattr(l_2_ospf_message_digest_key, 'key'))):
                pass
                yield '   ip ospf message-digest-key '
                yield str(environment.getattr(l_2_ospf_message_digest_key, 'id'))
                yield ' '
                yield str(environment.getattr(l_2_ospf_message_digest_key, 'hash_algorithm'))
                yield ' 7 '
                yield str(t_2(environment.getattr(l_2_ospf_message_digest_key, 'key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
                yield '\n'
        l_2_ospf_message_digest_key = missing
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'pim'), 'ipv4'), 'sparse_mode'), True):
            pass
            yield '   pim ipv4 sparse-mode\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'pim'), 'ipv4'), 'dr_priority')):
            pass
            yield '   pim ipv4 dr-priority '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'pim'), 'ipv4'), 'dr_priority'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'priority')):
            pass
            yield '   poe priority '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'priority'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'reboot'), 'action')):
            pass
            yield '   poe reboot action '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'reboot'), 'action'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'link_down'), 'action')):
            pass
            l_1_poe_link_down_action_cli = str_join(('poe link down action ', environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'link_down'), 'action'), ))
            _loop_vars['poe_link_down_action_cli'] = l_1_poe_link_down_action_cli
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'link_down'), 'power_off_delay')):
                pass
                l_1_poe_link_down_action_cli = str_join(((undefined(name='poe_link_down_action_cli') if l_1_poe_link_down_action_cli is missing else l_1_poe_link_down_action_cli), ' ', environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'link_down'), 'power_off_delay'), ))
                _loop_vars['poe_link_down_action_cli'] = l_1_poe_link_down_action_cli
            yield '   '
            yield str((undefined(name='poe_link_down_action_cli') if l_1_poe_link_down_action_cli is missing else l_1_poe_link_down_action_cli))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'shutdown'), 'action')):
            pass
            yield '   poe shutdown action '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'shutdown'), 'action'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'disabled'), True):
            pass
            yield '   poe disabled\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'limit')):
            pass
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'limit'), 'class')):
                pass
                l_1_poe_limit_cli = str_join(('poe limit ', environment.getitem((undefined(name='POE_CLASS_MAP') if l_0_POE_CLASS_MAP is missing else l_0_POE_CLASS_MAP), environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'limit'), 'class')), ' watts', ))
                _loop_vars['poe_limit_cli'] = l_1_poe_limit_cli
            elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'limit'), 'watts')):
                pass
                l_1_poe_limit_cli = str_join(('poe limit ', t_5('%.2f', t_4(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'limit'), 'watts'))), ' watts', ))
                _loop_vars['poe_limit_cli'] = l_1_poe_limit_cli
            if (t_8((undefined(name='poe_limit_cli') if l_1_poe_limit_cli is missing else l_1_poe_limit_cli)) and t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'limit'), 'fixed'), True)):
                pass
                l_1_poe_limit_cli = str_join(((undefined(name='poe_limit_cli') if l_1_poe_limit_cli is missing else l_1_poe_limit_cli), ' fixed', ))
                _loop_vars['poe_limit_cli'] = l_1_poe_limit_cli
            yield '   '
            yield str((undefined(name='poe_limit_cli') if l_1_poe_limit_cli is missing else l_1_poe_limit_cli))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'negotiation_lldp'), False):
            pass
            yield '   poe negotiation lldp disabled\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'poe'), 'legacy_detect'), True):
            pass
            yield '   poe legacy detect\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'qos'), 'trust')):
            pass
            if (environment.getattr(environment.getattr(l_1_ethernet_interface, 'qos'), 'trust') == 'disabled'):
                pass
                yield '   no qos trust\n'
            else:
                pass
                yield '   qos trust '
                yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'qos'), 'trust'))
                yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'qos'), 'cos')):
            pass
            yield '   qos cos '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'qos'), 'cos'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'qos'), 'dscp')):
            pass
            yield '   qos dscp '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'qos'), 'dscp'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'shape'), 'rate')):
            pass
            yield '   shape rate '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'shape'), 'rate'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'priority_flow_control'), 'enabled'), True):
            pass
            yield '   priority-flow-control on\n'
        elif t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'priority_flow_control'), 'enabled'), False):
            pass
            yield '   no priority-flow-control\n'
        for l_2_priority_block in t_3(environment.getattr(environment.getattr(l_1_ethernet_interface, 'priority_flow_control'), 'priorities')):
            _loop_vars = {}
            pass
            if t_8(environment.getattr(l_2_priority_block, 'priority')):
                pass
                if t_8(environment.getattr(l_2_priority_block, 'no_drop'), True):
                    pass
                    yield '   priority-flow-control priority '
                    yield str(environment.getattr(l_2_priority_block, 'priority'))
                    yield ' no-drop\n'
                elif t_8(environment.getattr(l_2_priority_block, 'no_drop'), False):
                    pass
                    yield '   priority-flow-control priority '
                    yield str(environment.getattr(l_2_priority_block, 'priority'))
                    yield ' drop\n'
        l_2_priority_block = missing
        for l_2_section in t_3(environment.getattr(l_1_ethernet_interface, 'storm_control')):
            _loop_vars = {}
            pass
            if t_8(environment.getattr(environment.getitem(environment.getattr(l_1_ethernet_interface, 'storm_control'), l_2_section), 'level')):
                pass
                if t_8(environment.getattr(environment.getitem(environment.getattr(l_1_ethernet_interface, 'storm_control'), l_2_section), 'unit'), 'pps'):
                    pass
                    yield '   storm-control '
                    yield str(t_7(context.eval_ctx, l_2_section, '_', '-'))
                    yield ' level pps '
                    yield str(environment.getattr(environment.getitem(environment.getattr(l_1_ethernet_interface, 'storm_control'), l_2_section), 'level'))
                    yield '\n'
                else:
                    pass
                    yield '   storm-control '
                    yield str(t_7(context.eval_ctx, l_2_section, '_', '-'))
                    yield ' level '
                    yield str(environment.getattr(environment.getitem(environment.getattr(l_1_ethernet_interface, 'storm_control'), l_2_section), 'level'))
                    yield '\n'
        l_2_section = missing
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'enable'), True):
            pass
            yield '   ptp enable\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'sync_message'), 'interval')):
            pass
            yield '   ptp sync-message interval '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'sync_message'), 'interval'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'delay_mechanism')):
            pass
            yield '   ptp delay-mechanism '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'delay_mechanism'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'announce'), 'interval')):
            pass
            yield '   ptp announce interval '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'announce'), 'interval'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'transport')):
            pass
            yield '   ptp transport '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'transport'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'announce'), 'timeout')):
            pass
            yield '   ptp announce timeout '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'announce'), 'timeout'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'delay_req')):
            pass
            yield '   ptp delay-req interval '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'delay_req'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'role')):
            pass
            yield '   ptp role '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'role'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'vlan')):
            pass
            yield '   ptp vlan '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'ptp'), 'vlan'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'service_policy'), 'pbr'), 'input')):
            pass
            yield '   service-policy type pbr input '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'service_policy'), 'pbr'), 'input'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'service_policy'), 'qos'), 'input')):
            pass
            yield '   service-policy type qos input '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'service_policy'), 'qos'), 'input'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'service_profile')):
            pass
            yield '   service-profile '
            yield str(environment.getattr(l_1_ethernet_interface, 'service_profile'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'isis_enable')):
            pass
            yield '   isis enable '
            yield str(environment.getattr(l_1_ethernet_interface, 'isis_enable'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'isis_circuit_type')):
            pass
            yield '   isis circuit-type '
            yield str(environment.getattr(l_1_ethernet_interface, 'isis_circuit_type'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'isis_metric')):
            pass
            yield '   isis metric '
            yield str(environment.getattr(l_1_ethernet_interface, 'isis_metric'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'isis_passive'), True):
            pass
            yield '   isis passive\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'isis_hello_padding'), False):
            pass
            yield '   no isis hello padding\n'
        elif t_8(environment.getattr(l_1_ethernet_interface, 'isis_hello_padding'), True):
            pass
            yield '   isis hello padding\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'isis_network_point_to_point'), True):
            pass
            yield '   isis network point-to-point\n'
        if (t_8(environment.getattr(l_1_ethernet_interface, 'isis_authentication_mode')) and (environment.getattr(l_1_ethernet_interface, 'isis_authentication_mode') in ['text', 'md5'])):
            pass
            yield '   isis authentication mode '
            yield str(environment.getattr(l_1_ethernet_interface, 'isis_authentication_mode'))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'isis_authentication_key')):
            pass
            yield '   isis authentication key 7 '
            yield str(t_2(environment.getattr(l_1_ethernet_interface, 'isis_authentication_key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
            yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'spanning_tree_portfast'), 'edge'):
            pass
            yield '   spanning-tree portfast\n'
        elif t_8(environment.getattr(l_1_ethernet_interface, 'spanning_tree_portfast'), 'network'):
            pass
            yield '   spanning-tree portfast network\n'
        if (t_8(environment.getattr(l_1_ethernet_interface, 'spanning_tree_bpduguard')) and (environment.getattr(l_1_ethernet_interface, 'spanning_tree_bpduguard') in [True, 'True', 'enabled'])):
            pass
            yield '   spanning-tree bpduguard enable\n'
        elif t_8(environment.getattr(l_1_ethernet_interface, 'spanning_tree_bpduguard'), 'disabled'):
            pass
            yield '   spanning-tree bpduguard disable\n'
        if (t_8(environment.getattr(l_1_ethernet_interface, 'spanning_tree_bpdufilter')) and (environment.getattr(l_1_ethernet_interface, 'spanning_tree_bpdufilter') in [True, 'True', 'enabled'])):
            pass
            yield '   spanning-tree bpdufilter enable\n'
        elif t_8(environment.getattr(l_1_ethernet_interface, 'spanning_tree_bpdufilter'), 'disabled'):
            pass
            yield '   spanning-tree bpdufilter disable\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'spanning_tree_guard')):
            pass
            if (environment.getattr(l_1_ethernet_interface, 'spanning_tree_guard') == 'disabled'):
                pass
                yield '   spanning-tree guard none\n'
            else:
                pass
                yield '   spanning-tree guard '
                yield str(environment.getattr(l_1_ethernet_interface, 'spanning_tree_guard'))
                yield '\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'sflow')):
            pass
            if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'sflow'), 'enable'), True):
                pass
                yield '   sflow enable\n'
            elif t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'sflow'), 'enable'), False):
                pass
                yield '   no sflow enable\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'sflow'), 'egress'), 'enable'), True):
                pass
                yield '   sflow egress enable\n'
            elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'sflow'), 'egress'), 'enable'), False):
                pass
                yield '   no sflow egress enable\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'sflow'), 'egress'), 'unmodified_enable'), True):
                pass
                yield '   sflow egress unmodified enable\n'
            elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'sflow'), 'egress'), 'unmodified_enable'), False):
                pass
                yield '   no sflow egress unmodified enable\n'
        if t_8(environment.getattr(l_1_ethernet_interface, 'vmtracer'), True):
            pass
            yield '   vmtracer vmware-esx\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'transceiver'), 'media'), 'override')):
            pass
            yield '   transceiver media override '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_ethernet_interface, 'transceiver'), 'media'), 'override'))
            yield '\n'
        for l_2_link_tracking_group in t_3(environment.getattr(l_1_ethernet_interface, 'link_tracking_groups')):
            _loop_vars = {}
            pass
            if (t_8(environment.getattr(l_2_link_tracking_group, 'name')) and t_8(environment.getattr(l_2_link_tracking_group, 'direction'))):
                pass
                yield '   link tracking group '
                yield str(environment.getattr(l_2_link_tracking_group, 'name'))
                yield ' '
                yield str(environment.getattr(l_2_link_tracking_group, 'direction'))
                yield '\n'
        l_2_link_tracking_group = missing
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'traffic_policy'), 'input')):
            pass
            yield '   traffic-policy input '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'traffic_policy'), 'input'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_ethernet_interface, 'traffic_policy'), 'output')):
            pass
            yield '   traffic-policy output '
            yield str(environment.getattr(environment.getattr(l_1_ethernet_interface, 'traffic_policy'), 'output'))
            yield '\n'
        for l_2_tx_queue in t_3(environment.getattr(l_1_ethernet_interface, 'tx_queues'), 'id'):
            _loop_vars = {}
            pass
            template = environment.get_template('eos/ethernet-interface-tx-queues.j2', 'eos/ethernet-interfaces.j2')
            for event in template.root_render_func(template.new_context(context.get_all(), True, {'tx_queue': l_2_tx_queue, 'address_locking_cli': l_1_address_locking_cli, 'auth_cli': l_1_auth_cli, 'auth_failure_fallback_mba': l_1_auth_failure_fallback_mba, 'dfe_algo_cli': l_1_dfe_algo_cli, 'dfe_hold_time_cli': l_1_dfe_hold_time_cli, 'encapsulation_cli': l_1_encapsulation_cli, 'ethernet_interface': l_1_ethernet_interface, 'host_mode_cli': l_1_host_mode_cli, 'interface_ip_nat': l_1_interface_ip_nat, 'poe_limit_cli': l_1_poe_limit_cli, 'poe_link_down_action_cli': l_1_poe_link_down_action_cli, 'POE_CLASS_MAP': l_0_POE_CLASS_MAP})):
                yield event
        l_2_tx_queue = missing
        for l_2_uc_tx_queue in t_3(environment.getattr(l_1_ethernet_interface, 'uc_tx_queues'), 'id'):
            _loop_vars = {}
            pass
            template = environment.get_template('eos/ethernet-interface-uc-tx-queues.j2', 'eos/ethernet-interfaces.j2')
            for event in template.root_render_func(template.new_context(context.get_all(), True, {'uc_tx_queue': l_2_uc_tx_queue, 'address_locking_cli': l_1_address_locking_cli, 'auth_cli': l_1_auth_cli, 'auth_failure_fallback_mba': l_1_auth_failure_fallback_mba, 'dfe_algo_cli': l_1_dfe_algo_cli, 'dfe_hold_time_cli': l_1_dfe_hold_time_cli, 'encapsulation_cli': l_1_encapsulation_cli, 'ethernet_interface': l_1_ethernet_interface, 'host_mode_cli': l_1_host_mode_cli, 'interface_ip_nat': l_1_interface_ip_nat, 'poe_limit_cli': l_1_poe_limit_cli, 'poe_link_down_action_cli': l_1_poe_link_down_action_cli, 'POE_CLASS_MAP': l_0_POE_CLASS_MAP})):
                yield event
        l_2_uc_tx_queue = missing
        if t_8(environment.getattr(l_1_ethernet_interface, 'vrrp_ids')):
            pass
            def t_9(fiter):
                for l_2_vrid in fiter:
                    if t_8(environment.getattr(l_2_vrid, 'id')):
                        yield l_2_vrid
            for l_2_vrid in t_9(t_3(environment.getattr(l_1_ethernet_interface, 'vrrp_ids'), 'id')):
                l_2_delay_cli = resolve('delay_cli')
                _loop_vars = {}
                pass
                if t_8(environment.getattr(l_2_vrid, 'priority_level')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' priority-level '
                    yield str(environment.getattr(l_2_vrid, 'priority_level'))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(l_2_vrid, 'advertisement'), 'interval')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' advertisement interval '
                    yield str(environment.getattr(environment.getattr(l_2_vrid, 'advertisement'), 'interval'))
                    yield '\n'
                if (t_8(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'enabled'), True) and (t_8(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'minimum')) or t_8(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'reload')))):
                    pass
                    l_2_delay_cli = str_join(('vrrp ', environment.getattr(l_2_vrid, 'id'), ' preempt delay', ))
                    _loop_vars['delay_cli'] = l_2_delay_cli
                    if t_8(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'minimum')):
                        pass
                        l_2_delay_cli = str_join(((undefined(name='delay_cli') if l_2_delay_cli is missing else l_2_delay_cli), ' minimum ', environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'minimum'), ))
                        _loop_vars['delay_cli'] = l_2_delay_cli
                    if t_8(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'reload')):
                        pass
                        l_2_delay_cli = str_join(((undefined(name='delay_cli') if l_2_delay_cli is missing else l_2_delay_cli), ' reload ', environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'reload'), ))
                        _loop_vars['delay_cli'] = l_2_delay_cli
                    yield '   '
                    yield str((undefined(name='delay_cli') if l_2_delay_cli is missing else l_2_delay_cli))
                    yield '\n'
                elif t_8(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'enabled'), False):
                    pass
                    yield '   no vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' preempt\n'
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'timers'), 'delay'), 'reload')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' timers delay reload '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'timers'), 'delay'), 'reload'))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(l_2_vrid, 'ipv4'), 'address')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' ipv4 '
                    yield str(environment.getattr(environment.getattr(l_2_vrid, 'ipv4'), 'address'))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(l_2_vrid, 'ipv4'), 'version')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' ipv4 version '
                    yield str(environment.getattr(environment.getattr(l_2_vrid, 'ipv4'), 'version'))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(l_2_vrid, 'ipv6'), 'address')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' ipv6 '
                    yield str(environment.getattr(environment.getattr(l_2_vrid, 'ipv6'), 'address'))
                    yield '\n'
                for l_3_tracked_obj in t_3(environment.getattr(l_2_vrid, 'tracked_object'), 'name'):
                    l_3_tracked_obj_cli = resolve('tracked_obj_cli')
                    _loop_vars = {}
                    pass
                    if t_8(environment.getattr(l_3_tracked_obj, 'name')):
                        pass
                        l_3_tracked_obj_cli = str_join(('vrrp ', environment.getattr(l_2_vrid, 'id'), ' tracked-object ', environment.getattr(l_3_tracked_obj, 'name'), ))
                        _loop_vars['tracked_obj_cli'] = l_3_tracked_obj_cli
                        if t_8(environment.getattr(l_3_tracked_obj, 'decrement')):
                            pass
                            l_3_tracked_obj_cli = str_join(((undefined(name='tracked_obj_cli') if l_3_tracked_obj_cli is missing else l_3_tracked_obj_cli), ' decrement ', environment.getattr(l_3_tracked_obj, 'decrement'), ))
                            _loop_vars['tracked_obj_cli'] = l_3_tracked_obj_cli
                        elif t_8(environment.getattr(l_3_tracked_obj, 'shutdown'), True):
                            pass
                            l_3_tracked_obj_cli = str_join(((undefined(name='tracked_obj_cli') if l_3_tracked_obj_cli is missing else l_3_tracked_obj_cli), ' shutdown', ))
                            _loop_vars['tracked_obj_cli'] = l_3_tracked_obj_cli
                        yield '   '
                        yield str((undefined(name='tracked_obj_cli') if l_3_tracked_obj_cli is missing else l_3_tracked_obj_cli))
                        yield '\n'
                l_3_tracked_obj = l_3_tracked_obj_cli = missing
            l_2_vrid = l_2_delay_cli = missing
        if t_8(environment.getattr(l_1_ethernet_interface, 'eos_cli')):
            pass
            yield '   '
            yield str(t_6(environment.getattr(l_1_ethernet_interface, 'eos_cli'), 3, False))
            yield '\n'
    l_1_ethernet_interface = l_1_encapsulation_cli = l_1_dfe_algo_cli = l_1_dfe_hold_time_cli = l_1_host_mode_cli = l_1_auth_cli = l_1_auth_failure_fallback_mba = l_1_address_locking_cli = l_1_interface_ip_nat = l_1_hide_passwords = l_1_poe_link_down_action_cli = l_1_poe_limit_cli = missing

blocks = {}
debug_info = '7=61&8=64&10=79&11=81&12=84&14=86&15=89&17=91&19=94&22=97&23=100&25=102&26=105&28=107&29=109&31=112&34=115&36=118&39=121&41=124&44=127&46=130&50=133&51=136&53=138&54=141&56=143&57=146&59=148&60=151&62=153&63=156&65=158&66=161&68=163&71=168&73=171&76=174&78=177&82=180&83=182&84=185&87=187&88=189&90=192&91=195&94=197&95=200&97=202&98=205&100=207&101=211&102=213&103=215&104=217&106=219&107=221&108=224&111=227&112=229&113=232&116=234&117=237&119=239&120=243&122=246&124=249&125=251&127=254&129=256&130=259&131=261&132=263&133=265&134=267&135=269&136=271&138=273&139=275&140=277&141=279&142=281&143=283&145=285&146=287&148=289&150=292&152=294&155=297&157=300&160=303&161=306&163=308&164=311&166=313&167=316&169=318&170=321&172=323&173=326&175=328&177=331&178=334&180=336&181=339&183=341&184=343&186=346&187=348&188=350&189=352&191=355&193=357&194=359&195=361&196=363&198=366&200=368&202=371&206=374&207=377&209=379&210=382&212=384&213=387&216=389&217=391&218=394&220=396&221=398&223=401&224=403&228=406&231=409&232=412&234=414&236=417&239=420&240=422&242=425&243=427&244=429&245=431&247=434&250=436&251=438&253=441&257=446&258=448&259=450&261=453&264=455&265=457&266=460&268=462&271=465&272=468&274=470&275=473&277=475&278=478&281=480&282=483&284=485&287=488&290=491&291=493&293=496&294=498&295=500&296=502&298=505&302=507&304=510&307=513&308=515&309=517&310=519&312=521&313=523&315=526&317=528&318=531&320=533&323=536&324=539&325=541&326=543&327=547&330=550&331=554&332=556&333=558&335=560&336=562&338=565&341=568&344=571&345=574&347=576&350=579&352=585&354=588&357=591&360=594&363=597&366=600&367=603&369=605&370=608&372=610&375=613&378=616&379=618&380=622&381=624&382=626&383=628&384=630&387=632&388=634&390=637&393=640&394=644&395=646&396=648&398=650&399=652&400=654&401=656&403=658&404=660&406=663&408=666&409=669&410=673&411=676&413=678&414=681&416=683&417=686&420=688&423=691&426=694&427=697&429=699&432=702&434=705&437=708&438=711&440=713&441=716&443=718&444=721&446=723&447=726&449=728&450=731&452=733&453=736&455=738&456=740&457=742&458=746&459=748&460=750&462=753&465=756&466=758&467=762&470=765&473=768&477=771&479=774&482=777&483=779&484=781&485=784&486=787&489=789&490=792&492=794&495=797&497=800&500=803&501=806&503=808&504=811&506=813&507=816&508=819&511=826&514=829&515=832&517=834&518=837&520=839&521=842&523=844&524=846&525=848&526=850&528=853&530=855&531=858&533=860&536=863&537=865&538=867&539=869&540=871&542=873&543=875&545=878&547=880&550=883&553=886&554=888&557=894&560=896&561=899&563=901&564=904&566=906&567=909&569=911&571=914&574=917&575=920&576=922&577=925&578=927&579=930&583=933&584=936&585=938&586=941&588=948&592=953&595=956&596=959&598=961&599=964&601=966&602=969&604=971&605=974&607=976&608=979&610=981&611=984&613=986&614=989&616=991&617=994&619=996&620=999&622=1001&623=1004&625=1006&626=1009&628=1011&629=1014&631=1016&632=1019&634=1021&635=1024&637=1026&640=1029&642=1032&645=1035&648=1038&650=1041&652=1043&653=1046&655=1048&657=1051&660=1054&662=1057&665=1060&667=1063&670=1066&671=1068&674=1074&677=1076&678=1078&680=1081&683=1084&685=1087&688=1090&690=1093&694=1096&697=1099&698=1102&700=1104&701=1107&702=1110&705=1115&706=1118&708=1120&709=1123&711=1125&712=1128&714=1132&715=1135&717=1139&718=1141&719=1149&720=1152&722=1156&723=1159&725=1163&728=1165&729=1167&730=1169&732=1171&733=1173&735=1176&736=1178&737=1181&739=1183&740=1186&742=1190&743=1193&745=1197&746=1200&748=1204&749=1207&751=1211&752=1215&753=1217&754=1219&755=1221&756=1223&757=1225&759=1228&764=1232&765=1235'