from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/router-msdp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_router_msdp = resolve('router_msdp')
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
    if t_2((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp)):
        pass
        yield '!\nrouter msdp\n'
        for l_1_group_limit in t_1(environment.getattr((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp), 'group_limits'), []):
            _loop_vars = {}
            pass
            yield '   group-limit '
            yield str(environment.getattr(l_1_group_limit, 'limit'))
            yield ' source '
            yield str(environment.getattr(l_1_group_limit, 'source_prefix'))
            yield '\n'
        l_1_group_limit = missing
        if t_2(environment.getattr((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp), 'originator_id_local_interface')):
            pass
            yield '   originator-id local-interface '
            yield str(environment.getattr((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp), 'originator_id_local_interface'))
            yield '\n'
        if t_2(environment.getattr((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp), 'rejected_limit')):
            pass
            yield '   rejected-limit '
            yield str(environment.getattr((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp), 'rejected_limit'))
            yield '\n'
        if t_2(environment.getattr((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp), 'forward_register_packets'), True):
            pass
            yield '   forward register-packets\n'
        if t_2(environment.getattr((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp), 'connection_retry_interval')):
            pass
            yield '   connection retry interval '
            yield str(environment.getattr((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp), 'connection_retry_interval'))
            yield '\n'
        for l_1_peer in t_1(environment.getattr((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp), 'peers'), []):
            l_1_default_peer_cli = resolve('default_peer_cli')
            _loop_vars = {}
            pass
            if t_2(environment.getattr(l_1_peer, 'ipv4_address')):
                pass
                yield '   !\n   peer '
                yield str(environment.getattr(l_1_peer, 'ipv4_address'))
                yield '\n'
                if t_2(environment.getattr(environment.getattr(l_1_peer, 'default_peer'), 'enabled'), True):
                    pass
                    l_1_default_peer_cli = 'default-peer'
                    _loop_vars['default_peer_cli'] = l_1_default_peer_cli
                    if t_2(environment.getattr(environment.getattr(l_1_peer, 'default_peer'), 'prefix_list')):
                        pass
                        l_1_default_peer_cli = str_join(((undefined(name='default_peer_cli') if l_1_default_peer_cli is missing else l_1_default_peer_cli), ' prefix-list ', environment.getattr(environment.getattr(l_1_peer, 'default_peer'), 'prefix_list'), ))
                        _loop_vars['default_peer_cli'] = l_1_default_peer_cli
                    yield '      '
                    yield str((undefined(name='default_peer_cli') if l_1_default_peer_cli is missing else l_1_default_peer_cli))
                    yield '\n'
                for l_2_mesh_group in t_1(environment.getattr(l_1_peer, 'mesh_groups'), []):
                    _loop_vars = {}
                    pass
                    if t_2(environment.getattr(l_2_mesh_group, 'name')):
                        pass
                        yield '      mesh-group '
                        yield str(environment.getattr(l_2_mesh_group, 'name'))
                        yield '\n'
                l_2_mesh_group = missing
                if t_2(environment.getattr(l_1_peer, 'local_interface')):
                    pass
                    yield '      local-interface '
                    yield str(environment.getattr(l_1_peer, 'local_interface'))
                    yield '\n'
                if (t_2(environment.getattr(environment.getattr(l_1_peer, 'keepalive'), 'keepalive_timer')) and t_2(environment.getattr(environment.getattr(l_1_peer, 'keepalive'), 'hold_timer'))):
                    pass
                    yield '      keepalive '
                    yield str(environment.getattr(environment.getattr(l_1_peer, 'keepalive'), 'keepalive_timer'))
                    yield ' '
                    yield str(environment.getattr(environment.getattr(l_1_peer, 'keepalive'), 'hold_timer'))
                    yield '\n'
                if t_2(environment.getattr(environment.getattr(l_1_peer, 'sa_filter'), 'in_list')):
                    pass
                    yield '      sa-filter in list '
                    yield str(environment.getattr(environment.getattr(l_1_peer, 'sa_filter'), 'in_list'))
                    yield '\n'
                if t_2(environment.getattr(environment.getattr(l_1_peer, 'sa_filter'), 'out_list')):
                    pass
                    yield '      sa-filter out list '
                    yield str(environment.getattr(environment.getattr(l_1_peer, 'sa_filter'), 'in_list'))
                    yield '\n'
                if t_2(environment.getattr(l_1_peer, 'description')):
                    pass
                    yield '      description '
                    yield str(environment.getattr(l_1_peer, 'description'))
                    yield '\n'
                if t_2(environment.getattr(l_1_peer, 'disabled'), True):
                    pass
                    yield '      disabled\n'
                if t_2(environment.getattr(l_1_peer, 'sa_limit')):
                    pass
                    yield '      sa-limit '
                    yield str(environment.getattr(l_1_peer, 'sa_limit'))
                    yield '\n'
        l_1_peer = l_1_default_peer_cli = missing
        for l_1_vrf in t_1(environment.getattr((undefined(name='router_msdp') if l_0_router_msdp is missing else l_0_router_msdp), 'vrfs'), []):
            _loop_vars = {}
            pass
            if (t_2(environment.getattr(l_1_vrf, 'name')) and (environment.getattr(l_1_vrf, 'name') != 'default')):
                pass
                yield '   !\n   vrf '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield '\n'
                for l_2_group_limit in t_1(environment.getattr(l_1_vrf, 'group_limits'), []):
                    _loop_vars = {}
                    pass
                    yield '      group-limit '
                    yield str(environment.getattr(l_2_group_limit, 'limit'))
                    yield ' source '
                    yield str(environment.getattr(l_2_group_limit, 'source_prefix'))
                    yield '\n'
                l_2_group_limit = missing
                if t_2(environment.getattr(l_1_vrf, 'originator_id_local_interface')):
                    pass
                    yield '      originator-id local-interface '
                    yield str(environment.getattr(l_1_vrf, 'originator_id_local_interface'))
                    yield '\n'
                if t_2(environment.getattr(l_1_vrf, 'rejected_limit')):
                    pass
                    yield '      rejected-limit '
                    yield str(environment.getattr(l_1_vrf, 'rejected_limit'))
                    yield '\n'
                if t_2(environment.getattr(l_1_vrf, 'forward_register_packets'), True):
                    pass
                    yield '      forward register-packets\n'
                if t_2(environment.getattr(l_1_vrf, 'connection_retry_interval')):
                    pass
                    yield '      connection retry interval '
                    yield str(environment.getattr(l_1_vrf, 'connection_retry_interval'))
                    yield '\n'
                for l_2_peer in t_1(environment.getattr(l_1_vrf, 'peers'), []):
                    l_2_default_peer_cli = resolve('default_peer_cli')
                    _loop_vars = {}
                    pass
                    if t_2(environment.getattr(l_2_peer, 'ipv4_address')):
                        pass
                        yield '      !\n      peer '
                        yield str(environment.getattr(l_2_peer, 'ipv4_address'))
                        yield '\n'
                        if t_2(environment.getattr(environment.getattr(l_2_peer, 'default_peer'), 'enabled'), True):
                            pass
                            l_2_default_peer_cli = 'default-peer'
                            _loop_vars['default_peer_cli'] = l_2_default_peer_cli
                            if t_2(environment.getattr(environment.getattr(l_2_peer, 'default_peer'), 'prefix_list')):
                                pass
                                l_2_default_peer_cli = str_join(((undefined(name='default_peer_cli') if l_2_default_peer_cli is missing else l_2_default_peer_cli), ' prefix-list ', environment.getattr(environment.getattr(l_2_peer, 'default_peer'), 'prefix_list'), ))
                                _loop_vars['default_peer_cli'] = l_2_default_peer_cli
                            yield '         '
                            yield str((undefined(name='default_peer_cli') if l_2_default_peer_cli is missing else l_2_default_peer_cli))
                            yield '\n'
                        for l_3_mesh_group in t_1(environment.getattr(l_2_peer, 'mesh_groups'), []):
                            _loop_vars = {}
                            pass
                            if t_2(environment.getattr(l_3_mesh_group, 'name')):
                                pass
                                yield '         mesh-group '
                                yield str(environment.getattr(l_3_mesh_group, 'name'))
                                yield '\n'
                        l_3_mesh_group = missing
                        if t_2(environment.getattr(l_2_peer, 'local_interface')):
                            pass
                            yield '         local-interface '
                            yield str(environment.getattr(l_2_peer, 'local_interface'))
                            yield '\n'
                        if (t_2(environment.getattr(environment.getattr(l_2_peer, 'keepalive'), 'keepalive_timer')) and t_2(environment.getattr(environment.getattr(l_2_peer, 'keepalive'), 'hold_timer'))):
                            pass
                            yield '         keepalive '
                            yield str(environment.getattr(environment.getattr(l_2_peer, 'keepalive'), 'keepalive_timer'))
                            yield ' '
                            yield str(environment.getattr(environment.getattr(l_2_peer, 'keepalive'), 'hold_timer'))
                            yield '\n'
                        if t_2(environment.getattr(environment.getattr(l_2_peer, 'sa_filter'), 'in_list')):
                            pass
                            yield '         sa-filter in list '
                            yield str(environment.getattr(environment.getattr(l_2_peer, 'sa_filter'), 'in_list'))
                            yield '\n'
                        if t_2(environment.getattr(environment.getattr(l_2_peer, 'sa_filter'), 'out_list')):
                            pass
                            yield '         sa-filter out list '
                            yield str(environment.getattr(environment.getattr(l_2_peer, 'sa_filter'), 'in_list'))
                            yield '\n'
                        if t_2(environment.getattr(l_2_peer, 'description')):
                            pass
                            yield '         description '
                            yield str(environment.getattr(l_2_peer, 'description'))
                            yield '\n'
                        if t_2(environment.getattr(l_2_peer, 'disabled'), True):
                            pass
                            yield '         disabled\n'
                        if t_2(environment.getattr(l_2_peer, 'sa_limit')):
                            pass
                            yield '         sa-limit '
                            yield str(environment.getattr(l_2_peer, 'sa_limit'))
                            yield '\n'
                l_2_peer = l_2_default_peer_cli = missing
        l_1_vrf = missing

blocks = {}
debug_info = '7=24&10=27&11=31&13=36&14=39&16=41&17=44&19=46&22=49&23=52&25=54&26=58&28=61&29=63&30=65&31=67&32=69&34=72&36=74&37=77&38=80&41=83&42=86&44=88&45=91&47=95&48=98&50=100&51=103&53=105&54=108&56=110&59=113&60=116&64=119&65=122&67=125&68=127&69=131&71=136&72=139&74=141&75=144&77=146&80=149&81=152&83=154&84=158&86=161&87=163&88=165&89=167&90=169&92=172&94=174&95=177&96=180&99=183&100=186&102=188&103=191&105=195&106=198&108=200&109=203&111=205&112=208&114=210&117=213&118=216'