from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/flow-tracking.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_flow_tracking = resolve('flow_tracking')
    l_0_flow_trackings = resolve('flow_trackings')
    l_0_sample_size = resolve('sample_size')
    l_0_min_sample_size = resolve('min_sample_size')
    l_0_hardware_offload_ipv4 = resolve('hardware_offload_ipv4')
    l_0_hardware_offload_ipv6 = resolve('hardware_offload_ipv6')
    l_0_encapsulations_list = resolve('encapsulations_list')
    l_0_encapsulations = resolve('encapsulations')
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
    if (t_5((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking)) or t_5((undefined(name='flow_trackings') if l_0_flow_trackings is missing else l_0_flow_trackings))):
        pass
        yield '\n### Flow Tracking\n'
        if (t_5(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled')) or t_5((undefined(name='flow_trackings') if l_0_flow_trackings is missing else l_0_flow_trackings))):
            pass
            yield '\n#### Flow Tracking Sampled\n\n| Sample Size | Minimum Sample Size | Hardware Offload for IPv4 | Hardware Offload for IPv6 | Encapsulations |\n| ----------- | ------------------- | ------------------------- | ------------------------- | -------------- |\n'
            l_0_sample_size = t_1(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'sample'), environment.getattr(environment.getitem((undefined(name='flow_trackings') if l_0_flow_trackings is missing else l_0_flow_trackings), 0), 'sample'), 'default')
            context.vars['sample_size'] = l_0_sample_size
            context.exported_vars.add('sample_size')
            l_0_min_sample_size = t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'threshold_minimum'), 'default')
            context.vars['min_sample_size'] = l_0_min_sample_size
            context.exported_vars.add('min_sample_size')
            l_0_hardware_offload_ipv4 = 'disabled'
            context.vars['hardware_offload_ipv4'] = l_0_hardware_offload_ipv4
            context.exported_vars.add('hardware_offload_ipv4')
            l_0_hardware_offload_ipv6 = 'disabled'
            context.vars['hardware_offload_ipv6'] = l_0_hardware_offload_ipv6
            context.exported_vars.add('hardware_offload_ipv6')
            l_0_encapsulations_list = []
            context.vars['encapsulations_list'] = l_0_encapsulations_list
            context.exported_vars.add('encapsulations_list')
            if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'encapsulation'), 'ipv4_ipv6'), True):
                pass
                context.call(environment.getattr((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list), 'append'), 'ipv4')
                context.call(environment.getattr((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list), 'append'), 'ipv6')
                if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'encapsulation'), 'mpls'), True):
                    pass
                    context.call(environment.getattr((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list), 'append'), 'mpls')
            l_0_encapsulations = t_3(context.eval_ctx, ((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list) or ['-']), ', ')
            context.vars['encapsulations'] = l_0_encapsulations
            context.exported_vars.add('encapsulations')
            if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'ipv4'), True):
                pass
                l_0_hardware_offload_ipv4 = 'enabled'
                context.vars['hardware_offload_ipv4'] = l_0_hardware_offload_ipv4
                context.exported_vars.add('hardware_offload_ipv4')
            if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'ipv6'), True):
                pass
                l_0_hardware_offload_ipv6 = 'enabled'
                context.vars['hardware_offload_ipv6'] = l_0_hardware_offload_ipv6
                context.exported_vars.add('hardware_offload_ipv6')
            yield '| '
            yield str((undefined(name='sample_size') if l_0_sample_size is missing else l_0_sample_size))
            yield ' | '
            yield str((undefined(name='min_sample_size') if l_0_min_sample_size is missing else l_0_min_sample_size))
            yield ' | '
            yield str((undefined(name='hardware_offload_ipv4') if l_0_hardware_offload_ipv4 is missing else l_0_hardware_offload_ipv4))
            yield ' | '
            yield str((undefined(name='hardware_offload_ipv6') if l_0_hardware_offload_ipv6 is missing else l_0_hardware_offload_ipv6))
            yield ' | '
            yield str((undefined(name='encapsulations') if l_0_encapsulations is missing else l_0_encapsulations))
            yield ' |\n'
            if (t_5(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'trackers')) or t_5(environment.getattr(environment.getitem((undefined(name='flow_trackings') if l_0_flow_trackings is missing else l_0_flow_trackings), 0), 'trackers'))):
                pass
                yield '\n##### Trackers Summary\n\n| Tracker Name | Record Export On Inactive Timeout | Record Export On Interval | MPLS | Number of Exporters | Applied On | Table Size |\n| ------------ | --------------------------------- | ------------------------- | ---- | ------------------- | ---------- | ---------- |\n'
                for l_1_tracker in t_2(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'trackers'), 'name'):
                    l_1_ethernet_interfaces = resolve('ethernet_interfaces')
                    l_1_port_channel_interfaces = resolve('port_channel_interfaces')
                    l_1_on_inactive_timeout = l_1_on_interval = l_1_mpls = l_1_count_exporter = l_1_applied_on = l_1_table_size = missing
                    _loop_vars = {}
                    pass
                    l_1_on_inactive_timeout = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout'), '-')
                    _loop_vars['on_inactive_timeout'] = l_1_on_inactive_timeout
                    l_1_on_interval = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval'), '-')
                    _loop_vars['on_interval'] = l_1_on_interval
                    l_1_mpls = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'mpls'), '-')
                    _loop_vars['mpls'] = l_1_mpls
                    l_1_count_exporter = t_4(t_1(environment.getattr(l_1_tracker, 'exporters'), []))
                    _loop_vars['count_exporter'] = l_1_count_exporter
                    l_1_applied_on = []
                    _loop_vars['applied_on'] = l_1_applied_on
                    l_1_table_size = t_1(environment.getattr(l_1_tracker, 'table_size'), '-')
                    _loop_vars['table_size'] = l_1_table_size
                    for l_2_ethernet_interface in t_1((undefined(name='ethernet_interfaces') if l_1_ethernet_interfaces is missing else l_1_ethernet_interfaces), []):
                        _loop_vars = {}
                        pass
                        if t_5(environment.getattr(environment.getattr(l_2_ethernet_interface, 'flow_tracker'), 'sampled'), environment.getattr(l_1_tracker, 'name')):
                            pass
                            context.call(environment.getattr((undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), 'append'), environment.getattr(l_2_ethernet_interface, 'name'), _loop_vars=_loop_vars)
                    l_2_ethernet_interface = missing
                    for l_2_port_channel_interface in t_1((undefined(name='port_channel_interfaces') if l_1_port_channel_interfaces is missing else l_1_port_channel_interfaces), []):
                        _loop_vars = {}
                        pass
                        if t_5(environment.getattr(environment.getattr(l_2_port_channel_interface, 'flow_tracker'), 'sampled'), environment.getattr(l_1_tracker, 'name')):
                            pass
                            context.call(environment.getattr((undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), 'append'), environment.getattr(l_2_port_channel_interface, 'name'), _loop_vars=_loop_vars)
                    l_2_port_channel_interface = missing
                    yield '| '
                    yield str(environment.getattr(l_1_tracker, 'name'))
                    yield ' | '
                    yield str((undefined(name='on_inactive_timeout') if l_1_on_inactive_timeout is missing else l_1_on_inactive_timeout))
                    yield ' | '
                    yield str((undefined(name='on_interval') if l_1_on_interval is missing else l_1_on_interval))
                    yield ' | '
                    yield str((undefined(name='mpls') if l_1_mpls is missing else l_1_mpls))
                    yield ' | '
                    yield str((undefined(name='count_exporter') if l_1_count_exporter is missing else l_1_count_exporter))
                    yield ' | '
                    yield str(t_3(context.eval_ctx, (undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), '<br>'))
                    yield ' | '
                    yield str((undefined(name='table_size') if l_1_table_size is missing else l_1_table_size))
                    yield ' |\n'
                l_1_tracker = l_1_on_inactive_timeout = l_1_on_interval = l_1_mpls = l_1_count_exporter = l_1_applied_on = l_1_table_size = l_1_ethernet_interfaces = l_1_port_channel_interfaces = missing
                for l_1_flow_tracking_obj in t_1((undefined(name='flow_trackings') if l_0_flow_trackings is missing else l_0_flow_trackings), []):
                    _loop_vars = {}
                    pass
                    for l_2_tracker in t_2(environment.getattr(l_1_flow_tracking_obj, 'trackers'), 'name'):
                        l_2_ethernet_interfaces = resolve('ethernet_interfaces')
                        l_2_port_channel_interfaces = resolve('port_channel_interfaces')
                        l_2_on_inactive_timeout = l_2_on_interval = l_2_mpls = l_2_count_exporter = l_2_applied_on = l_2_table_size = missing
                        _loop_vars = {}
                        pass
                        l_2_on_inactive_timeout = t_1(environment.getattr(environment.getattr(l_2_tracker, 'record_export'), 'on_inactive_timeout'), '-')
                        _loop_vars['on_inactive_timeout'] = l_2_on_inactive_timeout
                        l_2_on_interval = t_1(environment.getattr(environment.getattr(l_2_tracker, 'record_export'), 'on_interval'), '-')
                        _loop_vars['on_interval'] = l_2_on_interval
                        l_2_mpls = t_1(environment.getattr(environment.getattr(l_2_tracker, 'record_export'), 'mpls'), '-')
                        _loop_vars['mpls'] = l_2_mpls
                        l_2_count_exporter = t_4(t_1(environment.getattr(l_2_tracker, 'exporters'), []))
                        _loop_vars['count_exporter'] = l_2_count_exporter
                        l_2_applied_on = []
                        _loop_vars['applied_on'] = l_2_applied_on
                        l_2_table_size = t_1(environment.getattr(l_2_tracker, 'table_size'), '-')
                        _loop_vars['table_size'] = l_2_table_size
                        for l_3_ethernet_interface in t_1((undefined(name='ethernet_interfaces') if l_2_ethernet_interfaces is missing else l_2_ethernet_interfaces), []):
                            _loop_vars = {}
                            pass
                            if t_5(environment.getattr(environment.getattr(l_3_ethernet_interface, 'flow_tracker'), 'sampled'), environment.getattr(l_2_tracker, 'name')):
                                pass
                                context.call(environment.getattr((undefined(name='applied_on') if l_2_applied_on is missing else l_2_applied_on), 'append'), environment.getattr(l_3_ethernet_interface, 'name'), _loop_vars=_loop_vars)
                        l_3_ethernet_interface = missing
                        for l_3_port_channel_interface in t_1((undefined(name='port_channel_interfaces') if l_2_port_channel_interfaces is missing else l_2_port_channel_interfaces), []):
                            _loop_vars = {}
                            pass
                            if t_5(environment.getattr(environment.getattr(l_3_port_channel_interface, 'flow_tracker'), 'sampled'), environment.getattr(l_2_tracker, 'name')):
                                pass
                                context.call(environment.getattr((undefined(name='applied_on') if l_2_applied_on is missing else l_2_applied_on), 'append'), environment.getattr(l_3_port_channel_interface, 'name'), _loop_vars=_loop_vars)
                        l_3_port_channel_interface = missing
                        yield '| '
                        yield str(environment.getattr(l_2_tracker, 'name'))
                        yield ' | '
                        yield str((undefined(name='on_inactive_timeout') if l_2_on_inactive_timeout is missing else l_2_on_inactive_timeout))
                        yield ' | '
                        yield str((undefined(name='on_interval') if l_2_on_interval is missing else l_2_on_interval))
                        yield ' | '
                        yield str((undefined(name='mpls') if l_2_mpls is missing else l_2_mpls))
                        yield ' | '
                        yield str((undefined(name='count_exporter') if l_2_count_exporter is missing else l_2_count_exporter))
                        yield ' | '
                        yield str(t_3(context.eval_ctx, (undefined(name='applied_on') if l_2_applied_on is missing else l_2_applied_on), '<br>'))
                        yield ' | '
                        yield str((undefined(name='table_size') if l_2_table_size is missing else l_2_table_size))
                        yield ' |\n'
                    l_2_tracker = l_2_on_inactive_timeout = l_2_on_interval = l_2_mpls = l_2_count_exporter = l_2_applied_on = l_2_table_size = l_2_ethernet_interfaces = l_2_port_channel_interfaces = missing
                l_1_flow_tracking_obj = missing
                yield '\n##### Exporters Summary\n\n| Tracker Name | Exporter Name | Collector IP/Host | Collector Port | Local Interface |\n| ------------ | ------------- | ----------------- | -------------- | --------------- |\n'
                for l_1_tracker in t_2(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'trackers'), 'name'):
                    _loop_vars = {}
                    pass
                    for l_2_exporter in t_2(environment.getattr(l_1_tracker, 'exporters'), 'name'):
                        l_2_host = l_2_port = l_2_local_interface = missing
                        _loop_vars = {}
                        pass
                        l_2_host = t_1(environment.getattr(l_2_exporter, 'host'), '-')
                        _loop_vars['host'] = l_2_host
                        l_2_port = t_1(environment.getattr(l_2_exporter, 'port'), '-')
                        _loop_vars['port'] = l_2_port
                        l_2_local_interface = t_1(environment.getattr(l_2_exporter, 'local_interface'), 'No local interface')
                        _loop_vars['local_interface'] = l_2_local_interface
                        yield '| '
                        yield str(environment.getattr(l_1_tracker, 'name'))
                        yield ' | '
                        yield str(environment.getattr(l_2_exporter, 'name'))
                        yield ' | '
                        yield str((undefined(name='host') if l_2_host is missing else l_2_host))
                        yield ' | '
                        yield str((undefined(name='port') if l_2_port is missing else l_2_port))
                        yield ' | '
                        yield str((undefined(name='local_interface') if l_2_local_interface is missing else l_2_local_interface))
                        yield ' |\n'
                    l_2_exporter = l_2_host = l_2_port = l_2_local_interface = missing
                l_1_tracker = missing
                for l_1_flow_tracking_obj in t_1((undefined(name='flow_trackings') if l_0_flow_trackings is missing else l_0_flow_trackings), []):
                    _loop_vars = {}
                    pass
                    for l_2_tracker in t_2(environment.getattr(l_1_flow_tracking_obj, 'trackers'), 'name'):
                        _loop_vars = {}
                        pass
                        for l_3_exporter in t_2(environment.getattr(l_2_tracker, 'exporters'), 'name'):
                            l_3_host = l_3_port = l_3_local_interface = missing
                            _loop_vars = {}
                            pass
                            l_3_host = t_1(environment.getattr(l_3_exporter, 'host'), '-')
                            _loop_vars['host'] = l_3_host
                            l_3_port = t_1(environment.getattr(l_3_exporter, 'port'), '-')
                            _loop_vars['port'] = l_3_port
                            l_3_local_interface = t_1(environment.getattr(l_3_exporter, 'local_interface'), 'No local interface')
                            _loop_vars['local_interface'] = l_3_local_interface
                            yield '| '
                            yield str(environment.getattr(l_2_tracker, 'name'))
                            yield ' | '
                            yield str(environment.getattr(l_3_exporter, 'name'))
                            yield ' | '
                            yield str((undefined(name='host') if l_3_host is missing else l_3_host))
                            yield ' | '
                            yield str((undefined(name='port') if l_3_port is missing else l_3_port))
                            yield ' | '
                            yield str((undefined(name='local_interface') if l_3_local_interface is missing else l_3_local_interface))
                            yield ' |\n'
                        l_3_exporter = l_3_host = l_3_port = l_3_local_interface = missing
                    l_2_tracker = missing
                l_1_flow_tracking_obj = missing
        if t_5(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware')):
            pass
            yield '\n#### Flow Tracking Hardware\n\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'trackers')):
                pass
                yield '##### Trackers Summary\n\n| Tracker Name | Record Export On Inactive Timeout | Record Export On Interval | Number of Exporters | Applied On |\n| ------------ | --------------------------------- | ------------------------- | ------------------- | ---------- |\n'
                for l_1_tracker in t_2(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'trackers'), 'name'):
                    l_1_ethernet_interfaces = resolve('ethernet_interfaces')
                    l_1_port_channel_interfaces = resolve('port_channel_interfaces')
                    l_1_on_inactive_timeout = l_1_on_interval = l_1_count_exporter = l_1_applied_on = missing
                    _loop_vars = {}
                    pass
                    l_1_on_inactive_timeout = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout'), '-')
                    _loop_vars['on_inactive_timeout'] = l_1_on_inactive_timeout
                    l_1_on_interval = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval'), '-')
                    _loop_vars['on_interval'] = l_1_on_interval
                    l_1_count_exporter = t_4(t_1(environment.getattr(l_1_tracker, 'exporters'), []))
                    _loop_vars['count_exporter'] = l_1_count_exporter
                    l_1_applied_on = []
                    _loop_vars['applied_on'] = l_1_applied_on
                    for l_2_ethernet_interface in t_1((undefined(name='ethernet_interfaces') if l_1_ethernet_interfaces is missing else l_1_ethernet_interfaces), []):
                        _loop_vars = {}
                        pass
                        if t_5(environment.getattr(environment.getattr(l_2_ethernet_interface, 'flow_tracker'), 'hardware'), environment.getattr(l_1_tracker, 'name')):
                            pass
                            context.call(environment.getattr((undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), 'append'), environment.getattr(l_2_ethernet_interface, 'name'), _loop_vars=_loop_vars)
                    l_2_ethernet_interface = missing
                    for l_2_port_channel_interface in t_1((undefined(name='port_channel_interfaces') if l_1_port_channel_interfaces is missing else l_1_port_channel_interfaces), []):
                        _loop_vars = {}
                        pass
                        if t_5(environment.getattr(environment.getattr(l_2_port_channel_interface, 'flow_tracker'), 'hardware'), environment.getattr(l_1_tracker, 'name')):
                            pass
                            context.call(environment.getattr((undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), 'append'), environment.getattr(l_2_port_channel_interface, 'name'), _loop_vars=_loop_vars)
                    l_2_port_channel_interface = missing
                    yield '| '
                    yield str(environment.getattr(l_1_tracker, 'name'))
                    yield ' | '
                    yield str((undefined(name='on_inactive_timeout') if l_1_on_inactive_timeout is missing else l_1_on_inactive_timeout))
                    yield ' | '
                    yield str((undefined(name='on_interval') if l_1_on_interval is missing else l_1_on_interval))
                    yield ' | '
                    yield str((undefined(name='count_exporter') if l_1_count_exporter is missing else l_1_count_exporter))
                    yield ' | '
                    yield str(t_3(context.eval_ctx, (undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), '<br>'))
                    yield ' |\n'
                l_1_tracker = l_1_on_inactive_timeout = l_1_on_interval = l_1_count_exporter = l_1_applied_on = l_1_ethernet_interfaces = l_1_port_channel_interfaces = missing
                yield '\n##### Exporters Summary\n\n| Tracker Name | Exporter Name | Collector IP/Host | Collector Port | Local Interface |\n| ------------ | ------------- | ----------------- | -------------- | --------------- |\n'
                for l_1_tracker in t_2(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'trackers'), 'name'):
                    _loop_vars = {}
                    pass
                    for l_2_exporter in t_2(environment.getattr(l_1_tracker, 'exporters'), 'name'):
                        l_2_host = l_2_port = l_2_local_interface = missing
                        _loop_vars = {}
                        pass
                        l_2_host = t_1(environment.getattr(l_2_exporter, 'host'), '-')
                        _loop_vars['host'] = l_2_host
                        l_2_port = t_1(environment.getattr(l_2_exporter, 'port'), '-')
                        _loop_vars['port'] = l_2_port
                        l_2_local_interface = t_1(environment.getattr(l_2_exporter, 'local_interface'), 'No local interface')
                        _loop_vars['local_interface'] = l_2_local_interface
                        yield '| '
                        yield str(environment.getattr(l_1_tracker, 'name'))
                        yield ' | '
                        yield str(environment.getattr(l_2_exporter, 'name'))
                        yield ' | '
                        yield str((undefined(name='host') if l_2_host is missing else l_2_host))
                        yield ' | '
                        yield str((undefined(name='port') if l_2_port is missing else l_2_port))
                        yield ' | '
                        yield str((undefined(name='local_interface') if l_2_local_interface is missing else l_2_local_interface))
                        yield ' |\n'
                    l_2_exporter = l_2_host = l_2_port = l_2_local_interface = missing
                l_1_tracker = missing
        yield '\n#### Flow Tracking Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/flow-tracking.j2', 'documentation/flow-tracking.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {'encapsulations': l_0_encapsulations, 'encapsulations_list': l_0_encapsulations_list, 'hardware_offload_ipv4': l_0_hardware_offload_ipv4, 'hardware_offload_ipv6': l_0_hardware_offload_ipv6, 'min_sample_size': l_0_min_sample_size, 'sample_size': l_0_sample_size})):
            yield event
        template = environment.get_template('eos/flow-trackings.j2', 'documentation/flow-tracking.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {'encapsulations': l_0_encapsulations, 'encapsulations_list': l_0_encapsulations_list, 'hardware_offload_ipv4': l_0_hardware_offload_ipv4, 'hardware_offload_ipv6': l_0_hardware_offload_ipv6, 'min_sample_size': l_0_min_sample_size, 'sample_size': l_0_sample_size})):
            yield event
        yield '```\n'

blocks = {}
debug_info = '7=49&11=52&17=55&18=58&19=61&20=64&21=67&22=70&23=72&24=73&25=74&26=76&29=77&30=80&31=82&33=85&34=87&36=91&37=101&43=104&44=110&45=112&46=114&47=116&48=118&49=120&50=122&51=125&52=127&55=129&56=132&57=134&60=137&63=152&64=155&65=161&66=163&67=165&68=167&69=169&70=171&71=173&72=176&73=178&76=180&77=183&78=185&81=188&89=205&90=208&91=212&92=214&93=216&94=219&98=231&99=234&100=237&101=241&102=243&103=245&104=248&110=261&114=264&119=267&120=273&121=275&122=277&123=279&124=281&125=284&126=286&129=288&130=291&131=293&134=296&141=308&142=311&143=315&144=317&145=319&146=322&155=335&156=338'