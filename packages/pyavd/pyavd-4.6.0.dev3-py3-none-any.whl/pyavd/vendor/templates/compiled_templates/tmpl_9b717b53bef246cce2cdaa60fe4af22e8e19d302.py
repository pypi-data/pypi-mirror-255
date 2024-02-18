from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/vxlan-interface.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_vxlan_interface = resolve('vxlan_interface')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['indent']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'indent' found.")
    try:
        t_3 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_4 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_4(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1')):
        pass
        yield '!\ninterface Vxlan1\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'description')):
            pass
            yield '   description '
            yield str(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'description'))
            yield '\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'source_interface')):
            pass
            yield '   vxlan source-interface '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'source_interface'))
            yield '\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'controller_client'), 'enabled'), True):
            pass
            yield '   vxlan controller-client\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'virtual_router_encapsulation_mac_address')):
            pass
            yield '   vxlan virtual-router encapsulation mac-address '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'virtual_router_encapsulation_mac_address'))
            yield '\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'udp_port')):
            pass
            yield '   vxlan udp-port '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'udp_port'))
            yield '\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'flood_vtep_learned_data_plane'), True):
            pass
            yield '   vxlan flood vtep learned data-plane\n'
        for l_1_vlan in t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'vlans'), 'id'):
            _loop_vars = {}
            pass
            if t_4(environment.getattr(l_1_vlan, 'vni')):
                pass
                yield '   vxlan vlan '
                yield str(environment.getattr(l_1_vlan, 'id'))
                yield ' vni '
                yield str(environment.getattr(l_1_vlan, 'vni'))
                yield '\n'
            if t_4(environment.getattr(l_1_vlan, 'flood_vteps')):
                pass
                yield '   vxlan vlan '
                yield str(environment.getattr(l_1_vlan, 'id'))
                yield ' flood vtep '
                yield str(t_3(context.eval_ctx, environment.getattr(l_1_vlan, 'flood_vteps'), ' '))
                yield '\n'
        l_1_vlan = missing
        for l_1_vrf in t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'vrfs'), 'name'):
            _loop_vars = {}
            pass
            if t_4(environment.getattr(l_1_vrf, 'vni')):
                pass
                yield '   vxlan vrf '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield ' vni '
                yield str(environment.getattr(l_1_vrf, 'vni'))
                yield '\n'
        l_1_vrf = missing
        if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'mlag_source_interface')):
            pass
            yield '   vxlan mlag source-interface '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'mlag_source_interface'))
            yield '\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'bfd_vtep_evpn')):
            pass
            if ((t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'bfd_vtep_evpn'), 'interval')) and t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'bfd_vtep_evpn'), 'min_rx'))) and t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'bfd_vtep_evpn'), 'multiplier'))):
                pass
                yield '   bfd vtep evpn interval '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'bfd_vtep_evpn'), 'interval'))
                yield ' min-rx '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'bfd_vtep_evpn'), 'min_rx'))
                yield ' multiplier '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'bfd_vtep_evpn'), 'multiplier'))
                yield '\n'
            if t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'bfd_vtep_evpn'), 'prefix_list')):
                pass
                yield '   bfd vtep evpn prefix-list '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'bfd_vtep_evpn'), 'prefix_list'))
                yield '\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'flood_vteps')):
            pass
            yield '   vxlan flood vtep '
            yield str(t_3(context.eval_ctx, environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'flood_vteps'), ' '))
            yield '\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'qos'), 'dscp_propagation_encapsulation'), True):
            pass
            yield '   vxlan qos dscp propagation encapsulation\n'
        elif t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'qos'), 'dscp_propagation_encapsulation'), False):
            pass
            yield '   no vxlan qos dscp propagation encapsulation\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'qos'), 'ecn_propagation'), True):
            pass
            yield '   vxlan qos ecn propagation\n'
        elif t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'qos'), 'ecn_propagation'), False):
            pass
            yield '   no vxlan qos ecn propagation\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'qos'), 'map_dscp_to_traffic_class_decapsulation'), True):
            pass
            yield '   vxlan qos map dscp to traffic-class decapsulation\n'
        elif t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'qos'), 'map_dscp_to_traffic_class_decapsulation'), False):
            pass
            yield '   no vxlan qos map dscp to traffic-class decapsulation\n'
        def t_5(fiter):
            for l_1_vlan in fiter:
                if t_4(environment.getattr(l_1_vlan, 'multicast_group')):
                    yield l_1_vlan
        for l_1_vlan in t_5(t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'vlans'), 'id')):
            _loop_vars = {}
            pass
            yield '   vxlan vlan '
            yield str(environment.getattr(l_1_vlan, 'id'))
            yield ' multicast group '
            yield str(environment.getattr(l_1_vlan, 'multicast_group'))
            yield '\n'
        l_1_vlan = missing
        def t_6(fiter):
            for l_1_vrf in fiter:
                if t_4(environment.getattr(l_1_vrf, 'multicast_group')):
                    yield l_1_vrf
        for l_1_vrf in t_6(t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'vrfs'), 'name')):
            _loop_vars = {}
            pass
            yield '   vxlan vrf '
            yield str(environment.getattr(l_1_vrf, 'name'))
            yield ' multicast group '
            yield str(environment.getattr(l_1_vrf, 'multicast_group'))
            yield '\n'
        l_1_vrf = missing
        if t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'vxlan'), 'multicast'), 'headend_replication'), True):
            pass
            yield '   vxlan multicast headend-replication\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'eos_cli')):
            pass
            yield '   '
            yield str(t_2(environment.getattr(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'), 'eos_cli'), 3, False))
            yield '\n'

blocks = {}
debug_info = '8=36&11=39&12=42&14=44&15=47&17=49&20=52&21=55&23=57&24=60&26=62&29=65&30=68&31=71&33=75&34=78&37=83&38=86&39=89&42=94&43=97&45=99&46=101&49=104&51=110&52=113&55=115&56=118&58=120&60=123&63=126&65=129&68=132&70=135&73=138&74=146&76=151&77=159&79=164&82=167&83=170'