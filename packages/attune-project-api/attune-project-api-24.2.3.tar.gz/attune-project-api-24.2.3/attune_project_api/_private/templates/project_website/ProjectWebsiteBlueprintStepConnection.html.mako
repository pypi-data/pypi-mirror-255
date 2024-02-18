<%page args="step"/>

<%
    from attune_project_api.items.step_tuples.step_tuple import (
        StepTupleTypeEnum,
        )

    hcpLang = {BashLexer : "bash",
        PerlLexer : "bash",
        PythonLexer : "python",
        PowerShellLexer : "powershell",
        BatchLexer : "batch",
        SqlLexer : "sql",
        }.get(Lexer, "plain")

%>

% if step.type == StepTupleTypeEnum.GROUP.value:
    <% return STOP_RENDERING %>
% endif

% if step.type == StepTupleTypeEnum.PROJECT_LINK.value:
    <% return STOP_RENDERING %>
% endif

<%
    connKey = '%s, %s, %s' % (
        step.server.key,
        step.osCred.key if hasattr(step, "osCred") else None,
        step.sqlCred.key if hasattr(step, "sqlCred") else None
    )
    connDetailsUnchanged = makoGlobal.get('connKey') == connKey
    makoGlobal['connKey'] = connKey
%>

% if connDetailsUnchanged:
    <% return STOP_RENDERING %>
% endif

% if getattr(step, "server", None) and getattr(step, "osCred", None):
    % if step.server.type == step.server.LIN_SERVER:
                        <div class="row">
                            <p>
                                Connect via ssh:
                            </p>
                        </div>
                        <div class="row py-1">
                            <code class="language-${hcpLang}">
ssh {${step.osCred.key}}@{${step.server.key}}
                            </code>
                        </div>
        % if getattr(step, "sqlCred", None):
                        <div class="row py-1">
                            <code class="language-${hcpLang}">
# Use details from parameter
# ${step.sqlCred.name}
sqlplus username/password@service_id
                            </code>
                        </div>
        % endif
    % elif step.server.type == step.server.WIN_SERVER:
                        <div class="row">
                            <p>
                                Connect via RDP:
                            </p>
                        </div>
                        <div class="row py-1">
                            <code class="language-${hcpLang}">
mstsc /admin /v:{${step.server.key}}
                            </code>
                        </div>
                        <div class="row">
                            <p>
                                Login as user {${step.osCred.key}} and open a
                                command prompt.
                            </p>
                        </div>
    % endif
% endif