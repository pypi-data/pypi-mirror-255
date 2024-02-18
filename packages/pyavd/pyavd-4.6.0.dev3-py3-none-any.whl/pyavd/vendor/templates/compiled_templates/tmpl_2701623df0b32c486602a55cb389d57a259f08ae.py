from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/management-api-gnmi.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_management_api_gnmi = resolve('management_api_gnmi')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    try:
        t_4 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    if t_3((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi)):
        pass
        yield '!\nmanagement api gnmi\n'
        for l_1_vrf in t_1(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'enable_vrfs')):
            _loop_vars = {}
            pass
            if (environment.getattr(l_1_vrf, 'name') == 'default'):
                pass
                yield '   transport grpc default\n'
            else:
                pass
                yield '   transport grpc '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield '\n'
                if t_3(environment.getattr(l_1_vrf, 'access_group')):
                    pass
                    yield '      ip access-group '
                    yield str(environment.getattr(l_1_vrf, 'access_group'))
                    yield '\n'
                yield '      vrf '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield '\n'
        l_1_vrf = missing
        if t_4(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'octa')):
            pass
            yield '   provider eos-native\n'
        if t_3(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'transport')):
            pass
            if t_3(environment.getattr(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'transport'), 'grpc')):
                pass
                for l_1_transport in environment.getattr(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'transport'), 'grpc'):
                    _loop_vars = {}
                    pass
                    if t_3(environment.getattr(l_1_transport, 'name')):
                        pass
                        yield '   transport grpc '
                        yield str(environment.getattr(l_1_transport, 'name'))
                        yield '\n'
                        if t_3(environment.getattr(l_1_transport, 'ssl_profile')):
                            pass
                            yield '      ssl profile '
                            yield str(environment.getattr(l_1_transport, 'ssl_profile'))
                            yield '\n'
                        if t_3(environment.getattr(l_1_transport, 'port')):
                            pass
                            yield '      port '
                            yield str(environment.getattr(l_1_transport, 'port'))
                            yield '\n'
                        if t_3(environment.getattr(l_1_transport, 'vrf')):
                            pass
                            yield '      vrf '
                            yield str(environment.getattr(l_1_transport, 'vrf'))
                            yield '\n'
                        if t_3(environment.getattr(l_1_transport, 'ip_access_group')):
                            pass
                            yield '      ip access-group '
                            yield str(environment.getattr(l_1_transport, 'ip_access_group'))
                            yield '\n'
                        if t_3(environment.getattr(l_1_transport, 'notification_timestamp')):
                            pass
                            yield '      notification timestamp '
                            yield str(environment.getattr(l_1_transport, 'notification_timestamp'))
                            yield '\n'
                l_1_transport = missing
            if t_3(environment.getattr(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'transport'), 'grpc_tunnels')):
                pass
                for l_1_transport in environment.getattr(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'transport'), 'grpc_tunnels'):
                    _loop_vars = {}
                    pass
                    yield '   transport grpc-tunnel '
                    yield str(environment.getattr(l_1_transport, 'name'))
                    yield '\n'
                    if t_3(environment.getattr(l_1_transport, 'shutdown'), True):
                        pass
                        yield '      shutdown\n'
                    elif t_3(environment.getattr(l_1_transport, 'shutdown'), False):
                        pass
                        yield '      no shutdown\n'
                    if t_3(environment.getattr(l_1_transport, 'vrf')):
                        pass
                        yield '      vrf '
                        yield str(environment.getattr(l_1_transport, 'vrf'))
                        yield '\n'
                    if t_3(environment.getattr(l_1_transport, 'tunnel_ssl_profile')):
                        pass
                        yield '      tunnel ssl profile '
                        yield str(environment.getattr(l_1_transport, 'tunnel_ssl_profile'))
                        yield '\n'
                    if t_3(environment.getattr(l_1_transport, 'gnmi_ssl_profile')):
                        pass
                        yield '      gnmi ssl profile '
                        yield str(environment.getattr(l_1_transport, 'gnmi_ssl_profile'))
                        yield '\n'
                    if t_3(environment.getattr(l_1_transport, 'destination')):
                        pass
                        yield '      destination '
                        yield str(environment.getattr(environment.getattr(l_1_transport, 'destination'), 'address'))
                        yield ' port '
                        yield str(environment.getattr(environment.getattr(l_1_transport, 'destination'), 'port'))
                        yield '\n'
                    if t_3(environment.getattr(l_1_transport, 'local_interface')):
                        pass
                        yield '      local interface '
                        yield str(environment.getattr(environment.getattr(l_1_transport, 'local_interface'), 'name'))
                        yield ' port '
                        yield str(environment.getattr(environment.getattr(l_1_transport, 'local_interface'), 'port'))
                        yield '\n'
                    if t_3(environment.getattr(environment.getattr(l_1_transport, 'target'), 'use_serial_number'), True):
                        pass
                        if t_3(environment.getattr(environment.getattr(l_1_transport, 'target'), 'target_ids')):
                            pass
                            yield '      target serial-number '
                            yield str(t_2(context.eval_ctx, environment.getattr(environment.getattr(l_1_transport, 'target'), 'target_ids'), ' '))
                            yield '\n'
                        else:
                            pass
                            yield '      target serial-number\n'
                    elif t_3(environment.getattr(environment.getattr(l_1_transport, 'target'), 'target_ids')):
                        pass
                        yield '      target '
                        yield str(t_2(context.eval_ctx, environment.getattr(environment.getattr(l_1_transport, 'target'), 'target_ids'), ' '))
                        yield '\n'
                l_1_transport = missing
        if t_3(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'provider')):
            pass
            yield '   provider '
            yield str(environment.getattr((undefined(name='management_api_gnmi') if l_0_management_api_gnmi is missing else l_0_management_api_gnmi), 'provider'))
            yield '\n'

blocks = {}
debug_info = '7=36&10=39&11=42&14=48&15=50&16=53&18=56&21=59&24=62&25=64&26=66&27=69&28=72&29=74&30=77&32=79&33=82&35=84&36=87&38=89&39=92&41=94&42=97&47=100&48=102&49=106&50=108&52=111&55=114&56=117&58=119&59=122&61=124&62=127&64=129&65=132&67=136&68=139&70=143&71=145&72=148&76=153&77=156&82=159&83=162'