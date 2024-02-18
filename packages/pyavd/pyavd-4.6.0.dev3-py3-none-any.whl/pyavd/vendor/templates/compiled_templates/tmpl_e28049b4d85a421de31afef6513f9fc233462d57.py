from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/router-bgp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_router_bgp = resolve('router_bgp')
    l_0_distance_cli = resolve('distance_cli')
    l_0_rr_preserve_attributes_cli = resolve('rr_preserve_attributes_cli')
    l_0_paths_cli = resolve('paths_cli')
    l_0_bgp_vlans = resolve('bgp_vlans')
    l_0_hostflap_detection_cli = resolve('hostflap_detection_cli')
    l_0_evpn_neighbor_default_encap_cli = resolve('evpn_neighbor_default_encap_cli')
    l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli = resolve('evpn_neighbor_default_nhs_received_evpn_routes_cli')
    l_0_path_selection_roles = resolve('path_selection_roles')
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
        t_4 = environment.filters['indent']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'indent' found.")
    try:
        t_5 = environment.filters['sort']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'sort' found.")
    try:
        t_6 = environment.filters['string']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'string' found.")
    try:
        t_7 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    try:
        t_8 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_8(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    try:
        t_9 = environment.tests['number']
    except KeyError:
        @internalcode
        def t_9(*unused):
            raise TemplateRuntimeError("No test named 'number' found.")
    pass
    if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'as')):
        pass
        yield '!\nrouter bgp '
        yield str(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'as'))
        yield '\n'
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'router_id')):
            pass
            yield '   router-id '
            yield str(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'router_id'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'external_routes')):
            pass
            l_0_distance_cli = str_join(('distance bgp ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'external_routes'), ))
            context.vars['distance_cli'] = l_0_distance_cli
            context.exported_vars.add('distance_cli')
            if (t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'internal_routes')) and t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'local_routes'))):
                pass
                l_0_distance_cli = str_join(((undefined(name='distance_cli') if l_0_distance_cli is missing else l_0_distance_cli), ' ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'internal_routes'), ' ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'local_routes'), ))
                context.vars['distance_cli'] = l_0_distance_cli
                context.exported_vars.add('distance_cli')
            yield '   '
            yield str((undefined(name='distance_cli') if l_0_distance_cli is missing else l_0_distance_cli))
            yield '\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart'), 'enabled'), True):
            pass
            if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart'), 'restart_time')):
                pass
                yield '   graceful-restart restart-time '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart'), 'restart_time'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart'), 'stalepath_time')):
                pass
                yield '   graceful-restart stalepath-time '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart'), 'stalepath_time'))
                yield '\n'
            yield '   graceful-restart\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart_helper'), 'enabled'), False):
            pass
            yield '   no graceful-restart-helper\n'
        elif t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart_helper'), 'enabled'), True):
            pass
            if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart_helper'), 'restart_time')):
                pass
                yield '   graceful-restart-helper restart-time '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart_helper'), 'restart_time'))
                yield '\n'
            elif t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart_helper'), 'long_lived'), True):
                pass
                yield '   graceful-restart-helper long-lived\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'route_reflector_preserve_attributes'), 'enabled'), True):
            pass
            l_0_rr_preserve_attributes_cli = 'bgp route-reflector preserve-attributes'
            context.vars['rr_preserve_attributes_cli'] = l_0_rr_preserve_attributes_cli
            context.exported_vars.add('rr_preserve_attributes_cli')
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'route_reflector_preserve_attributes'), 'always'), True):
                pass
                l_0_rr_preserve_attributes_cli = str_join(((undefined(name='rr_preserve_attributes_cli') if l_0_rr_preserve_attributes_cli is missing else l_0_rr_preserve_attributes_cli), ' always', ))
                context.vars['rr_preserve_attributes_cli'] = l_0_rr_preserve_attributes_cli
                context.exported_vars.add('rr_preserve_attributes_cli')
            yield '   '
            yield str((undefined(name='rr_preserve_attributes_cli') if l_0_rr_preserve_attributes_cli is missing else l_0_rr_preserve_attributes_cli))
            yield '\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'maximum_paths'), 'paths')):
            pass
            l_0_paths_cli = str_join(('maximum-paths ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'maximum_paths'), 'paths'), ))
            context.vars['paths_cli'] = l_0_paths_cli
            context.exported_vars.add('paths_cli')
            if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'maximum_paths'), 'ecmp')):
                pass
                l_0_paths_cli = str_join(((undefined(name='paths_cli') if l_0_paths_cli is missing else l_0_paths_cli), ' ecmp ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'maximum_paths'), 'ecmp'), ))
                context.vars['paths_cli'] = l_0_paths_cli
                context.exported_vars.add('paths_cli')
            yield '   '
            yield str((undefined(name='paths_cli') if l_0_paths_cli is missing else l_0_paths_cli))
            yield '\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'updates'), 'wait_for_convergence'), True):
            pass
            yield '   update wait-for-convergence\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'updates'), 'wait_install'), True):
            pass
            yield '   update wait-install\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'default'), 'ipv4_unicast'), True):
            pass
            yield '   bgp default ipv4-unicast\n'
        elif t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'default'), 'ipv4_unicast'), False):
            pass
            yield '   no bgp default ipv4-unicast\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'default'), 'ipv4_unicast_transport_ipv6'), True):
            pass
            yield '   bgp default ipv4-unicast transport ipv6\n'
        elif t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'default'), 'ipv4_unicast_transport_ipv6'), False):
            pass
            yield '   no bgp default ipv4-unicast transport ipv6\n'
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp_cluster_id')):
            pass
            yield '   bgp cluster-id '
            yield str(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp_cluster_id'))
            yield '\n'
        for l_1_bgp_default in t_1(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp_defaults'), []):
            _loop_vars = {}
            pass
            yield '   '
            yield str(l_1_bgp_default)
            yield '\n'
        l_1_bgp_default = missing
        if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'bestpath'), 'd_path'), True):
            pass
            yield '   bgp bestpath d-path\n'
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'listen_ranges')):
            pass
            def t_10(fiter):
                for l_1_listen_range in fiter:
                    if ((t_7(environment.getattr(l_1_listen_range, 'peer_group')) and t_7(environment.getattr(l_1_listen_range, 'prefix'))) and (t_7(environment.getattr(l_1_listen_range, 'peer_filter')) or t_7(environment.getattr(l_1_listen_range, 'remote_as')))):
                        yield l_1_listen_range
            for l_1_listen_range in t_10(t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'listen_ranges'), 'peer_group')):
                l_1_listen_range_cli = missing
                _loop_vars = {}
                pass
                l_1_listen_range_cli = str_join(('bgp listen range ', environment.getattr(l_1_listen_range, 'prefix'), ))
                _loop_vars['listen_range_cli'] = l_1_listen_range_cli
                if t_7(environment.getattr(l_1_listen_range, 'peer_id_include_router_id'), True):
                    pass
                    l_1_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_1_listen_range_cli is missing else l_1_listen_range_cli), ' peer-id include router-id', ))
                    _loop_vars['listen_range_cli'] = l_1_listen_range_cli
                l_1_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_1_listen_range_cli is missing else l_1_listen_range_cli), ' peer-group ', environment.getattr(l_1_listen_range, 'peer_group'), ))
                _loop_vars['listen_range_cli'] = l_1_listen_range_cli
                if t_7(environment.getattr(l_1_listen_range, 'peer_filter')):
                    pass
                    l_1_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_1_listen_range_cli is missing else l_1_listen_range_cli), ' peer-filter ', environment.getattr(l_1_listen_range, 'peer_filter'), ))
                    _loop_vars['listen_range_cli'] = l_1_listen_range_cli
                elif t_7(environment.getattr(l_1_listen_range, 'remote_as')):
                    pass
                    l_1_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_1_listen_range_cli is missing else l_1_listen_range_cli), ' remote-as ', environment.getattr(l_1_listen_range, 'remote_as'), ))
                    _loop_vars['listen_range_cli'] = l_1_listen_range_cli
                yield '   '
                yield str((undefined(name='listen_range_cli') if l_1_listen_range_cli is missing else l_1_listen_range_cli))
                yield '\n'
            l_1_listen_range = l_1_listen_range_cli = missing
        for l_1_peer_group in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'peer_groups'), 'name'):
            _loop_vars = {}
            pass
            if (t_7(environment.getattr(l_1_peer_group, 'bgp_listen_range_prefix')) and t_7(environment.getattr(l_1_peer_group, 'peer_filter'))):
                pass
                yield '   bgp listen range '
                yield str(environment.getattr(l_1_peer_group, 'bgp_listen_range_prefix'))
                yield ' peer-group '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' peer-filter '
                yield str(environment.getattr(l_1_peer_group, 'peer_filter'))
                yield '\n'
        l_1_peer_group = missing
        for l_1_peer_group in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'peer_groups'), 'name'):
            l_1_remove_private_as_cli = resolve('remove_private_as_cli')
            l_1_remove_private_as_ingress_cli = resolve('remove_private_as_ingress_cli')
            l_1_allowas_in_cli = resolve('allowas_in_cli')
            l_1_neighbor_rib_in_pre_policy_retain_cli = resolve('neighbor_rib_in_pre_policy_retain_cli')
            l_1_hide_passwords = resolve('hide_passwords')
            l_1_default_originate_cli = resolve('default_originate_cli')
            l_1_maximum_routes_cli = resolve('maximum_routes_cli')
            l_1_link_bandwidth_cli = resolve('link_bandwidth_cli')
            _loop_vars = {}
            pass
            if t_7(environment.getattr(l_1_peer_group, 'shutdown'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' shutdown\n'
            yield '   neighbor '
            yield str(environment.getattr(l_1_peer_group, 'name'))
            yield ' peer group\n'
            if t_7(environment.getattr(l_1_peer_group, 'remote_as')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' remote-as '
                yield str(environment.getattr(l_1_peer_group, 'remote_as'))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'local_as')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' local-as '
                yield str(environment.getattr(l_1_peer_group, 'local_as'))
                yield ' no-prepend replace-as\n'
            if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'as_path'), 'remote_as_replace_out'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' as-path remote-as replace out\n'
            if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'as_path'), 'prepend_own_disabled'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' as-path prepend-own disabled\n'
            if t_7(environment.getattr(l_1_peer_group, 'next_hop_self'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' next-hop-self\n'
            if t_7(environment.getattr(l_1_peer_group, 'next_hop_unchanged'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' next-hop-unchanged\n'
            if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as'), 'enabled'), True):
                pass
                l_1_remove_private_as_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' remove-private-as', ))
                _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as'), 'all'), True):
                    pass
                    l_1_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli), ' all', ))
                    _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                    if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as'), 'replace_as'), True):
                        pass
                        l_1_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli), ' replace-as', ))
                        _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                yield '   '
                yield str((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli))
                yield '\n'
            elif t_7(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as'), 'enabled'), False):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' remove-private-as\n'
            if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as_ingress'), 'enabled'), True):
                pass
                l_1_remove_private_as_ingress_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' remove-private-as ingress', ))
                _loop_vars['remove_private_as_ingress_cli'] = l_1_remove_private_as_ingress_cli
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as_ingress'), 'replace_as'), True):
                    pass
                    l_1_remove_private_as_ingress_cli = str_join(((undefined(name='remove_private_as_ingress_cli') if l_1_remove_private_as_ingress_cli is missing else l_1_remove_private_as_ingress_cli), ' replace-as', ))
                    _loop_vars['remove_private_as_ingress_cli'] = l_1_remove_private_as_ingress_cli
                yield '   '
                yield str((undefined(name='remove_private_as_ingress_cli') if l_1_remove_private_as_ingress_cli is missing else l_1_remove_private_as_ingress_cli))
                yield '\n'
            elif t_7(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as_ingress'), 'enabled'), False):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' remove-private-as ingress\n'
            if t_7(environment.getattr(l_1_peer_group, 'update_source')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' update-source '
                yield str(environment.getattr(l_1_peer_group, 'update_source'))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'description')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' description '
                yield str(environment.getattr(l_1_peer_group, 'description'))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'route_reflector_client'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' route-reflector-client\n'
            if t_7(environment.getattr(l_1_peer_group, 'bfd'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' bfd\n'
                if ((t_7(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'interval')) and t_7(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'min_rx'))) and t_7(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'multiplier'))):
                    pass
                    yield '   neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' bfd interval '
                    yield str(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'interval'))
                    yield ' min-rx '
                    yield str(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'min_rx'))
                    yield ' multiplier '
                    yield str(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'multiplier'))
                    yield '\n'
            if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'allowas_in'), 'enabled'), True):
                pass
                l_1_allowas_in_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' allowas-in', ))
                _loop_vars['allowas_in_cli'] = l_1_allowas_in_cli
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'allowas_in'), 'times')):
                    pass
                    l_1_allowas_in_cli = str_join(((undefined(name='allowas_in_cli') if l_1_allowas_in_cli is missing else l_1_allowas_in_cli), ' ', environment.getattr(environment.getattr(l_1_peer_group, 'allowas_in'), 'times'), ))
                    _loop_vars['allowas_in_cli'] = l_1_allowas_in_cli
                yield '   '
                yield str((undefined(name='allowas_in_cli') if l_1_allowas_in_cli is missing else l_1_allowas_in_cli))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'rib_in_pre_policy_retain'), 'enabled'), True):
                pass
                l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' rib-in pre-policy retain', ))
                _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'rib_in_pre_policy_retain'), 'all'), True):
                    pass
                    l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli), ' all', ))
                    _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                yield '   '
                yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli))
                yield '\n'
            elif t_7(environment.getattr(environment.getattr(l_1_peer_group, 'rib_in_pre_policy_retain'), 'enabled'), False):
                pass
                l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(('no neighbor ', environment.getattr(l_1_peer_group, 'name'), ' rib-in pre-policy retain', ))
                _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                yield '   '
                yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'ebgp_multihop')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' ebgp-multihop '
                yield str(environment.getattr(l_1_peer_group, 'ebgp_multihop'))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'ttl_maximum_hops')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' ttl maximum-hops '
                yield str(environment.getattr(l_1_peer_group, 'ttl_maximum_hops'))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'password')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' password 7 '
                yield str(t_2(environment.getattr(l_1_peer_group, 'password'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'enabled'), True):
                pass
                l_1_default_originate_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' default-originate', ))
                _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'route_map')):
                    pass
                    l_1_default_originate_cli = str_join(((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli), ' route-map ', environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'route_map'), ))
                    _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'always'), True):
                    pass
                    l_1_default_originate_cli = str_join(((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli), ' always', ))
                    _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                yield '   '
                yield str((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'passive'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' passive\n'
            if t_7(environment.getattr(l_1_peer_group, 'session_tracker')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' session tracker '
                yield str(environment.getattr(l_1_peer_group, 'session_tracker'))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'send_community'), 'all'):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' send-community\n'
            elif t_7(environment.getattr(l_1_peer_group, 'send_community')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' send-community '
                yield str(environment.getattr(l_1_peer_group, 'send_community'))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'maximum_routes')):
                pass
                l_1_maximum_routes_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' maximum-routes ', environment.getattr(l_1_peer_group, 'maximum_routes'), ))
                _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                if t_7(environment.getattr(l_1_peer_group, 'maximum_routes_warning_limit')):
                    pass
                    l_1_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli), ' warning-limit ', environment.getattr(l_1_peer_group, 'maximum_routes_warning_limit'), ))
                    _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                if t_7(environment.getattr(l_1_peer_group, 'maximum_routes_warning_only'), True):
                    pass
                    l_1_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli), ' warning-only', ))
                    _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                yield '   '
                yield str((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'link_bandwidth'), 'enabled'), True):
                pass
                l_1_link_bandwidth_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' link-bandwidth', ))
                _loop_vars['link_bandwidth_cli'] = l_1_link_bandwidth_cli
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'link_bandwidth'), 'default')):
                    pass
                    l_1_link_bandwidth_cli = str_join(((undefined(name='link_bandwidth_cli') if l_1_link_bandwidth_cli is missing else l_1_link_bandwidth_cli), ' default ', environment.getattr(environment.getattr(l_1_peer_group, 'link_bandwidth'), 'default'), ))
                    _loop_vars['link_bandwidth_cli'] = l_1_link_bandwidth_cli
                yield '   '
                yield str((undefined(name='link_bandwidth_cli') if l_1_link_bandwidth_cli is missing else l_1_link_bandwidth_cli))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'weight')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' weight '
                yield str(environment.getattr(l_1_peer_group, 'weight'))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'timers')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' timers '
                yield str(environment.getattr(l_1_peer_group, 'timers'))
                yield '\n'
            if t_7(environment.getattr(l_1_peer_group, 'route_map_in')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' route-map '
                yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                yield ' in\n'
            if t_7(environment.getattr(l_1_peer_group, 'route_map_out')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' route-map '
                yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                yield ' out\n'
        l_1_peer_group = l_1_remove_private_as_cli = l_1_remove_private_as_ingress_cli = l_1_allowas_in_cli = l_1_neighbor_rib_in_pre_policy_retain_cli = l_1_hide_passwords = l_1_default_originate_cli = l_1_maximum_routes_cli = l_1_link_bandwidth_cli = missing
        for l_1_neighbor_interface in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'neighbor_interfaces'), 'name'):
            _loop_vars = {}
            pass
            if (t_7(environment.getattr(l_1_neighbor_interface, 'peer_group')) and t_7(environment.getattr(l_1_neighbor_interface, 'remote_as'))):
                pass
                yield '   neighbor interface '
                yield str(environment.getattr(l_1_neighbor_interface, 'name'))
                yield ' peer-group '
                yield str(environment.getattr(l_1_neighbor_interface, 'peer_group'))
                yield ' remote-as '
                yield str(environment.getattr(l_1_neighbor_interface, 'remote_as'))
                yield '\n'
            elif (t_7(environment.getattr(l_1_neighbor_interface, 'peer_group')) and t_7(environment.getattr(l_1_neighbor_interface, 'peer_filter'))):
                pass
                yield '   neighbor interface '
                yield str(environment.getattr(l_1_neighbor_interface, 'name'))
                yield ' peer-group '
                yield str(environment.getattr(l_1_neighbor_interface, 'peer_group'))
                yield ' peer-filter '
                yield str(environment.getattr(l_1_neighbor_interface, 'peer_filter'))
                yield '\n'
        l_1_neighbor_interface = missing
        for l_1_neighbor in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'neighbors'), 'ip_address'):
            l_1_remove_private_as_cli = resolve('remove_private_as_cli')
            l_1_remove_private_as_ingress_cli = resolve('remove_private_as_ingress_cli')
            l_1_allowas_in_cli = resolve('allowas_in_cli')
            l_1_neighbor_rib_in_pre_policy_retain_cli = resolve('neighbor_rib_in_pre_policy_retain_cli')
            l_1_hide_passwords = resolve('hide_passwords')
            l_1_default_originate_cli = resolve('default_originate_cli')
            l_1_maximum_routes_cli = resolve('maximum_routes_cli')
            l_1_link_bandwidth_cli = resolve('link_bandwidth_cli')
            _loop_vars = {}
            pass
            if t_7(environment.getattr(l_1_neighbor, 'peer_group')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' peer group '
                yield str(environment.getattr(l_1_neighbor, 'peer_group'))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'remote_as')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' remote-as '
                yield str(environment.getattr(l_1_neighbor, 'remote_as'))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'next_hop_self'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' next-hop-self\n'
            if t_7(environment.getattr(l_1_neighbor, 'shutdown'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' shutdown\n'
            if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as'), 'enabled'), True):
                pass
                l_1_remove_private_as_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' remove-private-as', ))
                _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as'), 'all'), True):
                    pass
                    l_1_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli), ' all', ))
                    _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                    if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as'), 'replace_as'), True):
                        pass
                        l_1_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli), ' replace-as', ))
                        _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                yield '   '
                yield str((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli))
                yield '\n'
            elif t_7(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as'), 'enabled'), False):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' remove-private-as\n'
            if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as_ingress'), 'enabled'), True):
                pass
                l_1_remove_private_as_ingress_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' remove-private-as ingress', ))
                _loop_vars['remove_private_as_ingress_cli'] = l_1_remove_private_as_ingress_cli
                if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as_ingress'), 'replace_as'), True):
                    pass
                    l_1_remove_private_as_ingress_cli = str_join(((undefined(name='remove_private_as_ingress_cli') if l_1_remove_private_as_ingress_cli is missing else l_1_remove_private_as_ingress_cli), ' replace-as', ))
                    _loop_vars['remove_private_as_ingress_cli'] = l_1_remove_private_as_ingress_cli
                yield '   '
                yield str((undefined(name='remove_private_as_ingress_cli') if l_1_remove_private_as_ingress_cli is missing else l_1_remove_private_as_ingress_cli))
                yield '\n'
            elif t_7(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as_ingress'), 'enabled'), False):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' remove-private-as ingress\n'
            if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'as_path'), 'remote_as_replace_out'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' as-path remote-as replace out\n'
            if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'as_path'), 'prepend_own_disabled'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' as-path prepend-own disabled\n'
            if t_7(environment.getattr(l_1_neighbor, 'local_as')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' local-as '
                yield str(environment.getattr(l_1_neighbor, 'local_as'))
                yield ' no-prepend replace-as\n'
            if t_7(environment.getattr(l_1_neighbor, 'description')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' description '
                yield str(environment.getattr(l_1_neighbor, 'description'))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'route_reflector_client'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' route-reflector-client\n'
            elif t_7(environment.getattr(l_1_neighbor, 'route_reflector_client'), False):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' route-reflector-client\n'
            if t_7(environment.getattr(l_1_neighbor, 'ebgp_multihop')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' ebgp-multihop '
                yield str(environment.getattr(l_1_neighbor, 'ebgp_multihop'))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'ttl_maximum_hops')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' ttl maximum-hops '
                yield str(environment.getattr(l_1_neighbor, 'ttl_maximum_hops'))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'update_source')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' update-source '
                yield str(environment.getattr(l_1_neighbor, 'update_source'))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'bfd'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' bfd\n'
                if ((t_7(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'interval')) and t_7(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'min_rx'))) and t_7(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'multiplier'))):
                    pass
                    yield '   neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' bfd interval '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'interval'))
                    yield ' min-rx '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'min_rx'))
                    yield ' multiplier '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'multiplier'))
                    yield '\n'
            elif (t_7(environment.getattr(l_1_neighbor, 'bfd'), False) and t_7(environment.getattr(l_1_neighbor, 'peer_group'))):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' bfd\n'
            if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'allowas_in'), 'enabled'), True):
                pass
                l_1_allowas_in_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' allowas-in', ))
                _loop_vars['allowas_in_cli'] = l_1_allowas_in_cli
                if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'allowas_in'), 'times')):
                    pass
                    l_1_allowas_in_cli = str_join(((undefined(name='allowas_in_cli') if l_1_allowas_in_cli is missing else l_1_allowas_in_cli), ' ', environment.getattr(environment.getattr(l_1_neighbor, 'allowas_in'), 'times'), ))
                    _loop_vars['allowas_in_cli'] = l_1_allowas_in_cli
                yield '   '
                yield str((undefined(name='allowas_in_cli') if l_1_allowas_in_cli is missing else l_1_allowas_in_cli))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'rib_in_pre_policy_retain'), 'enabled'), True):
                pass
                l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' rib-in pre-policy retain', ))
                _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'rib_in_pre_policy_retain'), 'all'), True):
                    pass
                    l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli), ' all', ))
                    _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                yield '   '
                yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli))
                yield '\n'
            elif t_7(environment.getattr(environment.getattr(l_1_neighbor, 'rib_in_pre_policy_retain'), 'enabled'), False):
                pass
                l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(('no neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' rib-in pre-policy retain', ))
                _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                yield '   '
                yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'password')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' password 7 '
                yield str(t_2(environment.getattr(l_1_neighbor, 'password'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'passive'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' passive\n'
            if t_7(environment.getattr(l_1_neighbor, 'weight')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' weight '
                yield str(environment.getattr(l_1_neighbor, 'weight'))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'session_tracker')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' session tracker '
                yield str(environment.getattr(l_1_neighbor, 'session_tracker'))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'timers')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' timers '
                yield str(environment.getattr(l_1_neighbor, 'timers'))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'route_map_in')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' route-map '
                yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                yield ' in\n'
            if t_7(environment.getattr(l_1_neighbor, 'route_map_out')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' route-map '
                yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                yield ' out\n'
            if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'enabled'), True):
                pass
                l_1_default_originate_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' default-originate', ))
                _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'route_map')):
                    pass
                    l_1_default_originate_cli = str_join(((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli), ' route-map ', environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'route_map'), ))
                    _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'always'), True):
                    pass
                    l_1_default_originate_cli = str_join(((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli), ' always', ))
                    _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                yield '   '
                yield str((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'send_community'), 'all'):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' send-community\n'
            elif t_7(environment.getattr(l_1_neighbor, 'send_community')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' send-community '
                yield str(environment.getattr(l_1_neighbor, 'send_community'))
                yield '\n'
            if t_7(environment.getattr(l_1_neighbor, 'maximum_routes')):
                pass
                l_1_maximum_routes_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' maximum-routes ', environment.getattr(l_1_neighbor, 'maximum_routes'), ))
                _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                if t_7(environment.getattr(l_1_neighbor, 'maximum_routes_warning_limit')):
                    pass
                    l_1_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli), ' warning-limit ', environment.getattr(l_1_neighbor, 'maximum_routes_warning_limit'), ))
                    _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                if t_7(environment.getattr(l_1_neighbor, 'maximum_routes_warning_only'), True):
                    pass
                    l_1_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli), ' warning-only', ))
                    _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                yield '   '
                yield str((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'link_bandwidth'), 'enabled'), True):
                pass
                l_1_link_bandwidth_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' link-bandwidth', ))
                _loop_vars['link_bandwidth_cli'] = l_1_link_bandwidth_cli
                if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'link_bandwidth'), 'default')):
                    pass
                    l_1_link_bandwidth_cli = str_join(((undefined(name='link_bandwidth_cli') if l_1_link_bandwidth_cli is missing else l_1_link_bandwidth_cli), ' default ', environment.getattr(environment.getattr(l_1_neighbor, 'link_bandwidth'), 'default'), ))
                    _loop_vars['link_bandwidth_cli'] = l_1_link_bandwidth_cli
                yield '   '
                yield str((undefined(name='link_bandwidth_cli') if l_1_link_bandwidth_cli is missing else l_1_link_bandwidth_cli))
                yield '\n'
        l_1_neighbor = l_1_remove_private_as_cli = l_1_remove_private_as_ingress_cli = l_1_allowas_in_cli = l_1_neighbor_rib_in_pre_policy_retain_cli = l_1_hide_passwords = l_1_default_originate_cli = l_1_maximum_routes_cli = l_1_link_bandwidth_cli = missing
        for l_1_aggregate_address in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'aggregate_addresses'), 'prefix'):
            l_1_aggregate_address_cli = missing
            _loop_vars = {}
            pass
            l_1_aggregate_address_cli = str_join(('aggregate-address ', environment.getattr(l_1_aggregate_address, 'prefix'), ))
            _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_7(environment.getattr(l_1_aggregate_address, 'as_set'), True):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' as-set', ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_7(environment.getattr(l_1_aggregate_address, 'advertise_map')):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' advertise-map ', environment.getattr(l_1_aggregate_address, 'advertise_map'), ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_7(environment.getattr(l_1_aggregate_address, 'supress_map')):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' supress-map ', environment.getattr(l_1_aggregate_address, 'supress_map'), ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_7(environment.getattr(l_1_aggregate_address, 'summary_only'), True):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' summary-only', ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_7(environment.getattr(l_1_aggregate_address, 'attribute_map')):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' attribute-map ', environment.getattr(l_1_aggregate_address, 'attribute_map'), ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_7(environment.getattr(l_1_aggregate_address, 'match_map')):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' match-map ', environment.getattr(l_1_aggregate_address, 'match_map'), ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_7(environment.getattr(l_1_aggregate_address, 'advertise_only'), True):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' advertise-only', ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            yield '   '
            yield str((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli))
            yield '\n'
        l_1_aggregate_address = l_1_aggregate_address_cli = missing
        for l_1_redistribute_route in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'redistribute_routes'), 'source_protocol'):
            l_1_redistribute_route_cli = resolve('redistribute_route_cli')
            _loop_vars = {}
            pass
            if t_7(environment.getattr(l_1_redistribute_route, 'source_protocol')):
                pass
                l_1_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_1_redistribute_route, 'source_protocol'), ))
                _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                if (environment.getattr(l_1_redistribute_route, 'source_protocol') == 'bgp'):
                    pass
                    l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' leaked', ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                elif t_7(environment.getattr(l_1_redistribute_route, 'include_leaked')):
                    pass
                    l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' include leaked', ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                if t_7(environment.getattr(l_1_redistribute_route, 'route_map')):
                    pass
                    l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' route-map ', environment.getattr(l_1_redistribute_route, 'route_map'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                yield '   '
                yield str((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli))
                yield '\n'
        l_1_redistribute_route = l_1_redistribute_route_cli = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vlans')):
            pass
            l_0_bgp_vlans = environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vlans')
            context.vars['bgp_vlans'] = l_0_bgp_vlans
            context.exported_vars.add('bgp_vlans')
            for l_1_bgp_vlan in (undefined(name='bgp_vlans') if l_0_bgp_vlans is missing else l_0_bgp_vlans):
                _loop_vars = {}
                pass
                context.call(environment.getattr(l_1_bgp_vlan, 'update'), {'id': t_6(environment.getitem(l_1_bgp_vlan, 'id'))}, _loop_vars=_loop_vars)
            l_1_bgp_vlan = missing
            for l_1_vlan in t_5(environment, (undefined(name='bgp_vlans') if l_0_bgp_vlans is missing else l_0_bgp_vlans), attribute='id'):
                _loop_vars = {}
                pass
                yield '   !\n   vlan '
                yield str(environment.getattr(l_1_vlan, 'id'))
                yield '\n'
                if t_7(environment.getattr(l_1_vlan, 'rd')):
                    pass
                    yield '      rd '
                    yield str(environment.getattr(l_1_vlan, 'rd'))
                    yield '\n'
                if (t_7(environment.getattr(environment.getattr(l_1_vlan, 'rd_evpn_domain'), 'domain')) and t_7(environment.getattr(environment.getattr(l_1_vlan, 'rd_evpn_domain'), 'rd'))):
                    pass
                    yield '      rd evpn domain '
                    yield str(environment.getattr(environment.getattr(l_1_vlan, 'rd_evpn_domain'), 'domain'))
                    yield ' '
                    yield str(environment.getattr(environment.getattr(l_1_vlan, 'rd_evpn_domain'), 'rd'))
                    yield '\n'
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'both')):
                    _loop_vars = {}
                    pass
                    yield '      route-target both '
                    yield str(l_2_route_target)
                    yield '\n'
                l_2_route_target = missing
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'import')):
                    _loop_vars = {}
                    pass
                    yield '      route-target import '
                    yield str(l_2_route_target)
                    yield '\n'
                l_2_route_target = missing
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'export')):
                    _loop_vars = {}
                    pass
                    yield '      route-target export '
                    yield str(l_2_route_target)
                    yield '\n'
                l_2_route_target = missing
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'import_evpn_domains')):
                    _loop_vars = {}
                    pass
                    yield '      route-target import evpn domain '
                    yield str(environment.getattr(l_2_route_target, 'domain'))
                    yield ' '
                    yield str(environment.getattr(l_2_route_target, 'route_target'))
                    yield '\n'
                l_2_route_target = missing
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'export_evpn_domains')):
                    _loop_vars = {}
                    pass
                    yield '      route-target export evpn domain '
                    yield str(environment.getattr(l_2_route_target, 'domain'))
                    yield ' '
                    yield str(environment.getattr(l_2_route_target, 'route_target'))
                    yield '\n'
                l_2_route_target = missing
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'import_export_evpn_domains')):
                    _loop_vars = {}
                    pass
                    yield '      route-target import export evpn domain '
                    yield str(environment.getattr(l_2_route_target, 'domain'))
                    yield ' '
                    yield str(environment.getattr(l_2_route_target, 'route_target'))
                    yield '\n'
                l_2_route_target = missing
                for l_2_redistribute_route in t_3(environment.getattr(l_1_vlan, 'redistribute_routes')):
                    _loop_vars = {}
                    pass
                    yield '      redistribute '
                    yield str(l_2_redistribute_route)
                    yield '\n'
                l_2_redistribute_route = missing
                for l_2_no_redistribute_route in t_3(environment.getattr(l_1_vlan, 'no_redistribute_routes')):
                    _loop_vars = {}
                    pass
                    yield '      no redistribute '
                    yield str(l_2_no_redistribute_route)
                    yield '\n'
                l_2_no_redistribute_route = missing
                if t_7(environment.getattr(l_1_vlan, 'eos_cli')):
                    pass
                    yield '      !\n      '
                    yield str(t_4(environment.getattr(l_1_vlan, 'eos_cli'), 6, False))
                    yield '\n'
            l_1_vlan = missing
        for l_1_vlan_aware_bundle in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vlan_aware_bundles'), 'name'):
            _loop_vars = {}
            pass
            yield '   !\n   vlan-aware-bundle '
            yield str(environment.getattr(l_1_vlan_aware_bundle, 'name'))
            yield '\n'
            if t_7(environment.getattr(l_1_vlan_aware_bundle, 'rd')):
                pass
                yield '      rd '
                yield str(environment.getattr(l_1_vlan_aware_bundle, 'rd'))
                yield '\n'
            if (t_7(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'rd_evpn_domain'), 'domain')) and t_7(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'rd_evpn_domain'), 'rd'))):
                pass
                yield '      rd evpn domain '
                yield str(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'rd_evpn_domain'), 'domain'))
                yield ' '
                yield str(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'rd_evpn_domain'), 'rd'))
                yield '\n'
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'both')):
                _loop_vars = {}
                pass
                yield '      route-target both '
                yield str(l_2_route_target)
                yield '\n'
            l_2_route_target = missing
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'import')):
                _loop_vars = {}
                pass
                yield '      route-target import '
                yield str(l_2_route_target)
                yield '\n'
            l_2_route_target = missing
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'export')):
                _loop_vars = {}
                pass
                yield '      route-target export '
                yield str(l_2_route_target)
                yield '\n'
            l_2_route_target = missing
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'import_evpn_domains')):
                _loop_vars = {}
                pass
                yield '      route-target import evpn domain '
                yield str(environment.getattr(l_2_route_target, 'domain'))
                yield ' '
                yield str(environment.getattr(l_2_route_target, 'route_target'))
                yield '\n'
            l_2_route_target = missing
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'export_evpn_domains')):
                _loop_vars = {}
                pass
                yield '      route-target export evpn domain '
                yield str(environment.getattr(l_2_route_target, 'domain'))
                yield ' '
                yield str(environment.getattr(l_2_route_target, 'route_target'))
                yield '\n'
            l_2_route_target = missing
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'import_export_evpn_domains')):
                _loop_vars = {}
                pass
                yield '      route-target import export evpn domain '
                yield str(environment.getattr(l_2_route_target, 'domain'))
                yield ' '
                yield str(environment.getattr(l_2_route_target, 'route_target'))
                yield '\n'
            l_2_route_target = missing
            for l_2_redistribute_route in t_3(environment.getattr(l_1_vlan_aware_bundle, 'redistribute_routes')):
                _loop_vars = {}
                pass
                yield '      redistribute '
                yield str(l_2_redistribute_route)
                yield '\n'
            l_2_redistribute_route = missing
            for l_2_no_redistribute_route in t_3(environment.getattr(l_1_vlan_aware_bundle, 'no_redistribute_routes')):
                _loop_vars = {}
                pass
                yield '      no redistribute '
                yield str(l_2_no_redistribute_route)
                yield '\n'
            l_2_no_redistribute_route = missing
            yield '      vlan '
            yield str(environment.getattr(l_1_vlan_aware_bundle, 'vlan'))
            yield '\n'
            if t_7(environment.getattr(l_1_vlan_aware_bundle, 'eos_cli')):
                pass
                yield '      !\n      '
                yield str(t_4(environment.getattr(l_1_vlan_aware_bundle, 'eos_cli'), 6, False))
                yield '\n'
        l_1_vlan_aware_bundle = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vpws')):
            pass
            for l_1_vpws_service in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vpws'), 'name'):
                _loop_vars = {}
                pass
                yield '   !\n'
                if t_7(environment.getattr(l_1_vpws_service, 'name')):
                    pass
                    yield '   vpws '
                    yield str(environment.getattr(l_1_vpws_service, 'name'))
                    yield '\n'
                    if t_7(environment.getattr(l_1_vpws_service, 'rd')):
                        pass
                        yield '      rd '
                        yield str(environment.getattr(l_1_vpws_service, 'rd'))
                        yield '\n'
                    if t_7(environment.getattr(environment.getattr(l_1_vpws_service, 'route_targets'), 'import_export')):
                        pass
                        yield '      route-target import export evpn '
                        yield str(environment.getattr(environment.getattr(l_1_vpws_service, 'route_targets'), 'import_export'))
                        yield '\n'
                    if t_7(environment.getattr(l_1_vpws_service, 'mpls_control_word'), True):
                        pass
                        yield '      mpls control-word\n'
                    if t_7(environment.getattr(l_1_vpws_service, 'label_flow'), True):
                        pass
                        yield '      label flow\n'
                    if t_7(environment.getattr(l_1_vpws_service, 'mtu')):
                        pass
                        yield '      mtu '
                        yield str(environment.getattr(l_1_vpws_service, 'mtu'))
                        yield '\n'
                    for l_2_pw in t_3(environment.getattr(l_1_vpws_service, 'pseudowires'), 'name'):
                        _loop_vars = {}
                        pass
                        if ((t_7(environment.getattr(l_2_pw, 'name')) and t_7(environment.getattr(l_2_pw, 'id_local'))) and t_7(environment.getattr(l_2_pw, 'id_remote'))):
                            pass
                            yield '      !\n      pseudowire '
                            yield str(environment.getattr(l_2_pw, 'name'))
                            yield '\n         evpn vpws id local '
                            yield str(environment.getattr(l_2_pw, 'id_local'))
                            yield ' remote '
                            yield str(environment.getattr(l_2_pw, 'id_remote'))
                            yield '\n'
                    l_2_pw = missing
            l_1_vpws_service = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn')):
            pass
            yield '   !\n   address-family evpn\n'
            if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'next_hop_unchanged'), True):
                pass
                yield '      bgp next-hop-unchanged\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'enabled'), False):
                pass
                yield '      no host-flap detection\n'
            elif t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'enabled'), True):
                pass
                l_0_hostflap_detection_cli = ''
                context.vars['hostflap_detection_cli'] = l_0_hostflap_detection_cli
                context.exported_vars.add('hostflap_detection_cli')
                if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'window')):
                    pass
                    l_0_hostflap_detection_cli = str_join(((undefined(name='hostflap_detection_cli') if l_0_hostflap_detection_cli is missing else l_0_hostflap_detection_cli), ' window ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'window'), ))
                    context.vars['hostflap_detection_cli'] = l_0_hostflap_detection_cli
                    context.exported_vars.add('hostflap_detection_cli')
                if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'threshold')):
                    pass
                    l_0_hostflap_detection_cli = str_join(((undefined(name='hostflap_detection_cli') if l_0_hostflap_detection_cli is missing else l_0_hostflap_detection_cli), ' threshold ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'threshold'), ))
                    context.vars['hostflap_detection_cli'] = l_0_hostflap_detection_cli
                    context.exported_vars.add('hostflap_detection_cli')
                if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'expiry_timeout')):
                    pass
                    l_0_hostflap_detection_cli = str_join(((undefined(name='hostflap_detection_cli') if l_0_hostflap_detection_cli is missing else l_0_hostflap_detection_cli), ' expiry timeout ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'expiry_timeout'), ' seconds', ))
                    context.vars['hostflap_detection_cli'] = l_0_hostflap_detection_cli
                    context.exported_vars.add('hostflap_detection_cli')
                if ((undefined(name='hostflap_detection_cli') if l_0_hostflap_detection_cli is missing else l_0_hostflap_detection_cli) != ''):
                    pass
                    yield '      host-flap detection'
                    yield str((undefined(name='hostflap_detection_cli') if l_0_hostflap_detection_cli is missing else l_0_hostflap_detection_cli))
                    yield '\n'
            if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'domain_identifier')):
                pass
                yield '      domain identifier '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'domain_identifier'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'encapsulation'), 'mpls'):
                pass
                l_0_evpn_neighbor_default_encap_cli = 'neighbor default encapsulation mpls'
                context.vars['evpn_neighbor_default_encap_cli'] = l_0_evpn_neighbor_default_encap_cli
                context.exported_vars.add('evpn_neighbor_default_encap_cli')
                if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'next_hop_self_source_interface')):
                    pass
                    l_0_evpn_neighbor_default_encap_cli = str_join(((undefined(name='evpn_neighbor_default_encap_cli') if l_0_evpn_neighbor_default_encap_cli is missing else l_0_evpn_neighbor_default_encap_cli), ' next-hop-self source-interface ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'next_hop_self_source_interface'), ))
                    context.vars['evpn_neighbor_default_encap_cli'] = l_0_evpn_neighbor_default_encap_cli
                    context.exported_vars.add('evpn_neighbor_default_encap_cli')
                yield '      '
                yield str((undefined(name='evpn_neighbor_default_encap_cli') if l_0_evpn_neighbor_default_encap_cli is missing else l_0_evpn_neighbor_default_encap_cli))
                yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths receive\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'any'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send any\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'any'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send any\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'backup'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send backup\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'ecmp'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send ecmp\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'ecmp_limit')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'ecmp_limit'))
                    yield '\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'limit')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'limit'))
                    yield '\n'
                if t_7(environment.getattr(l_1_peer_group, 'domain_remote'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' domain remote\n'
                if t_7(environment.getattr(l_1_peer_group, 'encapsulation')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' encapsulation '
                    yield str(environment.getattr(l_1_peer_group, 'encapsulation'))
                    yield '\n'
            l_1_peer_group = missing
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'next_hop'), 'resolution_disabled'), True):
                pass
                yield '      next-hop resolution disabled\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'next_hop_self_received_evpn_routes'), 'enable'), True):
                pass
                l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli = 'neighbor default next-hop-self received-evpn-routes route-type ip-prefix'
                context.vars['evpn_neighbor_default_nhs_received_evpn_routes_cli'] = l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli
                context.exported_vars.add('evpn_neighbor_default_nhs_received_evpn_routes_cli')
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'next_hop_self_received_evpn_routes'), 'inter_domain'), True):
                    pass
                    l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli = str_join(((undefined(name='evpn_neighbor_default_nhs_received_evpn_routes_cli') if l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli is missing else l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli), ' inter-domain', ))
                    context.vars['evpn_neighbor_default_nhs_received_evpn_routes_cli'] = l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli
                    context.exported_vars.add('evpn_neighbor_default_nhs_received_evpn_routes_cli')
                yield '      '
                yield str((undefined(name='evpn_neighbor_default_nhs_received_evpn_routes_cli') if l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli is missing else l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'route'), 'import_match_failure_action'), 'discard'):
                pass
                yield '      route import match-failure action discard\n'
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4')):
            pass
            yield '   !\n   address-family flow-spec ipv4\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                pass
                yield '      bgp missing-policy direction in action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                pass
                yield '      bgp missing-policy direction out action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
            l_1_neighbor = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6')):
            pass
            yield '   !\n   address-family flow-spec ipv6\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                pass
                yield '      bgp missing-policy direction in action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                pass
                yield '      bgp missing-policy direction out action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
            l_1_neighbor = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_rtc')):
            pass
            yield '   !\n   address-family rt-membership\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_rtc'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_8(environment.getattr(l_1_peer_group, 'default_route_target')):
                    pass
                    if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'default_route_target'), 'only'), True):
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' default-route-target only\n'
                    else:
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' default-route-target\n'
                if t_8(environment.getattr(environment.getattr(l_1_peer_group, 'default_route_target'), 'encoding_origin_as_omit')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' default-route-target encoding origin-as omit\n'
            l_1_peer_group = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4')):
            pass
            yield '   !\n   address-family ipv4\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'peer_groups'), 'name'):
                l_1_neighbor_default_originate_cli = resolve('neighbor_default_originate_cli')
                l_1_nexthop_v6_cli = resolve('nexthop_v6_cli')
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_peer_group, 'prefix_list_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_peer_group, 'prefix_list_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_peer_group, 'prefix_list_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_peer_group, 'prefix_list_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_peer_group, 'default_originate')):
                    pass
                    l_1_neighbor_default_originate_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' default-originate', ))
                    _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'route_map')):
                        pass
                        l_1_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli), ' route-map ', environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'route_map'), ))
                        _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'always'), True):
                        pass
                        l_1_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli), ' always', ))
                        _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    yield '      '
                    yield str((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'next_hop'), 'address_family_ipv6'), 'enabled'), True):
                    pass
                    l_1_nexthop_v6_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' next-hop address-family ipv6', ))
                    _loop_vars['nexthop_v6_cli'] = l_1_nexthop_v6_cli
                    if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'next_hop'), 'address_family_ipv6'), 'originate'), True):
                        pass
                        l_1_nexthop_v6_cli = str_join(((undefined(name='nexthop_v6_cli') if l_1_nexthop_v6_cli is missing else l_1_nexthop_v6_cli), ' originate', ))
                        _loop_vars['nexthop_v6_cli'] = l_1_nexthop_v6_cli
                    yield '      '
                    yield str((undefined(name='nexthop_v6_cli') if l_1_nexthop_v6_cli is missing else l_1_nexthop_v6_cli))
                    yield '\n'
                elif t_7(environment.getattr(environment.getattr(l_1_peer_group, 'next_hop'), 'address_family_ipv6_originate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' next-hop address-family ipv6 originate\n'
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
            l_1_peer_group = l_1_neighbor_default_originate_cli = l_1_nexthop_v6_cli = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'neighbors'), 'ip_address'):
                l_1_neighbor_default_originate_cli = resolve('neighbor_default_originate_cli')
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_neighbor, 'prefix_list_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_neighbor, 'prefix_list_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_neighbor, 'prefix_list_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_neighbor, 'prefix_list_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_neighbor, 'default_originate')):
                    pass
                    l_1_neighbor_default_originate_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' default-originate', ))
                    _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'route_map')):
                        pass
                        l_1_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli), ' route-map ', environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'route_map'), ))
                        _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'always'), True):
                        pass
                        l_1_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli), ' always', ))
                        _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    yield '      '
                    yield str((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli))
                    yield '\n'
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
            l_1_neighbor = l_1_neighbor_default_originate_cli = missing
            for l_1_network in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'networks'), 'prefix'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_network, 'route_map')):
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_1_network, 'prefix'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_network, 'route_map'))
                    yield '\n'
                else:
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_1_network, 'prefix'))
                    yield '\n'
            l_1_network = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast')):
            pass
            yield '   !\n   address-family ipv4 multicast\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
            l_1_neighbor = missing
            for l_1_redistribute_route in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast'), 'redistribute_routes'), 'source_protocol'):
                l_1_redistribute_route_cli = resolve('redistribute_route_cli')
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_redistribute_route, 'source_protocol')):
                    pass
                    l_1_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_1_redistribute_route, 'source_protocol'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if t_7(environment.getattr(l_1_redistribute_route, 'route_map')):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' route-map ', environment.getattr(l_1_redistribute_route, 'route_map'), ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    yield '      '
                    yield str((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli))
                    yield '\n'
            l_1_redistribute_route = l_1_redistribute_route_cli = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_sr_te')):
            pass
            yield '   !\n   address-family ipv4 sr-te\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_sr_te'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_sr_te'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
            l_1_neighbor = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6')):
            pass
            yield '   !\n   address-family ipv6\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_peer_group, 'prefix_list_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_peer_group, 'prefix_list_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_peer_group, 'prefix_list_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_peer_group, 'prefix_list_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_neighbor, 'prefix_list_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_neighbor, 'prefix_list_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_neighbor, 'prefix_list_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_neighbor, 'prefix_list_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
            l_1_neighbor = missing
            for l_1_network in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'networks'), 'prefix'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_network, 'route_map')):
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_1_network, 'prefix'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_network, 'route_map'))
                    yield '\n'
                else:
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_1_network, 'prefix'))
                    yield '\n'
            l_1_network = missing
            for l_1_redistribute_route in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'redistribute_routes'), 'source_protocol'):
                l_1_redistribute_route_cli = resolve('redistribute_route_cli')
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_redistribute_route, 'source_protocol')):
                    pass
                    l_1_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_1_redistribute_route, 'source_protocol'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if (environment.getattr(l_1_redistribute_route, 'source_protocol') == 'bgp'):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    elif t_7(environment.getattr(l_1_redistribute_route, 'include_leaked')):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' include leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if t_7(environment.getattr(l_1_redistribute_route, 'route_map')):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' route-map ', environment.getattr(l_1_redistribute_route, 'route_map'), ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    yield '      '
                    yield str((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli))
                    yield '\n'
            l_1_redistribute_route = l_1_redistribute_route_cli = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast')):
            pass
            yield '   !\n   address-family ipv6 multicast\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                pass
                yield '      bgp missing-policy direction in action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                pass
                yield '      bgp missing-policy direction out action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'bgp'), 'additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
            l_1_neighbor = missing
            for l_1_network in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'networks'), 'prefix'):
                l_1_network_cli = missing
                _loop_vars = {}
                pass
                l_1_network_cli = str_join(('network ', environment.getattr(l_1_network, 'prefix'), ))
                _loop_vars['network_cli'] = l_1_network_cli
                if t_7(environment.getattr(l_1_network, 'route_map')):
                    pass
                    l_1_network_cli = str_join(((undefined(name='network_cli') if l_1_network_cli is missing else l_1_network_cli), ' route-map ', environment.getattr(l_1_network, 'route_map'), ))
                    _loop_vars['network_cli'] = l_1_network_cli
                yield '      '
                yield str((undefined(name='network_cli') if l_1_network_cli is missing else l_1_network_cli))
                yield '\n'
            l_1_network = l_1_network_cli = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_sr_te')):
            pass
            yield '   !\n   address-family ipv6 sr-te\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_sr_te'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_sr_te'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
            l_1_neighbor = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state')):
            pass
            yield '   !\n   address-family link-state\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                pass
                yield '      bgp missing-policy direction in action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                pass
                yield '      bgp missing-policy direction out action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(l_1_peer_group, 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(l_1_peer_group, 'missing_policy'), 'direction_out_action'))
                    yield '\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'missing_policy'), 'direction_out_action'))
                    yield '\n'
            l_1_neighbor = missing
            if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection')):
                pass
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection'), 'roles'), 'producer'), True):
                    pass
                    yield '      path-selection\n'
                if (t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection'), 'roles'), 'consumer'), True) or t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection'), 'roles'), 'propagator'), True)):
                    pass
                    l_0_path_selection_roles = 'path-selection role'
                    context.vars['path_selection_roles'] = l_0_path_selection_roles
                    context.exported_vars.add('path_selection_roles')
                    if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection'), 'roles'), 'consumer'), True):
                        pass
                        l_0_path_selection_roles = str_join(((undefined(name='path_selection_roles') if l_0_path_selection_roles is missing else l_0_path_selection_roles), ' consumer', ))
                        context.vars['path_selection_roles'] = l_0_path_selection_roles
                        context.exported_vars.add('path_selection_roles')
                    if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection'), 'roles'), 'propagator'), True):
                        pass
                        l_0_path_selection_roles = str_join(((undefined(name='path_selection_roles') if l_0_path_selection_roles is missing else l_0_path_selection_roles), ' propagator', ))
                        context.vars['path_selection_roles'] = l_0_path_selection_roles
                        context.exported_vars.add('path_selection_roles')
                    yield '      '
                    yield str((undefined(name='path_selection_roles') if l_0_path_selection_roles is missing else l_0_path_selection_roles))
                    yield '\n'
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection')):
            pass
            yield '   !\n   address-family path-selection\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send'), 'any'), True):
                pass
                yield '      bgp additional-paths send any\n'
            elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send'), 'backup'), True):
                pass
                yield '      bgp additional-paths send backup\n'
            elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send'), 'ecmp'), True):
                pass
                yield '      bgp additional-paths send ecmp\n'
            elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send'), 'ecmp_limit')):
                pass
                yield '      bgp additional-paths send ecmp limit '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send'), 'ecmp_limit'))
                yield '\n'
            elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send'), 'limit')):
                pass
                yield '      bgp additional-paths send limit '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send'), 'limit'))
                yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths receive\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'any'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send any\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'backup'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send backup\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'ecmp'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send ecmp\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'ecmp_limit')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'ecmp_limit'))
                    yield '\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'limit')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths send limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), 'limit'))
                    yield '\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_7(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths receive\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'), 'any'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths send any\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'), 'backup'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths send backup\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'), 'ecmp'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths send ecmp\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'), 'ecmp_limit')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'), 'ecmp_limit'))
                    yield '\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'), 'limit')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths send limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'), 'limit'))
                    yield '\n'
            l_1_neighbor = missing
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4')):
            pass
            yield '   !\n   address-family vpn-ipv4\n'
            if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'domain_identifier')):
                pass
                yield '      domain identifier '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'domain_identifier'))
                yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
            l_1_neighbor = missing
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'neighbor_default_encapsulation_mpls_next_hop_self'), 'source_interface')):
                pass
                yield '      neighbor default encapsulation mpls next-hop-self source-interface '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'neighbor_default_encapsulation_mpls_next_hop_self'), 'source_interface'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'route'), 'import_match_failure_action'), 'discard'):
                pass
                yield '      route import match-failure action discard\n'
        if t_7(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6')):
            pass
            yield '   !\n   address-family vpn-ipv6\n'
            if t_7(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'domain_identifier')):
                pass
                yield '      domain identifier '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'domain_identifier'))
                yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_7(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
            l_1_neighbor = missing
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'neighbor_default_encapsulation_mpls_next_hop_self'), 'source_interface')):
                pass
                yield '      neighbor default encapsulation mpls next-hop-self source-interface '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'neighbor_default_encapsulation_mpls_next_hop_self'), 'source_interface'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'route'), 'import_match_failure_action'), 'discard'):
                pass
                yield '      route import match-failure action discard\n'
        for l_1_vrf in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vrfs'), 'name'):
            l_1_tmp_vrf_neighbor_prefix_list_in = l_1_tmp_vrf_neighbor_prefix_list_out = missing
            _loop_vars = {}
            pass
            yield '   !\n   vrf '
            yield str(environment.getattr(l_1_vrf, 'name'))
            yield '\n'
            if t_7(environment.getattr(l_1_vrf, 'rd')):
                pass
                yield '      rd '
                yield str(environment.getattr(l_1_vrf, 'rd'))
                yield '\n'
            if t_7(environment.getattr(l_1_vrf, 'evpn_multicast'), True):
                pass
                yield '      evpn multicast\n'
                if (t_7(environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_address_family'), 'ipv4')) and t_7(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_address_family'), 'ipv4'), 'transit'), True)):
                    pass
                    yield '         address-family ipv4\n'
                    if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_address_family'), 'ipv4'), 'transit'), True):
                        pass
                        yield '            transit\n'
            if t_7(environment.getattr(environment.getattr(l_1_vrf, 'route_targets'), 'import')):
                pass
                for l_2_address_family in environment.getattr(environment.getattr(l_1_vrf, 'route_targets'), 'import'):
                    _loop_vars = {}
                    pass
                    for l_3_route_target in environment.getattr(l_2_address_family, 'route_targets'):
                        _loop_vars = {}
                        pass
                        yield '      route-target import '
                        yield str(environment.getattr(l_2_address_family, 'address_family'))
                        yield ' '
                        yield str(l_3_route_target)
                        yield '\n'
                    l_3_route_target = missing
                    if t_7(environment.getattr(l_2_address_family, 'route_map')):
                        pass
                        yield '      route-target import '
                        yield str(environment.getattr(l_2_address_family, 'address_family'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_address_family, 'route_map'))
                        yield '\n'
                l_2_address_family = missing
            if t_7(environment.getattr(environment.getattr(l_1_vrf, 'route_targets'), 'export')):
                pass
                for l_2_address_family in environment.getattr(environment.getattr(l_1_vrf, 'route_targets'), 'export'):
                    _loop_vars = {}
                    pass
                    for l_3_route_target in environment.getattr(l_2_address_family, 'route_targets'):
                        _loop_vars = {}
                        pass
                        yield '      route-target export '
                        yield str(environment.getattr(l_2_address_family, 'address_family'))
                        yield ' '
                        yield str(l_3_route_target)
                        yield '\n'
                    l_3_route_target = missing
                    if t_7(environment.getattr(l_2_address_family, 'route_map')):
                        pass
                        yield '      route-target export '
                        yield str(environment.getattr(l_2_address_family, 'address_family'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_address_family, 'route_map'))
                        yield '\n'
                l_2_address_family = missing
            if t_7(environment.getattr(l_1_vrf, 'router_id')):
                pass
                yield '      router-id '
                yield str(environment.getattr(l_1_vrf, 'router_id'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(l_1_vrf, 'updates'), 'wait_for_convergence'), True):
                pass
                yield '      update wait-for-convergence\n'
            if t_7(environment.getattr(environment.getattr(l_1_vrf, 'updates'), 'wait_install'), True):
                pass
                yield '      update wait-install\n'
            if t_7(environment.getattr(l_1_vrf, 'timers')):
                pass
                yield '      timers bgp '
                yield str(environment.getattr(l_1_vrf, 'timers'))
                yield '\n'
            if t_7(environment.getattr(l_1_vrf, 'listen_ranges')):
                pass
                def t_11(fiter):
                    for l_2_listen_range in fiter:
                        if ((t_7(environment.getattr(l_2_listen_range, 'peer_group')) and t_7(environment.getattr(l_2_listen_range, 'prefix'))) and (t_7(environment.getattr(l_2_listen_range, 'peer_filter')) or t_7(environment.getattr(l_2_listen_range, 'remote_as')))):
                            yield l_2_listen_range
                for l_2_listen_range in t_11(t_3(environment.getattr(l_1_vrf, 'listen_ranges'), 'peer_group')):
                    l_2_listen_range_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_listen_range_cli = str_join(('bgp listen range ', environment.getattr(l_2_listen_range, 'prefix'), ))
                    _loop_vars['listen_range_cli'] = l_2_listen_range_cli
                    if t_7(environment.getattr(l_2_listen_range, 'peer_id_include_router_id'), True):
                        pass
                        l_2_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_2_listen_range_cli is missing else l_2_listen_range_cli), ' peer-id include router-id', ))
                        _loop_vars['listen_range_cli'] = l_2_listen_range_cli
                    l_2_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_2_listen_range_cli is missing else l_2_listen_range_cli), ' peer-group ', environment.getattr(l_2_listen_range, 'peer_group'), ))
                    _loop_vars['listen_range_cli'] = l_2_listen_range_cli
                    if t_7(environment.getattr(l_2_listen_range, 'peer_filter')):
                        pass
                        l_2_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_2_listen_range_cli is missing else l_2_listen_range_cli), ' peer-filter ', environment.getattr(l_2_listen_range, 'peer_filter'), ))
                        _loop_vars['listen_range_cli'] = l_2_listen_range_cli
                    elif t_7(environment.getattr(l_2_listen_range, 'remote_as')):
                        pass
                        l_2_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_2_listen_range_cli is missing else l_2_listen_range_cli), ' remote-as ', environment.getattr(l_2_listen_range, 'remote_as'), ))
                        _loop_vars['listen_range_cli'] = l_2_listen_range_cli
                    yield '      '
                    yield str((undefined(name='listen_range_cli') if l_2_listen_range_cli is missing else l_2_listen_range_cli))
                    yield '\n'
                l_2_listen_range = l_2_listen_range_cli = missing
            for l_2_neighbor_interface in t_3(environment.getattr(l_1_vrf, 'neighbor_interfaces'), 'name'):
                _loop_vars = {}
                pass
                if (t_7(environment.getattr(l_2_neighbor_interface, 'peer_group')) and t_7(environment.getattr(l_2_neighbor_interface, 'remote_as'))):
                    pass
                    yield '      neighbor interface '
                    yield str(environment.getattr(l_2_neighbor_interface, 'name'))
                    yield ' peer-group '
                    yield str(environment.getattr(l_2_neighbor_interface, 'peer_group'))
                    yield ' remote-as '
                    yield str(environment.getattr(l_2_neighbor_interface, 'remote_as'))
                    yield '\n'
                elif (t_7(environment.getattr(l_2_neighbor_interface, 'peer_group')) and t_7(environment.getattr(l_2_neighbor_interface, 'peer_filter'))):
                    pass
                    yield '      neighbor interface '
                    yield str(environment.getattr(l_2_neighbor_interface, 'name'))
                    yield ' peer-group '
                    yield str(environment.getattr(l_2_neighbor_interface, 'peer_group'))
                    yield ' peer-filter '
                    yield str(environment.getattr(l_2_neighbor_interface, 'peer_filter'))
                    yield '\n'
            l_2_neighbor_interface = missing
            l_1_tmp_vrf_neighbor_prefix_list_in = {}
            _loop_vars['tmp_vrf_neighbor_prefix_list_in'] = l_1_tmp_vrf_neighbor_prefix_list_in
            l_1_tmp_vrf_neighbor_prefix_list_out = {}
            _loop_vars['tmp_vrf_neighbor_prefix_list_out'] = l_1_tmp_vrf_neighbor_prefix_list_out
            for l_2_neighbor in t_3(environment.getattr(l_1_vrf, 'neighbors'), 'ip_address'):
                l_2_remove_private_as_cli = resolve('remove_private_as_cli')
                l_2_remove_private_as_ingress_cli = resolve('remove_private_as_ingress_cli')
                l_2_hide_passwords = resolve('hide_passwords')
                l_2_neighbor_ebgp_multihop_cli = resolve('neighbor_ebgp_multihop_cli')
                l_2_allowas_in_cli = resolve('allowas_in_cli')
                l_2_neighbor_rib_in_pre_policy_retain_cli = resolve('neighbor_rib_in_pre_policy_retain_cli')
                l_2_maximum_routes_cli = resolve('maximum_routes_cli')
                l_2_neighbor_default_originate_cli = resolve('neighbor_default_originate_cli')
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_2_neighbor, 'remote_as')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' remote-as '
                    yield str(environment.getattr(l_2_neighbor, 'remote_as'))
                    yield '\n'
                if t_7(environment.getattr(l_2_neighbor, 'peer_group')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' peer group '
                    yield str(environment.getattr(l_2_neighbor, 'peer_group'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as'), 'enabled'), True):
                    pass
                    l_2_remove_private_as_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' remove-private-as', ))
                    _loop_vars['remove_private_as_cli'] = l_2_remove_private_as_cli
                    if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as'), 'all'), True):
                        pass
                        l_2_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_2_remove_private_as_cli is missing else l_2_remove_private_as_cli), ' all', ))
                        _loop_vars['remove_private_as_cli'] = l_2_remove_private_as_cli
                        if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as'), 'replace_as'), True):
                            pass
                            l_2_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_2_remove_private_as_cli is missing else l_2_remove_private_as_cli), ' replace-as', ))
                            _loop_vars['remove_private_as_cli'] = l_2_remove_private_as_cli
                    yield '      '
                    yield str((undefined(name='remove_private_as_cli') if l_2_remove_private_as_cli is missing else l_2_remove_private_as_cli))
                    yield '\n'
                elif t_7(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as'), 'enabled'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' remove-private-as\n'
                if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as_ingress'), 'enabled'), True):
                    pass
                    l_2_remove_private_as_ingress_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' remove-private-as ingress', ))
                    _loop_vars['remove_private_as_ingress_cli'] = l_2_remove_private_as_ingress_cli
                    if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as_ingress'), 'replace_as'), True):
                        pass
                        l_2_remove_private_as_ingress_cli = str_join(((undefined(name='remove_private_as_ingress_cli') if l_2_remove_private_as_ingress_cli is missing else l_2_remove_private_as_ingress_cli), ' replace-as', ))
                        _loop_vars['remove_private_as_ingress_cli'] = l_2_remove_private_as_ingress_cli
                    yield '      '
                    yield str((undefined(name='remove_private_as_ingress_cli') if l_2_remove_private_as_ingress_cli is missing else l_2_remove_private_as_ingress_cli))
                    yield '\n'
                elif t_7(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as_ingress'), 'enabled'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' remove-private-as ingress\n'
                if t_7(environment.getattr(l_2_neighbor, 'password')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' password 7 '
                    yield str(t_2(environment.getattr(l_2_neighbor, 'password'), (undefined(name='hide_passwords') if l_2_hide_passwords is missing else l_2_hide_passwords)))
                    yield '\n'
                if t_7(environment.getattr(l_2_neighbor, 'passive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' passive\n'
                if t_7(environment.getattr(l_2_neighbor, 'weight')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' weight '
                    yield str(environment.getattr(l_2_neighbor, 'weight'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'as_path'), 'remote_as_replace_out'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' as-path remote-as replace out\n'
                if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'as_path'), 'prepend_own_disabled'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' as-path prepend-own disabled\n'
                if t_7(environment.getattr(l_2_neighbor, 'local_as')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' local-as '
                    yield str(environment.getattr(l_2_neighbor, 'local_as'))
                    yield ' no-prepend replace-as\n'
                if t_7(environment.getattr(l_2_neighbor, 'description')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' description '
                    yield str(environment.getattr(l_2_neighbor, 'description'))
                    yield '\n'
                if t_7(environment.getattr(l_2_neighbor, 'ebgp_multihop')):
                    pass
                    l_2_neighbor_ebgp_multihop_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' ebgp-multihop', ))
                    _loop_vars['neighbor_ebgp_multihop_cli'] = l_2_neighbor_ebgp_multihop_cli
                    if t_9(environment.getattr(l_2_neighbor, 'ebgp_multihop')):
                        pass
                        l_2_neighbor_ebgp_multihop_cli = str_join(((undefined(name='neighbor_ebgp_multihop_cli') if l_2_neighbor_ebgp_multihop_cli is missing else l_2_neighbor_ebgp_multihop_cli), ' ', environment.getattr(l_2_neighbor, 'ebgp_multihop'), ))
                        _loop_vars['neighbor_ebgp_multihop_cli'] = l_2_neighbor_ebgp_multihop_cli
                    yield '      '
                    yield str((undefined(name='neighbor_ebgp_multihop_cli') if l_2_neighbor_ebgp_multihop_cli is missing else l_2_neighbor_ebgp_multihop_cli))
                    yield '\n'
                if t_7(environment.getattr(l_2_neighbor, 'next_hop_self'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' next-hop-self\n'
                if t_7(environment.getattr(l_2_neighbor, 'bfd'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' bfd\n'
                    if ((t_7(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'interval')) and t_7(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'min_rx'))) and t_7(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'multiplier'))):
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' bfd interval '
                        yield str(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'interval'))
                        yield ' min-rx '
                        yield str(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'min_rx'))
                        yield ' multiplier '
                        yield str(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'multiplier'))
                        yield '\n'
                elif (t_7(environment.getattr(l_2_neighbor, 'bfd'), False) and t_7(environment.getattr(l_2_neighbor, 'peer_group'))):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' bfd\n'
                if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'allowas_in'), 'enabled'), True):
                    pass
                    l_2_allowas_in_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' allowas-in', ))
                    _loop_vars['allowas_in_cli'] = l_2_allowas_in_cli
                    if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'allowas_in'), 'times')):
                        pass
                        l_2_allowas_in_cli = str_join(((undefined(name='allowas_in_cli') if l_2_allowas_in_cli is missing else l_2_allowas_in_cli), ' ', environment.getattr(environment.getattr(l_2_neighbor, 'allowas_in'), 'times'), ))
                        _loop_vars['allowas_in_cli'] = l_2_allowas_in_cli
                    yield '      '
                    yield str((undefined(name='allowas_in_cli') if l_2_allowas_in_cli is missing else l_2_allowas_in_cli))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'rib_in_pre_policy_retain'), 'enabled'), True):
                    pass
                    l_2_neighbor_rib_in_pre_policy_retain_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' rib-in pre-policy retain', ))
                    _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_2_neighbor_rib_in_pre_policy_retain_cli
                    if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'rib_in_pre_policy_retain'), 'all'), True):
                        pass
                        l_2_neighbor_rib_in_pre_policy_retain_cli = str_join(((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_2_neighbor_rib_in_pre_policy_retain_cli is missing else l_2_neighbor_rib_in_pre_policy_retain_cli), ' all', ))
                        _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_2_neighbor_rib_in_pre_policy_retain_cli
                    yield '      '
                    yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_2_neighbor_rib_in_pre_policy_retain_cli is missing else l_2_neighbor_rib_in_pre_policy_retain_cli))
                    yield '\n'
                elif t_7(environment.getattr(environment.getattr(l_2_neighbor, 'rib_in_pre_policy_retain'), 'enabled'), False):
                    pass
                    l_2_neighbor_rib_in_pre_policy_retain_cli = str_join(('no neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' rib-in pre-policy retain', ))
                    _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_2_neighbor_rib_in_pre_policy_retain_cli
                    yield '      '
                    yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_2_neighbor_rib_in_pre_policy_retain_cli is missing else l_2_neighbor_rib_in_pre_policy_retain_cli))
                    yield '\n'
                if t_7(environment.getattr(l_2_neighbor, 'timers')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' timers '
                    yield str(environment.getattr(l_2_neighbor, 'timers'))
                    yield '\n'
                if t_7(environment.getattr(l_2_neighbor, 'shutdown'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' shutdown\n'
                if t_7(environment.getattr(l_2_neighbor, 'send_community'), 'all'):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' send-community\n'
                elif t_7(environment.getattr(l_2_neighbor, 'send_community')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' send-community '
                    yield str(environment.getattr(l_2_neighbor, 'send_community'))
                    yield '\n'
                if t_7(environment.getattr(l_2_neighbor, 'route_reflector_client'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' route-reflector-client\n'
                elif t_7(environment.getattr(l_2_neighbor, 'route_reflector_client'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' route-reflector-client\n'
                if t_7(environment.getattr(l_2_neighbor, 'maximum_routes')):
                    pass
                    l_2_maximum_routes_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' maximum-routes ', environment.getattr(l_2_neighbor, 'maximum_routes'), ))
                    _loop_vars['maximum_routes_cli'] = l_2_maximum_routes_cli
                    if t_7(environment.getattr(l_2_neighbor, 'maximum_routes_warning_limit')):
                        pass
                        l_2_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_2_maximum_routes_cli is missing else l_2_maximum_routes_cli), ' warning-limit ', environment.getattr(l_2_neighbor, 'maximum_routes_warning_limit'), ))
                        _loop_vars['maximum_routes_cli'] = l_2_maximum_routes_cli
                    if t_7(environment.getattr(l_2_neighbor, 'maximum_routes_warning_only'), True):
                        pass
                        l_2_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_2_maximum_routes_cli is missing else l_2_maximum_routes_cli), ' warning-only', ))
                        _loop_vars['maximum_routes_cli'] = l_2_maximum_routes_cli
                    yield '      '
                    yield str((undefined(name='maximum_routes_cli') if l_2_maximum_routes_cli is missing else l_2_maximum_routes_cli))
                    yield '\n'
                if t_7(environment.getattr(l_2_neighbor, 'default_originate')):
                    pass
                    l_2_neighbor_default_originate_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' default-originate', ))
                    _loop_vars['neighbor_default_originate_cli'] = l_2_neighbor_default_originate_cli
                    if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'default_originate'), 'route_map')):
                        pass
                        l_2_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_2_neighbor_default_originate_cli is missing else l_2_neighbor_default_originate_cli), ' route-map ', environment.getattr(environment.getattr(l_2_neighbor, 'default_originate'), 'route_map'), ))
                        _loop_vars['neighbor_default_originate_cli'] = l_2_neighbor_default_originate_cli
                    if t_7(environment.getattr(environment.getattr(l_2_neighbor, 'default_originate'), 'always'), True):
                        pass
                        l_2_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_2_neighbor_default_originate_cli is missing else l_2_neighbor_default_originate_cli), ' always', ))
                        _loop_vars['neighbor_default_originate_cli'] = l_2_neighbor_default_originate_cli
                    yield '      '
                    yield str((undefined(name='neighbor_default_originate_cli') if l_2_neighbor_default_originate_cli is missing else l_2_neighbor_default_originate_cli))
                    yield '\n'
                if t_7(environment.getattr(l_2_neighbor, 'update_source')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' update-source '
                    yield str(environment.getattr(l_2_neighbor, 'update_source'))
                    yield '\n'
                if t_7(environment.getattr(l_2_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_2_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_7(environment.getattr(l_2_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_2_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_7(environment.getattr(l_2_neighbor, 'prefix_list_in')):
                    pass
                    context.call(environment.getattr((undefined(name='tmp_vrf_neighbor_prefix_list_in') if l_1_tmp_vrf_neighbor_prefix_list_in is missing else l_1_tmp_vrf_neighbor_prefix_list_in), 'update'), {environment.getattr(l_2_neighbor, 'ip_address'): environment.getattr(l_2_neighbor, 'prefix_list_in')}, _loop_vars=_loop_vars)
                if t_7(environment.getattr(l_2_neighbor, 'prefix_list_out')):
                    pass
                    context.call(environment.getattr((undefined(name='tmp_vrf_neighbor_prefix_list_out') if l_1_tmp_vrf_neighbor_prefix_list_out is missing else l_1_tmp_vrf_neighbor_prefix_list_out), 'update'), {environment.getattr(l_2_neighbor, 'ip_address'): environment.getattr(l_2_neighbor, 'prefix_list_out')}, _loop_vars=_loop_vars)
            l_2_neighbor = l_2_remove_private_as_cli = l_2_remove_private_as_ingress_cli = l_2_hide_passwords = l_2_neighbor_ebgp_multihop_cli = l_2_allowas_in_cli = l_2_neighbor_rib_in_pre_policy_retain_cli = l_2_maximum_routes_cli = l_2_neighbor_default_originate_cli = missing
            for l_2_network in t_3(environment.getattr(l_1_vrf, 'networks'), 'prefix'):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_2_network, 'route_map')):
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_2_network, 'prefix'))
                    yield ' route-map '
                    yield str(environment.getattr(l_2_network, 'route_map'))
                    yield '\n'
                else:
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_2_network, 'prefix'))
                    yield '\n'
            l_2_network = missing
            for l_2_aggregate_address in t_3(environment.getattr(l_1_vrf, 'aggregate_addresses'), 'prefix'):
                l_2_aggregate_address_cli = missing
                _loop_vars = {}
                pass
                l_2_aggregate_address_cli = str_join(('aggregate-address ', environment.getattr(l_2_aggregate_address, 'prefix'), ))
                _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_7(environment.getattr(l_2_aggregate_address, 'as_set'), True):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' as-set', ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_7(environment.getattr(l_2_aggregate_address, 'advertise_map')):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' advertise-map ', environment.getattr(l_2_aggregate_address, 'advertise_map'), ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_7(environment.getattr(l_2_aggregate_address, 'supress_map')):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' supress-map ', environment.getattr(l_2_aggregate_address, 'supress_map'), ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_7(environment.getattr(l_2_aggregate_address, 'summary_only'), True):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' summary-only', ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_7(environment.getattr(l_2_aggregate_address, 'attribute_map')):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' attribute-map ', environment.getattr(l_2_aggregate_address, 'attribute_map'), ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_7(environment.getattr(l_2_aggregate_address, 'match_map')):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' match-map ', environment.getattr(l_2_aggregate_address, 'match_map'), ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_7(environment.getattr(l_2_aggregate_address, 'advertise_only'), True):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' advertise-only', ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                yield '      '
                yield str((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli))
                yield '\n'
            l_2_aggregate_address = l_2_aggregate_address_cli = missing
            for l_2_redistribute_route in t_3(environment.getattr(l_1_vrf, 'redistribute_routes'), 'source_protocol'):
                l_2_redistribute_route_cli = resolve('redistribute_route_cli')
                _loop_vars = {}
                pass
                if t_7(environment.getattr(l_2_redistribute_route, 'source_protocol')):
                    pass
                    l_2_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_2_redistribute_route, 'source_protocol'), ))
                    _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                    if (environment.getattr(l_2_redistribute_route, 'source_protocol') == 'bgp'):
                        pass
                        l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                    elif t_7(environment.getattr(l_2_redistribute_route, 'include_leaked')):
                        pass
                        l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' include leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                    if t_7(environment.getattr(l_2_redistribute_route, 'route_map')):
                        pass
                        l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' route-map ', environment.getattr(l_2_redistribute_route, 'route_map'), ))
                        _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                    yield '      '
                    yield str((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli))
                    yield '\n'
            l_2_redistribute_route = l_2_redistribute_route_cli = missing
            if t_7(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4')):
                pass
                yield '      !\n      address-family flow-spec ipv4\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4'), 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_7(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                l_2_neighbor = missing
            if t_7(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6')):
                pass
                yield '      !\n      address-family flow-spec ipv6\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6'), 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_7(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                l_2_neighbor = missing
            if ((t_7(environment.getattr(l_1_vrf, 'address_family_ipv4')) or (undefined(name='tmp_vrf_neighbor_prefix_list_in') if l_1_tmp_vrf_neighbor_prefix_list_in is missing else l_1_tmp_vrf_neighbor_prefix_list_in)) or (undefined(name='tmp_vrf_neighbor_prefix_list_out') if l_1_tmp_vrf_neighbor_prefix_list_out is missing else l_1_tmp_vrf_neighbor_prefix_list_out)):
                pass
                yield '      !\n      address-family ipv4\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'install'), True):
                    pass
                    yield '         bgp additional-paths install\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'install_ecmp_primary'), True):
                    pass
                    yield '         bgp additional-paths install ecmp-primary\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'receive'), True):
                    pass
                    yield '         bgp additional-paths receive\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send'), 'any'), True):
                    pass
                    yield '         bgp additional-paths send any\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send'), 'backup'), True):
                    pass
                    yield '         bgp additional-paths send backup\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send'), 'ecmp'), True):
                    pass
                    yield '         bgp additional-paths send ecmp\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send'), 'ecmp_limit')):
                    pass
                    yield '         bgp additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send'), 'ecmp_limit'))
                    yield '\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send'), 'limit')):
                    pass
                    yield '         bgp additional-paths send limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send'), 'limit'))
                    yield '\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'neighbors'), 'ip_address'):
                    l_2_ipv6_originate_cli = resolve('ipv6_originate_cli')
                    _loop_vars = {}
                    pass
                    if t_7(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                    if t_7(environment.getattr(l_2_neighbor, 'route_map_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_in'))
                        yield ' in\n'
                    if t_7(environment.getattr(l_2_neighbor, 'route_map_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_out'))
                        yield ' out\n'
                    if t_7(environment.getattr(l_2_neighbor, 'prefix_list_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' prefix-list '
                        yield str(environment.getattr(l_2_neighbor, 'prefix_list_in'))
                        yield ' in\n'
                        if t_7(environment.getitem((undefined(name='tmp_vrf_neighbor_prefix_list_in') if l_1_tmp_vrf_neighbor_prefix_list_in is missing else l_1_tmp_vrf_neighbor_prefix_list_in), environment.getattr(l_2_neighbor, 'ip_address'))):
                            pass
                            context.call(environment.getattr((undefined(name='tmp_vrf_neighbor_prefix_list_in') if l_1_tmp_vrf_neighbor_prefix_list_in is missing else l_1_tmp_vrf_neighbor_prefix_list_in), 'pop'), environment.getattr(l_2_neighbor, 'ip_address'), _loop_vars=_loop_vars)
                    elif t_7(environment.getitem((undefined(name='tmp_vrf_neighbor_prefix_list_in') if l_1_tmp_vrf_neighbor_prefix_list_in is missing else l_1_tmp_vrf_neighbor_prefix_list_in), environment.getattr(l_2_neighbor, 'ip_address'))):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' prefix-list '
                        yield str(context.call(environment.getattr((undefined(name='tmp_vrf_neighbor_prefix_list_in') if l_1_tmp_vrf_neighbor_prefix_list_in is missing else l_1_tmp_vrf_neighbor_prefix_list_in), 'pop'), environment.getattr(l_2_neighbor, 'ip_address'), _loop_vars=_loop_vars))
                        yield ' in\n'
                    if t_7(environment.getattr(l_2_neighbor, 'prefix_list_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' prefix-list '
                        yield str(environment.getattr(l_2_neighbor, 'prefix_list_out'))
                        yield ' out\n'
                        if t_7(environment.getitem((undefined(name='tmp_vrf_neighbor_prefix_list_out') if l_1_tmp_vrf_neighbor_prefix_list_out is missing else l_1_tmp_vrf_neighbor_prefix_list_out), environment.getattr(l_2_neighbor, 'ip_address'))):
                            pass
                            context.call(environment.getattr((undefined(name='tmp_vrf_neighbor_prefix_list_out') if l_1_tmp_vrf_neighbor_prefix_list_out is missing else l_1_tmp_vrf_neighbor_prefix_list_out), 'pop'), environment.getattr(l_2_neighbor, 'ip_address'), _loop_vars=_loop_vars)
                    elif t_7(environment.getitem((undefined(name='tmp_vrf_neighbor_prefix_list_out') if l_1_tmp_vrf_neighbor_prefix_list_out is missing else l_1_tmp_vrf_neighbor_prefix_list_out), environment.getattr(l_2_neighbor, 'ip_address'))):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' prefix-list '
                        yield str(context.call(environment.getattr((undefined(name='tmp_vrf_neighbor_prefix_list_out') if l_1_tmp_vrf_neighbor_prefix_list_out is missing else l_1_tmp_vrf_neighbor_prefix_list_out), 'pop'), environment.getattr(l_2_neighbor, 'ip_address'), _loop_vars=_loop_vars))
                        yield ' out\n'
                    if t_7(environment.getattr(environment.getattr(environment.getattr(l_2_neighbor, 'next_hop'), 'address_family_ipv6'), 'enabled')):
                        pass
                        if t_7(environment.getattr(environment.getattr(environment.getattr(l_2_neighbor, 'next_hop'), 'address_family_ipv6'), 'enabled'), True):
                            pass
                            l_2_ipv6_originate_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' next-hop address-family ipv6', ))
                            _loop_vars['ipv6_originate_cli'] = l_2_ipv6_originate_cli
                            if t_7(environment.getattr(environment.getattr(environment.getattr(l_2_neighbor, 'next_hop'), 'address_family_ipv6'), 'originate'), True):
                                pass
                                l_2_ipv6_originate_cli = str_join(((undefined(name='ipv6_originate_cli') if l_2_ipv6_originate_cli is missing else l_2_ipv6_originate_cli), ' originate', ))
                                _loop_vars['ipv6_originate_cli'] = l_2_ipv6_originate_cli
                        elif t_7(environment.getattr(environment.getattr(environment.getattr(l_2_neighbor, 'next_hop'), 'address_family_ipv6'), 'enabled'), False):
                            pass
                            l_2_ipv6_originate_cli = str_join(('no neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' next-hop address-family ipv6', ))
                            _loop_vars['ipv6_originate_cli'] = l_2_ipv6_originate_cli
                        yield '         '
                        yield str((undefined(name='ipv6_originate_cli') if l_2_ipv6_originate_cli is missing else l_2_ipv6_originate_cli))
                        yield '\n'
                l_2_neighbor = l_2_ipv6_originate_cli = missing
                for l_2_tmp_neighbor_ip in t_3((undefined(name='tmp_vrf_neighbor_prefix_list_in') if l_1_tmp_vrf_neighbor_prefix_list_in is missing else l_1_tmp_vrf_neighbor_prefix_list_in)):
                    _loop_vars = {}
                    pass
                    yield '         neighbor '
                    yield str(l_2_tmp_neighbor_ip)
                    yield ' prefix-list '
                    yield str(environment.getitem((undefined(name='tmp_vrf_neighbor_prefix_list_in') if l_1_tmp_vrf_neighbor_prefix_list_in is missing else l_1_tmp_vrf_neighbor_prefix_list_in), l_2_tmp_neighbor_ip))
                    yield ' in\n'
                l_2_tmp_neighbor_ip = missing
                for l_2_tmp_neighbor_ip in t_3((undefined(name='tmp_vrf_neighbor_prefix_list_out') if l_1_tmp_vrf_neighbor_prefix_list_out is missing else l_1_tmp_vrf_neighbor_prefix_list_out)):
                    _loop_vars = {}
                    pass
                    yield '         neighbor '
                    yield str(l_2_tmp_neighbor_ip)
                    yield ' prefix-list '
                    yield str(environment.getitem((undefined(name='tmp_vrf_neighbor_prefix_list_out') if l_1_tmp_vrf_neighbor_prefix_list_out is missing else l_1_tmp_vrf_neighbor_prefix_list_out), l_2_tmp_neighbor_ip))
                    yield ' out\n'
                l_2_tmp_neighbor_ip = missing
                for l_2_network in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'networks'), 'prefix'):
                    l_2_network_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_network_cli = str_join(('network ', environment.getattr(l_2_network, 'prefix'), ))
                    _loop_vars['network_cli'] = l_2_network_cli
                    if t_7(environment.getattr(l_2_network, 'route_map')):
                        pass
                        l_2_network_cli = str_join(((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli), ' route-map ', environment.getattr(l_2_network, 'route_map'), ))
                        _loop_vars['network_cli'] = l_2_network_cli
                    yield '         '
                    yield str((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli))
                    yield '\n'
                l_2_network = l_2_network_cli = missing
            if t_7(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast')):
                pass
                yield '      !\n      address-family ipv4 multicast\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'bgp'), 'additional_paths'), 'receive'), True):
                    pass
                    yield '         bgp additional-paths receive\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_7(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                    if t_7(environment.getattr(l_2_neighbor, 'route_map_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_in'))
                        yield ' in\n'
                    if t_7(environment.getattr(l_2_neighbor, 'route_map_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_out'))
                        yield ' out\n'
                l_2_neighbor = missing
                for l_2_network in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'networks'), 'prefix'):
                    l_2_network_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_network_cli = str_join(('network ', environment.getattr(l_2_network, 'prefix'), ))
                    _loop_vars['network_cli'] = l_2_network_cli
                    if t_7(environment.getattr(l_2_network, 'route_map')):
                        pass
                        l_2_network_cli = str_join(((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli), ' route-map ', environment.getattr(l_2_network, 'route_map'), ))
                        _loop_vars['network_cli'] = l_2_network_cli
                    yield '         '
                    yield str((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli))
                    yield '\n'
                l_2_network = l_2_network_cli = missing
            if t_7(environment.getattr(l_1_vrf, 'address_family_ipv6')):
                pass
                yield '      !\n      address-family ipv6\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'install'), True):
                    pass
                    yield '         bgp additional-paths install\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'install_ecmp_primary'), True):
                    pass
                    yield '         bgp additional-paths install ecmp-primary\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'receive'), True):
                    pass
                    yield '         bgp additional-paths receive\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send'), 'any'), True):
                    pass
                    yield '         bgp additional-paths send any\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send'), 'backup'), True):
                    pass
                    yield '         bgp additional-paths send backup\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send'), 'ecmp'), True):
                    pass
                    yield '         bgp additional-paths send ecmp\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send'), 'ecmp_limit')):
                    pass
                    yield '         bgp additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send'), 'ecmp_limit'))
                    yield '\n'
                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send'), 'limit')):
                    pass
                    yield '         bgp additional-paths send limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send'), 'limit'))
                    yield '\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_7(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                    if t_7(environment.getattr(l_2_neighbor, 'route_map_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_in'))
                        yield ' in\n'
                    if t_7(environment.getattr(l_2_neighbor, 'route_map_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_out'))
                        yield ' out\n'
                    if t_7(environment.getattr(l_2_neighbor, 'prefix_list_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' prefix-list '
                        yield str(environment.getattr(l_2_neighbor, 'prefix_list_in'))
                        yield ' in\n'
                    if t_7(environment.getattr(l_2_neighbor, 'prefix_list_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' prefix-list '
                        yield str(environment.getattr(l_2_neighbor, 'prefix_list_out'))
                        yield ' out\n'
                l_2_neighbor = missing
                for l_2_network in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'networks'), 'prefix'):
                    l_2_network_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_network_cli = str_join(('network ', environment.getattr(l_2_network, 'prefix'), ))
                    _loop_vars['network_cli'] = l_2_network_cli
                    if t_7(environment.getattr(l_2_network, 'route_map')):
                        pass
                        l_2_network_cli = str_join(((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli), ' route-map ', environment.getattr(l_2_network, 'route_map'), ))
                        _loop_vars['network_cli'] = l_2_network_cli
                    yield '         '
                    yield str((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli))
                    yield '\n'
                l_2_network = l_2_network_cli = missing
            if t_7(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast')):
                pass
                yield '      !\n      address-family ipv6 multicast\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'bgp'), 'additional_paths'), 'receive'), True):
                    pass
                    yield '         bgp additional-paths receive\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_7(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                    if t_7(environment.getattr(l_2_neighbor, 'route_map_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_in'))
                        yield ' in\n'
                    if t_7(environment.getattr(l_2_neighbor, 'route_map_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_out'))
                        yield ' out\n'
                l_2_neighbor = missing
                for l_2_network in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'networks'), 'prefix'):
                    l_2_network_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_network_cli = str_join(('network ', environment.getattr(l_2_network, 'prefix'), ))
                    _loop_vars['network_cli'] = l_2_network_cli
                    if t_7(environment.getattr(l_2_network, 'route_map')):
                        pass
                        l_2_network_cli = str_join(((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli), ' route-map ', environment.getattr(l_2_network, 'route_map'), ))
                        _loop_vars['network_cli'] = l_2_network_cli
                    yield '         '
                    yield str((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli))
                    yield '\n'
                l_2_network = l_2_network_cli = missing
            for l_2_address_family in t_3(environment.getattr(l_1_vrf, 'address_families'), 'address_family'):
                _loop_vars = {}
                pass
                yield '      !\n      address-family '
                yield str(environment.getattr(l_2_address_family, 'address_family'))
                yield '\n'
                if t_7(environment.getattr(l_2_address_family, 'bgp')):
                    pass
                    if t_7(environment.getattr(environment.getattr(environment.getattr(l_2_address_family, 'bgp'), 'missing_policy'), 'direction_in_action')):
                        pass
                        yield '         bgp missing-policy direction in action '
                        yield str(environment.getattr(environment.getattr(environment.getattr(l_2_address_family, 'bgp'), 'missing_policy'), 'direction_in_action'))
                        yield '\n'
                    if t_7(environment.getattr(environment.getattr(environment.getattr(l_2_address_family, 'bgp'), 'missing_policy'), 'direction_out_action')):
                        pass
                        yield '         bgp missing-policy direction out action '
                        yield str(environment.getattr(environment.getattr(environment.getattr(l_2_address_family, 'bgp'), 'missing_policy'), 'direction_out_action'))
                        yield '\n'
                    for l_3_additional_path in t_3(environment.getattr(environment.getattr(l_2_address_family, 'bgp'), 'additional_paths')):
                        _loop_vars = {}
                        pass
                        yield '         bgp additional-paths '
                        yield str(l_3_additional_path)
                        yield '\n'
                    l_3_additional_path = missing
                for l_3_peer_group in t_3(environment.getattr(l_2_address_family, 'peer_groups'), 'name'):
                    _loop_vars = {}
                    pass
                    if t_7(environment.getattr(l_3_peer_group, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_3_peer_group, 'name'))
                        yield ' activate\n'
                    elif t_7(environment.getattr(l_3_peer_group, 'activate'), False):
                        pass
                        yield '         no neighbor '
                        yield str(environment.getattr(l_3_peer_group, 'name'))
                        yield ' activate\n'
                    if t_7(environment.getattr(environment.getattr(l_3_peer_group, 'next_hop'), 'address_family_ipv6_originate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_3_peer_group, 'name'))
                        yield ' next-hop address-family ipv6 originate\n'
                l_3_peer_group = missing
                for l_3_neighbor in t_3(environment.getattr(l_2_address_family, 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_7(environment.getattr(l_3_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_3_neighbor, 'ip_address'))
                        yield ' activate\n'
                    if t_7(environment.getattr(l_3_neighbor, 'route_map_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_3_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_3_neighbor, 'route_map_in'))
                        yield ' in\n'
                    if t_7(environment.getattr(l_3_neighbor, 'route_map_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_3_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_3_neighbor, 'route_map_out'))
                        yield ' out\n'
                l_3_neighbor = missing
                for l_3_network in t_3(environment.getattr(l_2_address_family, 'networks'), 'prefix'):
                    l_3_network_cli = missing
                    _loop_vars = {}
                    pass
                    l_3_network_cli = str_join(('network ', environment.getattr(l_3_network, 'prefix'), ))
                    _loop_vars['network_cli'] = l_3_network_cli
                    if t_7(environment.getattr(l_3_network, 'route_map')):
                        pass
                        l_3_network_cli = str_join(((undefined(name='network_cli') if l_3_network_cli is missing else l_3_network_cli), ' route-map ', environment.getattr(l_3_network, 'route_map'), ))
                        _loop_vars['network_cli'] = l_3_network_cli
                    yield '         '
                    yield str((undefined(name='network_cli') if l_3_network_cli is missing else l_3_network_cli))
                    yield '\n'
                l_3_network = l_3_network_cli = missing
            l_2_address_family = missing
            if t_7(environment.getattr(l_1_vrf, 'eos_cli')):
                pass
                yield '      !\n      '
                yield str(t_4(environment.getattr(l_1_vrf, 'eos_cli'), 6, False))
                yield '\n'
        l_1_vrf = l_1_tmp_vrf_neighbor_prefix_list_in = l_1_tmp_vrf_neighbor_prefix_list_out = missing
        for l_1_session_tracker in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'session_trackers'), 'name'):
            _loop_vars = {}
            pass
            yield '   session tracker '
            yield str(environment.getattr(l_1_session_tracker, 'name'))
            yield '\n'
            if t_7(environment.getattr(l_1_session_tracker, 'recovery_delay')):
                pass
                yield '      recovery delay '
                yield str(environment.getattr(l_1_session_tracker, 'recovery_delay'))
                yield ' seconds\n'
        l_1_session_tracker = missing

blocks = {}
debug_info = '7=74&9=77&10=79&11=82&13=84&14=86&15=89&16=91&18=95&20=97&21=99&22=102&24=104&25=107&29=110&31=113&32=115&33=118&34=120&38=123&39=125&40=128&41=130&43=134&45=136&46=138&47=141&48=143&50=147&52=149&55=152&58=155&60=158&63=161&65=164&68=167&69=170&71=172&72=176&74=179&77=182&79=184&78=188&80=192&81=194&82=196&84=198&85=200&86=202&87=204&88=206&90=209&93=212&94=215&95=218&98=225&99=236&100=239&102=242&103=244&104=247&106=251&107=254&109=258&110=261&112=263&113=266&115=268&116=271&118=273&119=276&121=278&122=280&123=282&124=284&125=286&126=288&129=291&130=293&131=296&133=298&134=300&135=302&136=304&138=307&139=309&140=312&142=314&143=317&145=321&146=324&148=328&149=331&151=333&152=336&153=338&156=341&159=349&160=351&161=353&162=355&164=358&166=360&167=362&168=364&169=366&171=369&172=371&173=373&174=376&176=378&177=381&179=385&180=388&182=392&183=395&185=399&186=401&187=403&188=405&190=407&191=409&193=412&195=414&196=417&198=419&199=422&201=426&202=429&203=431&204=434&206=438&207=440&208=442&209=444&211=446&212=448&214=451&216=453&217=455&218=457&219=459&221=462&223=464&224=467&226=471&227=474&229=478&230=481&232=485&233=488&236=493&237=496&238=499&239=505&240=508&243=515&244=526&245=529&247=533&248=536&250=540&251=543&253=545&254=548&256=550&257=552&258=554&259=556&260=558&261=560&264=563&265=565&266=568&268=570&269=572&270=574&271=576&273=579&274=581&275=584&277=586&278=589&280=591&281=594&283=596&284=599&286=603&287=606&289=610&290=613&291=615&292=618&294=620&295=623&297=627&298=630&300=634&301=637&303=641&304=644&305=646&308=649&310=657&311=660&313=662&314=664&315=666&316=668&318=671&320=673&321=675&322=677&323=679&325=682&326=684&327=686&328=689&330=691&331=694&333=698&334=701&336=703&337=706&339=710&340=713&342=717&343=720&345=724&346=727&348=731&349=734&351=738&352=740&353=742&354=744&356=746&357=748&359=751&361=753&362=756&363=758&364=761&366=765&367=767&368=769&369=771&371=773&372=775&374=778&376=780&377=782&378=784&379=786&381=789&384=792&385=796&386=798&387=800&389=802&390=804&392=806&393=808&395=810&396=812&398=814&399=816&401=818&402=820&404=822&405=824&407=827&409=830&410=834&411=836&412=838&413=840&414=842&415=844&417=846&418=848&420=851&424=854&426=856&427=859&428=862&430=864&432=868&433=870&434=873&436=875&437=878&439=882&440=886&442=889&443=893&445=896&446=900&448=903&449=907&451=912&452=916&454=921&455=925&457=930&458=934&460=937&461=941&463=944&465=947&470=950&472=954&473=956&474=959&476=961&477=964&479=968&480=972&482=975&483=979&485=982&486=986&488=989&489=993&491=998&492=1002&494=1007&495=1011&497=1016&498=1020&500=1023&501=1027&503=1031&504=1033&506=1036&510=1039&511=1041&513=1045&514=1048&515=1050&516=1053&518=1055&519=1058&521=1060&524=1063&527=1066&528=1069&530=1071&531=1074&533=1077&534=1079&542=1085&545=1088&548=1091&550=1094&551=1096&552=1099&553=1101&555=1104&556=1106&558=1109&559=1111&561=1114&562=1117&565=1119&566=1122&568=1124&569=1126&570=1129&571=1131&573=1135&575=1137&576=1140&577=1143&579=1147&580=1150&582=1154&583=1157&584=1159&585=1162&587=1164&588=1167&590=1169&591=1172&592=1174&593=1177&594=1179&595=1182&596=1184&597=1187&598=1189&599=1192&600=1196&601=1199&603=1203&604=1206&606=1208&607=1211&610=1216&613=1219&614=1221&615=1224&616=1226&618=1230&620=1232&625=1235&628=1238&629=1241&631=1243&632=1246&634=1248&635=1251&636=1254&637=1256&638=1259&641=1262&642=1265&643=1268&648=1271&651=1274&652=1277&654=1279&655=1282&657=1284&658=1287&659=1290&660=1292&661=1295&664=1298&665=1301&666=1304&671=1307&674=1310&675=1313&676=1316&677=1318&678=1321&680=1323&681=1325&682=1328&684=1333&687=1335&688=1338&693=1341&696=1344&697=1349&698=1352&700=1356&701=1359&703=1363&704=1366&706=1370&707=1373&709=1377&710=1379&711=1381&712=1383&714=1385&715=1387&717=1390&719=1392&720=1394&721=1396&722=1398&724=1401&725=1403&726=1406&728=1408&729=1411&730=1413&731=1416&734=1419&735=1423&736=1426&738=1430&739=1433&741=1437&742=1440&744=1444&745=1447&747=1451&748=1453&749=1455&750=1457&752=1459&753=1461&755=1464&757=1466&758=1469&759=1471&760=1474&763=1477&764=1480&765=1483&767=1490&772=1493&775=1496&776=1499&777=1502&779=1506&780=1509&782=1513&783=1516&784=1518&785=1521&788=1524&789=1527&790=1530&792=1534&793=1537&795=1541&796=1544&797=1546&798=1549&801=1552&802=1556&803=1558&804=1560&805=1562&807=1565&812=1568&815=1571&816=1574&817=1577&818=1579&819=1582&821=1584&822=1587&824=1591&825=1594&828=1599&829=1602&830=1605&831=1607&832=1610&834=1612&835=1615&837=1619&838=1622&843=1627&846=1630&847=1633&848=1636&850=1640&851=1643&853=1647&854=1650&856=1654&857=1657&859=1661&860=1664&861=1666&862=1669&865=1672&866=1675&867=1678&869=1682&870=1685&872=1689&873=1692&875=1696&876=1699&878=1703&879=1706&880=1708&881=1711&884=1714&885=1717&886=1720&888=1727&891=1730&892=1734&893=1736&894=1738&895=1740&896=1742&897=1744&899=1746&900=1748&902=1751&907=1754&910=1757&911=1760&913=1762&914=1765&916=1767&919=1770&920=1773&921=1776&922=1778&923=1781&926=1784&927=1787&928=1790&930=1792&931=1795&933=1799&934=1802&937=1807&938=1811&939=1813&940=1815&942=1818&946=1821&949=1824&950=1827&951=1830&952=1832&953=1835&955=1837&956=1840&958=1844&959=1847&962=1852&963=1855&964=1858&965=1860&966=1863&968=1865&969=1868&971=1872&972=1875&977=1880&980=1883&981=1886&983=1888&984=1891&986=1893&987=1896&988=1899&989=1901&990=1904&992=1906&993=1909&995=1913&996=1916&999=1921&1000=1924&1001=1927&1003=1929&1004=1932&1006=1936&1007=1939&1010=1944&1011=1946&1014=1949&1015=1951&1016=1954&1017=1956&1019=1959&1020=1961&1022=1965&1027=1967&1030=1970&1033=1973&1035=1976&1037=1979&1039=1982&1040=1985&1041=1987&1042=1990&1044=1992&1045=1995&1046=1998&1047=2000&1048=2003&1050=2005&1051=2008&1053=2010&1054=2013&1055=2015&1056=2018&1057=2020&1058=2023&1059=2025&1060=2028&1061=2032&1062=2035&1065=2040&1066=2043&1067=2046&1068=2048&1069=2051&1071=2053&1072=2056&1074=2058&1075=2061&1076=2063&1077=2066&1078=2068&1079=2071&1080=2073&1081=2076&1082=2080&1083=2083&1088=2088&1091=2091&1092=2094&1094=2096&1095=2099&1096=2102&1097=2104&1098=2107&1100=2109&1101=2112&1103=2116&1104=2119&1107=2124&1108=2127&1109=2130&1110=2132&1111=2135&1113=2137&1114=2140&1116=2144&1117=2147&1120=2152&1121=2155&1123=2157&1128=2160&1131=2163&1132=2166&1134=2168&1135=2171&1136=2174&1137=2176&1138=2179&1140=2181&1141=2184&1143=2188&1144=2191&1147=2196&1148=2199&1149=2202&1150=2204&1151=2207&1153=2209&1154=2212&1156=2216&1157=2219&1160=2224&1161=2227&1163=2229&1168=2232&1170=2237&1171=2239&1172=2242&1174=2244&1176=2247&1179=2250&1184=2253&1185=2255&1186=2258&1187=2262&1189=2267&1190=2270&1194=2275&1195=2277&1196=2280&1197=2284&1199=2289&1200=2292&1204=2297&1205=2300&1207=2302&1210=2305&1213=2308&1214=2311&1216=2313&1218=2315&1217=2319&1219=2323&1220=2325&1221=2327&1223=2329&1224=2331&1225=2333&1226=2335&1227=2337&1229=2340&1232=2343&1233=2346&1234=2349&1235=2355&1236=2358&1243=2365&1244=2367&1245=2369&1246=2380&1247=2383&1249=2387&1250=2390&1252=2394&1253=2396&1254=2398&1255=2400&1256=2402&1257=2404&1260=2407&1261=2409&1262=2412&1264=2414&1265=2416&1266=2418&1267=2420&1269=2423&1270=2425&1271=2428&1273=2430&1274=2433&1276=2437&1277=2440&1279=2442&1280=2445&1282=2449&1283=2452&1285=2454&1286=2457&1288=2459&1289=2462&1291=2466&1292=2469&1294=2473&1295=2475&1296=2477&1297=2479&1299=2482&1301=2484&1302=2487&1304=2489&1305=2492&1306=2494&1309=2497&1311=2505&1312=2508&1314=2510&1315=2512&1316=2514&1317=2516&1319=2519&1321=2521&1322=2523&1323=2525&1324=2527&1326=2530&1327=2532&1328=2534&1329=2537&1331=2539&1332=2542&1334=2546&1335=2549&1337=2551&1338=2554&1339=2556&1340=2559&1342=2563&1343=2566&1344=2568&1345=2571&1347=2573&1348=2575&1349=2577&1350=2579&1352=2581&1353=2583&1355=2586&1357=2588&1358=2590&1359=2592&1360=2594&1362=2596&1363=2598&1365=2601&1367=2603&1368=2606&1370=2610&1371=2613&1373=2617&1374=2620&1380=2624&1381=2626&1383=2627&1384=2629&1387=2631&1388=2634&1389=2637&1391=2644&1394=2647&1395=2651&1396=2653&1397=2655&1399=2657&1400=2659&1402=2661&1403=2663&1405=2665&1406=2667&1408=2669&1409=2671&1411=2673&1412=2675&1414=2677&1415=2679&1417=2682&1419=2685&1420=2689&1421=2691&1422=2693&1423=2695&1424=2697&1425=2699&1427=2701&1428=2703&1430=2706&1433=2709&1436=2712&1437=2715&1439=2717&1440=2720&1442=2722&1443=2725&1444=2728&1448=2731&1451=2734&1452=2737&1454=2739&1455=2742&1457=2744&1458=2747&1459=2750&1464=2753&1467=2756&1468=2759&1470=2761&1471=2764&1473=2766&1475=2769&1478=2772&1481=2775&1483=2778&1485=2781&1487=2784&1488=2787&1489=2789&1490=2792&1492=2794&1493=2798&1494=2801&1496=2803&1497=2806&1499=2810&1500=2813&1503=2817&1504=2820&1505=2824&1506=2826&1508=2827&1509=2830&1511=2834&1512=2837&1513=2841&1514=2843&1516=2844&1517=2847&1519=2851&1520=2853&1521=2855&1522=2857&1523=2859&1525=2861&1526=2863&1528=2866&1532=2869&1533=2873&1535=2878&1536=2882&1538=2887&1539=2891&1540=2893&1541=2895&1543=2898&1546=2901&1549=2904&1550=2907&1552=2909&1553=2912&1555=2914&1558=2917&1559=2920&1560=2923&1562=2925&1563=2928&1565=2932&1566=2935&1569=2940&1570=2944&1571=2946&1572=2948&1574=2951&1577=2954&1580=2957&1581=2960&1583=2962&1584=2965&1586=2967&1588=2970&1591=2973&1594=2976&1596=2979&1598=2982&1600=2985&1601=2988&1602=2990&1603=2993&1605=2995&1606=2998&1607=3001&1609=3003&1610=3006&1612=3010&1613=3013&1615=3017&1616=3020&1618=3024&1619=3027&1622=3032&1623=3036&1624=3038&1625=3040&1627=3043&1630=3046&1633=3049&1634=3052&1636=3054&1637=3057&1639=3059&1642=3062&1643=3065&1644=3068&1646=3070&1647=3073&1649=3077&1650=3080&1653=3085&1654=3089&1655=3091&1656=3093&1658=3096&1661=3099&1663=3103&1664=3105&1665=3107&1666=3110&1668=3112&1669=3115&1671=3117&1672=3121&1675=3124&1676=3127&1677=3130&1678=3132&1679=3135&1681=3137&1682=3140&1685=3143&1686=3146&1687=3149&1689=3151&1690=3154&1692=3158&1693=3161&1696=3166&1697=3170&1698=3172&1699=3174&1701=3177&1704=3181&1706=3184&1710=3187&1711=3191&1712=3193&1713=3196'