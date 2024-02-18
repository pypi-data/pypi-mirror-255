from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/flow-tracking.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_flow_tracking = resolve('flow_tracking')
    l_0_encapsulation = resolve('encapsulation')
    l_0_hardware_offload_protocols = resolve('hardware_offload_protocols')
    try:
        t_1 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_2 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_3(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled')):
        pass
        yield '!\nflow tracking sampled\n'
        if t_3(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'encapsulation')):
            pass
            l_0_encapsulation = 'encapsulation'
            context.vars['encapsulation'] = l_0_encapsulation
            context.exported_vars.add('encapsulation')
            if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'encapsulation'), 'ipv4_ipv6'), True):
                pass
                l_0_encapsulation = str_join(((undefined(name='encapsulation') if l_0_encapsulation is missing else l_0_encapsulation), ' ipv4 ipv6', ))
                context.vars['encapsulation'] = l_0_encapsulation
                context.exported_vars.add('encapsulation')
                if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'encapsulation'), 'mpls'), True):
                    pass
                    l_0_encapsulation = str_join(((undefined(name='encapsulation') if l_0_encapsulation is missing else l_0_encapsulation), ' mpls', ))
                    context.vars['encapsulation'] = l_0_encapsulation
                    context.exported_vars.add('encapsulation')
            yield '   '
            yield str((undefined(name='encapsulation') if l_0_encapsulation is missing else l_0_encapsulation))
            yield '\n'
        if t_3(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'sample')):
            pass
            yield '   sample '
            yield str(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'sample'))
            yield '\n'
        if t_3(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload')):
            pass
            l_0_hardware_offload_protocols = []
            context.vars['hardware_offload_protocols'] = l_0_hardware_offload_protocols
            context.exported_vars.add('hardware_offload_protocols')
            if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'ipv4'), True):
                pass
                context.call(environment.getattr((undefined(name='hardware_offload_protocols') if l_0_hardware_offload_protocols is missing else l_0_hardware_offload_protocols), 'append'), 'ipv4')
            if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'ipv6'), True):
                pass
                context.call(environment.getattr((undefined(name='hardware_offload_protocols') if l_0_hardware_offload_protocols is missing else l_0_hardware_offload_protocols), 'append'), 'ipv6')
            if (t_2((undefined(name='hardware_offload_protocols') if l_0_hardware_offload_protocols is missing else l_0_hardware_offload_protocols)) > 0):
                pass
                yield '   hardware offload '
                yield str(t_1(context.eval_ctx, (undefined(name='hardware_offload_protocols') if l_0_hardware_offload_protocols is missing else l_0_hardware_offload_protocols), ' '))
                yield '\n'
            if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'threshold_minimum')):
                pass
                yield '   hardware offload threshold minimum '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'threshold_minimum'))
                yield ' samples\n'
        for l_1_tracker in environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'trackers'):
            _loop_vars = {}
            pass
            yield '   tracker '
            yield str(environment.getattr(l_1_tracker, 'name'))
            yield '\n'
            if t_3(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout')):
                pass
                yield '      record export on inactive timeout '
                yield str(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout'))
                yield '\n'
            if t_3(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval')):
                pass
                yield '      record export on interval '
                yield str(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval'))
                yield '\n'
            if t_3(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'mpls'), True):
                pass
                yield '      record export mpls\n'
            if t_3(environment.getattr(l_1_tracker, 'exporters')):
                pass
                for l_2_exporter in environment.getattr(l_1_tracker, 'exporters'):
                    l_2_collector_cli = resolve('collector_cli')
                    _loop_vars = {}
                    pass
                    yield '      exporter '
                    yield str(environment.getattr(l_2_exporter, 'name'))
                    yield '\n'
                    if t_3(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host')):
                        pass
                        l_2_collector_cli = str_join(('collector ', environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host'), ))
                        _loop_vars['collector_cli'] = l_2_collector_cli
                        if t_3(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'port')):
                            pass
                            l_2_collector_cli = str_join(((undefined(name='collector_cli') if l_2_collector_cli is missing else l_2_collector_cli), ' port ', environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'port'), ))
                            _loop_vars['collector_cli'] = l_2_collector_cli
                        yield '         '
                        yield str((undefined(name='collector_cli') if l_2_collector_cli is missing else l_2_collector_cli))
                        yield '\n'
                    if t_3(environment.getattr(environment.getattr(l_2_exporter, 'format'), 'ipfix_version')):
                        pass
                        yield '         format ipfix version '
                        yield str(environment.getattr(environment.getattr(l_2_exporter, 'format'), 'ipfix_version'))
                        yield '\n'
                    if t_3(environment.getattr(l_2_exporter, 'local_interface')):
                        pass
                        yield '         local interface '
                        yield str(environment.getattr(l_2_exporter, 'local_interface'))
                        yield '\n'
                    if t_3(environment.getattr(l_2_exporter, 'template_interval')):
                        pass
                        yield '         template interval '
                        yield str(environment.getattr(l_2_exporter, 'template_interval'))
                        yield '\n'
                l_2_exporter = l_2_collector_cli = missing
            if t_3(environment.getattr(l_1_tracker, 'table_size')):
                pass
                yield '      flow table size '
                yield str(environment.getattr(l_1_tracker, 'table_size'))
                yield ' entries\n'
        l_1_tracker = missing
        if t_3(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'shutdown'), False):
            pass
            yield '   no shutdown\n'
    if t_3(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware')):
        pass
        yield '!\nflow tracking hardware\n'
        for l_1_tracker in environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'trackers'):
            _loop_vars = {}
            pass
            yield '   tracker '
            yield str(environment.getattr(l_1_tracker, 'name'))
            yield '\n'
            if t_3(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout')):
                pass
                yield '      record export on inactive timeout '
                yield str(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout'))
                yield '\n'
            if t_3(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval')):
                pass
                yield '      record export on interval '
                yield str(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval'))
                yield '\n'
            if t_3(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'mpls'), True):
                pass
                yield '      record export mpls\n'
            if t_3(environment.getattr(l_1_tracker, 'exporters')):
                pass
                for l_2_exporter in environment.getattr(l_1_tracker, 'exporters'):
                    l_2_collector_cli = resolve('collector_cli')
                    _loop_vars = {}
                    pass
                    yield '      exporter '
                    yield str(environment.getattr(l_2_exporter, 'name'))
                    yield '\n'
                    if t_3(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host')):
                        pass
                        l_2_collector_cli = str_join(('collector ', environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host'), ))
                        _loop_vars['collector_cli'] = l_2_collector_cli
                        if t_3(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'port')):
                            pass
                            l_2_collector_cli = str_join(((undefined(name='collector_cli') if l_2_collector_cli is missing else l_2_collector_cli), ' port ', environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'port'), ))
                            _loop_vars['collector_cli'] = l_2_collector_cli
                        yield '         '
                        yield str((undefined(name='collector_cli') if l_2_collector_cli is missing else l_2_collector_cli))
                        yield '\n'
                    if t_3(environment.getattr(environment.getattr(l_2_exporter, 'format'), 'ipfix_version')):
                        pass
                        yield '         format ipfix version '
                        yield str(environment.getattr(environment.getattr(l_2_exporter, 'format'), 'ipfix_version'))
                        yield '\n'
                    if t_3(environment.getattr(l_2_exporter, 'local_interface')):
                        pass
                        yield '         local interface '
                        yield str(environment.getattr(l_2_exporter, 'local_interface'))
                        yield '\n'
                    if t_3(environment.getattr(l_2_exporter, 'template_interval')):
                        pass
                        yield '         template interval '
                        yield str(environment.getattr(l_2_exporter, 'template_interval'))
                        yield '\n'
                l_2_exporter = l_2_collector_cli = missing
            if t_3(environment.getattr(l_1_tracker, 'table_size')):
                pass
                yield '      flow table size '
                yield str(environment.getattr(l_1_tracker, 'table_size'))
                yield ' entries\n'
        l_1_tracker = missing
        if t_3(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'shutdown'), False):
            pass
            yield '   no shutdown\n'

blocks = {}
debug_info = '8=32&11=35&12=37&13=40&14=42&15=45&16=47&19=51&21=53&22=56&24=58&25=60&26=63&27=65&29=66&30=68&32=69&33=72&35=74&36=77&39=79&40=83&41=85&42=88&44=90&45=93&47=95&50=98&51=100&52=105&53=107&54=109&55=111&56=113&58=116&60=118&61=121&63=123&64=126&66=128&67=131&71=134&72=137&75=140&80=143&83=146&84=150&85=152&86=155&88=157&89=160&91=162&94=165&95=167&96=172&97=174&98=176&99=178&100=180&102=183&104=185&105=188&107=190&108=193&110=195&111=198&115=201&116=204&119=207'