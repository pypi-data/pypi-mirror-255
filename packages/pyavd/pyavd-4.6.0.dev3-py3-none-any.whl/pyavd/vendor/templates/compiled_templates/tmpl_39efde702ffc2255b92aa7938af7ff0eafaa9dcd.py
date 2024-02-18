from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/dhcp-servers.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_dhcp_servers = resolve('dhcp_servers')
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
        t_5 = environment.tests['true']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No test named 'true' found.")
    pass
    if t_4((undefined(name='dhcp_servers') if l_0_dhcp_servers is missing else l_0_dhcp_servers)):
        pass
        for l_1_dhcp_server in t_2((undefined(name='dhcp_servers') if l_0_dhcp_servers is missing else l_0_dhcp_servers), 'vrf'):
            l_1_server_cli = missing
            _loop_vars = {}
            pass
            l_1_server_cli = 'dhcp server'
            _loop_vars['server_cli'] = l_1_server_cli
            if (environment.getattr(l_1_dhcp_server, 'vrf') != 'default'):
                pass
                l_1_server_cli = str_join(((undefined(name='server_cli') if l_1_server_cli is missing else l_1_server_cli), ' vrf ', environment.getattr(l_1_dhcp_server, 'vrf'), ))
                _loop_vars['server_cli'] = l_1_server_cli
            yield '!\n'
            yield str((undefined(name='server_cli') if l_1_server_cli is missing else l_1_server_cli))
            yield '\n'
            if t_4(environment.getattr(l_1_dhcp_server, 'dns_domain_name_ipv4')):
                pass
                yield '   dns domain name ipv4 '
                yield str(environment.getattr(l_1_dhcp_server, 'dns_domain_name_ipv4'))
                yield '\n'
            if t_4(environment.getattr(l_1_dhcp_server, 'dns_domain_name_ipv6')):
                pass
                yield '   dns domain name ipv6 '
                yield str(environment.getattr(l_1_dhcp_server, 'dns_domain_name_ipv6'))
                yield '\n'
            for l_2_subnet in t_2(environment.getattr(l_1_dhcp_server, 'subnets')):
                _loop_vars = {}
                pass
                yield '   !\n   subnet '
                yield str(environment.getattr(l_2_subnet, 'subnet'))
                yield '\n'
                for l_3_range in t_2(t_2(environment.getattr(l_2_subnet, 'ranges'), 'end'), 'start'):
                    _loop_vars = {}
                    pass
                    yield '      !\n      range '
                    yield str(environment.getattr(l_3_range, 'start'))
                    yield ' '
                    yield str(environment.getattr(l_3_range, 'end'))
                    yield '\n'
                l_3_range = missing
                if t_4(environment.getattr(l_2_subnet, 'name')):
                    pass
                    yield '      name '
                    yield str(environment.getattr(l_2_subnet, 'name'))
                    yield '\n'
                if t_4(environment.getattr(l_2_subnet, 'dns_servers')):
                    pass
                    yield '      dns server '
                    yield str(t_3(context.eval_ctx, environment.getattr(l_2_subnet, 'dns_servers'), ' '))
                    yield '\n'
                if t_4(environment.getattr(l_2_subnet, 'lease_time')):
                    pass
                    yield '      lease time '
                    yield str(environment.getattr(environment.getattr(l_2_subnet, 'lease_time'), 'days'))
                    yield ' days '
                    yield str(environment.getattr(environment.getattr(l_2_subnet, 'lease_time'), 'hours'))
                    yield ' hours '
                    yield str(environment.getattr(environment.getattr(l_2_subnet, 'lease_time'), 'minutes'))
                    yield ' minutes\n'
                if t_4(environment.getattr(l_2_subnet, 'default_gateway')):
                    pass
                    yield '      default-gateway '
                    yield str(environment.getattr(l_2_subnet, 'default_gateway'))
                    yield '\n'
            l_2_subnet = missing
            if t_5(t_1(environment.getattr(l_1_dhcp_server, 'disabled'), False)):
                pass
                yield '   disabled\n'
            for l_2_option in t_2(environment.getattr(l_1_dhcp_server, 'ipv4_vendor_options'), 'vendor_id'):
                _loop_vars = {}
                pass
                yield '   !\n   vendor-option ipv4 '
                yield str(environment.getattr(l_2_option, 'vendor_id'))
                yield '\n'
                for l_3_sub_option in t_2(environment.getattr(l_2_option, 'sub_options')):
                    _loop_vars = {}
                    pass
                    if t_4(environment.getattr(l_3_sub_option, 'string')):
                        pass
                        yield '      sub-option '
                        yield str(environment.getattr(l_3_sub_option, 'code'))
                        yield ' type string data "'
                        yield str(environment.getattr(l_3_sub_option, 'string'))
                        yield '"\n'
                    elif t_4(environment.getattr(l_3_sub_option, 'ipv4_address')):
                        pass
                        yield '      sub-option '
                        yield str(environment.getattr(l_3_sub_option, 'code'))
                        yield ' type ipv4-address data '
                        yield str(environment.getattr(l_3_sub_option, 'ipv4_address'))
                        yield '\n'
                    elif t_4(environment.getattr(l_3_sub_option, 'array_ipv4_address')):
                        pass
                        yield '      sub-option '
                        yield str(environment.getattr(l_3_sub_option, 'code'))
                        yield ' type array ipv4-address data '
                        yield str(t_3(context.eval_ctx, environment.getattr(l_3_sub_option, 'array_ipv4_address'), ' '))
                        yield '\n'
                l_3_sub_option = missing
            l_2_option = missing
        l_1_dhcp_server = l_1_server_cli = missing

blocks = {}
debug_info = '7=42&8=44&9=48&10=50&11=52&14=55&15=57&16=60&18=62&19=65&21=67&23=71&24=73&26=77&28=82&29=85&31=87&32=90&34=92&35=95&37=101&38=104&41=107&44=110&46=114&47=116&48=119&49=122&50=126&51=129&52=133&53=136'