from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/ip-nat.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_nat = resolve('ip_nat')
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
        t_3 = environment.filters['upper']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'upper' found.")
    try:
        t_4 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_4((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat)):
        pass
        yield '\n## IP NAT\n'
        if t_4(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'kernel_buffer_size')):
            pass
            yield '\n| Setting | Value |\n| -------- | ----- |\n| Kernel Buffer Size | '
            yield str(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'kernel_buffer_size'))
            yield ' MB |\n'
        if t_4(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'profiles')):
            pass
            yield '\n### NAT Profiles\n'
            for l_1_profile in t_2(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'profiles'), 'name'):
                l_1_namespace = resolve('namespace')
                l_1_ip_nat = l_0_ip_nat
                _loop_vars = {}
                pass
                yield '\n#### Profile: '
                yield str(environment.getattr(l_1_profile, 'name'))
                yield '\n'
                if t_4(environment.getattr(l_1_profile, 'vrf')):
                    pass
                    yield '\nNAT profile VRF is: '
                    yield str(environment.getattr(l_1_profile, 'vrf'))
                    yield '\n'
                l_1_ip_nat = context.call((undefined(name='namespace') if l_1_namespace is missing else l_1_namespace), dst_dyn=[], src_dyn=[], dst_static=[], src_static=[], _loop_vars=_loop_vars)
                _loop_vars['ip_nat'] = l_1_ip_nat
                for l_2_dst_dyn in t_2(t_1(environment.getattr(environment.getattr(l_1_profile, 'destination'), 'dynamic'), []), 'access_list'):
                    _loop_vars = {}
                    pass
                    context.call(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'dst_dyn'), 'append'), {'acl': environment.getattr(l_2_dst_dyn, 'access_list'), 'pool': environment.getattr(l_2_dst_dyn, 'pool_name'), 'comment': t_1(environment.getattr(l_2_dst_dyn, 'comment'), '-'), 'priority': t_1(environment.getattr(l_2_dst_dyn, 'priority'), 0)}, _loop_vars=_loop_vars)
                l_2_dst_dyn = missing
                for l_2_src_dyn in t_2(t_1(environment.getattr(environment.getattr(l_1_profile, 'source'), 'dynamic'), []), 'access_list'):
                    l_2_pool = resolve('pool')
                    l_2_valid = missing
                    _loop_vars = {}
                    pass
                    l_2_valid = False
                    _loop_vars['valid'] = l_2_valid
                    if (environment.getattr(l_2_src_dyn, 'nat_type') == 'overload'):
                        pass
                        l_2_pool = '-'
                        _loop_vars['pool'] = l_2_pool
                        l_2_valid = True
                        _loop_vars['valid'] = l_2_valid
                    elif t_4(environment.getattr(l_2_src_dyn, 'pool_name')):
                        pass
                        l_2_pool = environment.getattr(l_2_src_dyn, 'pool_name')
                        _loop_vars['pool'] = l_2_pool
                        l_2_valid = True
                        _loop_vars['valid'] = l_2_valid
                    if (undefined(name='valid') if l_2_valid is missing else l_2_valid):
                        pass
                        context.call(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'src_dyn'), 'append'), {'acl': environment.getattr(l_2_src_dyn, 'access_list'), 'type': environment.getattr(l_2_src_dyn, 'nat_type'), 'pool': (undefined(name='pool') if l_2_pool is missing else l_2_pool), 'comment': t_1(environment.getattr(l_2_src_dyn, 'comment'), '-'), 'priority': t_1(environment.getattr(l_2_src_dyn, 'priority'), 0)}, _loop_vars=_loop_vars)
                l_2_src_dyn = l_2_valid = l_2_pool = missing
                for l_2_dst_static in t_2(t_1(environment.getattr(environment.getattr(l_1_profile, 'destination'), 'static'), []), 'original_ip'):
                    _loop_vars = {}
                    pass
                    if ((not (t_4(environment.getattr(l_2_dst_static, 'access_list')) and t_4(environment.getattr(l_2_dst_static, 'group')))) and (not ((not t_4(environment.getattr(l_2_dst_static, 'original_port'))) and t_4(environment.getattr(l_2_dst_static, 'translated_port'))))):
                        pass
                        context.call(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'dst_static'), 'append'), {'direction': t_1(environment.getattr(l_2_dst_static, 'direction'), '-'), 'o_ip': environment.getattr(l_2_dst_static, 'original_ip'), 'o_port': t_1(environment.getattr(l_2_dst_static, 'original_port'), '-'), 'acl': t_1(environment.getattr(l_2_dst_static, 'access_list'), '-'), 't_ip': environment.getattr(l_2_dst_static, 'translated_ip'), 't_port': t_1(environment.getattr(l_2_dst_static, 'translated_port'), '-'), 'proto': t_1(environment.getattr(l_2_dst_static, 'protocol'), '-'), 'group': t_1(environment.getattr(l_2_dst_static, 'group'), '-'), 'priority': t_1(environment.getattr(l_2_dst_static, 'priority'), 0), 'comment': t_1(environment.getattr(l_2_dst_static, 'comment'), '-')}, _loop_vars=_loop_vars)
                l_2_dst_static = missing
                for l_2_src_static in t_2(t_1(environment.getattr(environment.getattr(l_1_profile, 'source'), 'static'), []), 'original_ip'):
                    _loop_vars = {}
                    pass
                    if ((not (t_4(environment.getattr(l_2_src_static, 'access_list')) and t_4(environment.getattr(l_2_src_static, 'group')))) and (not ((not t_4(environment.getattr(l_2_src_static, 'original_port'))) and t_4(environment.getattr(l_2_src_static, 'translated_port'))))):
                        pass
                        context.call(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'src_static'), 'append'), {'direction': t_1(environment.getattr(l_2_src_static, 'direction'), '-'), 'o_ip': environment.getattr(l_2_src_static, 'original_ip'), 'o_port': t_1(environment.getattr(l_2_src_static, 'original_port'), '-'), 'acl': t_1(environment.getattr(l_2_src_static, 'access_list'), '-'), 't_ip': environment.getattr(l_2_src_static, 'translated_ip'), 't_port': t_1(environment.getattr(l_2_src_static, 'translated_port'), '-'), 'proto': t_3(t_1(environment.getattr(l_2_src_static, 'protocol'), '-')), 'group': t_1(environment.getattr(l_2_src_static, 'group'), '-'), 'priority': t_1(environment.getattr(l_2_src_static, 'priority'), 0), 'comment': t_1(environment.getattr(l_2_src_static, 'comment'), '-')}, _loop_vars=_loop_vars)
                l_2_src_static = missing
                if environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'src_static'):
                    pass
                    yield '\n##### IP NAT: Source Static\n\n| Direction | Original IP | Original Port | Access List | Translated IP | Translated Port | Protocol | Group | Priority | Comment |\n| --------- | ----------- | ------------- | ----------- | ------------- | --------------- | -------- | ----- | -------- | ------- |\n'
                    for l_2_row in environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'src_static'):
                        _loop_vars = {}
                        pass
                        yield '| '
                        yield str(environment.getattr(l_2_row, 'direction'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'o_ip'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'o_port'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'acl'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 't_ip'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 't_port'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'proto'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'group'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'priority'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'comment'))
                        yield ' |\n'
                    l_2_row = missing
                if environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'src_dyn'):
                    pass
                    yield '\n##### IP NAT: Source Dynamic\n\n| Access List | NAT Type | Pool Name | Priority | Comment |\n| ----------- | -------- | --------- | -------- | ------- |\n'
                    for l_2_row in environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'src_dyn'):
                        _loop_vars = {}
                        pass
                        yield '| '
                        yield str(environment.getattr(l_2_row, 'acl'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'type'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'pool'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'priority'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'comment'))
                        yield ' |\n'
                    l_2_row = missing
                if environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'dst_static'):
                    pass
                    yield '\n##### IP NAT: Destination Static\n\n| Direction | Original IP | Original Port | Access List | Translated IP | Translated Port | Protocol | Group | Priority | Comment |\n| --------- | ----------- | ------------- | ----------- | ------------- | --------------- | -------- | ----- | -------- | ------- |\n'
                    for l_2_row in environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'dst_static'):
                        _loop_vars = {}
                        pass
                        yield '| '
                        yield str(environment.getattr(l_2_row, 'direction'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'o_ip'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'o_port'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'acl'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 't_ip'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 't_port'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'proto'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'group'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'priority'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'comment'))
                        yield ' |\n'
                    l_2_row = missing
                if environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'dst_dyn'):
                    pass
                    yield '\n##### IP NAT: Destination Dynamic\n\n| Access List | Pool Name | Priority | Comment |\n| ----------- | --------- | -------- | ------- |\n'
                    for l_2_row in environment.getattr((undefined(name='ip_nat') if l_1_ip_nat is missing else l_1_ip_nat), 'dst_dyn'):
                        _loop_vars = {}
                        pass
                        yield '| '
                        yield str(environment.getattr(l_2_row, 'acl'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'pool'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'priority'))
                        yield ' | '
                        yield str(environment.getattr(l_2_row, 'comment'))
                        yield ' |\n'
                    l_2_row = missing
            l_1_profile = l_1_namespace = l_1_ip_nat = missing
        if t_4(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'pools')):
            pass
            yield '\n### NAT Pools\n'
            for l_1_pool in environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'pools'):
                _loop_vars = {}
                pass
                yield '\n#### Pool: '
                yield str(environment.getattr(l_1_pool, 'name'))
                yield '\n\n| Setting | Value |\n| -------- | ----- |\n| Pool Prefix Length | '
                yield str(environment.getattr(l_1_pool, 'prefix_length'))
                yield ' |\n'
                if t_4(environment.getattr(l_1_pool, 'utilization_log_threshold')):
                    pass
                    yield '| Pool Utilization Threshold | '
                    yield str(environment.getattr(l_1_pool, 'utilization_log_threshold'))
                    yield ' % (action: log) |\n'
                yield '\n##### Pool Ranges\n\n| First IP Address  | Last IP Address | First Port | Last Port |\n| ----------------- | --------------- | ---------- | --------- |\n'
                for l_2_range in t_1(environment.getattr(l_1_pool, 'ranges'), []):
                    _loop_vars = {}
                    pass
                    yield '| '
                    yield str(environment.getattr(l_2_range, 'first_ip'))
                    yield ' | '
                    yield str(environment.getattr(l_2_range, 'last_ip'))
                    yield ' | '
                    yield str(t_1(environment.getattr(l_2_range, 'first_port'), '-'))
                    yield ' | '
                    yield str(t_1(environment.getattr(l_2_range, 'last_port'), '-'))
                    yield ' |\n'
                l_2_range = missing
            l_1_pool = missing
        if t_4(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization')):
            pass
            yield '\n### NAT Synchronization\n\n| Setting | Value |\n| -------- | ----- |\n'
            if t_1(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'shutdown'), False):
                pass
                yield '| State | Disabled !\n'
            else:
                pass
                yield '| State | Enabled !\n'
            if t_4(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'expiry_interval')):
                pass
                yield '| Expiry Interval | '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'expiry_interval'))
                yield ' Seconds |\n'
            if t_4(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'local_interface')):
                pass
                yield '| Interface | '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'local_interface'))
                yield ' |\n'
            if t_4(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'peer_address')):
                pass
                yield '| Peer IP Address | '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'peer_address'))
                yield ' |\n'
            if (t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'first_port')) and t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'last_port'))):
                pass
                yield '| Port Range | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'first_port'))
                yield ' - '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'last_port'))
                yield ' |\n'
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'split_disabled'), False):
                pass
                yield '| Port Range Split | Disabled |\n'
            else:
                pass
                yield '| Port Range Split | Enabled |\n'
        if t_4(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation')):
            pass
            yield '\n### NAT Translation Settings\n\n| Setting | Value |\n| -------- | ----- |\n'
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'address_selection'), 'any'), False):
                pass
                yield '| Address Selection | Any |\n'
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'address_selection'), 'hash_field_source_ip'), False):
                pass
                yield '| Address Selection | Hash Source IP Field |\n'
            if t_1(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'counters'), False):
                pass
                yield '| Counters | Enabled |\n'
            if t_4(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'max_entries')):
                pass
                if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'max_entries'), 'limit')):
                    pass
                    yield '| Global Connection Limit | max. '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'max_entries'), 'limit'))
                    yield ' Connections |\n'
                if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'max_entries'), 'host_limit')):
                    pass
                    yield '| per Host Connection Limit | max. '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'max_entries'), 'host_limit'))
                    yield ' Connections |\n'
                for l_1_ip_limit in t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'max_entries'), 'ip_limits'), []):
                    _loop_vars = {}
                    pass
                    yield '| IP Host '
                    yield str(environment.getattr(l_1_ip_limit, 'ip'))
                    yield ' Connection Limit | max. '
                    yield str(environment.getattr(l_1_ip_limit, 'limit'))
                    yield ' Connections |\n'
                l_1_ip_limit = missing
            if t_4(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'low_mark')):
                pass
                if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'low_mark'), 'percentage')):
                    pass
                    yield '| Global Connection Limit Low Mark | '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'low_mark'), 'percentage'))
                    yield ' % |\n'
                if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'low_mark'), 'host_percentage')):
                    pass
                    yield '| per Host Connection Limit Low Mark | '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'low_mark'), 'host_percentage'))
                    yield ' % |\n'
            for l_1_timeout in t_1(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'translation'), 'timeouts'), []):
                _loop_vars = {}
                pass
                yield '| '
                yield str(t_3(environment.getattr(l_1_timeout, 'protocol')))
                yield ' Connection Timeout | '
                yield str(environment.getattr(l_1_timeout, 'timeout'))
                yield ' Seconds |\n'
            l_1_timeout = missing
        yield '\n### IP NAT Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/ip-nat-part1.j2', 'documentation/ip-nat.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {})):
            yield event
        template = environment.get_template('eos/ip-nat-part2.j2', 'documentation/ip-nat.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {})):
            yield event
        yield '```\n'

blocks = {}
debug_info = '7=36&10=39&14=42&16=44&19=47&21=53&22=55&24=58&26=60&28=62&29=65&36=67&37=72&38=74&39=76&40=78&41=80&42=82&43=84&45=86&46=88&55=90&56=93&58=95&72=97&73=100&75=102&88=104&94=107&95=111&98=132&104=135&105=139&108=150&114=153&115=157&118=178&124=181&125=185&130=195&133=198&135=202&139=204&140=206&141=209&148=212&149=216&153=226&159=229&164=235&165=238&167=240&168=243&170=245&171=248&173=250&175=253&177=257&183=263&189=266&192=269&195=272&198=275&199=277&200=280&202=282&203=285&205=287&206=291&209=296&210=298&211=301&213=303&214=306&217=308&218=312&225=318&226=321'