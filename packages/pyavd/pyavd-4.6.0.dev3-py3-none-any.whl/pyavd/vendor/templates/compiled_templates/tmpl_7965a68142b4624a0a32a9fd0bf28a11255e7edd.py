from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/management-api-gnmi.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_management_api_gnmi = resolve('management_api_gnmi')
    l_0_octa = resolve('octa')
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
        t_4 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    try:
        t_5 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    if t_4((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi)):
        pass
        yield '\n### Management API gNMI\n\n#### Management API gNMI Summary\n'
        if t_5(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'enable_vrfs')):
            pass
            if t_5(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'octa')):
                pass
                l_0_octa = 'enabled'
                context.vars['octa'] = l_0_octa
                context.exported_vars.add('octa')
            else:
                pass
                l_0_octa = 'disabled'
                context.vars['octa'] = l_0_octa
                context.exported_vars.add('octa')
            yield '\n| VRF with gNMI | OCTA |\n| ------------- | ---- |\n'
            for l_1_vrf in t_2(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'enable_vrfs')):
                _loop_vars = {}
                pass
                yield '| '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield ' | '
                yield str((undefined(name='octa') if l_0_octa is missing else l_0_octa))
                yield ' |\n'
            l_1_vrf = missing
        if t_4(environment.getattr(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'transport'), 'grpc')):
            pass
            yield '\n| Transport | SSL Profile | VRF | Notification Timestamp | ACL | Port |\n| --------- | ----------- | --- | ---------------------- | --- | ---- |\n'
            for l_1_transport in environment.getattr(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'transport'), 'grpc'):
                l_1_transport_name = resolve('transport_name')
                l_1_ssl_profile = resolve('ssl_profile')
                l_1_vrf = resolve('vrf')
                l_1_notif = resolve('notif')
                l_1_acl = resolve('acl')
                l_1_port = resolve('port')
                _loop_vars = {}
                pass
                if t_4(environment.getattr(l_1_transport, 'name')):
                    pass
                    l_1_transport_name = environment.getattr(l_1_transport, 'name')
                    _loop_vars['transport_name'] = l_1_transport_name
                    l_1_ssl_profile = t_1(environment.getattr(l_1_transport, 'ssl_profile'), '-')
                    _loop_vars['ssl_profile'] = l_1_ssl_profile
                    l_1_vrf = t_1(environment.getattr(l_1_transport, 'vrf'), '-')
                    _loop_vars['vrf'] = l_1_vrf
                    l_1_notif = t_1(environment.getattr(l_1_transport, 'notification_timestamp'), 'last-change-time')
                    _loop_vars['notif'] = l_1_notif
                    l_1_acl = t_1(environment.getattr(l_1_transport, 'ip_access_group'), '-')
                    _loop_vars['acl'] = l_1_acl
                    l_1_port = t_1(environment.getattr(l_1_transport, 'port'), '6030')
                    _loop_vars['port'] = l_1_port
                    yield '| '
                    yield str((undefined(name='transport_name') if l_1_transport_name is missing else l_1_transport_name))
                    yield ' | '
                    yield str((undefined(name='ssl_profile') if l_1_ssl_profile is missing else l_1_ssl_profile))
                    yield ' | '
                    yield str((undefined(name='vrf') if l_1_vrf is missing else l_1_vrf))
                    yield ' | '
                    yield str((undefined(name='notif') if l_1_notif is missing else l_1_notif))
                    yield ' | '
                    yield str((undefined(name='acl') if l_1_acl is missing else l_1_acl))
                    yield ' | '
                    yield str((undefined(name='port') if l_1_port is missing else l_1_port))
                    yield ' |\n'
            l_1_transport = l_1_transport_name = l_1_ssl_profile = l_1_vrf = l_1_notif = l_1_acl = l_1_port = missing
        if t_4(environment.getattr(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'transport'), 'grpc_tunnels')):
            pass
            yield '\n| Transport | Destination | Destination Port | gNMI SSL Profile | Tunnel SSL Profile | VRF | Local Interface | Local Port | Target ID |\n| --------- | ----------- | ---------------- | ---------------- | ------------------ | --- | --------------- | ---------- | --------- |\n'
            for l_1_transport in environment.getattr(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'transport'), 'grpc_tunnels'):
                l_1_transport_name = l_1_destination = l_1_port = l_1_gnmi_ssl_profile = l_1_tunnel_ssl_profile = l_1_vrf = l_1_local_interface = l_1_local_port = l_1_target_ids = l_1_target_id = missing
                _loop_vars = {}
                pass
                l_1_transport_name = environment.getattr(l_1_transport, 'name')
                _loop_vars['transport_name'] = l_1_transport_name
                l_1_destination = t_1(environment.getattr(environment.getattr(l_1_transport, 'destination'), 'address'), '-')
                _loop_vars['destination'] = l_1_destination
                l_1_port = t_1(environment.getattr(environment.getattr(l_1_transport, 'destination'), 'port'), '-')
                _loop_vars['port'] = l_1_port
                l_1_gnmi_ssl_profile = t_1(environment.getattr(l_1_transport, 'gnmi_ssl_profile'), '-')
                _loop_vars['gnmi_ssl_profile'] = l_1_gnmi_ssl_profile
                l_1_tunnel_ssl_profile = t_1(environment.getattr(l_1_transport, 'tunnel_ssl_profile'), '-')
                _loop_vars['tunnel_ssl_profile'] = l_1_tunnel_ssl_profile
                l_1_vrf = t_1(environment.getattr(l_1_transport, 'vrf'), '-')
                _loop_vars['vrf'] = l_1_vrf
                l_1_local_interface = t_1(environment.getattr(environment.getattr(l_1_transport, 'local_interface'), 'name'), '-')
                _loop_vars['local_interface'] = l_1_local_interface
                l_1_local_port = t_1(environment.getattr(environment.getattr(l_1_transport, 'local_interface'), 'port'), '-')
                _loop_vars['local_port'] = l_1_local_port
                l_1_target_ids = []
                _loop_vars['target_ids'] = l_1_target_ids
                if t_4(environment.getattr(environment.getattr(l_1_transport, 'target'), 'use_serial_number'), True):
                    pass
                    context.call(environment.getattr((undefined(name='target_ids') if l_1_target_ids is missing else l_1_target_ids), 'append'), 'Serial-Number', _loop_vars=_loop_vars)
                context.call(environment.getattr((undefined(name='target_ids') if l_1_target_ids is missing else l_1_target_ids), 'extend'), t_1(environment.getattr(environment.getattr(l_1_transport, 'target'), 'target_ids'), []), _loop_vars=_loop_vars)
                l_1_target_id = t_1(t_3(context.eval_ctx, (undefined(name='target_ids') if l_1_target_ids is missing else l_1_target_ids), ' '), '-')
                _loop_vars['target_id'] = l_1_target_id
                yield '| '
                yield str((undefined(name='transport_name') if l_1_transport_name is missing else l_1_transport_name))
                yield ' | '
                yield str((undefined(name='destination') if l_1_destination is missing else l_1_destination))
                yield ' | '
                yield str((undefined(name='port') if l_1_port is missing else l_1_port))
                yield ' | '
                yield str((undefined(name='gnmi_ssl_profile') if l_1_gnmi_ssl_profile is missing else l_1_gnmi_ssl_profile))
                yield ' | '
                yield str((undefined(name='tunnel_ssl_profile') if l_1_tunnel_ssl_profile is missing else l_1_tunnel_ssl_profile))
                yield ' | '
                yield str((undefined(name='vrf') if l_1_vrf is missing else l_1_vrf))
                yield ' | '
                yield str((undefined(name='local_interface') if l_1_local_interface is missing else l_1_local_interface))
                yield ' | '
                yield str((undefined(name='local_port') if l_1_local_port is missing else l_1_local_port))
                yield ' | '
                yield str((undefined(name='target_id') if l_1_target_id is missing else l_1_target_id))
                yield ' |\n'
            l_1_transport = l_1_transport_name = l_1_destination = l_1_port = l_1_gnmi_ssl_profile = l_1_tunnel_ssl_profile = l_1_vrf = l_1_local_interface = l_1_local_port = l_1_target_ids = l_1_target_id = missing
        if t_4(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'provider')):
            pass
            yield '\nProvider '
            yield str(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'provider'))
            yield ' is configured.\n'
        yield '\n#### Management API gNMI Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/management-api-gnmi.j2', 'documentation/management-api-gnmi.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {'octa': l_0_octa})):
            yield event
        yield '```\n'

blocks = {}
debug_info = '7=43&13=46&14=48&15=50&17=55&22=59&23=63&27=68&31=71&32=80&33=82&34=84&35=86&36=88&37=90&38=92&39=95&43=108&47=111&48=115&49=117&50=119&51=121&52=123&53=125&54=127&55=129&56=131&57=133&58=135&60=136&61=137&62=140&65=159&67=162&73=165'