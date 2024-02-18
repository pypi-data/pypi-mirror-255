from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/radius-server.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_radius_servers = resolve('radius_servers')
    l_0_radius_server = resolve('radius_server')
    l_0_doc_line = resolve('doc_line')
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
    if (t_2((undefined(name='radius_servers') if l_0_radius_servers is missing else l_0_radius_servers)) or t_2((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server))):
        pass
        yield '\n### RADIUS Server\n'
        if t_2(environment.getattr((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server), 'attribute_32_include_in_access_req')):
            pass
            l_0_doc_line = '- Attribute 32 is included in access requests'
            context.vars['doc_line'] = l_0_doc_line
            context.exported_vars.add('doc_line')
            if t_2(environment.getattr(environment.getattr((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server), 'attribute_32_include_in_access_req'), 'hostname'), True):
                pass
                l_0_doc_line = str_join(((undefined(name='doc_line') if l_0_doc_line is missing else l_0_doc_line), ' using hostname', ))
                context.vars['doc_line'] = l_0_doc_line
                context.exported_vars.add('doc_line')
            elif t_2(environment.getattr(environment.getattr((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server), 'attribute_32_include_in_access_req'), 'format')):
                pass
                l_0_doc_line = str_join(((undefined(name='doc_line') if l_0_doc_line is missing else l_0_doc_line), " using format '", environment.getattr(environment.getattr((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server), 'attribute_32_include_in_access_req'), 'format'), "'", ))
                context.vars['doc_line'] = l_0_doc_line
                context.exported_vars.add('doc_line')
            yield '\n'
            yield str((undefined(name='doc_line') if l_0_doc_line is missing else l_0_doc_line))
            yield '\n'
        if t_2(environment.getattr((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server), 'dynamic_authorization')):
            pass
            l_0_doc_line = '- Dynamic Authorization is enabled'
            context.vars['doc_line'] = l_0_doc_line
            context.exported_vars.add('doc_line')
            if t_2(environment.getattr(environment.getattr((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server), 'dynamic_authorization'), 'port')):
                pass
                l_0_doc_line = str_join(((undefined(name='doc_line') if l_0_doc_line is missing else l_0_doc_line), ' on port ', environment.getattr(environment.getattr((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server), 'dynamic_authorization'), 'port'), ))
                context.vars['doc_line'] = l_0_doc_line
                context.exported_vars.add('doc_line')
            if t_2(environment.getattr(environment.getattr((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server), 'dynamic_authorization'), 'tls_ssl_profile')):
                pass
                l_0_doc_line = str_join(((undefined(name='doc_line') if l_0_doc_line is missing else l_0_doc_line), ' with SSL profile ', environment.getattr(environment.getattr((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server), 'dynamic_authorization'), 'tls_ssl_profile'), ))
                context.vars['doc_line'] = l_0_doc_line
                context.exported_vars.add('doc_line')
            yield '\n'
            yield str((undefined(name='doc_line') if l_0_doc_line is missing else l_0_doc_line))
            yield '\n'
        yield '\n#### RADIUS Server Hosts\n\n| VRF | RADIUS Servers | Timeout | Retransmit |\n| --- | -------------- | ------- | ---------- |\n'
        for l_1_radius_server in t_1((undefined(name='radius_servers') if l_0_radius_servers is missing else l_0_radius_servers), []):
            l_1_vrf = l_1_timeout = l_1_retransmit = missing
            _loop_vars = {}
            pass
            l_1_vrf = t_1(environment.getattr(l_1_radius_server, 'vrf'), 'default')
            _loop_vars['vrf'] = l_1_vrf
            l_1_timeout = t_1(environment.getattr(l_1_radius_server, 'timeout'), '-')
            _loop_vars['timeout'] = l_1_timeout
            l_1_retransmit = t_1(environment.getattr(l_1_radius_server, 'retransmit'), '-')
            _loop_vars['retransmit'] = l_1_retransmit
            yield '| '
            yield str((undefined(name='vrf') if l_1_vrf is missing else l_1_vrf))
            yield ' | '
            yield str(environment.getattr(l_1_radius_server, 'host'))
            yield ' | '
            yield str((undefined(name='timeout') if l_1_timeout is missing else l_1_timeout))
            yield ' | '
            yield str((undefined(name='retransmit') if l_1_retransmit is missing else l_1_retransmit))
            yield ' |\n'
        l_1_radius_server = l_1_vrf = l_1_timeout = l_1_retransmit = missing
        for l_1_host in t_1(environment.getattr((undefined(name='radius_server') if l_0_radius_server is missing else l_0_radius_server), 'hosts'), []):
            l_1_vrf = l_1_timeout = l_1_retransmit = missing
            _loop_vars = {}
            pass
            l_1_vrf = t_1(environment.getattr(l_1_host, 'vrf'), 'default')
            _loop_vars['vrf'] = l_1_vrf
            l_1_timeout = t_1(environment.getattr(l_1_host, 'timeout'), '-')
            _loop_vars['timeout'] = l_1_timeout
            l_1_retransmit = t_1(environment.getattr(l_1_host, 'retransmit'), '-')
            _loop_vars['retransmit'] = l_1_retransmit
            yield '| '
            yield str((undefined(name='vrf') if l_1_vrf is missing else l_1_vrf))
            yield ' | '
            yield str(environment.getattr(l_1_host, 'host'))
            yield ' | '
            yield str((undefined(name='timeout') if l_1_timeout is missing else l_1_timeout))
            yield ' | '
            yield str((undefined(name='retransmit') if l_1_retransmit is missing else l_1_retransmit))
            yield ' |\n'
        l_1_host = l_1_vrf = l_1_timeout = l_1_retransmit = missing
        yield '\n#### RADIUS Server Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/radius-servers.j2', 'documentation/radius-server.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {'doc_line': l_0_doc_line})):
            yield event
        template = environment.get_template('eos/radius-server.j2', 'documentation/radius-server.j2')
        for event in template.root_render_func(template.new_context(context.get_all(), True, {'doc_line': l_0_doc_line})):
            yield event
        yield '```\n'

blocks = {}
debug_info = '7=26&10=29&11=31&12=34&13=36&14=39&15=41&18=45&20=47&21=49&22=52&23=54&25=57&26=59&29=63&37=66&38=70&39=72&40=74&41=77&44=86&45=90&46=92&47=94&48=97&54=107&55=110'